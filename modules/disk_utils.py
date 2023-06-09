"""This file contains everything related to the actual EWF
handling.

It opens up the image, find the NTFS image and iterates
over file using ArtifactExtractor derived classes to extract
useful artifacts and pass them over to the related modules.
"""

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
    """This class represents a EWF image and contains everything needed
    by the rest of the project."""
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

def find_file_systems(img_info: EWFImgInfo) -> list[pytsk3.FS_Info]:
    """
    This function finds the various filesystems in a given EWF image.
    """
    vol = pytsk3.Volume_Info(img_info)
    fs_partitions = []

    print("[+] Iterating over partitions to find NTFS file systems\n")
    for part in vol:
        try:
            fs_offset = part.start * vol.info.block_size
            fs = pytsk3.FS_Info(img_info, offset=fs_offset)
            fs_info = fs.info # TSK_FS_INFO
            if (fs_info.ftype != pytsk3.TSK_FS_TYPE_NTFS):
                print("[-] Skipping non-NTFS partition at {}".format(fs_offset))
                continue
            print("[+] Found NTFS partition at offset " + str(fs_offset))
            fs_partitions.append(fs)
        except IOError:
                _, e, _ = sys.exc_info()
                if "file system type" in str(e):
                    print("[-] Unable to open FS, unrecognized type at {}".format(fs_offset))
                continue

    return fs_partitions


def recurse_files(fs, root_dir, dirs, parent, extractors):
    """
    This function performs a recursive search over a filesystem
    :meta private:
    """
    dirs.append(root_dir.info.fs_file.meta.addr)
    for fs_object in root_dir:
        # Skip ".", ".." or directory entries without a name.
        if not hasattr(fs_object, "info") or \
                not hasattr(fs_object.info, "name") or \
                not hasattr(fs_object.info.name, "name") or \
                fs_object.info.name.name in [".", ".."]:
            continue
        try:
            # Set wether fs_object is file or directory
            try:
                if fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                    f_type = b"DIR"
                    file_ext = b""
                else:
                    f_type = b"FILE"
                    file_name = fs_object.info.name.name

                    if b"." in file_name:
                        file_ext = file_name.rsplit(b".")[-1].lower()
                    else:
                        file_ext = b""

                    for extractor in extractors:
                        if file_name.decode("utf-8").lower() in extractor.processable_file_names:
                            file_path = b"\\".join(parent[1:])
                            extractor.process_fs_object(fs_object, file_path)

            except AttributeError:
                continue

            if f_type == b"DIR" and fs_object.info.name.name != (b".." or b"."):
                current_path = b"\\".join(parent[1:])
                folder_name = fs_object.info.name.name

                for extractor in extractors:
                    if folder_name.decode("utf-8").lower() in extractor.processable_directories:
                        folder_path = b"\\".join(parent[1:])
                        extractor.process_fs_object(fs_object, folder_path)

                # Check if any extractor's starting path starts with the current directory path
                should_recurse = (any(
                    extractor.starting_path.startswith(current_path.decode("utf-8").lower())
                    or extractor.starting_path == ""
                    for extractor in extractors
                ))

                if should_recurse:
                    parent.append(fs_object.info.name.name)
                    sub_directory = fs_object.as_directory()
                    inode = fs_object.info.meta.addr

                    # This ensures that we don't recurse into a directory
                    # above the current level and thus avoid circular loops.
                    if inode not in dirs:
                        recurse_files(fs, sub_directory, dirs, parent, extractors)
                    parent.pop(-1)

        except IOError:
            continue
    dirs.pop(-1)

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
