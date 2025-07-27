import importlib
import shutil
import sys

def check_module(name):
    try:
        importlib.import_module(name)
        print(f"{name} is installed.")
    except ImportError:
        print(f"{name} is NOT installed.")

def check_tool(name):
    path = shutil.which(name)
    if path:
        print(f"{name} found at {path}")
    else:
        print(f"{name} not found.")

if __name__ == "__main__":
    check_module('pyperclip')
    check_module('colorama')
    check_tool('xclip')
    check_tool('xselect')
    check_tool('pbcopy')
    check_tool('clip')
    check_tool('matplotlib')