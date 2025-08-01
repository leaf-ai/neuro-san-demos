# Legal Discovery Memory Bank

This document summarizes the structure, configuration and startup steps for the `legal_discovery` module. It consolidates details from `README.md`, `AGENTS.md` files, registry manifests and coded tools so development can continue without re-reading all references.

## Repository Layout

- `apps/legal_discovery/` – Flask app exposing REST APIs and serving the React dashboard. Built with Vite (`package.json`, `vite.config.js`).
- `coded_tools/legal_discovery/` – Custom tools used by the legal discovery agent network such as `DocumentProcessor`, `TimelineManager` and `KnowledgeGraphManager`.
- `registries/legal_discovery.hocon` – Manifest defining the orchestrator and team structure. Tools are referenced by class name for each subteam.
- `registries/llm_config.hocon` – Default LLM configuration loaded via `AGENT_LLM_INFO_FILE`.
- `run.py` – Wrapper that starts the NeuroSAN server, nsflow client and optional Flask UI. Environment variables for the agent network are set here.
- `docker-compose.yml` – Spins up the Flask service, Neo4j and Tesseract OCR. React assets are built inside the Dockerfile.
- `tests/` – Unit tests for coded tools and API utilities. Running `pytest -q` should yield 2 passed, 2 skipped.

## Building the Frontend

From `apps/legal_discovery` run:
```bash
npm install
npm run build
```
This compiles React files in `src/` into `static/bundle.js`. The bundle is ignored by Git so build whenever the React code changes.

## Running Without Docker

1. `bash setup.sh` – creates a virtual environment and installs Python requirements.
2. Activate with `source venv/bin/activate`.
3. Build the React UI using the commands above.
4. Start the app via `python -m run` or directly run `apps/legal_discovery/interface_flask.py` after exporting:
   ```bash
   export PYTHONPATH=$(pwd)
   export AGENT_LLM_INFO_FILE=$(pwd)/registries/llm_config.hocon
   ```
5. The Flask server listens on port `5001` by default and serves the dashboard at `http://localhost:5001`.

## Docker Compose

Copy `.env.example` to `.env` and set `NEO4J_PASSWORD`. Then execute:
```bash
docker-compose build
docker-compose up
```
The stack launches the Flask front end on port `8080` plus Neo4j and Tesseract containers.

## Agent Manifest Highlights

`legal_discovery.hocon` enumerates subteams such as:
- Document Ingestion Team – uses `DataCollection`, `VectorDatabaseManager` and `DocumentProcessor`.
- Forensic Document Analysis Team – includes `FraudDetector` and `GraphAnalyzer`.
- Legal Analysis Case Strategy Team – uses `LegalSummary` and `KnowledgeGraphManager`.
- Timeline Construction Team – wraps `TimelineManager`.
- Trial Preparation & Presentation Team – exposes `PresentationGenerator`, `SubpoenaManager` and `DocumentModifier`.

Each tool appears in `coded_tools/legal_discovery/`. Example `KnowledgeGraphManager` connects to Neo4j and exposes helper methods for creating nodes and relationships【F:coded_tools/legal_discovery/knowledge_graph_manager.py†L1-L35】.

## Current Issue

Running `python -m run` currently fails because NeuroSAN cannot load `registries/llm_config.hocon`, reporting `ValueError: file_reference .../llm_config must be a .json or .hocon file`【F:logs/server.log†L1-L30】. The environment variable is not forwarded correctly when starting the server directly. Exporting `AGENT_LLM_INFO_FILE` before launching `interface_flask.py` still produces this error. Resolving the path handling in NeuroSAN is required to fully start the application outside Docker.

### Debugging Notes (2025-08-01)
Running `python -m run` initially failed because `AGENT_MANIFEST_FILE` defaulted to
`registries/legal_discovery.hocon`. The Neuro SAN server treated this network file
as a manifest and attempted to load `llm_config` as another file path, leading to
`ValueError: file_reference .../llm_config must be a .json or .hocon file`.
Exporting `AGENT_MANIFEST_FILE=registries/manifest.hocon` resolves the error.
The server can then be started with:
```bash
python -m neuro_san.service.main_loop.server_main_loop --port 30011 --http_port 8081
```
Followed by launching the Flask UI:
```bash
export FLASK_APP=apps/legal_discovery/interface_flask.py
python -m flask run --port 5001
```
