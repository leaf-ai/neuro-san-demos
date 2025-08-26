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

Copy `config/.env.sample` to `.env`. Neo4j, PostgreSQL and Chroma run without authentication by default, so no passwords are required. Then execute:
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
- Legal Research Team – provides case law and precedent lookup with `ResearchTools`.
- Forensic Financial Analysis Team – runs `ForensicTools` on financial records.
- Software Development Team – offers `CodeEditor` and `FileManager` utilities.
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

## Application Features

- Document uploads are stored in `uploads/` and indexed in a ChromaDB collection via `VectorDatabaseManager`.
- Knowledge graphs are persisted to Neo4j using `KnowledgeGraphManager`. Use `/api/graph` to query and `/api/graph/analyze` for centrality metrics.
- Timelines for each case are managed through `TimelineManager` with events stored in SQLite. Export via `/api/timeline/export`.
- The UI exposes tabs for ingestion, document tools, forensics, research, case management, vector search, graph visualisation, subpoena drafting and presentation generation.
- A dedicated **Agent Network** tab lists every subteam and tool from the manifest so users can understand the overall workflow.
- All coded tools are wired through dedicated Flask endpoints (e.g. `/api/document/redact`, `/api/agents/forensic_analysis`). See `interface_flask.py` for full list.

## End-to-End Startup Checklist

1. `npm --prefix apps/legal_discovery run build --silent`
2. `pytest -q`
3. `PYTHONPATH=$(pwd) AGENT_MANIFEST_FILE=$(pwd)/registries/manifest.hocon AGENT_LLM_INFO_FILE=$(pwd)/registries/llm_config.hocon python apps/legal_discovery/interface_flask.py`

This starts the Flask server on port 5001 without Docker. Docker Compose performs these steps inside the image automatically.
The helper `run.py` now uses `registries/manifest.hocon` as its default manifest so manual exports are rarely required.
