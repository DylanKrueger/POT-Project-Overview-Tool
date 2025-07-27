#!/usr/bin/env python3
"""
project_overview.py – colourised directory tree with LOC stats
• Copies plain report to clipboard (pyperclip / pbcopy / clip / xclip / xsel)
• Writes/refreshes _project_overview.txt (or .json) at project root
• NEW: Clean tabular summary & % of total lines for extensions / top files
"""

from __future__ import annotations
import argparse, json, os, re, subprocess, sys
from pathlib import Path
from collections import Counter, defaultdict

# ── Colour helpers ───────────────────────────────────────────
try:
    from colorama import init as _cinit, Fore, Style
    _cinit()
    COLOR = {
        "dir":     Fore.CYAN + Style.BRIGHT,
        "file":    Fore.GREEN,
        "big":     Fore.RED + Style.BRIGHT,
        "skipped": Fore.WHITE + Style.DIM,
        "reset":   Style.RESET_ALL,
    }
except ImportError:
    COLOR = defaultdict(str); COLOR["reset"] = ""

def colour(role: str, text: str) -> str:
    return f"{COLOR[role]}{text}{COLOR['reset']}"

# ── Clipboard helper ─────────────────────────────────────────
def copy_clipboard(text: str) -> bool:
    """Return True if copy succeeded."""
    try:                      # 1) pyperclip
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    try:                      # 2) platform fallbacks
        if sys.platform.startswith("darwin"):
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode())
            return p.returncode == 0
        elif sys.platform.startswith("win"):
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-16le"))
            return p.returncode == 0
        else:  # Linux / BSD
            for cmd in (["xclip", "-selection", "clipboard"],
                         ["xsel", "--clipboard", "--input"]):
                try:
                    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                    p.communicate(text.encode())
                    if p.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
    except Exception:
        pass
    return False

# ── CLI args
parser = argparse.ArgumentParser(
    description="Coloured directory tree with LOC statistics + clipboard dump",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("root", nargs="?", default=".",
                    help="root folder to scan (default '.')")
parser.add_argument("-e", "--ext", nargs="+",
                    default=[".py", ".js", ".ts", ".css", ".html", ".json",
                             ".md", ".txt", ".yml", ".yaml"],
                    help="extensions to count as source")
parser.add_argument("-x", "--exclude", nargs="*",
                    default=["__pycache__", ".git", "node_modules", "dist", "build"],
                    help="glob patterns to skip")
parser.add_argument("-n", "--top", type=int, default=10,
                    help="show N largest files (default 10)")
parser.add_argument("--no-color", action="store_true",
                    help="disable ANSI colours")
parser.add_argument("--json", action="store_true",
                    help="output JSON & save _project_overview.json")
args = parser.parse_args()

if args.no_color:
    for k in COLOR:
        COLOR[k] = ""

root = Path(args.root).resolve()
SRC_EXT = {e if e.startswith(".") else "." + e for e in args.ext}
EXCLUDE = set(args.exclude)
EXCLUDE.update(['venv'])  # Exclude 'venv' directory and its files
TOP_N = args.top
BIG_FILE = 300

# ── stats containers
TOTAL_LINES = 0
TOTAL_FILES = 0
TOTAL_DIRS = 0
COUNTED_FILES = 0
LINE_BY_EXT = Counter()
LARGEST: list[tuple[int, Path]] = []
TREE_LINES: list[str] = []

# ── Helper: pattern matching for ignored files/dirs
def ignored(path: Path) -> bool:
    if path.name.startswith("."):
        return True
    return any(path.match(pat) for pat in EXCLUDE)

# ── Helper: check if directory is user-created
def is_user_created_dir(path: Path) -> bool:
    # Exclude directories matching exclude patterns
    if any(path.match(pat) for pat in EXCLUDE):
        return False
    return path.is_dir()

# ── Helper: count lines in file
def loc(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0

# ── Main recursive walk
def walk(folder: Path, depth: int = 0) -> None:
    global TOTAL_FILES, TOTAL_DIRS, COUNTED_FILES, TOTAL_LINES
    TOTAL_DIRS += 1

    for p in sorted(folder.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if ignored(p):
            continue

        # If directory, decide whether to recurse
        if p.is_dir():
            # Skip directories matching exclude patterns
            if any(p.match(pat) for pat in EXCLUDE):
                continue
            # Only recurse into user-created or relevant directories
            if is_user_created_dir(p):
                indent = "│   " * depth + "├── "
                TREE_LINES.append(colour("dir", f"{indent}{p.name}/"))
                walk(p, depth + 1)
            else:
                # Skip walking into non-user directories
                continue
        else:
            # process files
            TOTAL_FILES += 1
            lines = 0
            if p.suffix.lower() in SRC_EXT:
                lines = loc(p)
                TOTAL_LINES += lines
                COUNTED_FILES += 1
                LINE_BY_EXT[p.suffix.lower()] += lines
                LARGEST.append((lines, p))
            role = "big" if lines >= BIG_FILE else "file"
            indent = "│   " * depth + "├── "
            TREE_LINES.append(
                f"{indent}{colour(role, p.name):35} {lines:>7}" if lines
                else f"{indent}{colour('skipped', p.name)}"
            )

# Run walk starting from root
walk(root)

# ── build report parts
sep = "─" * 70
title = f"{colour('dir', root.name)}  ({TOTAL_LINES:,} lines)\n"
tree = "\n".join(TREE_LINES) + "\n" if TREE_LINES else ""
footer = (f"{sep}\n"
          f"Dirs: {TOTAL_DIRS:<6} Files: {TOTAL_FILES:<6} "
          f"Counted: {TOTAL_DIRS}\n"  # corrected to show total dirs
          f"Total source lines: {TOTAL_LINES:,}\n")

# Extension & largest files summaries
ext_block = ""
if LINE_BY_EXT:
    ext_block += "\nBy extension:\n"
    ext_block += "  Ext      Lines       %\n"
    for ext, n in LINE_BY_EXT.most_common():
        pct = (n / TOTAL_LINES * 100) if TOTAL_LINES else 0
        ext_block += f"  {ext:<6} {n:>10,}  {pct:6.2f}%\n"

largest_block = ""
if LARGEST:
    # Filter out files inside 'venv' directory
    def is_in_venv(path: Path) -> bool:
        try:
            return 'venv' in path.relative_to(root).parts
        except Exception:
            return False

    largest_files_filtered = [item for item in LARGEST if not is_in_venv(item[1])]

    largest_block += f"\nTop {TOP_N} largest files:\n"
    largest_block += "  File" + " " * 46 + "Lines       %  \n"
    for lines, path in sorted(largest_files_filtered, reverse=True)[:TOP_N]:
        pct = (lines / TOTAL_LINES * 100) if TOTAL_LINES else 0
        tag = colour("big", "BIG") if lines >= BIG_FILE else ""
        rel = str(path.relative_to(root))
        largest_block += f"  {rel:<50} {lines:>7}  {pct:6.2f}% {tag}\n"

# Compose full report
plain_report = title + tree + footer + ext_block + largest_block

# ── Output JSON if requested
if args.json:
    payload = json.dumps({
        "root": str(root),
        "dirs": TOTAL_DIRS,
        "files": TOTAL_FILES,
        "counted": COUNTED_FILES,
        "total_lines": TOTAL_LINES,
        "by_ext": LINE_BY_EXT,
        "largest": sorted(LARGEST, reverse=True)[:TOP_N],
    }, indent=2)
    print(payload)
    copy_clipboard(payload)
    (root / "_project_overview.json").write_text(payload, encoding="utf-8")
    sys.exit()

# ── Output report, copy to clipboard, save to file
print(plain_report)

import re
ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
plain_txt = ansi_re.sub("", plain_report)

copied = copy_clipboard(plain_txt)
outfile = root / "_project_overview.txt"
outfile.write_text(plain_txt, encoding="utf-8")
if copied:
    print("📋 copied to clipboard")
print(f"💾 saved → {outfile.relative_to(root)}")