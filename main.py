from .modules.registry import RegistryExtractor
from .modules.events import EventLogExtractor
import modules.disk_utils as dutils

import importlib
import argparse
import yaml
import glob
import os

import pytsk3
import pyewf

def main():
    # Arguments and help
    parser = argparse.ArgumentParser(description='Windows EWF Artifact Extractor')
    parser.add_argument("-c","--cfg", type=str, help='YAML configuration file - Possible fields: extract_registry\nextract_browsers\nextract_event_logs\nextract_mft')
    parser.add_argument("-o", "--output", type=str, help="Output directory for extracted artifacts - ./output by default")
    parser.add_argument("-f","--ewf_file", type=str, help='Path to first Encase Windows file (.E01 extension)')
    args = parser.parse_args()

    output_dir = args.output or "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load configuration from a YAML file
    with open(args.cfg) as f:
        config = yaml.safe_load(f)

    if args.output is None:
        args.output = output_dir

    # Mapping of extractors we could have
    extractor_classes = {
        "registry": RegistryExtractor,
        # "chrome": ChromeExtractor,
        # "firefox": FirefoxExtractor,
        # "edge": EdgeExtractor,
        "event_logs": EventLogExtractor,
        # "mft": MFTExtractor,
    }

    # Adding those to the extractors array
    extractors = []
    for extractor_name, extractor_class in extractor_classes.items():
        if isinstance(config.get(extractor_name), bool) and config[extractor_name]:
            extractors.append(extractor_class(args.output, config))

    ewf_handle = pyewf.handle()
    files = pyewf.glob(args.ewf_file)
    # les donnée en entrée 
    ewf_handle.open(files)

    img_info = dutils.EWFImgInfo(ewf_handle)
    vol = pytsk3.Volume_Info(img_info)
    filesystems = dutils.find_file_systems(img_info)
    for fs in filesystems:
        
        root_dir = fs.open_dir("/")
        dutils.recurse_files(fs, root_dir, [], [""], extractors)
        

if __name__ == '__main__':
    main()
