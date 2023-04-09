import os
import sys
import csv
import subprocess
from datetime import datetime

import pytsk3
import pyewf
# From the python-registry library
from Registry import Registry

from .modules.artifact_extraction import ArtifactExtractor
import .modules.disk_utils

#TODO: Extend this class so it extracts registry key/value pairs to a .csv aswell
#TODO: Specify registry values which we want to extract
class RegistryExtractor(ArtifactExtractor):
    def __init__(self, output_dir, config):
        # Path to output directory
        self.output_dir = output_dir
        # Output directory inside registry directory
        self.registry_output_dir = os.path.join(output_dir, "registry")

        try:
            os.mkdir(self.registry_output_dir)
        except FileExistsError:
            pass

        # File names to process if found on recurse_files, leave empty for all of them.
        # Do not use extensions for them !

        # TODO: Support extensions, as you can see, NTUSER.DAT is the prime example of why extensions
        # may not be as trivial as they should.
        self.processable_file_names = ["system", "sam", "security", "software", "ntuser.dat", "default"]

        # Certain process_fs_object calls may want to process entire directories.
        # Leave empty if it's files you want
        # Unimplemented for now TODO in disk_utils.py
        self.processable_directories = []

        # Starting path for files we're interested it, allows us to optimize recursion
        # by only recursing into directories we're interested in. Leave empty for all of them.
        # TODO: Should be a list of paths like filenames, implement in disk_utils.py
        self.starting_path = "Windows\System32\config".lower()

        # Get keys from config
        self.keys_to_extract = self.parse_keys_to_extract(config)

        # CSV file for registry hive file info
        self.hive_csv_file = open(os.path.join(self.registry_output_dir, "registry_hive_files.csv"), "w+", newline="", encoding="utf-8")

        self.writer = csv.writer(self.hive_csv_file)
        self.writer.writerow(["Hive", "Hive Path", "Value Name", "Value Type", "Value Data", "Created At", "Modified At", "Deleted At"])

    def __del__(self):
        self.hive_csv_file.close()

    def process_fs_object(self, fs_object, file_path):
        try:
            file_name = fs_object.info.name.name
            if "RegBack".lower() in file_path.decode("utf-8").lower():
                print("[+] Found backup registry hive: {}".format(file_name.decode("utf-8")))
                self.write_registry_hive(fs_object, file_path, file_name, "")
                self.hive_file_writer(fs_object, file_name, ".regbak", self.registry_output_dir)
                outfile_path = os.path.join(self.registry_output_dir, file_name.decode("utf-8") + ".regbak")
                self.extract_key_values(outfile_path, file_name)
            else:
                print("[+] Found registry hive: {}".format(file_name.decode("utf-8")))
                self.write_registry_hive(fs_object, file_path, file_name, "")
                self.hive_file_writer(fs_object, file_name, "", self.registry_output_dir)
                outfile_path = os.path.join(self.registry_output_dir, file_name.decode("utf-8"))
                self.extract_key_values(outfile_path, file_name)
        except IOError:
            pass

    def extract_key_values(self, file_path, file_name):
            try:
                registry = Registry.Registry(file_path)
            except Registry.RegistryParse.ParseException as e:
                print("[-] Error parsing registry hive: {}".format(e))
                return

            csv_file_name = f"{file_name.decode('utf-8')}_keys.csv"
            csv_file_path = os.path.join(self.registry_output_dir, csv_file_name)
            with open(csv_file_path, "w+", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Hive Path", "Key Path", "Value Name", "Value Type", "Value Data", "Created At"])

                for hive_name, key_path, value_name in self.keys_to_extract:
                    if hive_name.lower() == file_name.decode("utf-8").lower():
                        try:
                            key = registry.open(key_path)
                            # Checks if we want a specific value under that key
                            if value_name:
                                value = key.value(value_name)

                                value_type = value.value_type_str()
                                value_data = value.value()
                                create = key.timestamp()

                                writer.writerow([file_name.decode("utf-8"), key_path, value_name, value_type, value_data, create])
                            # If not, list all values under the key
                            else:
                                for value in key.values():
                                    value_name = value.name()
                                    value_type = value.value_type_str()
                                    value_data = value.value()

                                    create = key.timestamp()

                                    writer.writerow([file_name.decode("utf-8"), key_path, value_name, value_type, value_data, create])

                        except Registry.RegistryKeyNotFoundException:
                            print(f"[-] Registry key not found: {key_path}")
                        except Registry.RegistryValueNotFoundException:
                            print(f"[-] Registry key value not found: {value_name} in {key_path}")

    def get_file_path(self, fs_object):
        file_path_parts = []
        current_object = fs_object

        while current_object.info.name.name not in [b".", b".."]:
            file_path_parts.insert(0, current_object.info.name.name.decode("utf-8"))
        return "".join(file_path_parts)

    def write_registry_hive(self, fs_object, file_path, file_name, file_suffix):
        create = self.convert_time(fs_object.info.meta.crtime)
        change = self.convert_time(fs_object.info.meta.ctime)
        modify = self.convert_time(fs_object.info.meta.mtime)
        size = fs_object.info.meta.size

        self.writer.writerow([file_name.decode("utf-8"), file_path, "", "", "", create, change, modify, ""])

    def hive_file_writer(self, fs_object, name, ext, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = name.decode("utf-8")
        filename = filename + ext
        outfile_path = os.path.join(output_dir, filename)

        with open(outfile_path, "wb") as outfile:
            outfile.write(fs_object.read_random(0, fs_object.info.meta.size))

    def parse_keys_to_extract(self, config):
        # Default if nothing in config
        keys_to_extract = [
            ("system", "ControlSet001\\Control\\ComputerName\\ComputerName", "ComputerName"),
            ("sam", "SAM\\Domains\\Account\\Users\\Names", ""),
            ("security", "Policy\\PolAdtEv", "AuditPolicy"),
            ("software", "Microsoft\\Windows\\CurrentVersion\\Run", ""),
            ("ntuser.dat", "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer", "Shell Folders"),
            ("default", "Software\\Microsoft\\Windows\\CurrentVersion\\Run", ""),
        ]

        if "keys_to_extract" in config:
            keys_to_extract = []
            for key in config["keys_to_extract"]:
                hive_name = key["hive_name"]
                key_path = key["key_path"]
                value_name = key["value_name"]
                keys_to_extract.append((hive_name, key_path, value_name))

        return keys_to_extract

    def convert_time(self, timestamp):
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
