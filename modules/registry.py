import os
import sys
import csv
import subprocess

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
    registry_output_dir = os.path.join(output_dir, "registry")

    if not os.path.exists(registry_output_dir):
        os.makedirs(registry_output_dir)

    ewf_handle = pyewf.handle()
    files = pyewf.glob(ewf_file)
    ewf_handle.open(files)

    img_info = EWFImgInfo(ewf_handle)

    vol = pytsk3.Volume_Info(img_info)

    for part in vol:
        if part.len > 2048 and b"data partition" in part.desc:
            fs = pytsk3.FS_Info(img_info, offset=part.start * vol.info.block_size)
            fs_offset = part.start * vol.info.block_size

    # Extract the registry hives
    hives = {
        "HKLM\\SYSTEM": "C:\\Windows\\System32\\config\\SYSTEM",
        "HKLM\\SAM": "C:\\Windows\\System32\\config\\SAM",
        "HKLM\\SECURITY": "C:\\Windows\\System32\\config\\SECURITY",
        "HKLM\\SOFTWARE": "C:\\Windows\\System32\\config\\SOFTWARE",
        "HKU\\UserProfile": "C:\\Users\\Default\\NTUSER.DAT",
        "HKU\\DEFAULT": "C:\\Windows\\System32\\config\\DEFAULT"
    }

    with open(os.path.join(registry_output_dir, "registry.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Hive", "Key Path", "Value Name", "Value Type", "Value Data", "Created At", "Modified At", "Deleted At"])

        for hive_name, hive_path in hives.items():
            try:
                print(f"Parsing {hive_name} hive...")
                key = fs.open(hive_path)
                parse_key(hive_name, key, writer)
                key.close()
            except Exception as e:
                print(f"Error parsing {hive_name} hive: {e}")


    def parse_key(hive_name, key, writer):
        for value in key.recurse_values():
            writer.writerow([
                hive_name,
                key.info.fs_file.path,
                value.name,
                pyregf.data_types.REGF_VALUE_TYPES.get(value.type, "Unknown"),
                value.data_as_string(),
                value.get_time_created_as_integer(),
                value.get_time_modified_as_integer(),
                value.get_time_deleted_as_integer()
            ])

        for sub_key in key.sub_keys():
            try:
                parse_key(hive_name, sub_key, writer)
            except Exception as e:
                print(f"Error parsing {hive_name}\\{sub_key.name}: {e}")
