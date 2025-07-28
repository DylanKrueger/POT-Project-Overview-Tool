import os
import webbrowser
import tempfile
from VLTRE import tree_progress

# Define your color codes for CLI mode
def colour(role, text, cli_mode=True):
    COLOR_CODES = {
        "reset": "\033[0m",
        "big": "\033[31m",     # Red
        "dir": "\033[36m",     # Cyan
        "file": "\033[32m",    # Green
        "skipped": "\033[37m", # White
    }
    if cli_mode:
        color_code = COLOR_CODES.get(role, "")
        return f"{color_code}{text}{COLOR_CODES['reset']}"
    else:
        return text

def get_banner_lines():
    """Return the banner as a list of lines with embedded ANSI color codes."""
    GREEN = "\033[32m"
    RESET = "\033[0m"
    return [
        f"{GREEN}.s5SSSs.              .s5SSSs.              .s5SSSSs.{RESET}",
        f"{GREEN}SS.                   SS.                      SSS{RESET}",
        f"{GREEN}sS    S%S             sS    S%S                S%S{RESET}",
        f"{GREEN}SS    S%S             SS    S%S                S%S{RESET}",
        f"{GREEN}SS .sS::'             SS    S%S                S%S{RESET}",
        f"{GREEN}SS                    SS    S%S                S%S{RESET}",
        f"{GREEN}SS                    SS    `:;                `:;{RESET}",
        f"{GREEN}SS                    SS    ;,.                ;,.{RESET}",
        f"{GREEN}`:                    `:;;;;;:'                ;:'{RESET}",
        f"{GREEN}roject                      verview            ool{RESET}"
    ]

def get_tree_lines(stage):
    """Load ASCII art for the current stage from a text file."""
    return tree_progress.get_tree_lines(stage)

# Add the display_banner_and_tree() function
def display_banner_and_tree(stage, indent=''):
    """Print banner and ASCII tree side-by-side."""
    banner_lines = get_banner_lines()
    tree_lines = get_tree_lines(stage)

    max_banner_width = max(len(line) for line in banner_lines)
    spacing = 4  # space between banner and tree

    padded_banner = [line.ljust(max_banner_width) for line in banner_lines]

    total_lines = max(len(banner_lines), len(tree_lines))
    banner_extended = padded_banner + [' ' * max_banner_width] * (total_lines - len(banner_lines))
    tree_extended = tree_lines + [' ' * max(len(line) for line in tree_lines)] * (total_lines - len(tree_lines))

    for b_line, t_line in zip(banner_extended, tree_extended):
        print(indent + b_line + ' ' * spacing + t_line)

def copy_clipboard(text):
    from pot import clipboard
    return clipboard.copy_clipboard(text)

def open_html_in_browser(html_content):
    """Create a temporary HTML file and open in the default browser."""
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
        f.write(html_content)
        filename = f.name
    webbrowser.open(f'file://{filename}')