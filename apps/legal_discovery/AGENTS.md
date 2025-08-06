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

## Update 2025-07-28T03:09Z
- Synced template with React components by removing old settings modal
- Set default manifest in run.py to legal_discovery.hocon
- Next: verify timeline export works and finalize Docker config

## Update 2025-07-28T03:19Z
- Installed dependencies for tests and verified coverage
- React dashboard and manifest integration confirmed working
- Next: ensure Docker serves React UI correctly

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

- Next: verify Docker compose when environment supports it

## Update 2025-07-28T06:55Z
- Added subpoena and presentation tabs to React UI
- Extended settings modal with full credential fields
- Next: finalize overview page for team interactions

## Update 2025-07-28T07:05Z
- Integrated CourtListener and statute scraping in ResearchTools
- Research tab now lets users pick source
- Next: link timeline events to file excerpts

## Update 2025-07-28T07:36Z
- Graph search and subnet filter implemented
- Added CaseManagementSection tying tasks and timeline
- Overview shows vector counts
- Next: refine styles

## Update 2025-07-28T10:31Z
- Upload progress bar and export spinners added
- Timeline filters by date range and export feedback
- Next: polish tab visuals

## Update 2025-07-28T10:50Z
- Timeline endpoints provide excerpts with citations
- React timeline modal displays citation or excerpt
- Added helper to read excerpts from uploaded files
- Next: tweak graph layout

## Update 2025-07-28T11:05Z
- Added Team Pipeline section to React dashboard
- Document tools now show output links after stamping or redaction
- Next: polish remaining styles

## Update 2025-07-28T14:23Z
- Upload endpoint stores documents and kicks off analysis automatically
- Default case created on first run
- Next: review vector DB contents and refine UI polish

## Update 2025-07-28T14:42Z
- Session reload ensures new uploads reach agent network
- Next: improve styling polish
- Next: polish tab visuals
## Update 2025-07-28T15:35Z
- Added Vite build setup and modular React components
- Updated dashboard template to load compiled bundle
- Documented build command in README
- Next: verify build artifacts in Docker image
## Update 2025-07-29T02:17Z
- Removed compiled bundle from repo and added ignore rules
- Documented that bundle.js must be built locally
- Next: confirm React build step works in Docker

## Update 2025-07-29T02:32Z
- Added icons to dashboard tabs and improved styles
- Built bundle.js via Vite
- Next: test Docker image with compiled assets
## Update 2025-07-29T03:01Z
- Introduced MetricCard component and overview metrics grid
- Updated stylesheet with metric card styles and built bundle
- Next: adjust pipeline view for smaller screens

## Update 2025-07-29T03:13Z
- Redesigned pipeline section with icons and grid layout
- Compiled latest React build and verified unit tests
- Next: refine case management timeline display
## Update 2025-07-29T03:22Z
- Created aggregated `/api/metrics` endpoint for dashboard stats
- Overview and Pipeline React components now fetch from this endpoint
- Readme documents the new API; bundle rebuilt via Vite
- Next: polish timeline UI and confirm Docker build on Windows

## Update 2025-07-29T03:32Z
- Display results from Forensic, Subpoena and Presentation tools in the UI
- Renamed dashboard tabs to reflect team names from the manifest
- Next: run tests and build to ensure everything compiles
## Update 2025-07-29T03:54Z
- Implemented /api/cases endpoint and case count metric
- Fixed duplicate code in upload_files
- Overview and Stats sections updated with new metrics
- Next: verify npm build and tests

## Update 2025-07-29T05:53Z
- Added case management controls to the React UI
- README updated with instructions for using the case selector
- Next: run npm build and pytest

## Update 2025-07-29T06:40Z
- Implemented case deletion endpoint and UI control
- Enhanced research tab with formatted results and summaries
- Vector search view now shows IDs and snippets
- Updated documentation and prepared for build
- Next: compile bundle and ensure tests pass
## Update 2025-07-29T07:06Z
- Added calendar UI with backend events
- Introduced graph analysis tool
- Next: build bundle and run tests
## Update 2025-07-29T08:34Z
- Updated graph analyze icon and added global lint hints
- Fixed newlines in Dockerfile and stylesheet
- Next: rebuild React bundle and run tests

## Update 2025-07-29T08:57Z
- Renamed default LLM config to `llm_config.hocon`
- Updated `.env` examples with new path
- Next: run npm build and pytest
## Update 2025-07-29T09:17Z
- Default AGENT_LLM_INFO_FILE added to Flask app
- run.py now passes this path via environment
- Next: npm build and pytest

## Update 2025-07-29T09:52Z
- Dockerfile now installs Node and builds React bundle automatically
- Added project .dockerignore to keep images slim
- Verified build and tests pass
- Next: finalize UI polish

## Update 2025-07-29T10:14Z
- Installed pyvis, flask and chromadb for tests
- Ran npm install and built bundle with Vite
- All unit tests pass and build succeeds
- Next: fix llm_config path in Docker startup

## Update 2025-07-29T10:25Z
- Updated Dockerfile to copy Node manifests before install
- Rebuilt React bundle and ran pytest successfully
- Next: ensure docker-compose build succeeds

## Update 2025-07-29T20:47Z
- Installed extra Python packages so tests run
- Reinstalled Node modules and built Vite bundle
- Verified pytest and npm build succeed
- Next: check docker-compose on Windows

## Update 2025-07-29T21:20Z
- Adjusted Dockerfile to export AGENT_LLM_INFO_FILE without quotes
- Next: run npm build and pytest to confirm fix

## Update 2025-07-29T21:35Z
- Resolved LLM config path with absolute directories
- Reinstalled dependencies and built Vite bundle
- Tests pass with all new packages
- Next: validate docker-compose startup

## Update 2025-07-29T22:06Z
- Switched Dockerfile to multi-stage build with Node 18 for frontend assets
- Confirmed npm build and pytest succeed after the change
- Next: check docker-compose build on Windows

## Update 2025-07-29T22:35Z
- Verified the builder stage installs Node modules and compiles React before copying assets
- `npm run build` and `pytest -q` both succeed
- Next: ensure docker-compose builds without missing npm
## Update 2025-07-29T23:31Z
- Installed pytest-cov and other deps so tests run
- Rebuilt Vite bundle and ran pytest
- Next: verify docker-compose build when docker available

## Update 2025-07-29T23:43Z
- Installed neuro-san, pyvis, flask and chromadb so tests run
- Rebuilt Vite bundle and confirmed pytest passes
- Next: confirm Docker build pipeline

## Update 2025-08-01T12:34Z
- Built React bundle and launched Flask on port 5001
- Verified server start by pointing AGENT_MANIFEST_FILE to manifest.hocon
- Next: adjust run script to avoid port conflicts

## Update 2025-08-01T12:50Z
- Confirmed Flask server runs with AGENT_MANIFEST_FILE=registries/manifest.hocon
- Npm build and pytest succeed
- Added detailed build instructions to docs/memory_bank.md
- Next: implement agent network cards in React UI

## Update 2025-08-01T13:25Z
- Created AgentNetworkSection component and new tab
- Updated defaults to use manifest.hocon for local runs
- Rebuilt bundle and confirmed tests pass
- Next: test docker-compose build when available

## Update 2025-08-02T22:08Z
- Added rfc3987 dependency and switched Flask imports to absolute paths
- Verified gunicorn serves bundle.js and main.css after build
- Next: audit dashboard for missing stylesheet references

## Update 2025-08-02T22:23Z
- Trigger npm build at startup if bundle.js is missing and link main.css in the template
- Removed obsolete dashboard.js to avoid serving stale assets
- Next: confirm UI renders in browser and broaden API test coverage

## Update 2025-08-02T23:05Z
- Removed host bind mount from Docker Compose to keep built React assets inside container
- Set AGENT_MANIFEST_FILE in Dockerfile for consistent registry loading
- Next: build compose stack and verify dashboard renders in container

## Update 2025-08-02T23:48Z
- Load legal discovery assistant on a background thread so HTTP requests return immediately
- Next: verify dashboard interactivity once agent initialization completes

## Update 2025-08-03T00:20Z
- Added /api/agents and /api/topics endpoints backed by registry and database
- Ensured React build outputs load by bundling when missing
- Next: validate dashboard renders data from new endpoints

## Update 2025-08-03T01:40Z
- Implemented resilient upload pipeline with per-file error handling and batch processing
- Frontend now uploads files in groups of 10 and refreshes view after each chunk
- Next: surface upload errors to users and expand ingestion metrics

## Update 2025-08-03T02:20Z
- Display current filename during uploads and dedupe by SHA256 hash
- Backend rejects files that exceed a 30s ingestion timeout and persists batches
- Next: verify dashboard renders in browser and tune timeout threshold

## Update 2025-08-03T02:48Z
- Batch uploads now time out after 30s and update Neo4j and vector DB simultaneously
- Added UPLOAD_ROOT env support and graph refresh hook in React uploader
- Next: run end-to-end analysis to ensure orchestrator picks up new documents automatically

## Update 2025-08-03T04:07Z
- Wrapped full document ingestion in 30s guarded threads; uploads now skip stalled files and continue
- Next: surface skipped-file info in the React uploader

## Update 2025-08-03T04:31Z
- Batch uploads trigger orchestrator after each commit and show per-stage progress bars
- Next: expose ingestion metrics and error details through dashboard

## Update 2025-08-03T05:10Z
- Reject unreadable, oversized (>1GB), or disallowed files without stalling batches
- Next: propagate skip reasons to frontend and refine retry UX
## Update 2025-08-03T06:30Z
- Added filename and path metadata during vector ingestion to satisfy Chromadb
- Next: ensure batch uploads succeed without metadata errors

## Update 2025-08-03T07:30Z
- Guarded vector add with metadata sanitization and retry to avoid ingestion failures
- Next: observe batch uploads to ensure all files index correctly

## Update 2025-08-03T09:40Z
- `VectorDatabaseManager` now inserts placeholder metadata when none is provided, preventing Chroma errors
- Next: test large batch uploads to confirm ingestion remains stable

## Update 2025-08-03T08:27Z
- Wrapped Chroma `add` calls in a retry with default metadata so malformed files are skipped without stalling uploads
- Next: verify batch uploads proceed even when some documents contain empty metadata

## Update 2025-08-03T11:00Z
- Switched document ingestion to subprocesses and kill on timeout to prevent frozen uploads
- Next: surface timeout skips in UI

## Update 2025-08-03T12:30Z
- Append processed filenames to each batch so agent session reinitializes when chunks succeed
- Next: report skipped files back to users for troubleshooting

## Update 2025-08-03T13:45Z
- Added Document Drafter endpoint and React panel so trial prep team can draft pleadings
- Integrated AAOSA macros into `legal_discovery.hocon` and enhanced tab styling with neon glow
- Next: stream drafted document summaries back to the dashboard

## Update 2025-08-03T16:00Z
- Logged skipped uploads and enforced 30s kill switches so hung files no longer freeze batches
- Restyled dashboard with smoky glass greys and backdrop blur for a spaceship-like feel
- Next: surface skip reasons in UI and tighten grey theme across components

## Update 2025-08-03T17:30Z
- Applied alien warship glass theme with neon accents across dashboard and timeline
- Added reusable design tokens (`theme.js`, `figma_tokens.json`) for UI expansion
- Next: integrate tokens into remaining React components and verify Docker styling

## Update 2025-08-03T18:30Z
- Repaired ingestion subprocess setup to close syntax gap and handle timeouts via queue
- Batch tracking restored so sessions reload after successful uploads
- Next: ensure gunicorn starts cleanly with updated interface

## Update 2025-08-03T19:50Z
- Commit uploads per 10-file batch with concurrent ingestion and dual-schema metadata storage
- Log and skip 30s timeouts without halting remaining uploads
- Next: expose skipped file details in dashboard UI

## Update 2025-08-03T21:45Z
- Moved ingestion wrapper to top level so multiprocessing can start worker processes in upload route
- Next: monitor batch uploads for stable completion and report skipped files to users

## Update 2025-08-03T22:40Z
- Fixed dormant settings button by binding click handler and rendering modal with flex display
- Added preset Cypher query buttons and backend endpoint so graph exploration works without manual query knowledge
- Darkened dashboard backdrop with gunmetal gradient to differentiate cards
- Next: style query results output and refine hover animations across components

## Update 2025-08-04T00:30Z
- Enabled PostgreSQL via `DATABASE_URL` and wired Chroma host/port through environment variables
- Vector database manager now uses `HttpClient` for external Postgres-backed Chroma
- `docker-compose.yml` includes a PostgreSQL service for persistent storage
- Next: surface ingestion metrics and improve graph exploration usability

## Update 2025-08-04T02:00Z
- Switched upload route to a thread pool for parallel file processing with 30s timeouts
- Next: monitor executor load and refine async workflow

## Update 2025-08-04T03:00Z
- Added relational models for causes of action, elements, defenses and facts
- Introduced ontology loader with initial JSON schema
- Added unit test scaffold for ontology loading
- Next: integrate fact extractor and graph persistence

## Update 2025-08-04T??Z
- Implemented `FactExtractor` leveraging spaCy to pull parties, dates and actions
- Added spaCy requirement and unit test
- Next: connect extractor to upload pipeline and persist facts/relationships
## Update 2025-08-04T05:30Z
- Integrated `FactExtractor` into ingestion flow storing JSON facts in SQL and Neo4j
- Added `add_fact` helper to `KnowledgeGraphManager`
- Next: link facts to ontology elements and expose theory suggestions

## Update 2025-08-04T07:00Z
- Linked extracted facts to ontology elements and causes in Neo4j
- Added LegalTheoryEngine with `/api/theories/suggest` and Case Theory dashboard tab
- Highlighted supported elements with neon glow for clarity
- Next: refine scoring metrics and broaden ontology coverage

## Update 2025-08-04T09:30Z
- Weighted element links with spaCy similarity and Jaccard heuristics
- Surfaced element scores in Case Theory tab with neon progress bars
- Next: expand ontology vocabulary and tune similarity thresholds

## Update 2025-08-04T09:30Z
- Automated privilege detection with redaction logs and audit trail
- Upload pipeline stores originals securely and serves redacted copies
- Document tree marks privileged files for review with stealth icon
- Next: surface override controls in dashboard

## Update 2025-08-04T10:14Z
- Added dispute and origin relationships to KnowledgeGraphManager and cause subgraph export
- Expanded ontology tests and graph relationship coverage
- Next: incorporate scoring weights and timeline overlays in theory engine
## Update 2025-08-04T11:00Z

- Expanded legal theory ontology with negligence, defamation, false imprisonment, intentional infliction of emotional distress, and strict products liability.
- LegalTheoryEngine now exposes defenses and factual indicators alongside element support scores.
- Next: implement weighted scoring and add jurisdiction-specific defenses.

## Update 2025-08-04T12:30Z
- Extended Document model with exhibit fields and added ExhibitCounter and audit log tables.
- Introduced `exhibit_manager` service with binder generation and export helpers.
- Added unit test covering exhibit numbering and binder creation.
- Next: wire exhibit manager into dashboard UI and provide export controls.

## Update 2025-08-04T12:45Z
- Fixed exhibit manager test setup to avoid detached instances.
- Simplified exhibit_manager imports and verified all tests pass.
- Next: begin UI integration for exhibit controls.

## Update 2025-08-04T13:30Z
- Hardened exhibit logging with optional document IDs and export validation.
- Added zip export test and keyboard-focus styling for navigation links.
- Next: connect exhibit exports to dashboard controls.

## Update 2025-08-04T14:00Z
- Made exhibit numbering idempotent and corrected missing test imports.
- Refined navigation focus styling with an accent glow for accessibility.
- Next: wire binder and ZIP export actions into the dashboard UI.

## Update 2025-08-04T14:30Z
- Exposed exhibit operations via REST blueprint and registered routes.
- Added React Exhibits tab with assignment, binder and ZIP export controls.
- Styled exhibit table headers for better visual hierarchy.
- Next: support exhibit reordering and privilege filters in UI.

## Update 2025-08-04T12:00Z
- Introduced witness models and deposition prep tool with question generation, export, and React dashboard tab.
- Next: enhance review logging and offer PDF export.

## Update 2025-08-04T13:30Z
- Added contradiction detection with FactConflict records and prompt context.
- Export supports PDF including case ID, timestamp, and footnoted sources; UI offers separate DOCX/PDF buttons with improved styling.
- Next: implement deposition review approvals with permission controls.

## Update 2025-08-04T14:30Z
- Introduced deposition review logging with role-based checks and blocked exports for non-attorneys.
- React panel now collects reviewer ID and notes with enhanced hover styling on question items.
- Next: investigate optional deposition prep enhancements and deeper audit trails.
- Linked facts to ontology elements and generated cause support scores.
- Next: weight confidence by document credibility and expose metrics in UI.
## Update 2025-08-04T15:00Z
- Documented knowledge graph tests and re-ran suite after review fixes.
- Next: refine scoring weights for cause support metrics.

## Update 2025-08-05T03:22Z
- Added spaCy model and graph dependencies to requirements and Dockerfiles.
- Registered FactExtractor and LegalTheoryEngine in agent registry.
- Next: verify graph visualisations and theory suggestions.
## Update 2025-08-05T12:00Z
- Added tests for fact-element linking, theory scoring, and API endpoint coverage
- Documented `/api/theories/suggest` usage in README
- Next: broaden graph visualisations and extend endpoint coverage

## Update 2025-08-05T15:00Z
- Linked facts to supporting elements with `SUPPORTS` edges and tallied satisfied elements in `LegalTheoryEngine`
- Exposed `/api/theories/suggest` endpoint returning ranked theories with supporting facts
- Next: expand graph visualisation and refine element weighting metrics

## Update 2025-08-05T18:00Z
- Added weighted edge data to `get_cause_subgraph` and exposed `/api/theories/graph`
- Refined theory scoring to average element weights for ranking
- Next: surface graph visuals in dashboard and tune weighting heuristics

## Update 2025-08-05T20:00Z
- Surfaced cause-of-action graphs in the dashboard via event dispatch
- Scoring now blends element weights with coverage ratio
- Next: tune weighting thresholds and annotate graph nodes with fact counts

## Update 2025-08-05T21:00Z
- Upgraded privilege detection with legal spaCy model support and textcat scoring
- Logged redaction snippets and added privilege override API/UI controls
- Next: polish reviewer workflow and monitor classifier performance

## Update 2025-08-05T22:30Z
- Removed outdated deposition export from review endpoint to enforce reviewer IDs and avoid undefined variables
- Next: add unit tests covering deposition review logging

## Update 2025-08-05T10:56Z
- Added chain-of-custody logging model and event triggers
- Integrated logging utility across ingest, redaction, stamping, and export flows
- Exposed retrieval API and React dashboard panel for chain logs
- Next: extend filtering and export options for audit reports
## Update 2025-08-05T11:12Z
- Added `DocumentSource` enum and `source` field with migration
- Upload pipeline records source and returns it in file APIs
- Vector database now skips duplicate/similar documents
- React upload panel offers source selection, filtering, and color coding
- Next: fix failing KnowledgeGraphManager relationship test
## Update 2025-08-05T11:13Z
- Removed duplicate logging import in vector database manager
- Next: none
## Update 2025-08-06T00:00Z
- Added conversation and message tables for chat memory with privilege-aware visibility
- Implemented retrieval chat agent querying vector/graph stores with audit logging
- React chat panel now uses Socket.IO client for real-time updates
- Next: expand chat tests and manage multi-conversation UI

## Update 2025-08-06T03:51Z
- Swapped OpenAI dependencies for Google Generative AI in requirements
- Updated tooling to reference `google-generativeai`
- Next: verify Google API key configuration across services

## Update 2025-08-06T02:30Z
- Replaced OpenAI usage with Gemini equivalents and removed OpenAI dependency
- Next: verify cross-tool compatibility across modules
## Update 2025-08-06T02:40Z
- Cleaned up RAG docstrings to reference Gemini embeddings
- Next: confirm documentation aligns with new defaults

## Update 2025-08-06T04:45Z
- Implemented ChainOfCustodyLog model with immutable append-only records
- Wired logging utility into ingest, redaction, stamping, and export flows with retrieval API and dashboard panel
- Next: extend chain log filters and add report export options

## Update 2025-08-06T05:30Z
- Enhanced privilege detector with legal-model fallback and optional classifier
- Recorded span scores in `RedactionLog` and exposed manual privilege override API/UI
- Next: refine reviewer workflow and monitor classifier accuracy

## Update 2025-08-06T08:00Z
- Added migration for conversation and message tables with visibility enum.
- Verified retrieval chat agent wiring with privilege filtering and audit logging.
- Next: expand chat tests and support multi-conversation management.
## Update 2025-08-06T09:00Z
- Added Redis-backed message bus and listener module.
- Chain-of-custody logs now record `source_team` for provenance.
- Next: persist research insights received via message bus.

## Update 2025-08-06T10:30Z
- Extended ontology with new causes, defenses and jurisdiction mapping.
- Added `TheoryConfidence` model and migration linking facts to theories with source provenance.
- Upgraded fact extractor for NER tagging, relationship extraction and confidence scoring.
- Next: surface theory confidence metrics in API responses and dashboard graphs.

## Update 2025-08-06T12:30Z
- Added confidence-weighted SUPPORTS/CONTRADICTS edges and theory acceptance routing to drafter, pretrial and timeline APIs.
- Next: surface accepted theory outputs in dashboard UI.

## Update 2025-08-06T14:00Z
- Implemented approval, rejection and comment endpoints with UI controls and confidence bar.
- Graph and timeline auto-refresh on theory decisions and Cypress tests cover the workflow.
- Next: capture reviewer identity and expose theory review history.

## Update 2025-08-06T16:00Z
- Added legal crawler for bench cards, jury instructions, statutes and case law with Neo4j storage.
- Exposed CoCounsel and auto-drafter search APIs and scheduled daily crawler updates.
- Next: expand source-specific parsing and connect search results to dashboard UI.

## Update 2025-08-06T15:30Z
- Added `exhibit_order` column with migration and default assignment.
- Exposed reorder API and filtered exhibit listings by privilege and source team; UI highlights privileged entries.
- Next: add drag-and-drop reordering in React dashboard.

## Update 2025-08-06T17:30Z
- Added Gemini auto-drafter with motion templates and DOCX/PDF export.
- Added React Auto Draft panel with manual review before export.
- Next: expand motion templates and integrate deeper opposition metrics.

## Update 2025-08-06T18:30Z
- Embedded chat messages into Chroma with conversation vector IDs and graph links.
- Applied privilege-aware filters to retrieval to exclude restricted content.
- Next: broaden chat tests and surface similar message context in UI.

## Update 2025-08-06T19:00Z
- Added React ExhibitTab with drag-and-drop ordering plus privilege and source filters; entries show linked theories and timeline dates.
- Extended exhibit API with source filter and links endpoint; updated tests to cover ordering, filtering, and link retrieval.
- Next: connect exhibit links to detailed timeline view and broaden source options.

## Update 2025-08-06T20:30Z
- Enhanced exhibit export to bundle deposition excerpts, theory references, scorecards, and sanctions notes into PDF/ZIP.
- Added tests for exhibit numbering, cross-links, and privilege exclusions.
- Next: enrich PDF export formatting for metadata pages.
