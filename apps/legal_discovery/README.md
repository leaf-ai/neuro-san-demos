# Legal Discovery Application

This directory contains a Flask application that provides a simple UI for running
Neuro SAN's legal discovery agent network.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and `docker-compose`
- API keys configured in `.env`

Make a copy of `.env.example` to `.env` and fill in the required values. In
particular set a password for Neo4j:

```bash
cp .env.example .env  # if you haven't created one
# then edit .env and set NEO4J_PASSWORD=your_password
```

## Running with Docker Compose

From the project root run:

```bash
docker-compose build
docker-compose up
```


- **legal_discovery** – the Flask frontend exposed on <http://localhost:8080>
- **neo4j** – graph database used by the app
- **tesseract** – OCR engine

Once the containers are running, open <http://localhost:8080> in a browser to

use the UI.

To stop the stack press `Ctrl+C` and run `docker-compose down`.

## Building the React Dashboard

The dashboard React code is built using [Vite](https://vitejs.dev/). Run the
following command from this directory to compile the assets into the `static/`
folder:

```bash
npm install
npm run build
```

The resulting `static/bundle.js` file is not committed to version control, so run
the build command whenever you update the React code.
