import os
import sys
import csv
import subprocess
from datetime import datetime

import pytsk3
import pyewf

# Stolen from the Python Foresics Cookbook
# https://github.com/PacktPublishing/Python-Digital-Forensics-Cookbook
class EWFImgInfo(pytsk3.Img_Info):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super(EWFImgInfo, self).__init__(url="",
                                         type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def close(self):
        self._ewf_handle.close()

    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)

    def get_size(self):
        return self._ewf_handle.get_media_size()

def extract(ewf_file, output_dir, config):
    print("\n[*] REGISTRY MODULE [*]\n")
    registry_output_dir = os.path.join(output_dir, "registry")

    if not os.path.exists(registry_output_dir):
        os.makedirs(registry_output_dir)

    ewf_handle = pyewf.handle()
    files = pyewf.glob(ewf_file)
    ewf_handle.open(files)

    img_info = EWFImgInfo(ewf_handle)

    vol = pytsk3.Volume_Info(img_info)

    print("[+] Iterating over partitions to find FS\n")
    for part in vol:
        try:
            fs_offset = part.start * vol.info.block_size
            fs = pytsk3.FS_Info(img_info, offset=fs_offset)
            fs_info = fs.info # TSK_FS_INFO
            if (fs_info.ftype != pytsk3.TSK_FS_TYPE_NTFS):
                print("[-] Skipping non-NTFS partition at {}".format(fs_offset))
                continue
            print("[+] Opened partition at offset " + str(fs_offset))
        except IOError:
                _, e, _ = sys.exc_info()
                if "file system type" in str(e):
                    print("[-] Unable to open FS, unrecognized type at {}".format(fs_offset))
                continue

        root_dir = fs.open_dir("/")

        config_folder = find_file(b"Windows/System32/config", fs, root_dir)

        if config_folder is None:
            print("[-] Couldn't find folder containing registry files")
            continue

        # Recursively parse config looking for registry files
        print("[+] Looking for registry files recursively in Windows\System32\config\n")
        data = recurse_files(1, fs, config_folder.as_directory(), [], [], [""], output_dir)

        with open(os.path.join(registry_output_dir, "registry_hive_files.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Hive", "Key Path", "Value Name", "Value Type", "Value Data", "Created At", "Modified At", "Deleted At"])

            for reg_info in data:
                hive = reg_info[0]
                key_path = reg_info[8]
                created_at = reg_info[4]
                modified_at = reg_info[5]
                deleted_at = reg_info[6]
                writer.writerow([hive, key_path, "", "", "", created_at, modified_at, deleted_at])


def recurse_files(part, fs, root_dir, dirs, data, parent, output_dir):
    dirs.append(root_dir.info.fs_file.meta.addr)
    for fs_object in root_dir:
        # Skip ".", ".." or directory entries without a name.
        if not hasattr(fs_object, "info") or \
                not hasattr(fs_object.info, "name") or \
                not hasattr(fs_object.info.name, "name") or \
                fs_object.info.name.name in [".", ".."]:
            continue
        try:
            file_name = fs_object.info.name.name
            file_path = "Windows\\System32\\config\\{}".format("".join("{}/{}".format(str(parent), str(file_name))).replace("/", "\\"))
            if file_name in [b"SYSTEM", b"SAM", b"SECURITY", b"SOFTWARE", b"NTUSER.DAT", b"DEFAULT"]:
                if "RegBack" in file_path:
                    print("[+] Found backup registry hive: {}".format(file_name.decode("utf-8")))
                    offset = fs_object.info.meta.addr * fs.info.block_size
                    create = convert_time(fs_object.info.meta.crtime)
                    change = convert_time(fs_object.info.meta.ctime)
                    modify = convert_time(fs_object.info.meta.mtime)
                    size = fs_object.info.meta.size

                    data.append(["PARTITION {}".format(part), str(file_name), file_ext,
                        f_type, create, change, modify, size, file_path])

                    print("[+] Writing hive {}.bak to {}\n".format(file_name.decode("utf-8"), output_dir))
                    file_writer(fs_object, file_name, ".bak", output_dir)
                else:
                    print("[+] Found registry hive: {}".format(file_name.decode("utf-8")))
                    offset = fs_object.info.meta.addr * fs.info.block_size
                    create = convert_time(fs_object.info.meta.crtime)
                    change = convert_time(fs_object.info.meta.ctime)
                    modify = convert_time(fs_object.info.meta.mtime)
                    size = fs_object.info.meta.size

                    data.append(["PARTITION {}".format(part), str(file_name), file_ext,
                        f_type, create, change, modify, size, file_path])

                    print("[+] Writing hive {} to {}\n".format(file_name.decode("utf-8"), output_dir))
                    file_writer(fs_object, file_name, "", output_dir)

            try:
                if fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                    f_type = b"DIR"
                    file_ext = b""
                else:
                    f_type = b"FILE"
                    if b"." in file_name:
                        file_ext = file_name.rsplit(b".")[-1].lower()
                    else:
                        file_ext = b""
            except AttributeError:
                continue

            if f_type == b"DIR" and fs_object.info.name.name != (b".." or b"."):
                parent.append(fs_object.info.name.name)
                sub_directory = fs_object.as_directory()
                inode = fs_object.info.meta.addr

                # This ensures that we don't recurse into a directory
                # above the current level and thus avoid circular loops.
                if inode not in dirs:
                    recurse_files(part, fs, sub_directory, dirs, data, parent, output_dir)
                parent.pop(-1)

        except IOError:
            continue
    dirs.pop(-1)
    return data

def find_file(path, fs, root_dir):
    """
    Recursively search for a file with the given path
    """
    components = path.split(b'/')
    for fs_object in root_dir:
        if fs_object.info.name.name == components[0]:
            if len(components) == 1:
                # Found the file, return the fs_object
                return fs_object
            elif fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                # Recurse into the directory
                sub_dir = fs_object.as_directory()
                inode = fs_object.info.meta.addr
                return find_file(b'/'.join(components[1:]), fs, sub_dir)
    # If we get here, the file was not found
    return None

def file_writer(fs_object, name, ext, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, name.decode("utf-8")), "wb") as outfile:
        outfile.write(fs_object.read_random(0, fs_object.info.meta.size))

def convert_time(ts):
    if str(ts) == "0":
        return ""
    return datetime.utcfromtimestamp(ts)
