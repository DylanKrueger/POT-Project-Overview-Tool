# config.py
import argparse

def get_args():
    parser = argparse.ArgumentParser(
        description="Configuration for directory overview CLI"
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
    parser.add_argument("--share-entire-pot", action="store_true",
                        help="Show all files including dependencies and system files")
    parser.add_argument("--list-drives", action="store_true",
                        help="List all available drives or mount points")
    parser.add_argument("--scan-whole", action="store_true",
                        help="Scan entire drive(s) if no specific root is provided")
    parser.add_argument("--full-path", action="store_true", help="Show full absolute path of root directory")
    parser.add_argument("--show-largest", action="store_true", help="Show top largest files")
    # Added argument for web view
    parser.add_argument("--open-url", action="store_true", help="Generate an HTML view of the structure and open in browser")
    return parser.parse_args()