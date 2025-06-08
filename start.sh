#!/bin/bash
# Start script for Neuro SAN
# Delegates to the main entrypoint used inside the Docker container.
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/deploy/entrypoint.sh" "$@"
