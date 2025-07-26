import os
import configparser

def load_config(config_path='~/.potconfig'):
    """
    Load configuration from a file.
    Default path: ~/.potconfig
    Returns a ConfigParser object if file exists, else None.
    """
    config = configparser.ConfigParser()
    path = os.path.expanduser(config_path)
    if os.path.exists(path):
        try:
            config.read(path)
            print(f"[INFO] Loaded config from {path}")
            return config
        except Exception as e:
            print(f"[ERROR] Failed to read config file: {e}")
    return None

def apply_config_to_args(config, args):
    """
    Override CLI args with settings from config file.
    """
    if not config:
        return args
    try:
        if 'settings' in config:
            settings = config['settings']
            if 'ext' in settings:
                args.ext = [e.strip() for e in settings['ext'].split(',')]
            if 'exclude' in settings:
                args.exclude = [e.strip() for e in settings['exclude'].split(',')]
            if 'top' in settings:
                args.top = int(settings['top'])
            if 'full_path' in settings:
                args.full_path = settings.getboolean('full_path')
            if 'json' in settings:
                args.json = settings.getboolean('json')
            if 'open_url' in settings:
                args.open_url = settings.getboolean('open_url')
            if 'share_entire_pot' in settings:
                args.share_entire_pot = settings.getboolean('share_entire_pot')
            # Add more options here as needed
    except Exception as e:
        print(f"[ERROR] Applying config options failed: {e}")
    return args