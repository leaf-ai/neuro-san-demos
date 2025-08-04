- Focus on production-ready code for the `/apps/legal_discovery` module.
- Integrate with `registries/manifest.hocon` and coded tools for the legal_discovery network.
- Ensure the docker-compose stack builds and runs on Windows; fix gunicorn issues.
- Keep the UI polished, responsive and fully functional.
- Log progress in this file before each commit with a short summary of work and next steps.


###START UP SCRIPT###

#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Create a Python virtual environment.
python3 -m venv venv

# Activate the virtual environment.
source venv/bin/activate

# Set the PYTHONPATH to the current directory.
export PYTHONPATH=$(pwd)

# Install the required Python packages.
pip install -r requirements.txt
pip install python-dotenv
pip install neuro-san
pip install gunicorn
pip install pillow
pip install requests
pip install flask

echo "Setup complete. To activate the virtual environment, run 'source venv/bin/activate'"

## Update 2025-07-27T12:54Z
- Added AGENTS guidelines and first entry.
- Modified Dockerfile to run gunicorn via `python -m` to address Windows path issues.


## Update 2025-07-27T13:01Z
- Updated knowledge graph test to skip if Neo4j unavailable

## Update 2025-07-27T13:11Z
- Installed Python dependencies to enable pytest coverage plugins
- Confirmed all tests pass (2 passed, 2 skipped)
- Next: ensure Docker Compose builds cleanly on Windows

## Update 2025-07-27T13:17Z
- Installed project dependencies for testing (neuro-san, requests, pyvis)
- Added PYTHONPATH export in Makefile so tests find local packages
- Verified all tests pass with `pytest -q`
- Next: verify Docker Compose build on Windows


## Update 2025-07-27T13:28Z
- Reviewed repository for unfinished code; no placeholder functions found
- Added `delete_node` and `delete_relationship` helpers to KnowledgeGraphManager
- Updated unit test to use new cleanup method
- Attempted installing dependencies but installation was interrupted

- Next: get a clean environment to run full test suite

## Update 2025-07-27T15:24Z
- Added Flask app factories in `apps/__init__.py` and submodules to expose application objects
- Focused on `/apps/legal_discovery` but applied pattern to other demos for consistency
- Next: ensure Docker compose works on Windows without manual tweaks


## Update 2025-07-27T15:53Z
- Removed obsolete `dashboardLogic.js` script and cleaned up stray terminal output
- Installed required dependencies (`python-dotenv`, `neo4j`, `neuro-san`, `pyvis`) for running tests
- Confirmed all tests pass after cleanup (2 passed, 2 skipped)
- Next: review Docker compose build on Windows and polish remaining UI

## Update 2025-07-27T16:04Z
- Integrated several coded tools into the Flask app with new API routes for document redaction, Bates stamping and vector search
- Enhanced the dashboard UI to expose these new features and wired up client-side JavaScript
- Next: verify endpoints work in Docker Compose and continue tightening UX

## Update 2025-07-27T16:15Z
- Added document text extraction and task tracker API endpoints
- Extended dashboard UI with new buttons for text extraction and managing tasks
- Next: run tests and ensure Docker build works smoothly

## Update 2025-07-27T16:32Z
- Installed dependencies from both requirements files to satisfy test imports
- Verified all tests pass again (2 passed, 2 skipped)
- Next: confirm Docker Compose on Windows builds without errors

- Next: get a clean environment to run full test suite

## Update 2025-07-27T19:54Z
- Expanded dashboard with stats, forensic analysis and research sections
- Added corresponding API hooks and refreshed dark theme styles
- Confirmed all tests pass (2 passed, 2 skipped)
- Next: verify docker compose on Windows

## Update 2025-07-27T20:15Z
- Improved dashboard layout with responsive card grid and navigation bar
- Added FontAwesome icons and collapsible folder tree for uploads
- Updated styles for modern dark theme and polished visuals
- Confirmed tests still pass (2 passed, 2 skipped)
- Next: continue refining UI interactions and verify Docker stack

## Update 2025-07-27T20:30Z
- Added dashboard chat panel and settings modal with socket.io integration
- Refined card grid layout and sticky nav for better UX
- Created module AGENTS guide and logged tasks
- Next: polish graphs and timeline exports

## Update 2025-07-27T21:07Z
- Fixed imports for CodedTool modules to use `neuro_san.interfaces.coded_tool`
- Attempted installing requirements but network prevented completion
- Next: rebuild Docker images and verify gunicorn now loads without ModuleNotFoundError

## Update 2025-07-27T21:25Z
- Installed required dependencies (neuro-san, neo4j, pyvis) to run tests
- Confirmed all tests pass (2 passed, 2 skipped)
- Next: run Docker compose to verify imports resolved

## Update 2025-07-27T21:29Z
- Installed missing packages for pytest (`python-dotenv`, `neuro-san`, `neo4j`, `pyvis`)
- Verified tests succeed again (2 passed, 2 skipped)
- Attempted `docker compose` but the tool is unavailable in this environment
- Next: test Docker build once Docker is accessible
## Update 2025-07-27T22:15Z
- Added tabbed layout to dashboard UI and new setupTabs JS
- Next: verify usability and continue docker work

## Update 2025-07-27T22:45Z
- Started React migration for the dashboard to deliver a modern UI
- Implemented dashboard-react.jsx with API-connected components
- Updated dashboard template to load React via CDN
- Next: run tests and confirm new interface

## Update 2025-07-27T23:17Z
- Added interactive timeline and graph export features in React dashboard
- Implemented settings modal with API integration
- Confirmed tests pass after installing missing dependencies
- Next: continue refining UI interactions and docker support

## Update 2025-07-27T23:30Z
- Installed coverage plugin and required packages so pytest runs cleanly
- Verified the new React dashboard loads via `dashboard.html`
- All tests pass (2 passed, 2 skipped)
- Next: finalize Docker support and polish remaining UI components

## Update 2025-07-28T00:24Z
- Removed obsolete templates and static files; index now serves React dashboard
- Next: verify docker container loads updated UI

## Update 2025-07-28T01:49Z
- Default manifest now points to `registries/legal_discovery.hocon`
- Assistant setup passes uploaded file list to session metadata
- Next: ensure corpus ingestion works smoothly in Docker

## Update 2025-07-28T02:30Z
- Added subpoena and presentation endpoints to Flask app
- Expanded React dashboard with tabs for presentations and subpoenas
- Installed missing test dependencies so `pytest` runs
- Next: flesh out remaining team tools and verify Docker build

### Plan 2025-07-28
- Map each subnetwork in `registries/legal_discovery.hocon` to a dedicated UI tab
- Expose coded tool functions via REST endpoints to keep React components thin
- Finalize Docker support for cross-platform use and document setup steps
- Polish the dark theme and responsive layout for production readiness

## Update 2025-07-28T03:09Z
- Merged React UI changes with manifest default updates
- Default manifest path set to `legal_discovery.hocon` in run script
- Removed duplicated settings modal in dashboard template
- Next: verify timeline modal works and finalize Docker build

## Update 2025-07-28T03:19Z
- Installed missing packages for tests (dotenv, neuro-san, neo4j, pyvis)
- Confirmed pytest passes with coverage plugin
- Next: finalize Docker configuration and polish React UI

## Update 2025-07-27T21:07Z
- Fixed imports for CodedTool modules to use `neuro_san.interfaces.coded_tool`
- Attempted installing requirements but network prevented completion
- Next: rebuild Docker images and verify gunicorn now loads without ModuleNotFoundError

## Update 2025-07-27T21:25Z
- Installed required dependencies (neuro-san, neo4j, pyvis) to run tests
- Confirmed all tests pass (2 passed, 2 skipped)
- Next: run Docker compose to verify imports resolved

## Update 2025-07-27T21:29Z
- Installed missing packages for pytest (`python-dotenv`, `neuro-san`, `neo4j`, `pyvis`)
- Verified tests succeed again (2 passed, 2 skipped)
- Attempted `docker compose` but the tool is unavailable in this environment
- Next: test Docker build once Docker is accessible

## Update 2025-07-27T22:15Z
- Added tabbed layout to dashboard UI and new setupTabs JS
- Next: verify usability and continue docker work
## Update 2025-07-27T22:15Z
- Added tabbed layout to dashboard UI and new setupTabs JS
- Next: verify usability and continue docker work

## Update 2025-07-27T22:45Z
- Started React migration for the dashboard to deliver a modern UI
- Implemented dashboard-react.jsx with API-connected components
- Updated dashboard template to load React via CDN
- Next: run tests and confirm new interface

## Update 2025-07-27T23:17Z
- Added interactive timeline and graph export features in React dashboard
- Implemented settings modal with API integration
- Confirmed tests pass after installing missing dependencies
- Next: continue refining UI interactions and docker support


## Update 2025-07-27T23:30Z
- Installed coverage plugin and required packages so pytest runs cleanly
- Verified the new React dashboard loads via `dashboard.html`
- All tests pass (2 passed, 2 skipped)
- Next: finalize Docker support and polish remaining UI components

- Next: test Docker build once Docker is accessible

## Update 2025-07-28T06:55Z
- Added subpoena and presentation tabs in React dashboard with improved overview layout
- Updated settings modal with all credential fields
- Next: refine case management view and verify full workflow

## Update 2025-07-28T07:05Z
- Integrated CourtListener and California Codes search with Gemini summarisation
- Added source selector in research tab
- Next: enhance timeline exports with file excerpts

## Update 2025-07-28T07:36Z
- Added graph filtering and search
- Created case management tab with tasks and timeline
- Improved overview metrics
- Next: polish layout

## Update 2025-07-28T10:31Z
- Added progress indicators for uploads and exports in React dashboard
- Added date filters for timeline and improved export handling
- Next: enhance styling of overview metrics

## Update 2025-07-28T10:50Z
- Timeline API now returns citations and file excerpts
- React timeline shows excerpts in modal if no citation
- Exported timelines include excerpts for context
- Next: continue polishing UI layout

## Update 2025-07-28T11:05Z
- Added Team Pipeline view and document tool output links
- Improved dashboard navigation tabs
- Next: finalize visual polish and ensure tests pass

## Update 2025-07-28T14:23Z
- Auto-trigger document analysis after upload and store records in DB
- Create default case entry if none exists
- Next: verify ingestion pipeline with vector and graph updates

## Update 2025-07-28T14:42Z
- Reinitialize agent session after uploads so new files are included
- Next: validate analysis outputs returned to UI
- Next: finalize visual polish and ensure tests pass
## Update 2025-07-28T15:35Z
- Introduced Vite build for legal_discovery UI
- Split dashboard-react.jsx into modular components
- Build outputs to static/bundle.js and template updated
- Next: ensure tests pass and check Docker on Windows
## Update 2025-07-29T02:17Z
- Removed bundle.js from version control and added gitignore rules
- Documented build step producing bundle.js
- Next: verify npm build once dependencies install

## Update 2025-07-29T02:32Z
- Polished React dashboard tabs with icons
- Verified npm build and tests pass
- Next: refine backend API documentation
## Update 2025-07-29T03:01Z
- Added metric cards in overview section for better at-a-glance stats
- Styled new metric grid and built React bundle with Vite
- Next: refine pipeline layout responsiveness

## Update 2025-07-29T03:13Z
- Improved pipeline grid layout with icons and responsive CSS
- Rebuilt React bundle and confirmed tests pass
- Next: polish modal styling across sections
## Update 2025-07-29T03:22Z
- Added `/api/metrics` endpoint aggregating counts for uploads, vectors, graph nodes and tasks
- Updated React Overview and Pipeline sections to use this single endpoint
- Documented metrics endpoint in module README and rebuilt bundle
- Next: refine Docker setup for Windows compatibility

## Update 2025-07-29T03:32Z
- Improved React UI to show results from coded tools in their respective team tabs
- Forensic, subpoena and presentation sections now display output links
- Tabs renamed to match legal_discovery.hocon teams
- Next: verify build and tests
## Update 2025-07-29T03:54Z
- Added case management API and metrics
- Removed duplicate code in upload handler
- Dashboard overview and stats now show case counts
- Next: run tests and build

## Update 2025-07-29T05:53Z
- Extended React dashboard with case selector and creation form
- Documented the new UI in the module README
- Next: run tests and compile bundle

## Update 2025-07-29T06:40Z
- Added case deletion API and button in Case Management tab
- Improved research results with summary and case links
- Vector search now lists document IDs and snippets
- Updated README and rebuilt React components
- Next: verify build and unit tests
## Update 2025-07-29T07:06Z
- Added graph analysis endpoint and calendar events
- Next: build React bundle and run tests
## Update 2025-07-29T08:34Z
- Polished UI components and fixed missing EOF newlines
- Added lint hints for global libraries and updated graph icon
- Next: build React bundle and run tests

## Update 2025-07-29T08:57Z
- Renamed `default-llm` to `llm_config.hocon` so Docker start-up succeeds
- Documented AGENT_LLM_INFO_FILE path in `.env` files
- Next: run tests and rebuild React bundle
## Update 2025-07-29T09:17Z
- Set default AGENT_LLM_INFO_FILE so Docker starts without env variables
- Exposed new setting in run.py
- Next: rebuild React bundle and run tests

## Update 2025-07-29T09:52Z
- Added .dockerignore to reduce image context and integrated npm build into Dockerfile
- Installed build dependencies in tests and verified `npm run build` and pytest pass
- Next: confirm Compose deployment on Windows

## Update 2025-07-29T10:14Z
- Installed missing Python dependencies and Node modules for tests
- Built React bundle successfully
- Verified pytest and npm build pass
- Next: ensure Docker uses llm_config.hocon path to avoid startup error

## Update 2025-07-29T10:25Z
- Fixed Dockerfile build by copying package.json before npm install
- Ran npm build and pytest after installing dependencies
- Next: verify docker-compose image builds without errors

## Update 2025-07-29T20:47Z
- Installed missing dependencies so pytest runs
- Built React bundle after npm install
- Verified tests pass (2 passed, 2 skipped)
- Next: confirm docker-compose build on Windows

## Update 2025-07-29T21:20Z
- Remove quotes from AGENT_LLM_INFO_FILE in Dockerfile to fix startup error
- Next: verify docker-compose build and run tests

## Update 2025-07-29T21:35Z
- Set absolute AGENT_LLM_INFO_FILE path and resolve paths in Flask
- Reinstalled Node modules and built React bundle
- Verified pytest and npm build succeed
- Next: ensure container starts without llm path error

## Update 2025-07-29T22:06Z
- Refactored legal_discovery Dockerfile to a multi-stage build using Node 18
- Copied built static assets into the Python runtime image
- Verified `npm --prefix apps/legal_discovery run build --silent` and `pytest -q` pass
- Next: confirm docker-compose builds cleanly

## Update 2025-07-29T22:35Z
- Confirmed multi-stage Dockerfile runs `npm` in the Node builder stage so the runtime image no longer requires Node
- Reinstalled Node modules, built the React bundle and ran tests
- Next: validate docker-compose build on Windows without npm errors
## Update 2025-07-29T23:31Z
- Installed dependencies so pytest-cov works
- Ran npm build and pytest to confirm build issues fixed
- Next: confirm docker-compose build when Docker is available

## Update 2025-07-29T23:43Z
- Installed neuro-san, pyvis, flask and chromadb for tests
- Verified npm build and pytest pass
- Next: ensure docker-compose build works in CI

## Update 2025-08-01T12:14Z
- Reviewed documentation and coded tools for legal discovery
- Built React bundle and ran pytest (2 passed)
- Attempted to start server; neuro-san fails due to AGENT_LLM_INFO_FILE path
- Next: resolve LLM config path and confirm server startup

## Update 2025-08-01T12:34Z
- Diagnosed server startup failure due to AGENT_MANIFEST_FILE pointing to legal_discovery.hocon
- Set AGENT_MANIFEST_FILE to registries/manifest.hocon and confirmed NeuroSAN starts on port 30011
- Launched Flask UI on port 5001 after building React assets
- Next: refine startup script to use manifest.hocon by default

## Update 2025-08-01T12:50Z
- Reviewed all docs and registry files for legal_discovery
- Verified npm build and pytest pass locally
- Documented full startup workflow in memory_bank.md
- Next: polish UI with agent team cards

## Update 2025-08-01T13:25Z
- Set default AGENT_MANIFEST_FILE to registries/manifest.hocon in run.py and Flask app
- Added Agent Network tab with team cards in React UI
- Documented standalone startup steps and expanded memory_bank
- Next: verify container startup with new defaults

## Update 2025-08-02T22:08Z
- Added missing rfc3987 dependency for Chromadb startup
- Converted Flask imports to absolute paths so gunicorn serves the UI
- Next: ensure frontend build assets are referenced consistently

## Update 2025-08-02T22:23Z
- Automatically build React assets when bundle.js is absent and include generated CSS
- Next: confirm dashboard renders in browser and broaden API coverage

## Update 2025-08-02T23:05Z
- Set manifest path in Legal Discovery Dockerfile and removed placeholder env var
- Dropped repo bind mount from docker-compose so built frontend assets are served
- Next: build compose stack to verify UI loads in container

## Update 2025-08-02T23:48Z
- Initialize legal discovery agent in background thread so Flask responds immediately
- Next: exercise UI once container stack is available

## Update 2025-08-03T00:20Z
- Exposed agent and topic APIs and fixed front-end build wiring
- Next: verify docker compose serves dashboard assets reliably

## Update 2025-08-03T01:40Z
- Hardened file ingestion: skip malformed uploads, avoid overwrites, and batch files to prevent freezes
- Next: monitor upload throughput and refine vector database indexing

## Update 2025-08-03T02:20Z
- Added per-file hashing and timeout to skip duplicates and hung uploads
- Frontend now reports current file during batch uploads
- Next: investigate UI rendering in browser and optimize ingestion throughput

## Update 2025-08-03T02:48Z
- Uploads now feed documents into vector DB and Neo4j with 30s per-batch timeout
- Added UPLOAD_ROOT for external corpus storage and mounted volume in docker-compose
- React uploader batches requests and refreshes the knowledge graph after ingestion
- Next: exercise full analysis pipeline and confirm graph updates appear in UI

## Update 2025-08-03T04:07Z
- Enforced 30s per-file ingestion timeouts to skip hung uploads without freezing batches
- Next: watch upload pipeline for edge-case failures and expand error reporting to UI

## Update 2025-08-03T04:31Z
- Trigger orchestrator after each 10-file batch and persist vectors immediately
- Added progress bars for vector, knowledge, and Neo4j stages in React uploader
- Next: expose detailed ingestion metrics via API

## Update 2025-08-03T05:10Z
- Guarded upload route against unreadable or oversized files and enforced 1GB limit
- Next: surface skip reasons in UI and monitor ingestion stability
## Update 2025-08-03T06:30Z
- Ensured vector ingestion supplies filename metadata to satisfy Chroma requirements
- Next: verify large batch uploads no longer error on empty metadata

## Update 2025-08-03T07:30Z
- Sanitized vector metadata and added fallback retry to prevent empty metadata errors during ingestion
- Next: monitor vector ingestion for remaining edge cases

## Update 2025-08-03T09:40Z
- Normalised vector metadata in `VectorDatabaseManager` so every document includes a placeholder entry
- Next: monitor uploads for any remaining vector ingestion issues

## Update 2025-08-03T08:27Z
- Hardened vector database writes with an automatic retry using placeholder metadata to prevent ingestion stalls
- Next: watch batch uploads for any files that still fail to index

## Update 2025-08-03T11:00Z
- Run file ingestion in separate processes and terminate tasks exceeding 30s so uploads never hang
- Next: monitor memory usage during large uploads

## Update 2025-08-03T12:30Z
- Track processed files per batch so agent session reloads after each successful chunk
- Next: monitor ingestion logs for skipped files and prompt reloads

## Update 2025-08-03T13:45Z
- Introduced Document Drafter agent with AAOSA delegation and frontend panel
- Added neon glow styling for active tabs and wired aaosa macros into `legal_discovery.hocon`
- Next: extend AAOSA pattern to remaining agents and expose drafted outputs in UI summaries

## Update 2025-08-03T16:00Z
- Hardened file ingestion with explicit termination and skip logging for files exceeding 30s
- Shifted UI palette toward smoky greys with translucent glass panels
- Next: audit skipped_uploads.log for recurring file issues and polish remaining grey theme elements

## Update 2025-08-03T17:30Z
- Overhauled dashboard and timeline with a glassy neon-blue "alien warship" theme
- Introduced shared design tokens via CSS variables, React `theme.js` and Figma export
- Next: extend token usage across all components and confirm Docker build serves new assets

## Update 2025-08-03T18:30Z
- Repaired file ingestion subprocess block to resolve gunicorn syntax errors
- Restored queue-based timeout handling and batch tracking in `interface_flask.py`
- Next: verify gunicorn startup in Docker

## Update 2025-08-03T19:50Z
- Batched document commits with dual-schema metadata storage and concurrent ingestion processes
- Skipped and logged files that exceed 30s without halting batch progress
- Next: monitor batch commit performance and tune concurrency

## Update 2025-08-03T20:30Z
- Moved AAOSA include inside root object in `legal_discovery.hocon` to resolve parse errors during agent initialization
- Next: confirm configuration loads and tests pass

## Update 2025-08-03T21:45Z
- Hoisted document ingestion wrapper to module scope so multiprocessing can spawn workers without pickling errors
- Next: ensure batch uploads run cleanly and surface skipped files in UI

## Update 2025-08-03T22:40Z
- Wired settings button to trigger modal and exposed `/api/graph/cypher` endpoint with starter query buttons
- Shifted dashboard container to dark gunmetal glass for clearer contrast against neon cards
- Next: enrich cypher results formatting and continue tightening glass theme consistency

## Update 2025-08-04T00:30Z
- Added PostgreSQL configuration for Flask via `DATABASE_URL` with SQLite fallback
- Pointed vector database manager to an external Chroma service
- Extended docker-compose with a PostgreSQL service and wiring for Chroma
- Next: refine graph exploration UI and document deployment steps
