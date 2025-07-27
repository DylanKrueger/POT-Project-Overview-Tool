# Changelog

## [Unreleased / Upcoming]
- Support for additional export formats: HTML, Markdown, CSV, Excel.
- Filtering options: by file size, modification date, and file type.
- Visualization tools: pie charts, bar graphs, and treemaps.
- Version control integration: detect untracked/modified files (e.g., Git).
- Configuration files for recurring scans and automation.
- Web UI for interactive browsing and detailed reports.
- Natural language summaries and project insights via LLMs.
- Performance optimizations with async scanning and streaming output.
- CLI commands for advanced control: `--help`, `--list-drives`, `--drive`, `--full-scan`, `--json`, `--clip`, `--depth`.

---

## [v0.0.2] - 2025-07-10
- Initial release with core features:
  - Colourized directory tree with LOC stats for selected extensions.
  - Drive listing on Windows and mount points on Unix/Linux.
  - Full drive scanning and system-wide overview.
  - JSON report output for integration and scripting.
  - Copy report directly to clipboard (multi-platform support).
  - Command-line interface with comprehensive help and options.
- Dependencies managed via `requirements.txt`.
- Included license (MIT License).
- Detailed `README.md` for setup and usage instructions.
 **Enhanced HTML report generation:**  
  - When using `--open-url`, the directory structure now displays **without color codes** for cleaner web presentation.
  - Implemented a new plain-text version stripped of ANSI escape sequences for HTML export.
- **Code refactor for clarity:**  
  - Added comments and structure to handle HTML report creation.
- **Bug fixes and stability improvements:**  
  - Ensured temporary files are properly cleaned up.
  - Fixed minor issues with path handling across platforms.
- **Performance improvements:**  
  - Optimized directory walking and file reading.
- **Future-proofing:**  
  - Prepared code for upcoming new features and flags.
  - **Added `tests/` directory for testing purposes**.

---

## **Added in this release**
- **Directory tree overview** with:
  - Colourized output for readability.
  - Lines of code (LOC) stats for user-specified extensions.
  - File size info and largest files.
- **CLI commands** for:
  - Scanning specific directories, entire drives, or system-wide.
  - Listing drives on Windows and mount points on Linux/macOS.
  - Support for filtering and ignoring common system/dependency directories.
  - Export report to JSON or copy directly to clipboard.
  - Opening reports in the default web browser.
- **New flags** and their descriptions:
  - `--full-path`: Show full absolute path of the root directory.
  - `--show-largest`: Display the top N largest files.
  - `--json`: Generate and save a JSON report.
  - `--clip`: Copy the report to clipboard.
  - `--list-drives`: List available drives or mount points.
  - `--scan-whole`: Scan entire drive(s) if no specific root is provided.
  - `--depth`: Limit the directory traversal depth (future flag, planned).
  - `--top`: Specify how many of the largest files to display (default: 10).
  - `--output`: Save the output to a specified file.
  - `--copy`: Copy the report directly to the clipboard.
  - `--open-url`: Open the report in the default web browser.
  - `--verbose`: Enable verbose output for debugging.
  - `--no-color`: Disable colored output for better compatibility.
  - `--share-entire-pot`: Share the entire project, ignoring ignore patterns.
  - `--max-depth`: Limit the directory traversal depth (0 for unlimited).

## **Note:** To add more flags or options in the future:
- Expand your argument parser in `config.py`.
- Implement corresponding logic in `cli.py`.
- Use the existing pattern for clean, modular code.

---

 ~~                                                                         ~~

