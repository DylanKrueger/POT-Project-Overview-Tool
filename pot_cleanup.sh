#!/bin/bash

echo "Starting cleanup of 'pot'..."

# Remove the main executable (adjust the path if different)
if [ -f /usr/local/bin/pot ]; then
    sudo rm -f /usr/local/bin/pot
    echo "Removed /usr/local/bin/pot"
else
    echo "/usr/local/bin/pot not found."
fi

# Uninstall the 'pot' Python package
pip uninstall -y pot

# Remove output files (if exist)
OUTPUT_FILE="$HOME/pot_output.txt"
if [ -f "$OUTPUT_FILE" ]; then
    rm -f "$OUTPUT_FILE"
    echo "Removed $OUTPUT_FILE"
else
    echo "$OUTPUT_FILE not found."
fi

# Optional: Remove config or other residual files if any
# For example:
# CONFIG_FILE="$HOME/.config/pot/config.json"
# if [ -f "$CONFIG_FILE" ]; then
#     rm -f "$CONFIG_FILE"
#     echo "Removed $CONFIG_FILE"
# fi

echo "Cleanup complete."