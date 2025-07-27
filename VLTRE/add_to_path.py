import os
import sys
import platform
import subprocess

def get_scripts_dir():
    system = platform.system()
    if system == 'Windows':
        # Typically in %APPDATA%\Python\Scripts
        appdata = os.environ.get('APPDATA')
        if appdata:
            return os.path.join(appdata, 'Python', 'Scripts')
        else:
            return None
    else:
        # Linux/macOS: ~/.local/bin
        return os.path.expanduser('~/.local/bin')

def is_in_path(dir_path):
    current_path = os.environ.get('PATH', '')
    paths = current_path.split(os.pathsep)
    return any(os.path.normcase(os.path.normpath(p)) == os.path.normcase(os.path.normpath(dir_path)) for p in paths)

def add_to_path(dir_path):
    system = platform.system()
    if system == 'Windows':
        # Use setx to add to user environment variables
        # Note: setx has length limits and requires a new terminal to take effect
        command = f'setx PATH "%PATH%;{dir_path}"'
        print(f"Running: {command}")
        os.system(command)
        print("Please restart your terminal or log out and log back in.")
    else:
        # For Linux/macOS, update shell config
        shell_config = os.path.expanduser('~/.bashrc')
        # Or ~/.zshrc, depending on user's shell
        line = f'\n# Added by add_to_path.py\nexport PATH="$PATH:{dir_path}"\n'
        with open(shell_config, 'a') as f:
            f.write(line)
        print(f"Added to {shell_config}. Please run 'source {shell_config}' or restart your terminal.")

def main():
    dir_path = get_scripts_dir()
    if not dir_path:
        print("Could not determine scripts directory.")
        return

    if is_in_path(dir_path):
        print(f"The directory {dir_path} is already in your PATH.")
    else:
        print(f"Adding {dir_path} to your PATH...")
        add_to_path(dir_path)

if __name__ == '__main__':
    main()