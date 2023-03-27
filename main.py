import importlib
import argparse
import yaml
import os

def main():
    # Arguments
    parser = argparse.ArgumentParser(description='Windows EWF Artifact Extractor')
    parser.add_argument("-c","--cfg", type=str, help='YAML configuration file - Possible fields: extract_registry\nextract_browsers\nextract_event_logs\nextract_mft')
    parser.add_argument("-o", "--output", type=str, help="Output directory for extracted artifacts - ./output by default")
    parser.add_argument("-f","--ewf_file", type=str, help='Path to Encase Windows file')
    args = parser.parse_args()

    output_dir = args.output or "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load configuration from a YAML file
    with open(args.cfg) as f:
        config = yaml.safe_load(f)
    
    # Parse config file for the desired modules, and extract them.
    for module_name, extract in config.items():
        if extract:
            module = importlib.import_module(module_name)
            module.extract(args.ewf_file)

if __name__ == '__main__':
    main()