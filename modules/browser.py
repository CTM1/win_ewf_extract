import os
import sys
import csv
import subprocess
from datetime import datetime

import pytsk3
import pyewf

from modules.artifact_extraction import ArtifactExtractor
import modules.disk_utils

class BrowserExtractor(ArtifactExtractor):
    """This class goes into the Users folders and launches the BrowserExtraction for each user according to the Extractors
    defined in the configuration file.

    Args:
        ArtifactExtractor (_superclass_): Extends ArtifactExtractor
    """
    def __init__(self, output_dir, config):
        # Path to output directory
        self.output_dir = output_dir
        # Output directory inside registry directory
        self.browser_output_dir = os.path.join(output_dir, "browsers")

        try:
            os.mkdir(self.browser_output_dir)
        except FileExistsError:
            pass

        # File names to process if found on recurse_files, leave empty for all of them.
        # Do not use extensions for them !
        self.processable_file_names = []

        # Unimplemented for now TODO in disk_utils.py
        self.processable_directories = ["users"]

        # Here the User path can have many names
        # We'll use this class to launch browser extractors on different Users and get their AppData folder
        self.starting_path = "\\".lower()

        self.browsers_to_search = self.parse_browsers_from_config(config)

        # CSV file for registry hive file info
        self.browser_csv_file = open(os.path.join(self.browser_output_dir, "browser_files.csv"), "w+", newline="", encoding="utf-8")

        self.writer = csv.writer(self.browser_csv_file)

    def parse_browsers_from_config(self, config):
        browsers = []
        if config.get("browsers"):
            if config.get("browsers_to_extract"):
                for browser_name, enabled in config["browsers_to_extract"].items():
                    if enabled:
                        browsers.append(browser_name)
            else:
                # Add all supported browsers if 'browsers_to_extract' is not present
                browsers = ["chrome", "firefox", "edge"]
        return browsers

    def process_fs_object(self, fs_object, file_path):
        print("[+] Found Users folder")
        if fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
            user_path = file_path.decode("utf-8")
            for browser in self.browsers_to_search:
                browser_output_dir = os.path.join(self.browser_output_dir, browser)
                browser_extractor_class = globals()[f"{browser.capitalize()}Extractor"]
                browser_extractor = browser_extractor_class(user_path, self.output_dir, self.config)
                browser_extractor.process()
