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

# Ensure Neo4j schema constraints exist
python -c "from apps.legal_discovery import bootstrap_graph; bootstrap_graph()"

# Start the server and client.
python -m run
