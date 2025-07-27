# utils.py

import argparse
import os
import threading
import socketserver
import http.server
import webbrowser

def generate_html_report(structure_data, filename="structure.html"):
    html_content = f"""
    <html>
    <head>
        <title>Project Structure</title>
        <style>
            body {{ font-family: monospace; background: #222; color: #eee; padding: 20px; }}
            pre {{ white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <h1>Project Directory Structure</h1>
        <pre>{structure_data}</pre>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[DEBUG] HTML report written to {filename}")
    return filename

def print_html_file_url(html_path):
    abs_path = os.path.abspath(html_path)
    file_url = 'file://' + abs_path.replace('\\', '/')
    print(f"[INFO] You can also open this file directly: {file_url}")

def serve_html_report(html_path):
    dir_path = os.path.dirname(os.path.abspath(html_path))
    filename = os.path.basename(html_path)
    port = 8000

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dir_path, **kwargs)

    def start_server():
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}/{filename}"
            print(f"[DEBUG] Server URL: {url}")
            # Attempt to open in default browser
            try:
                webbrowser.open(url)
                print("[INFO] Browser should have opened automatically.")
            except Exception as e:
                print(f"[WARNING] Could not open browser automatically: {e}")
            print(f"[DEBUG] Serving at {url}")
            httpd.serve_forever()

    # Run server in background thread
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
