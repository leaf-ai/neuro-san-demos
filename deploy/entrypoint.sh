#!/bin/bash

# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

# Entry point script which manages the transition from
# Docker bash to Python

cat /etc/os-release

PYTHON=python3
# Use Python 3.12 by default as newer f-string syntax requires it
# PYTHON=${PYTHON:-python3.12}
echo "Using python ${PYTHON}"

PIP=pip3
echo "Using pip ${PIP}"

echo "Preparing app..."
if [ -z "${PYTHONPATH}" ]
then
    PYTHONPATH=$(pwd)
fi
export PYTHONPATH

echo "Toolchain:"
${PYTHON} --version
${PIP} --version
${PIP} freeze

PACKAGE_INSTALL=${PACKAGE_INSTALL:-.}
echo "PACKAGE_INSTALL is ${PACKAGE_INSTALL}"

# echo "Starting grpc service with args '$1'..."
# ${PYTHON} "${PACKAGE_INSTALL}"/neuro_san/service/agent_main_loop.py "$@"
# echo "Starting grpc service with args '$@'..."
echo "Starting grpc service with args $@..."
# Patch a known bug in neuro-san 0.5.31 where a quoting error
prevents the server from starting. If the file exists, fix it.
NS_PATCH_FILE="$(${PYTHON} - <<'EOF'
import pathlib, importlib.util, sys
spec = importlib.util.find_spec('neuro_san')
path = pathlib.Path(spec.origin).parent / 'internals/run_context/langchain/langchain_run_context.py'
print(path)
EOF
)"
if [ -f "${NS_PATCH_FILE}" ]; then
    sed -i "s/agent_spec.name={agent_spec.get(\"name\")}/agent_spec.name={agent_spec.get('name')}/" "${NS_PATCH_FILE}"
fi

# Start the nsflow web client so the dashboard is available.
NSFLOW_PORT=${NSFLOW_PORT:-${PORT:-8080}}
echo "Starting nsflow on port ${NSFLOW_PORT}..."
"${PYTHON}" -m uvicorn nsflow.backend.main:app --host 0.0.0.0 --port "${NSFLOW_PORT}" &

# Display and forward all provided arguments
echo "Starting grpc service with args $@..."
# Directly invoke the installed module
exec "${PYTHON}" -m neuro_san.service.agent_main_loop "$@"
echo "Done."
