#!/usr/bin/env python3
"""
VLTRE/cli.py – Directory tree with LOC stats, web view support, clipboard, JSON output, visualization,
and a progress indicator. Banner aligned right, tree/status below.
"""

import sys
import platform
import os
import json
import threading
import tempfile
import webbrowser
import socketserver
import http.server
from pathlib import Path
import re
import matplotlib.pyplot as plt
from VLTRE import display

from VLTRE import clipboard
from VLTRE import utils  # Import get_banner_lines from utils
from VLTRE import tree_progress
from VLTRE.config import parse_args

# Support for color output
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

# Global flag
IS_CLI_MODE = True

def display_banner():
    banner_lines = display.get_banner_lines()
    def print_left_aligned(lines):
        term_width = os.get_terminal_size().columns
        max_line_length = max(len(line) for line in lines)
        padding = max(0, term_width - max_line_length)
        for line in lines:
            print(' ' * padding + line)
    lines = [line for line in banner_lines if line.strip()]
    print_left_aligned(lines)

def display_banner_with_tree():
    """Display banner and tree, update progress."""
    user_data = tree_progress.load_user_data()
    current_stage = user_data['growth_stage']
    # Define indent for display
    indent = ' ' * 0

    # Display banner and ASCII tree
    display.display_banner_and_tree(current_stage, indent=indent)

    # Show current stage explicitly
    print(f"\nCurrent Stage: {current_stage}\n")

    # Update progress
    user_data['total_runs'] = user_data.get('total_runs', 0) + 1
    if user_data['total_runs'] % 10 == 0:
        if user_data['growth_stage'] < 4:
            user_data['growth_stage'] += 1
        else:
            # Keep at max stage 4 or wrap to 0 if desired
            user_data['growth_stage'] = 0
        user_data['regrow_count'] = user_data.get('regrow_count', 0) + 1
    # Save user data
    tree_progress.save_user_data(user_data)

    # Show progress bar
    progress = (user_data['total_runs'] % 10) / 10
    tree_progress.show_progress_bar(progress, indent=indent)

    # Show regrow count
    print(f"Tree has regrown {user_data.get('regrow_count', 0)} times.\n")

def copy_clipboard(text):
    from VLTRE import clipboard
    return clipboard.copy_clipboard(text)

def open_html_in_browser(html_content):
    """Create a temporary HTML file and open in the default browser."""
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
        f.write(html_content)
        filename = f.name
    webbrowser.open(f'file://{filename}')

def serve_html_report(html_path):
    # Serve HTML report in browser
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
    return f"""
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

def main():
    args = parse_args()

    # Show the pot tree and status below banner
    display_banner_with_tree()

    # Exit if no arguments
    if len(sys.argv) <= 1:
        sys.exit(0)

    verbose = getattr(args, 'verbose', False)

    if verbose:
        print("[DEBUG] Parsed arguments:", args)

    # Handle --list-drives
    if getattr(args, 'list_drives', False):
        for d in list_drives():
            print(d)
        sys.exit(0)

    # Set CLI mode
    global IS_CLI_MODE
    if getattr(args, 'no_color', False):
        IS_CLI_MODE = False

    # Handle --grow (with optional --animate)
    if getattr(args, 'grow', False):
        if getattr(args, 'animate', False):
            # Run animation
            from VLTRE import animations
            animations.animate_growth()
        else:
            # Show final stage (assuming stage 4)
            try:
                with open("stages/stage4.txt", 'r') as f:
                    print(f.read())
            except:
                print("[ERROR] Final stage file not found.")
        sys.exit(0)

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

    verbose = getattr(args, 'verbose', False)
    if verbose:
        print(f"[DEBUG] Roots to scan: {roots}")

    # Initialize stats
    TOTAL_LINES = 0
    TOTAL_FILES = 0
    TOTAL_DIRS = 0
    COUNTED_FILES = 0
    LINE_BY_EXT = {}
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
        except:
            return True

    def loc(p):
        try:
            with p.open("r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0

    def walk(folder, show_all, depth=0, max_depth=0):
        nonlocal TOTAL_FILES, TOTAL_DIRS, COUNTED_FILES, TOTAL_LINES
        try:
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
                indent = "│   " * (depth) + "├── "
                if p.is_dir():
                    display.colour("dir", p.name, IS_CLI_MODE)
                    TREE_LINES.append(f"{indent}{display.colour('dir', p.name, IS_CLI_MODE)}/")
                    walk(p, show_all, depth + 1, max_depth)
                else:
                    TOTAL_FILES += 1
                    lines = 0
                    if hasattr(args, 'ext') and p.suffix.lower() in args.ext:
                        lines = loc(p)
                        TOTAL_LINES += lines
                        COUNTED_FILES += 1
                        LINE_BY_EXT[p.suffix.lower()] = LINE_BY_EXT.get(p.suffix.lower(), 0) + lines
                        LARGEST.append((lines, p))
                    role = "big" if lines >= getattr(args, 'BIG_FILE', 300) else "file"
                    display_name = display.colour(role, p.name, IS_CLI_MODE)
                    line_str = f"{indent}{display_name:35} {lines:>7}" if lines else f"{indent}{display_name}"
                    TREE_LINES.append(line_str)
        except Exception as e:
            print(f"[ERROR] Error during directory walk {folder}: {e}")

    max_depth_value = getattr(args, 'max_depth', 0)
    for root in roots:
        walk(root, show_all=getattr(args, 'share_entire_pot', False), max_depth=max_depth_value)

    # Build root display
    root_path_str = str(roots[0].resolve())
    root_disp = root_path_str if getattr(args, 'full_path', False) else Path(root_path_str).name

    from colorama import Fore, Style
    root_color = Fore.MAGENTA + Style.BRIGHT
    default_color = COLOR["reset"]
    title = f"{display.colour('dir', roots[0].name)}\n"
    tree_str = "\n".join(TREE_LINES) if TREE_LINES else ""

    root_node = f"{root_color}├── {root_disp}{default_color}\n"

    report_str = f"{root_node}{tree_str}\n" + \
                 f"{' ' * 4}{'─'*70}\n" + \
                 f"{title}\n" + \
                 f"{'─'*70}\n" + \
                 f"{display.colour('dir', 'Dirs')}: {TOTAL_DIRS}  " \
                 f"{display.colour('file', 'Files')}: {TOTAL_FILES}  " \
                 f"{display.colour('big', 'Total source lines')}: {TOTAL_LINES:,}\n"

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
                Path(args.output).write_text(payload, encoding='utf-8')
            except Exception as e:
                print(f"[ERROR] Saving JSON output failed: {e}")
        sys.exit(0)

    # Handle --open-url
    if getattr(args, 'open_url', False):
        print("[DEBUG] --open-url triggered")
        ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
        plain_text = ansi_re.sub("", report_str)
        html_content = build_html_from_text(plain_text)
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w', encoding='utf-8') as tmpf:
            tmpf.write(html_content)
            tmp_path = tmpf.name
        print(f"[INFO] Opening report in your browser: {tmp_path}")
        webbrowser.open(f'file://{tmp_path}')
        sys.exit(0)

    # Print report
    print("[DEBUG] Printing report")
    print(report_str)

    # Save to text file and copy to clipboard if --copy
    ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
    plain_txt = ansi_re.sub("", report_str)
    copied = False
    if getattr(args, 'copy', False):
        copied = copy_clipboard(plain_txt)

    # Save report to .txt if --txt
    if getattr(args, 'txt', False):
        try:
            output_path = Path(roots[0]) / "pot_output.txt"
            output_path.write_text(plain_txt, encoding='utf-8')
            print(f"✓ Report saved to {output_path}")
        except Exception as e:
            print(f"[ERROR] Saving report to text file: {e}")

    # Final status messages
    if copied:
        print("📋 copied to clipboard")
    if getattr(args, 'txt', False):
        print(f"💾 saved → {output_path.relative_to(roots[0])}")
    else:
        print(f"💾 (not saved to .txt, only displayed)")

    # Visualization
    if getattr(args, 'visualize', False):
        labels = list(LINE_BY_EXT.keys())
        sizes = list(LINE_BY_EXT.values())
        plt.figure(figsize=(8,8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("File Types Distribution")
        plt.show()

if __name__ == "__main__":
    main()