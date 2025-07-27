import os
import json
from VLTRE import display

# Path for user data
DATA_FILE = os.path.expanduser("~/.pot_progress.json")
# Path for ASCII art files
STAGE_DIR = 'stages'  # Make sure this directory exists and contains stage0.txt, stage1.txt, etc.

def load_user_data():
    """Load user progress or return defaults."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Defaults: start at stage 0, zero regrow count, zero total runs
    return {
        "growth_stage": 0,
        "regrow_count": 0,
        "total_runs": 0
    }

def save_user_data(data):
    """Save user progress."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def get_tree_lines(stage):
    """Load ASCII art for the current stage from a text file."""
    filename = os.path.join(STAGE_DIR, f'stage{stage}.txt')
    try:
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
        return lines
    except FileNotFoundError:
        return ["[Tree stage not found]"]

def show_progress_bar(progress, indent=''):
    """Display a progress bar and handle stage advancement when progress reaches 100%."""
    total_bars = 20
    filled = int(progress * total_bars)
    bar = '[' + '#' * filled + '-' * (total_bars - filled) + ']'
    print(indent + f"{bar} {int(progress * 100)}%")
    
    # Check if progress is complete
    if progress >= 100:
        # Load user data
        data = load_user_data()

        # Reset total_runs
        data['total_runs'] = 0

        # Advance stage: cycle from 0 to 4
        if data['growth_stage'] < 4:
            data['growth_stage'] += 1
        else:
            data['growth_stage'] = 0

        # Save updated data
        save_user_data(data)

        print(f"\n--- Progress complete! Moving to stage {data['growth_stage']} ---\n")

def display_banner_with_tree():
    """Show current stage, display banner and ASCII art, and progress bar."""
    data = load_user_data()
    current_stage = data['growth_stage']
    total_runs = data['total_runs']
    progress = (total_runs % 10) / 10
    indent = ' ' * 20

    # Show current stage explicitly for debugging
    print(f"\n=== Current Stage: {current_stage} ===\n")

    # Display banner and ASCII art for current stage
    display.display_banner_and_tree(current_stage, indent=indent)

    # Show progress bar
    show_progress_bar(progress, indent=indent)

    # Save current state in case progress changed
    save_user_data(data)