
import os
import sys
import csv
import subprocess
from datetime import datetime
import pytsk3

import pyewf
import evtx
# From the python-registry library

from Registry import Registry
from modules.artifact_extraction import ArtifactExtractor
import modules.disk_utils

class EventLogExtractor(ArtifactExtractor):
    def __init__(self, output_dir, config):
        # Path to output directory
        self.output_dir = output_dir
        # Output directory inside registry directory
        self.evtx_output_dir = os.path.join(output_dir, "evtx")
        try:
            os.mkdir(self.registry_output_dir)
        except FileExistsError:
            pass
        self.processable_file_names = ["Applications.evtx","Setup.evtx","Security.evtx"]
        self.processable_directories = []	
        self.starting_path = "Windows\System32\Winevt\Logs".lower()
        """ cvs creations file part 
        # CSV file for registry hive file info
        self.evtx_csv_file = open(os.path.join(self.registry_output_dir, "evtx_file.csv"), "w+", newline="", encoding="utf-8")

        self.writer = csv.writer(self.evtx_csv_file)
        self.writer.writerow(["Hive", "Hive Path", "Value Name", "Value Type", "Value Data", "Created At", "Modified At", "Deleted At"])
        """

