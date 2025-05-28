#!/bin/bash

# Script to check/create Docker volume, build image, and run container

# Variables
VOLUME_NAME="neuro-san-studio-history"
IMAGE_NAME="neuro-san-dev"
CONTAINER_NAME="neuro-san-container"
DOCKERFILE_PATH="dev/Dockerfile"

# Check if the Docker volume exists
if docker volume inspect "$VOLUME_NAME" >/dev/null 2>&1; then
    echo "Volume $VOLUME_NAME exists."
else
    echo "Volume $VOLUME_NAME does not exist. Creating it..."
    docker volume create "$VOLUME_NAME"
    if [ $? -eq 0 ]; then
        echo "Volume $VOLUME_NAME created successfully."
    else
        echo "Failed to create volume $VOLUME_NAME."
        exit 1
    fi
fi

# Build the Docker image
echo "Building Docker image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
if [ $? -eq 0 ]; then
    echo "Docker image $IMAGE_NAME built successfully."
else
    echo "Failed to build Docker image $IMAGE_NAME."
    exit 1
fi

# Run the Docker container
echo "Running Docker container $CONTAINER_NAME..."
docker run -it --env-file .env --rm --name "$CONTAINER_NAME" \
  -p 4173:4173 \
  -p 30013:30013 \
  -v "$VOLUME_NAME:/home/user/" \
  -v "$(pwd):/home/user/app/" \
  --entrypoint bash \
  "$IMAGE_NAME" -c "chmod +x /home/user/app/dev/entrypoint.sh && \
  exec /home/user/app/dev/entrypoint.sh"
if [ $? -eq 0 ]; then
    echo "Docker container $CONTAINER_NAME ran successfully."
else
    echo "Failed to run Docker container $CONTAINER_NAME."
    exit 1
fi