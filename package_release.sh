#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(pwd)

# Build frontend assets
npm --prefix apps/legal_discovery ci
npm --prefix apps/legal_discovery run build

# Build backend wheel
mkdir -p dist
python -m build --wheel --outdir dist

# Package wheel and frontend build output
WHEEL=$(ls dist/*.whl | head -n 1)
if [ -z "$WHEEL" ]; then
  echo "Wheel build failed" >&2
  exit 1
fi

tar -czf dist/neuro-san-studio.tar.gz -C dist "$(basename "$WHEEL")" -C "$ROOT_DIR/apps/legal_discovery" static

echo "Created dist/neuro-san-studio.tar.gz"
