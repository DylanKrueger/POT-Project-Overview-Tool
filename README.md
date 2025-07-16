# CLI Project Overview Tool

A command-line utility to generate a colourful, detailed directory tree with LOC (lines of code) statistics.  
Includes options to scan full drives, list available drives, and copy reports to clipboard.

---

## Features

- Colorized, visually appealing directory tree: Provides an easy-to-read, color-coded visualization of folder structures, making it simple to understand project organization at a glance.
- Detailed LOC and size stats: Counts lines of code for specific file extensions, helping assess codebase size and complexity.
- Largest files identification: Quickly identify the biggest files that may need optimization or cleanup.
- Drive and mount point listing: Supports both Windows and Unix/Linux systems to list available storage options.
- Full drive/system scans: Capable of scanning entire drives for comprehensive project and space analysis.
- Flexible output options: Export reports as plain text or JSON for easy sharing, automation, or further processing.
- Clipboard integration: Copy reports directly to clipboard for quick sharing or documentation.
- Customizable depth: Limit directory traversal to focus on relevant parts of large projects.
- Filtering and ignoring: Support for excluding system, dependency, or cache directories to focus on your source code.
- Extension-specific LOC counting: Focus on relevant file types, making reports tailored to your project language.

**What Makes This Tool Unique on GitHub?**
- User-Friendly, Colorized Visualization: Unlike many tools that produce plain text outputs, this tool offers a colourful, intuitive directory tree, simplifying comprehension of complex project structures.
- Integrated Size & LOC Analytics: Combines file size, LOC, and largest files analysis in one lightweight CLI, providing a comprehensive overview without complex setup.
- Cross-Platform Drive Listing & Scanning: Supports both Windows and Unix-like systems seamlessly, making it versatile for diverse development environments.
- Easy Export & Sharing: Built-in options to generate JSON reports and copy outputs directly to clipboard, streamlining integration into reports or team communications.
-Focused on Developer Workflow: Designed to be simple, fast, and customizable, allowing developers to tailor scans and reports to their specific needs with minimal setup.

---

## Installation

Clone the repository or download the source code, then install dependencies:

```bash
git clone https://github.com/DylanKrueger/POT-Project-Overview-Tool.git
cd "POT-Project-Overview-Tool"

### Create a virtual environment (if not already created):

```bash
python -m venv venv

Activate the virtual environment:
On Windows (Command Prompt):
venv\Scripts\activate

On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

On macOS/Linux:
source venv/bin/activate

##installation
pip install -e .