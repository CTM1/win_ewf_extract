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

class EventLogExtractor():
    # le paramétre config et le fichier de conf yaml
    def __init__(self, output_dir, config):
        print("hello cccccwordl", config)
        # Path to output directory
        self.output_dir = output_dir
        # Output directory inside registry directory
        self.evtx_output_dir = os.path.join(output_dir, "evtx")
        try:
            os.mkdir(self.evtx_output_dir)
        except FileExistsError:
            pass
        self.processable_file_names = ["Applications.evtx","Setup.evtx","Security.evtx"]
        self.processable_directories = []	
        self.starting_path = "Windows\System32\Winevt\Logs".lower()

        #############################################
        ## warning zone in progress 
        self.event_to_extract = self.parse_event_to_extract(config)


        #############################################
        
        #cvs creations file part 
        # CSV file for registry hive file info
        self.evtx_csv_file = open(os.path.join(self.evtx_output_dir, "evtx_file.csv"), "w+", newline="", encoding="utf-8")
        self.writer = csv.writer(self.evtx_csv_file)
        self.writer.writerow(["Event ID"])
        


    #def process_fs_object(self, fs_object, file_path):
    def process_fs_object(self, fs_object, file_path):
        print("--------" ,file_path)
        try:
            file_name = fs_object.info.name.name
            if "ElfFile".lower() in file_path.decode("utf-8").lower():
                print("[+] ------------- EVTX file found")
        except IOError:
            pass

    def parse_event_to_extract(self, config):
        print("enter the event value") 
        if "events_to_extract" in config:
            event_to_extract = []
            for event in config["events_to_extract"]:
                journal_name = event["journal_name"]
                event_id  = event["events"]
                event_to_extract.append((journal_name,event_id))
            return event_to_extract
                


