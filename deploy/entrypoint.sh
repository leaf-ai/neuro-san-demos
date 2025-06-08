#!/bin/bash

# --- System Setup ---
cat /etc/os-release
PYTHON=python3
PIP=pip3

echo "Using python ${PYTHON}"
echo "Using pip ${PIP}"

echo "Preparing app..."
if [ -z "${PYTHONPATH}" ]; then
    PYTHONPATH=$(pwd)
fi
export PYTHONPATH

echo "Toolchain:"
${PYTHON} --version
${PIP} --version
${PIP} freeze

PACKAGE_INSTALL=${PACKAGE_INSTALL:-.}
echo "PACKAGE_INSTALL is ${PACKAGE_INSTALL}"

# --- NeuroSan Agent Config ---
NEURO_SAN_SERVER_HOST=localhost
NEURO_SAN_SERVER_PORT=30015
export NEURO_SAN_SERVER_HOST NEURO_SAN_SERVER_PORT
echo "NEURO_SAN_SERVER_HOST=${NEURO_SAN_SERVER_HOST}"
echo "NEURO_SAN_SERVER_PORT=${NEURO_SAN_SERVER_PORT}"
AGENT_MANIFEST_FILE=${AGENT_MANIFEST_FILE:-${PYTHONPATH}/registries/manifest.hocon}
AGENT_TOOL_PATH=${AGENT_TOOL_PATH:-${PYTHONPATH}/coded_tools}

echo "AGENT_MANIFEST_FILE=${AGENT_MANIFEST_FILE}"
echo "AGENT_TOOL_PATH=${AGENT_TOOL_PATH}"

# Patch neuro-san bug if needed
NS_PATCH_FILE="$(${PYTHON} - <<'EOF'
import pathlib, importlib.util
spec = importlib.util.find_spec('neuro_san')
path = pathlib.Path(spec.origin).parent / 'internals/run_context/langchain/langchain_run_context.py'
print(path)
EOF
)"
if [ -f "${NS_PATCH_FILE}" ]; then
    sed -i "s/agent_spec.name={agent_spec.get(\"name\")}/agent_spec.name={agent_spec.get('name')}/" "${NS_PATCH_FILE}"
fi

# --- Start NeuroSan Agent in Background ---
echo "Starting NeuroSan agent on port ${NEURO_SAN_SERVER_PORT}..."
${PYTHON} -m neuro_san.service.agent_main_loop --port ${NEURO_SAN_SERVER_PORT} &



# --- Start nsflow UI (optional) ---
NSFLOW_PORT=${NSFLOW_PORT:-${PORT:-8080}}
echo "Starting nsflow UI on port ${NSFLOW_PORT}..."
if ${PYTHON} - <<'EOF' >/dev/null 2>&1
import importlib.util
exit(0) if importlib.util.find_spec('nsflow.backend.main') else exit(1)
EOF
then
    "${PYTHON}" -m uvicorn nsflow.backend.main:app --host 0.0.0.0 --port "${NSFLOW_PORT}" &
else
    echo "nsflow not installed, starting fallback HTTP server"
    "${PYTHON}" -m http.server "${NSFLOW_PORT}" --bind 0.0.0.0 &
fi

# --- Wait on foreground process ---
# Tail logs or block to keep container alive
wait
