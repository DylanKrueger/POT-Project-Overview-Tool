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


---
## version[0.0.3] - 2025-06-22
### Added
- Implemented `--txt` flag in `cli.py` to allow users to save the project overview report to a `.txt` file explicitly. Report is only saved if `--txt` is specified; otherwise, it displays only in the console.
- Added a banner display that appears when running `pot` with no arguments, acting as a "home screen" with stylized ASCII art and info.
- Enforced that the project overview is generated only when `--scan` is used; otherwise, the CLI shows the banner and exits.
- Updated `setup.py` to support cross-platform, system-wide installation of the `pot` CLI tool using `entry_points`.
- Enhanced the CLI to support the `pot` command on Windows PowerShell, macOS Terminal, and Linux shells.
- Improved configuration handling to support the `--txt` flag via `config.py`.
- Added a `pot_cleanup.sh` script for easy removal of residual files and package uninstallation.
- Improved CLI argument parsing to support a `--scan` flag that triggers project overview generation.

### Fixed
- [Optional: list any bugs fixed in this release]

### Deprecated
- [Optional: list deprecated features]

### Removed
- [Optional: list features removed in this release]

### Notes
- Users can install the package system-wide on Windows PowerShell, macOS Terminal, and Linux shells using `pip install .`.
- To generate and save a report as a `.txt` file, run:
  ```bash
  pot --scan --txt