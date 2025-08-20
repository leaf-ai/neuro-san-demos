#!/bin/bash
set -e

# Start PostgreSQL, Chroma and Neo4j containers
# Requires docker-compose to be installed

docker-compose up -d postgres chromadb neo4j
