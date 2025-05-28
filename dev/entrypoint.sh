#!/usr/bin/env bash
set -euo pipefail

# entrypoint.sh: Simple initialization script for the Docker container

# Print hello message
echo "hello from entrypoint"

# 0) fix up PATH so ~/.local/bin (where --user installs land) is found
export PATH="$HOME/.local/bin:$PATH"

# move into the app directory
cd /home/user/app

# 2) print a greeting
echo "hello from entrypoint, let's install requirements and run the app"
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt

python -m run
# 3) drop into interactive bash
exec /bin/bash -i