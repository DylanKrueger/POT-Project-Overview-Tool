# CLI Project Overview Tool

A command-line utility to generate a colorful, detailed directory tree with LOC (lines of code) statistics.  
Includes options to scan full drives, list available drives, export reports in JSON, and copy outputs to clipboard.

---

## Features

- **Colorized Directory Tree:** Visually appealing, color-coded folder structure for easy comprehension.
- **LOC & Size Stats:** Counts lines of code for specified file extensions, helping assess project size and complexity.
- **Largest Files Identification:** Quickly spot the biggest files that may need optimization.
- **Drive & Mount Point Listing:** Cross-platform support for Windows and Unix/Linux systems.
- **Full Drive/Drive Scan:** Capable of scanning entire drives for comprehensive analysis.
- **Flexible Export Options:** Save reports as plain text or JSON for automation or sharing.
- **Clipboard Integration:** Copy reports directly to clipboard for easy sharing.
- **Customizable Depth & Filtering:** Limit traversal depth and exclude system/dependency directories.
- **Extension-specific LOC Counting:** Focus on relevant file types tailored to your project/language.

---

## What Makes This Tool Unique on GitHub?

- **User-Friendly, Colorized Visualization:** Bright, intuitive directory trees that improve readability over plain text outputs.
- **Integrated Size & LOC Analytics:** Combines file size, LOC, and largest file analysis in one lightweight CLI.
- **Cross-Platform Drive Listing & Scanning:** Seamlessly supports Windows and Unix-like systems.
- **Easy Export & Sharing:** Built-in JSON report generation and clipboard copying streamline team communication.
- **Developer-Centric Design:** Fast, customizable, and simple to use with minimal setup.

---

## Installation

Clone the repository or download the source code, then install dependencies:

```bash
git clone https://github.com/DylanKrueger/POT-Project-Overview-Tool.git
cd "POT-Project-Overview-Tool"

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment:

# On Windows (Command Prompt):
venv\Scripts\activate

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate

# Install the package in editable mode
pip install -e .

# Install required dependencies
pip install -r requirements.txt

# uninstall CLI Tool
chmod +x pot_cleanup.sh
sudo ./pot_cleanup.sh
