import argparse

def load_config():
    parser = argparse.ArgumentParser(
        description="Directory overview CLI tool: generate source code stats, visualize structure, and more."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root folder to scan (default: current directory '.')"
    )
    parser.add_argument(
        "-e", "--ext",
        nargs="+",
        default=[".py", ".js", ".ts", ".css", ".html", ".json",
                 ".md", ".txt", ".yml", ".yaml"],
        help="File extensions to count as source (default: common code files)"
    )
    parser.add_argument(
        "-x", "--exclude",
        nargs="*",
        default=["__pycache__", ".git", "node_modules", "dist", "build"],
        help="Glob patterns to exclude from scan (default: common build/system dirs)"
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=10,
        help="Number of top largest files to display (default: 10)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors for better compatibility on some terminals"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report and save to '_project_overview.json'"
    )
    parser.add_argument(
        "--share-entire-pot",
        action="store_true",
        help="Include system and dependency files in the report"
    )
    parser.add_argument(
        "--list-drives",
        action="store_true",
        help="List all available drives or mount points"
    )
    parser.add_argument(
        "--scan-whole",
        action="store_true",
        help="Scan entire drive(s) if no specific root is provided"
    )
    parser.add_argument(
        "--full-path",
        action="store_true",
        help="Show full absolute path of the root directory"
    )
    parser.add_argument(
        "--show-largest",
        action="store_true",
        help="Display top largest files (requires --top)"
    )
    parser.add_argument(
        "--open-url",
        action="store_true",
        help="Generate an HTML view of the structure and open in browser"
    )
    # Additional user experience options
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy the report output to clipboard"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Specify output file path for the report (default: none)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging and detailed logs"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=0,
        help="Limit directory traversal depth (0 for unlimited)"
    )
    # New flag for saving output as text
    parser.add_argument(
        "--txt",
        action="store_true",
        help="Save the report output to a .txt file"
    )
    parser.add_argument(
     "--scan",
    action='store_true',
    help='Generate project overview report'
    )
    parser.add_argument(
    '--visualize',
    action='store_true',
    help='Display a pie chart of project overview statistics'
    )
    parser.add_argument(
    '--save-graph',
    action='store_true',
    help='Save the visualization as an image instead of displaying'
    )
    return parser.parse_args()