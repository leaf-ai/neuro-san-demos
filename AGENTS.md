- Focus on production-ready code for the `/apps/legal_discovery` module.
- Integrate with `registries/manifest.hocon` and coded tools for the legal_discovery network.
- Ensure the docker-compose stack builds and runs on Windows; fix gunicorn issues.
- Keep the UI polished, responsive and fully functional.
- Log progress in this file before each commit with a short summary of work and next steps.


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
