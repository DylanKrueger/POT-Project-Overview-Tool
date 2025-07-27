#!/usr/bin/env python3
"""
VLTRE/cli.py – Directory tree with LOC stats, web view support, clipboard, JSON output
"""

import sys
import platform
import subprocess
import json
import threading
import os
import tempfile
import webbrowser
import socketserver
import http.server
from pathlib import Path
from collections import Counter
from VLTRE.config import get_args

# Import config loader functions
from VLTRE.config_loader import load_config, apply_config_to_args

# ── color helpers
try:
    from colorama import init as _cinit, Fore, Style
    _cinit()
    COLOR = {
        "dir": Fore.CYAN + Style.BRIGHT,
        "file": Fore.GREEN,
        "big": Fore.RED + Style.BRIGHT,
        "skipped": Fore.WHITE + Style.DIM,
        "reset": Style.RESET_ALL,
    }
except ImportError:
    from collections import defaultdict
    COLOR = defaultdict(str)
    COLOR["reset"] = ""

# Global flag to control color application
IS_CLI_MODE = True

def colour(role, text):
    if IS_CLI_MODE:
        return f"{COLOR[role]}{text}{COLOR['reset']}"
    else:
        return text

def copy_clipboard(text):
    import platform
    system_name = platform.system()

    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass

    if system_name == 'Darwin':
        try:
            p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            p.communicate(text.encode())
            return p.returncode == 0
        except Exception:
            pass
    elif system_name == 'Windows':
        try:
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
            p.communicate(text.encode('utf-16le'))
            return p.returncode == 0
        except Exception:
            pass
    else:
        for cmd in (['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input']):
            try:
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                p.communicate(text.encode())
                if p.returncode == 0:
                    return True
            except FileNotFoundError:
                continue
    return False

def serve_html_report(html_path):
    dir_path = os.path.dirname(os.path.abspath(html_path))
    filename = os.path.basename(html_path)
    port = 8000

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dir_path, **kwargs)

    def start_server():
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}/{filename}"
            print(f"[DEBUG] Serving at {url}")
            webbrowser.open(url)
            httpd.serve_forever()

    threading.Thread(target=start_server, daemon=True).start()

def list_drives():
    system_name = platform.system()
    drives = []

    if system_name == 'Windows':
        import string, ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(Path(f"{letter}:/"))
            bitmask >>= 1
    else:
        for d in ['/mnt', '/media', '/']:
            if os.path.exists(d):
                for item in os.listdir(d):
                    drives.append(Path(d) / item)
    return drives

def build_html_from_text(text):
    html = f"""
    <html>
    <head>
        <title>Project Structure</title>
        <style>
            body {{
                font-family: monospace;
                background: #222;
                color: #eee;
                padding: 20px;
            }}
            pre {{
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <h1>Directory Structure</h1>
        <pre>{text}</pre>
    </body>
    </html>
    """
    return html

def main():
    # Parse CLI arguments
    args = get_args()

    # Load config file and override args
    config = load_config()
    args = apply_config_to_args(config, args)

    # Verbose mode
    verbose = getattr(args, 'verbose', False)

    if verbose:
        print("[DEBUG] Parsed arguments:", args)

    # Handle --list-drives
    if getattr(args, 'list_drives', False):
        drives = list_drives()
        print("Available drives/mount points:")
        for d in drives:
            print(d)
        sys.exit(0)

    # Set color mode
    global IS_CLI_MODE
    if getattr(args, 'no_color', False):
        IS_CLI_MODE = False

    # Determine roots
    system_name = platform.system()
    roots = []

    if getattr(args, 'scan_whole', False):
        if system_name == 'Windows':
            import string, ctypes
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    roots.append(Path(f"{letter}:/"))
                bitmask >>= 1
        else:
            roots = [Path('/')]
    else:
        try:
            roots = [Path(args.root)]
        except Exception as e:
            print(f"[ERROR] Invalid root path: {args.root}")
            sys.exit(1)

    if verbose:
        print(f"[DEBUG] Roots to scan: {roots}")

    # Initialize stats
    TOTAL_LINES = 0
    TOTAL_FILES = 0
    TOTAL_DIRS = 0
    COUNTED_FILES = 0
    LINE_BY_EXT = Counter()
    LARGEST = []
    TREE_LINES = []

    def ignored(p):
        try:
            if p.name.startswith('.'):
                return True
            if getattr(args, 'share_entire_pot', False):
                return False
            ignore_patterns = {
                "__pycache__", ".git", "node_modules", "dist", "build",
                "venv", "env", "env.bak", "site-packages"
            }
            return any(pat in p.name for pat in ignore_patterns)
        except Exception as e:
            print(f"[ERROR] Error checking ignore pattern for {p}: {e}")
            return True

    def loc(p):
        try:
            with p.open("r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for line in f if line.strip())
        except Exception as e:
            print(f"[ERROR] Reading file {p}: {e}")
            return 0

    def walk(folder, show_all, depth=0, max_depth=0):
        nonlocal TOTAL_FILES, TOTAL_DIRS, COUNTED_FILES, TOTAL_LINES
        try:
            # Respect max_depth limit
            if max_depth > 0 and depth >= max_depth:
                return
            if not os.path.exists(folder):
                print(f"[ERROR] Path does not exist: {folder}")
                return
            if not os.access(folder, os.R_OK):
                print(f"[ERROR] Cannot read directory: {folder}")
                return
            TOTAL_DIRS += 1
            for p in sorted(Path(folder).iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
                if ignored(p):
                    continue
                indent = "│   " * depth + "├── "
                if p.is_dir():
                    TREE_LINES.append(colour("dir", f"{indent}{p.name}/"))
                    walk(p, show_all, depth + 1, max_depth)
                else:
                    TOTAL_FILES += 1
                    lines = 0
                    if hasattr(args, 'ext') and p.suffix.lower() in args.ext:
                        lines = loc(p)
                        TOTAL_LINES += lines
                        COUNTED_FILES += 1
                        LINE_BY_EXT[p.suffix.lower()] += lines
                        LARGEST.append((lines, p))
                    role = "big" if lines >= getattr(args, 'BIG_FILE', 300) else "file"
                    TREE_LINES.append(
                        f"{indent}{colour(role, p.name):35} {lines:>7}" if lines else f"{indent}{colour('skipped', p.name)}"
                    )
        except Exception as e:
            print(f"[ERROR] Error during directory walk {folder}: {e}")

    # Walk roots with max_depth
    max_depth_value = getattr(args, 'max_depth', 0)
    for root in roots:
        if verbose:
            print(f"[DEBUG] Walking root: {root}")
        walk(root, show_all=getattr(args, 'share_entire_pot', False), max_depth=max_depth_value)

    # Build report with root in distinct color
    # Determine root display string
    root_path_str = str(roots[0].resolve())
    if getattr(args, 'full_path', False):
        root_disp = root_path_str
    else:
        root_disp = Path(root_path_str).name

    # Use a special color for root
    from colorama import Fore, Style
    root_color = Fore.MAGENTA + Style.BRIGHT
    default_color = COLOR["reset"]

    header = f"{root_color}Root: {root_disp}{default_color}\n" + ("─" * 70)

    title = f"{colour('dir', roots[0].name)}\n"

    tree_str = "\n".join(TREE_LINES) + ("\n" if TREE_LINES else "")

    footer = (f"{'─'*70}\n"
          f"{colour('dir', 'Dirs')}: {TOTAL_DIRS}  "
          f"{colour('file', 'Files')}: {TOTAL_FILES}  "
          f"{colour('big', 'Total source lines')}: {TOTAL_LINES:,}\n")

    # Prepare the full report
    report_str = f"{header}\n{title}\n{tree_str}\n{footer}"

    # JSON output
    if getattr(args, 'json', False):
        payload = json.dumps({
            "roots": [str(r) for r in roots],
            "dirs": TOTAL_DIRS,
            "files": TOTAL_FILES,
            "total_lines": TOTAL_LINES,
            "by_ext": dict(LINE_BY_EXT),
            "largest": [
                {"lines": lines, "path": str(p)}
                for lines, p in sorted(LARGEST, reverse=True)[:getattr(args, 'top', 10)]
            ],
        }, indent=2)
        print(payload)
        if getattr(args, 'copy', False):
            copy_clipboard(payload)
        if getattr(args, 'output', ''):
            try:
                Path(args.output).write_text(payload, encoding="utf-8")
            except Exception as e:
                print(f"[ERROR] Saving JSON output failed: {e}")
        sys.exit(0)

    # Handle open URL
    if getattr(args, 'open_url', False):
        print("[DEBUG] --open-url triggered")
        import re
        ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
        plain_text = ansi_re.sub("", report_str)
        html_content = build_html_from_text(plain_text)
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w', encoding='utf-8') as tmpf:
            tmpf.write(html_content)
            tmp_path = tmpf.name
        IS_CLI_MODE = True
        url = 'file://' + os.path.abspath(tmp_path).replace('\\', '/')
        print(f"[INFO] Opening report in your browser: {url}")
        webbrowser.open(url)
        sys.exit(0)

    # Print report
    print("[DEBUG] Printing report")
    print(report_str)

    # Save to file and copy to clipboard
    import re
    ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
    plain_txt = ansi_re.sub("", report_str)
    copied = False
    if getattr(args, 'copy', False):
        copied = copy_clipboard(plain_txt)
    outfile = Path(roots[0]) / "_project_overview.txt"
    try:
        outfile.write_text(plain_txt, encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Saving report failed: {e}")
    if copied:
        print("📋 copied to clipboard")
    print(f"💾 saved → {outfile.relative_to(roots[0])}")

if __name__ == "__main__":
    main()