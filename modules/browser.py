import os
import sys
import csv
import sqlite3
import subprocess
from datetime import datetime

import pytsk3
import pyewf

from modules.artifact_extraction import ArtifactExtractor
import modules.disk_utils as dutils
class BrowserExtractor(ArtifactExtractor):
    """This class goes into the Users folders and launches the BrowserExtraction for each user according to the Extractors
        in the configuration file.
    Args:
        ArtifactExtractor (_superclass_): Extends ArtifactExtractor
    """
    def __init__(self, output_dir, config):
        # Path to output directory
        self.output_dir = output_dir
        # Output directory inside registry directory
        self.browser_output_dir = os.path.join(output_dir, "browsers")

        self.config = config

        try:
            os.mkdir(self.browser_output_dir)
        except FileExistsError:
            pass

        self.processable_file_names = []
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

    # fs_object here is the "Users" folder, we iterate over each folder and give it to the child browser
    # extractors.
    def process_fs_object(self, fs_object, file_path):
        print("\n[BrowserExtractor] [+] Found Users folder - iterating over each\n")
        for user_folder in fs_object.as_directory():
            if hasattr(user_folder, "info") and \
                hasattr(user_folder.info, "meta") and \
                user_folder.info.name.name not in [b".", b".."] and \
                user_folder.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:

                for browser in self.browsers_to_search:
                    browser_output_dir = os.path.join(self.output_dir, "browsers", browser, user_folder.info.name.name.decode("utf8"))
                    browser_extractor_class = globals()[f"{browser.capitalize()}Extractor"]
                    print(f"[BrowserExtractor] [+] Launching {browser.capitalize()} Extractor for user " + user_folder.info.name.name.decode("utf8"))
                    try:
                        browser_extractor = browser_extractor_class(browser_output_dir, self.config, user_folder)
                    except Exception as e:
                        print(f"[BrowserExtractor] [-] Error occurred while executing {browser.capitalize()}Extractor: {e}")

class ChromeExtractor(BrowserExtractor):
    def __init__(self, output_dir, config, fs_object):
        self.output_dir = output_dir
        self.config = config

        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except FileExistsError:
            pass

        self.processable_file_names = ["History", "Archived History", "Login Data", "Web Data", "Shortcuts", "Top Sites"]
        self.processable_file_names = [name.lower() for name in self.processable_file_names]

        # Supposing root dir is an user folder
        user_folder_name = fs_object.info.name.name.decode("utf-8")
        self.starting_path = "AppData\\Local\\Google\\Chrome\\User Data\\Default".lower()

        self.extract_files(fs_object, "", self.starting_path.split("\\"))

    def extract_files(self, fs_object, current_path, target_path):
        if not target_path:
            if os.path.basename(current_path).lower() == 'default':
                self.process_default_folder(fs_object, current_path)
            return

        current_directory = fs_object.as_directory()
        next_directory_name = target_path[0].lower()

        for entry in current_directory:
            if entry is not None:
                if hasattr(entry, "info") and hasattr(entry.info, "name") and hasattr(entry.info, "meta"):
                    entry_name = entry.info.name.name.decode("utf-8").lower()
                    if entry.info.meta is not None:
                        if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR and entry_name == next_directory_name:
                            sub_current_path = os.path.join(current_path, entry_name)
                            self.extract_files(entry, sub_current_path, target_path[1:])

    def process_default_folder(self, fs_object, current_path):
        current_directory = fs_object.as_directory()
        for entry in current_directory:
            if entry is not None:
                if hasattr(entry, "info") and hasattr(entry.info, "name") and hasattr(entry.info, "meta"):
                    entry_name = entry.info.name.name.decode("utf-8").lower()
                    if entry.info.meta is not None:
                        if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG and entry_name in self.processable_file_names:
                            print(f"[ChromeExtractor] [+] Found artifact: {entry_name.capitalize()}, writing to disk...")
                            self.write_file_to_disk(entry, self.output_dir)

    def write_file_to_disk(self, file_entry, output_file_path):
        with open(os.path.join(output_file_path, file_entry.info.name.name.decode("utf-8")), "wb") as output_file:
            file_data = file_entry.read_random(0, file_entry.info.meta.size)
            output_file.write(file_data)
            print("[ChromeExtractor] [+] Successfully wrote to disk !")
class EdgeExtractor(BrowserExtractor):
    def __init__(self, output_dir, config, fs_object):
        self.output_dir = output_dir
        self.config = config

        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except FileExistsError:
            pass

        self.processable_file_names = ["History", "Archived History", "Login Data", "Web Data", "Shortcuts", "Top Sites"]
        self.processable_file_names = [name.lower() for name in self.processable_file_names]

        # Supposing root dir is an user folder
        user_folder_name = fs_object.info.name.name.decode("utf-8")
        self.starting_path = "AppData\\Local\\Microsoft\\Edge\\User Data\\Default".lower()

        self.extract_files(fs_object, "", self.starting_path.split("\\"))

    def extract_files(self, fs_object, current_path, target_path):
        if not target_path:
            if os.path.basename(current_path).lower() == 'default':
                self.process_default_folder(fs_object, current_path)
            return

        current_directory = fs_object.as_directory()
        next_directory_name = target_path[0].lower()

        for entry in current_directory:
            if entry is not None:
                if hasattr(entry, "info") and hasattr(entry.info, "name") and hasattr(entry.info, "meta"):
                    entry_name = entry.info.name.name.decode("utf-8").lower()
                    if entry.info.meta is not None:
                        if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR and entry_name == next_directory_name:
                            sub_current_path = os.path.join(current_path, entry_name)
                            self.extract_files(entry, sub_current_path, target_path[1:])

    def process_default_folder(self, fs_object, current_path):
        current_directory = fs_object.as_directory()
        for entry in current_directory:
            if entry is not None:
                if hasattr(entry, "info") and hasattr(entry.info, "name") and hasattr(entry.info, "meta"):
                    entry_name = entry.info.name.name.decode("utf-8").lower()
                    if entry.info.meta is not None:
                        if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG and entry_name in self.processable_file_names:
                            print(f"[EdgeExtractor] [+] Found artifact: {entry_name.capitalize()}, writing to disk...")
                            self.write_file_to_disk(entry, self.output_dir)

    def write_file_to_disk(self, file_entry, output_file_path):
        with open(os.path.join(output_file_path, file_entry.info.name.name.decode("utf-8")), "wb") as output_file:
            file_data = file_entry.read_random(0, file_entry.info.meta.size)
            output_file.write(file_data)
            print("[EdgeExtractor] [+] Successfully wrote to disk !")

class FirefoxExtractor(BrowserExtractor):
    def __init__(self, output_dir, config, fs_object):
        self.output_dir = output_dir
        self.config = config

        try:
            os.mkdir(self.output_dir)
        except FileExistsError:
            pass

        self.processable_file_names = ["History", "Archived History", "Cookies", "Login Data", "Web Data", "Shortcuts", "Top Sites"]
        self.processable_file_names = [name.lower() for name in self.processable_file_names]

        # Supposing root dir is an user folder
        self.starting_path = "AppData\\Local\\Google\\Chrome\\User Data\\Default".lower()
