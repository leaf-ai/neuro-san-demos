#!/usr/bin/env bash
set -euo pipefail

# Check prerequisites
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Please install Docker." >&2
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  echo "Docker Compose is required. Please install docker compose." >&2
  exit 1
fi

# Pull and build images
$COMPOSE pull
$COMPOSE build

# Start dependencies for migrations
$COMPOSE up -d postgres neo4j chromadb redis

# Run database migrations (Alembic or Flask-Migrate)
set +e
$COMPOSE run --rm legal_discovery alembic upgrade head 2>/dev/null
if [ $? -ne 0 ]; then
  $COMPOSE run --rm -e FLASK_APP=apps.legal_discovery.startup:app legal_discovery flask db upgrade
fi
set -e

# Launch full stack
$COMPOSE up -d

echo "Stack is running. Access the app at http://localhost:8080"
