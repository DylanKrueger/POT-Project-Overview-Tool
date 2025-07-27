import os
import configparser

def load_config(config_path='~/.potconfig'):
    """
    Load configuration from a file.
    Default path: ~/.potconfig
    Returns a dictionary of options if file exists, else empty dict.
    """
    config = configparser.ConfigParser()
    path = os.path.expanduser(config_path)
    options = {}
    if os.path.exists(path):
        try:
            config.read(path)
            print(f"[INFO] Loaded config from {path}")
            # Flatten config into dict
            for section in config.sections():
                for key, value in config.items(section):
                    options[key] = value
            return options
        except Exception as e:
            print(f"[ERROR] Failed to read config file: {e}")
    return options

def apply_config_to_args(config, args):
    """
    Override CLI args with settings from config file.
    Assumes config is a dict.
    """
    if not config:
        return args
    try:
        # For each key in config, set attribute if exists
        for key, value in config.items():
            # Convert booleans and ints appropriately
            if hasattr(args, key):
                attr_type = type(getattr(args, key))
                if attr_type is bool:
                    # Convert 'true'/'false' string to bool
                    setattr(args, key, value.lower() in ('true', '1', 'yes'))
                elif attr_type is int:
                    setattr(args, key, int(value))
                elif attr_type is list:
                    setattr(args, key, [e.strip() for e in value.split(',')])
                else:
                    setattr(args, key, value)
    except Exception as e:
        print(f"[ERROR] Applying config options failed: {e}")
    return args