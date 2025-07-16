#!/usr/bin/env python3
"""
pot/cli.py – Directory tree with LOC stats, web view support, clipboard, JSON output
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
from pot.utils import generate_html_report
from pot.config import get_args

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

# ── clipboard helper
def copy_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except:
        pass
    try:
        if sys.platform.startswith("darwin"):
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode())
            return p.returncode == 0
        elif sys.platform.startswith("win"):
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-16le"))
            return p.returncode == 0
        else:
            for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
                try:
                    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                    p.communicate(text.encode())
                    if p.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
    except:
        pass
    return False

# ── generate styled HTML report from text (without color)
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

# ── serve HTML report
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

def main():
    global IS_CLI_MODE
    args = get_args()

    # Debug: print args.json status
    print("DEBUG: args.json =", args.json)

    # 1. Handle --list-drives early
    if args.list_drives:
        import platform
        drives = []
        if platform.system() == 'Windows':
            import string, ctypes
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:/")
                bitmask >>= 1
        else:
            # For Unix-like, list /mnt and /media
            for d in ['/mnt', '/media']:
                if os.path.exists(d):
                    for item in os.listdir(d):
                        drives.append(os.path.join(d, item))
        print("Available drives/mount points:")
        for d in drives:
            print(d)
        sys.exit(0)

    # 2. Set color mode
    if args.no_color:
        IS_CLI_MODE = False

    # 3. Determine roots
    roots = []
    if args.scan_whole:
        import platform
        if platform.system() == 'Windows':
            import string, ctypes
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    roots.append(Path(f"{letter}:/"))
                bitmask >>= 1
        else:
            roots = [Path('/')]
    else:
        roots = [Path(args.root)]

    # 4. Initialize stats
    TOTAL_LINES = 0
    TOTAL_FILES = 0
    TOTAL_DIRS = 0
    COUNTED_FILES = 0
    LINE_BY_EXT = Counter()
    LARGEST = []
    TREE_LINES = []

    def ignored(p):
        if p.name.startswith('.'):
            return True
        if hasattr(args, 'share_entire_pot') and args.share_entire_pot:
            return False
        ignore_patterns = {
            "__pycache__", ".git", "node_modules", "dist", "build",
            "venv", "env", "env.bak", "site-packages"
        }
        return any(pat in p.name for pat in ignore_patterns)

    def loc(p):
        try:
            with p.open("r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0

    def walk(folder, show_all, depth=0):
        nonlocal TOTAL_FILES, TOTAL_DIRS, COUNTED_FILES, TOTAL_LINES
        TOTAL_DIRS += 1
        for p in sorted(folder.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
            if ignored(p):
                continue
            indent = "│   " * depth + "├── "
            if p.is_dir():
                TREE_LINES.append(colour("dir", f"{indent}{p.name}/"))
                walk(p, show_all, depth + 1)
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

    # Walk roots
    for root in roots:
        print(f"[DEBUG] Walking root: {root}")
        walk(root, show_all=getattr(args, 'share_entire_pot', False))

    # Build report string
    root_str = str(roots[0].resolve())
    if getattr(args, 'full_path', False):
        root_disp = root_str
    else:
        root_disp = Path(root_str).name

    header = f"Root: {root_disp}\n" + ("│" * 3)
    title = f"{colour('dir', roots[0].name)}\n"
    tree_str = "\n".join(TREE_LINES) + ("\n" if TREE_LINES else "")
    footer = (f"{'─'*70}\n"
              f"Dirs: {TOTAL_DIRS}  Files: {TOTAL_FILES}  "
              f"Total source lines: {TOTAL_LINES:,}\n")
    ext_block = ""
    if hasattr(args, 'ext') and args.ext:
        ext_block += "\nBy extension:\n"
        ext_block += "  Ext      Lines       %\n"
        for ext, n in LINE_BY_EXT.most_common():
            pct = (n / TOTAL_LINES * 100) if TOTAL_LINES else 0
            ext_block += f"  {ext:<6} {n:>10,}  {pct:6.2f}%\n"

    largest_block = ""
    if hasattr(args, 'show_largest') and args.show_largest:
        TOP_N = getattr(args, 'top', 10)
        largest_block += f"\nTop {TOP_N} largest files:\n"
        largest_block += "  File" + " " * 46 + "Lines       %  \n"
        for lines, p in sorted(LARGEST, reverse=True)[:TOP_N]:
            pct = (lines / TOTAL_LINES * 100) if TOTAL_LINES else 0
            tag = colour("big", "BIG") if lines >= getattr(args, 'BIG_FILE', 300) else ""
            rel_path = str(p.relative_to(roots[0]))
            largest_block += f"  {rel_path:<50} {lines:>7}  {pct:6.2f}% {tag}\n"

    report_str = f"{header}\n{title}\n{tree_str}\n{footer}\n{ext_block}\n{largest_block}"

    # 9. Handle --json
    if args.json:
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
        copy_clipboard(payload)
        (roots[0] / "_project_overview.json").write_text(payload, encoding="utf-8")
        sys.exit(0)

    # 10. Handle --open-url
    if args.open_url:
        print("[DEBUG] --open-url triggered")
        # Generate plain text without ANSI codes
        import re
        ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
        plain_text = ansi_re.sub("", report_str)

        # Generate HTML and open in browser
        html_content = build_html_from_text(plain_text)
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w', encoding='utf-8') as tmpf:
            tmpf.write(html_content)
            tmp_path = tmpf.name
        IS_CLI_MODE = True
        url = 'file://' + os.path.abspath(tmp_path).replace('\\', '/')
        print(f"[INFO] Opening report in your browser: {url}")
        webbrowser.open(url)
        sys.exit(0)

    # 11. Default: print report
    print("[DEBUG] Printing report")
    print(report_str)

    # 12. Save and copy to clipboard
    import re
    ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
    plain_txt = ansi_re.sub("", report_str)
    copied = copy_clipboard(plain_txt)
    outfile = roots[0] / "_project_overview.txt"
    outfile.write_text(plain_txt, encoding="utf-8")
    if copied:
        print("📋 copied to clipboard")
    print(f"💾 saved → {outfile.relative_to(roots[0])}")

if __name__ == "__main__":
    main()