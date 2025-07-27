import os
import json

DATA_FILE = os.path.expanduser("~/.pot_progress.json")

def load_user_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Default data
    return {
        "growth_stage": 0,
        "regrow_count": 0,
        "total_runs": 0
    }

def save_user_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def advance_stage(user_data):
    """Advance the growth stage with wrap-around from 4 to 0."""
    if 'growth_stage' not in user_data:
        user_data['growth_stage'] = 0
    if user_data['growth_stage'] < 4:
        user_data['growth_stage'] += 1
    else:
        user_data['growth_stage'] = 0
    # Increment regrow count each time stage advances
    user_data['regrow_count'] = user_data.get('regrow_count', 0) + 1
    # Save immediately
    save_user_data(user_data)