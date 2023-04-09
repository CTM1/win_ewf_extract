import os
import sys
import csv
from datetime import datetime
from io import BytesIO

import pytsk3
import pyewf
import Evtx.Evtx as evtx
import Evtx.Views as e_views

from modules.artifact_extraction import ArtifactExtractor
import modules.disk_utils

class EventLogExtractor(ArtifactExtractor):
    """This class implements ArtifactExtractor to extract Windows Event Logs"""
    def __init__(self, output_dir, config):
        self.output_dir = output_dir
        self.event_logs_output_dir = os.path.join(output_dir, "event_logs")

        try:
            os.mkdir(self.event_logs_output_dir)
        except FileExistsError:
            pass

        self.starting_path = "Windows\System32\winevt\Logs".lower()

        self.processable_file_names = self.parse_processable_file_names(config)
        self.processable_directories = []

        self.events_to_extract = self.parse_events_to_extract(config)


    def process_fs_object(self, fs_object, file_path):
        file_name = fs_object.info.name.name.decode("utf-8").lower()

        for journal in self.events_to_extract:
            journal_name = journal["journal_name"]
            events = journal["events"]

            if journal_name.lower() in file_name:
                print(f"[+] Found event log: {file_name}")
                try:
                    output_file_path = os.path.join(self.event_logs_output_dir, f"{file_name}_events.xml")
                    self.extract_event_log(fs_object, output_file_path, events)
                except Exception as e:
                    print(f"[-] Error extracting events from {file_name}: {e}")

    def extract_event_log(self, fs_object, output_file_path, events):
        """Write the .evtx to disk, then parse it's XML to filter for EventIDs"""
        print("[+] Writing journal file to disk")
        journal_file_name = fs_object.info.name.name.decode("utf-8")
        journal_file_path = os.path.join(self.event_logs_output_dir, journal_file_name)

        with open(journal_file_path, "wb") as journal_file:
            journal_file.write(fs_object.read_random(0, fs_object.info.meta.size))

        print("[+] Processing journal file to .xml")
        with open(output_file_path, "w+", encoding="utf-8") as xml_file:
            xml_file.write(e_views.XML_HEADER)
            xml_file.write("<Events>\n")
            with evtx.Evtx(journal_file_path) as log:
                for record in log.records():
                    xml = record.xml()
                    event_id = None
                    for line in xml.splitlines():
                        if "<EventID" in line:
                            event_id = line[line.find(">")+1:line.find("</")]
                            break

                    if not events or str(event_id) in events:
                        xml_file.write(xml + "\n")
            xml_file.write("</Events>\n")

    def parse_events_to_extract(self, config):
        events_to_extract = []

        if "events_to_extract" in config:
            for event in config["events_to_extract"]:
                journal_name = event["journal_name"]
                events = event.get("events", None)  # Handle missing "events" key
                events_to_extract.append({"journal_name": journal_name, "events": events})

        return events_to_extract

    def parse_processable_file_names(self, config):
        processable_file_names = []

        if "events_to_extract" in config:
            for journal in config["events_to_extract"]:
                if "journal_name" in journal:
                    processable_file_names.append(f"{journal['journal_name']}.evtx")

        return processable_file_names
