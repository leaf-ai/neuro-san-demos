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
\n## Update 2025-07-27T22:15Z\n- Added tabbed layout to dashboard UI and new setupTabs JS\n- Next: verify usability and continue docker work
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
