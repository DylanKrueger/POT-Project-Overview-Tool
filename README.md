# Project Overview Tool

A Python script to generate a colourized directory tree with Lines of Code (LOC) statistics, including a tabular summary and top files detail. It can copy the report to clipboard, save it as text or JSON, and is customizable for excluding directories and file types.

## Features

- Recursively scans project directories
- Shows a colourized tree structure
- Counts LOC for selected file extensions
- Lists top N largest files
- Outputs report to console, file, and clipboard
- Supports JSON output for integration
- Excludes specified directories (e.g., `__pycache__`, `.git`, `venv`)

## Requirements

- Python 3.7+
- Required Python packages:
  - `colorama`
  - `pyperclip` (optional, for clipboard support)

Install dependencies via pip:

```bash
pip install colorama pyperclip