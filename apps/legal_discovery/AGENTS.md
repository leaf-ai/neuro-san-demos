# Legal Discovery Module Guide

- Keep the Flask routes and dashboard UI in sync. All features should be production ready with no placeholders.
- Ensure the dark theme remains responsive and professional.
- Log progress here before each commit with notes on next steps.

###STARTUP SCRIPT###
```bash
#!/bin/bash
set -e
python3 -m venv venv
source venv/bin/activate
export PYTHONPATH=$(pwd)
pip install -r requirements.txt
pip install python-dotenv flask gunicorn pillow requests neuro-san pyvis
```

### Update 2025-07-27T20:30Z
- Added interactive chat panel and settings modal to the dashboard.
- Refined styles with responsive grid and sticky navigation.
- Connected all controls to backend APIs via `dashboard.js`.
- Next: enhance data visualisations for the knowledge graph and timeline.

## Update 2025-07-27T21:07Z
- Updated imports for legal discovery tools to match new neuro_san package layout
- Install attempts failed due to network restrictions
- Next: test the Flask app in Docker once dependencies are resolved

## Update 2025-07-27T21:25Z
- Installed dependencies locally to run tests successfully
- Verified coded tool imports after update; tests pass
- Next: rebuild Docker image and ensure Flask app loads correctly

## Update 2025-07-27T21:29Z
- Confirmed tests run successfully after installing dependencies
- Docker tooling not available here so image build couldn't be tested
- Next: verify Docker compose when environment supports it
## Update 2025-07-27T22:15Z
- Introduced tabbed interface and updated dashboard scripts
- Next: refine styles and test Docker stack

## Update 2025-07-27T22:45Z
- Migrated dashboard to React for a richer UI
- Added dashboard-react.jsx and updated template to load React
- Next: run tests and verify Docker images once available

## Update 2025-07-27T23:17Z
- Added React settings modal tied to /api/settings
- Upgraded timeline view with vis.js and export action
- All tests pass after installing dependencies
- Next: polish remaining React components

## Update 2025-07-27T23:30Z
- Ensured coverage plugin installed so tests run
- Verified dashboard renders with new React design
- Tests succeed (2 passed, 2 skipped)
- Next: finalize Docker build scripts and refine CSS details

## Update 2025-07-28T00:24Z
- Cleaned up legacy HTML and JS; default route shows new React UI
- Next: ensure Docker front end refreshes

## Update 2025-07-28T01:49Z
- Use `legal_discovery.hocon` manifest and send uploaded files to the agent
- Next: verify ingestion pipeline within Docker compose

## Update 2025-07-28T02:30Z
- Created Flask routes for subpoena drafting and presentation generation
- Added React tabs to use these endpoints
- Installed missing Python packages so tests execute
- Next: integrate remaining sub-team tools and polish React styling

### Plan 2025-07-28
- Build tabs for each team in `legal_discovery.hocon` (case management, research, forensic, timeline, subpoena, trial prep)
- Provide REST endpoints for all coded tools with clear parameters and JSON responses
- Connect React components to these endpoints using fetch and intuitive forms
- Document Docker deployment and ensure gunicorn works on Windows
