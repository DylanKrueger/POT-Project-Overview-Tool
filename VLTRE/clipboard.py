# clipboard.py

import os
import platform
import subprocess

def is_headless():
    if os.name != 'nt':
        # Linux/macOS
        return os.environ.get('DISPLAY', '') == ''
    # Windows usually has display
    return False

def copy_clipboard(text):
    headless = is_headless()
    system_name = platform.system()

    # Try pyperclip first
    try:
        import pyperclip
        if not headless:
            pyperclip.copy(text)
            return True
        else:
            print("Headless environment detected. Cannot copy to system clipboard.")
            return False
    except ImportError:
        pass

    # Use system tools if not headless
    if not headless:
        try:
            if system_name == 'Darwin':
                p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                p.communicate(text.encode())
                return p.returncode == 0
            elif system_name == 'Windows':
                p = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                p.communicate(text.encode('utf-16le'))
                return p.returncode == 0
            else:
                for cmd in (['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input']):
                    try:
                        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                        p.communicate(text.encode())
                        if p.returncode == 0:
                            return True
                    except FileNotFoundError:
                        continue
        except Exception:
            pass
        print("Clipboard command failed.")
        return False
    else:
        # Headless: Save to a file
        filename = "clipboard_content.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Headless environment: Clipboard content saved to {filename}")
            return True
        except Exception:
            print("Failed to write clipboard content to file.")
            return False