# Legal Discovery Application

This directory contains a Flask application that provides a simple UI for running
Neuro SAN's legal discovery agent network. Core capabilities include legal theory
mapping with confidence scoring, an exhibit and trial binder, CoCounsel chat with
memory and voice support, and an opposition document tracker. Language tasks are
powered by Google's Gemini models.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and `docker compose`
- A running PostgreSQL instance (the provided `docker-compose.yml` spins one up automatically)
- API keys configured in `.env` (set `GOOGLE_API_KEY` for Gemini)

Make a copy of `.env.example` to `.env` and fill in the required values. In
particular set a password for Neo4j:

```bash
cp .env.example .env  # if you haven't created one
# then edit .env and set NEO4J_PASSWORD=your_password
```

## Running with Docker Compose

From the project root run:

```bash
docker compose build
docker compose up
```


- **legal_discovery** – the Flask frontend exposed on <http://localhost:8080>
- **neo4j** – graph database used by the app
- **tesseract** – OCR engine

Once the containers are running, open <http://localhost:8080> in a browser to

use the UI.

To stop the stack press `Ctrl+C` and run `docker compose down`.

## Running Without Docker

1. Execute `bash setup.sh` from the project root to create a virtual environment and install Python dependencies.
2. Run `npm install` and `npm run build` inside `apps/legal_discovery` to compile the React dashboard.
3. Export required variables so NeuroSAN loads the correct manifest and LLM config:
   ```bash
   export AGENT_MANIFEST_FILE=registries/manifest.hocon
   export AGENT_LLM_INFO_FILE=registries/llm_config.hocon
   ```
4. Start the Flask server with `python apps/legal_discovery/interface_flask.py` and open <http://localhost:5001>.

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

Each case includes a calendar for filing deadlines and court appearances.
Add events using the form below the calendar and they will appear as dots on
their respective dates.

The Graph tab now features an **Analyze** button which performs a centrality
check on the stored Neo4j graph and highlights the most connected nodes.
Insights from the analysis are also forwarded to the agent network.

### Case Management API

Use `/api/cases` to list existing cases or create a new one. POST requests require a JSON body with a `name` field and return the created case ID.

### Theory Suggestions API

Facts extracted from uploaded documents can be linked to ontology elements in the knowledge graph. Once linked, the `LegalTheoryEngine` scores each cause of action based on the proportion of supported elements.

```python
from coded_tools.legal_discovery.knowledge_graph_manager import KnowledgeGraphManager

kg = KnowledgeGraphManager()
fact_id = kg.create_node("Fact", {"text": "Alice signed a contract"})
kg.link_fact_to_element(fact_id, "Breach of Contract", "Existence of a contract")
```

Call the REST endpoint to retrieve scored theory suggestions:

```bash
curl http://localhost:5001/api/theories/suggest
```

The response returns each cause with a `score` from 0 to 1 and the supporting facts for its elements.
