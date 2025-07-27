#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Create a Python virtual environment.
python3 -m venv venv

# Activate the virtual environment.
source venv/bin/activate

# Set the PYTHONPATH to the current directory.
export PYTHONPATH=$(pwd)

# Install the required Python packages.
pip install -r requirements.txt
pip install python-dotenv

echo "Setup complete. To activate the virtual environment, run 'source venv/bin/activate'"
