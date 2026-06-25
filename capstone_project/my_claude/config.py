import yaml
from pathlib import Path

def load_config(config_file=Path(__file__).parent / "config.yaml"):
    """
    Load configuration from a YAML file.
    
    args:
        config_file (Path): Path to the YAML configuration file. Defaults to 'config.yaml' in the same directory as this script.
    """
    return yaml.safe_load(config_file.read_text())

config = load_config()