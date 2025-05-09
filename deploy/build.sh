#!/bin/bash -e

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

# Script used to build the container
# Usage:
#   build.sh [--no-cache]
#
# The script must be run from the top-level directory of where your
# registries and code lives so as to properly import them into the Dockerfile.
#

export SERVICE_TAG=${SERVICE_TAG:-neuro-san-demos}
export SERVICE_VERSION=${SERVICE_VERSION:-0.0.9}

function check_directory() {
    working_dir=$(pwd)
    if [ "neuro-san-demos" == "$(basename "${working_dir}")" ]
    then
        # We are in the neuro-san-demos repo.
        # Change directories so that the rest of the script will work OK.
        cd . || exit 1
    fi
}


function build_main() {
    # Outline function which delegates most work to other functions

    check_directory

    # Parse for a specific arg when debugging
    CACHE_OR_NO_CACHE="--rm"
    if [ "$1" == "--no-cache" ]
    then
        CACHE_OR_NO_CACHE="--no-cache --progress=plain"
    fi

    if [ -z "${TARGET_PLATFORM}" ]
    then
        TARGET_PLATFORM="linux/amd64"
    fi
    echo "Target Platform for Docker image generation: ${TARGET_PLATFORM}"

    DOCKERFILE=$(find . -name Dockerfile | sort | head -1)

    # Build the docker image
    # DOCKER_BUILDKIT needed for secrets
    # shellcheck disable=SC2086
    DOCKER_BUILDKIT=1 docker build \
        -t neuro-san/${SERVICE_TAG}:${SERVICE_VERSION} \
        --platform ${TARGET_PLATFORM} \
        --build-arg="NEURO_SAN_VERSION=${USER}-$(date +'%Y-%m-%d-%H-%M')" \
        -f "${DOCKERFILE}" \
        ${CACHE_OR_NO_CACHE} \
        .
}


# Call the build_main() outline function
build_main "$@"
