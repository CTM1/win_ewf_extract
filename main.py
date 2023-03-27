import importlib
import argparse
import yaml

def main():
    # Arguments
    parser = argparse.ArgumentParser(description='Windows EWF Artifact Extractor')
    parser.add_argument('cfg', help='YAML configuration file - Possible fields: extract_registry\nextract_browsers\nextract_event_logs\nextract_mft')
    parser.add_argument('ewf_file', help='Path to Encase Windows file')
    args = parser.parse_args()

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