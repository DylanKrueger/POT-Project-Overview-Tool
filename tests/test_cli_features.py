import subprocess
import sys
import os

# Set environment variable to enable UTF-8 mode
if os.name == 'nt':
    os.system('chcp 65001 >NUL')
    os.environ['PYTHONUTF8'] = '1'
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def run_cli_test(args, description):
    print(f"\n=== Running test: {description} ===")
    cmd = [sys.executable, "-m", "pot.cli"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Output:\n", result.stdout)
        if result.stderr:
            print("Errors:\n", result.stderr)
        print(f"--- Test '{description}' completed successfully ---")
    except subprocess.CalledProcessError as e:
        print(f"Error during '{description}': {e}")
        print("Stdout:\n", e.stdout)
        print("Stderr:\n", e.stderr)

if __name__ == "__main__":
    # Basic tests
    run_cli_test(["--list-drives"], "List drives")
    run_cli_test(["--root", "./nonexistent_dir"], "Invalid directory")
    run_cli_test(["--json", "--root", "./"], "JSON output in current directory")
    run_cli_test(["--copy", "--root", "./"], "Copy report in current directory")
    
    # Additional tests based on provided options
    run_cli_test(["--output", "test_output.txt"], "Save output to file")
    run_cli_test(["--open-url"], "Open report in browser")
    run_cli_test(["--verbose"], "Enable verbose output")
    run_cli_test(["--exclude", "node_modules", "tests"], "Exclude directories")
    run_cli_test(["--max-depth", "2"], "Limit directory traversal depth to 2")
    run_cli_test(["--show-largest", "--top", "5"], "Show top 5 largest files")
    
    # You can add more specific tests as needed