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

### Metrics Endpoint

Dashboard components use `/api/metrics` to retrieve counts for uploads,
vector documents, graph nodes, tasks, forensic logs and total cases in a single request.
This reduces network traffic and keeps the UI responsive.

The dashboard tabs are labelled after the teams defined in
`registries/legal_discovery.hocon`. Outputs from each coded tool are shown
directly within their respective sections so you can track the work of each
team at a glance.

Research results are summarised and displayed with direct links to matching
case law when available. Vector searches now list the matching document IDs
and text snippets instead of raw JSON for easier review.

The Case Management tab lets you create new cases and select one to view its
timeline. You can also delete the currently selected case. Use the form to
enter a case name, then refresh the list to pick it from the dropdown or remove
it with the **Delete** button.

### Case Management API

Use `/api/cases` to list existing cases or create a new one. POST requests require a JSON body with a `name` field and return the created case ID.
The Case Management tab lets you create new cases and select one to view its
timeline. Use the form to enter a case name, then refresh the list to pick it
from the dropdown.

### Case Management API

Use `/api/cases` to list existing cases or create a new one. POST requests require a JSON body with a `name` field and return the created case ID.
