import modules.registry

import importlib
import argparse
import yaml
import glob
import os

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

    for module_name, extract in config.items():
        if extract:
            module = importlib.import_module("modules." + module_name)
            module.extract(args.ewf_file, args.output, config)

if __name__ == '__main__':
    main()
