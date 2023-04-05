import os
import sys
import csv
import subprocess
from datetime import datetime

import pytsk3
import pyewf

from modules.artifact_extraction import ArtifactExtractor
import modules.disk_utils

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

        # CSV file for registry hive file info
        self.hive_csv_file = open(os.path.join(self.registry_output_dir, "registry_hive_files.csv"), "w+", newline="", encoding="utf-8")

        self.writer = csv.writer(self.hive_csv_file)
        self.writer.writerow(["Hive", "Key Path", "Value Name", "Value Type", "Value Data", "Created At", "Modified At", "Deleted At"])

    def __del__(self):
        self.hive_csv_file.close()

    def process_fs_object(self, fs_object, file_path):
        try:
            file_name = fs_object.info.name.name
            if "RegBack".lower() in file_path.decode("utf-8").lower():
                print("[+] Found backup registry hive: {}".format(file_name.decode("utf-8")))
                self.write_registry_hive(fs_object, file_path, file_name, "")
                self.hive_file_writer(fs_object, file_name, ".regbak", self.registry_output_dir)
            else:
                print("[+] Found registry hive: {}".format(file_name.decode("utf-8")))
                self.write_registry_hive(fs_object, file_path, file_name, "")
                self.hive_file_writer(fs_object, file_name, "", self.registry_output_dir)
        except IOError:
            pass

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
        outfile_path = os.path.join(output_dir, filename)

        # Ugly file name hack
        if os.path.exists(outfile_path):
            i = 1
            while True:
                new_filename = filename + f"({i})"
                new_outfile_path = os.path.join(output_dir, new_filename)
                if not os.path.exists(new_outfile_path):
                    filename = new_filename
                    outfile_path = new_outfile_path
                    break
                i += 1

        with open(outfile_path, "wb") as outfile:
            outfile.write(fs_object.read_random(0, fs_object.info.meta.size))

    def convert_time(self, timestamp):
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
