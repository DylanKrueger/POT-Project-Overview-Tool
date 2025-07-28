# reports.py

import json
import matplotlib.pyplot as plt
import tempfile
import os
import webbrowser
import re
from VLTRE import clipboard
from pathlib import Path

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

def generate_json_report(data, output_path=None, copy=False):
    payload = json.dumps(data, indent=2)
    if output_path:
        try:
            Path(output_path).write_text(payload, encoding='utf-8')
        except Exception as e:
            print(f"[ERROR] Saving JSON output failed: {e}")
    if copy:
        clipboard.copy_clipboard(payload)
    return payload

def show_pie_chart(line_by_ext):
    labels = list(line_by_ext.keys())
    sizes = list(line_by_ext.values())
    plt.figure(figsize=(8,8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("File Types Distribution")
    plt.show()

def open_html_in_browser(html_content):
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w', encoding='utf-8') as tmpf:
        tmpf.write(html_content)
        tmp_path = tmpf.name
    url = 'file://' + os.path.abspath(tmp_path).replace('\\', '/')
    webbrowser.open(url)