- Focus on production-ready code for the `/apps/legal_discovery` module.
- Integrate with `registries/manifest.hocon` and coded tools for the legal_discovery network.
- Ensure the docker-compose stack builds and runs on Windows.
- Keep the UI polished, responsive and fully functional making at least one improvement to the asthetic every commit cycle. If there is no more room          for improvement, then you're wrong, look again and think harder, amybe even think 'bigger/ more complexity', just don't break anything.
- Log progress in this file before each commit with a short summary of work and next steps.
- ONLY IMPLEMENT PRODUCTION READY CODE. NEVER ANY MOCK/ PLACEHOLDER/ SIMULATION/ STUB/ FAKE/ TEMP/ TODO/ 'IF THIS WAS A REAL _________ (FILL IN THE BLANK), THEN....'. THE ONLY TIME THIS SORT OF PRACTICE IS ACCEPTABLE IS WHEN IT IS NECESSARY TO IMPLEMENT A FEATURE OVER MULTIPLE STEPS/ ITERATIONS, AND YOU ARE STUBBING A METHOD/ FUNCTION/ API CALL/ WHATEVER. USE IT SPARINGLY, OR I WILL STOP YOU MID COMMIT AND MAKE YOU FIX IT. thank you, sorry for yelling, carry on. BUT NOT WITH MOCK CODE!!!


AGENTS.md (Condensed)
Module Goals & Workflow
Build production-ready code for /apps/legal_discovery
Integrate with registries/manifest.hocon and tools for the legal_discovery network
Ensure Docker Compose builds and runs on Windows (fix gunicorn issues)
Keep UI polished, responsive, and functional (React migration, dark "alien warship" theme)
Log progress in this file before each commit—summarize work and next steps
Quick Setup Script
bash
#!/bin/bash
set -e
python3 -m venv venv
source venv/bin/activate
export PYTHONPATH=$(pwd)
pip install -r requirements.txt
pip install python-dotenv neuro-san gunicorn pillow requests flask
echo "Setup complete. To activate, run 'source venv/bin/activate'"
Major Progress Milestones
Testing & Environment:
Installed all required Python/Node dependencies for development and testing (pytest, coverage, linting, React bundle via Vite). Confirmed all tests pass before major changes.

Docker & Cross-Platform Support:
Dockerfile and docker-compose refactored for multi-stage builds and Windows compatibility. React frontend assets built during image creation; Node is only required at build time.
PostgreSQL and Chroma integrated for data persistence and vector search.

UI & Frontend:
Migrated dashboard to React for modular, modern UI.
Introduced tabs for team tools, case management, upload pipeline, metrics, and graph/timeline exports.
Glassy neon-blue dark theme with design tokens and Figma export.

Backend & API:
Added Flask API endpoints for document analysis, subpoena/presentation, task management, metrics, and graph queries.
Hardened file ingestion pipeline:

Batch uploads, per-file timeouts, parallel workers
Skipped/errored files logged, UI progress shown
Metadata normalization and retry logic for vector DB
Agent/Tool Integration:
Coded tools (redaction, Bates stamping, vector search, AAOSA pattern) exposed via REST endpoints.
Manifest and LLM config paths standardized for container startup.

Key Recent Updates
Implemented background agent initialization for responsive Flask API.
Hardened uploads: timeout, deduplication, error logging, vector/graph sync.
Refined dashboard: team tabs, case cards, metrics, progress bars, modals.
PostgreSQL & Chroma services added to docker-compose.
All startup scripts and environment variables documented in memory_bank.md.
Setup and build instructions documented; bundle.js removed from version control.
Typical Next Steps (Pattern)
Polish UI/UX and theme consistency.
Monitor/optimize upload and ingestion workflows.
Ensure Docker Compose and local workflows stay in sync.
Expand API/documentation for new features or agents.
For full details on any specific feature, agent, or deployment step, see the latest detailed entry before this summary or check memory_bank.md

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

## Update 2025-08-04T02:00Z
- Parallelized document ingestion using a thread pool with per-file timeouts
- Next: observe upload performance and tune worker counts


we are now working on implementing a major feature, so stand by, this is  A GDDMN PLACEHOLDER ARRRRRRRGGGGGGGHHh!!!!!!!!!!!!
## Update 2025-08-04T09:30Z
- Added privilege detection and redaction pipeline using spaCy keywords
- Stored originals in `_original` with reviewable redacted copies and audit logs
- Upload UI now flags privileged files with a stealth icon
- Next: build attorney review dashboard and refine classifier precision

## Update 2025-08-05T21:00Z
- Enhanced privilege detector with legal spaCy/textcat support and span logging
- Added API and UI controls to override privilege flags
- Next: expand review dashboard and tune classifier accuracy

## Update 2025-08-06T03:56Z
- Consolidated deposition question export into a single authorized method returning the generated file path
- Added unit tests covering PDF and DOCX exports with reviewer authorization
- Next: extend export tests to handle edge cases and additional formats

## Update 2025-08-06T04:18Z
- Added weasyprint stub for tests and expanded deposition prep assertions for contradiction detection and review logs
- Next: cover additional deposition prep edge cases

## Update 2025-08-06T10:30Z
- Expanded legal theory ontology with additional causes, defenses and jurisdiction data.
- Introduced `TheoryConfidence` model with migration linking facts to theories with scored confidence.
- Enhanced fact extractor to tag relationships and compute confidence from similarity and source reliability.
- Next: expose confidence metrics through API and UI visualisations.

## Update 2025-08-06T14:00Z
- Added theory review workflow with approval, rejection and comment endpoints plus confidence bar UI.
- Dashboard now refreshes graph and timeline on theory state changes with Cypress end-to-end coverage.
- Next: persist per-user review metadata and expand theory analytics.

## Update 2025-08-06T15:30Z
- Added `exhibit_order` field with migration and wired binder/zip exports to respect custom order.
- Introduced exhibit reorder API with privilege and source-team aware listing; highlighted privileged rows in UI.
- Next: surface drag-and-drop ordering in dashboard and extend source filters.

## Update 2025-08-06T18:30Z
- Stored chat message embeddings with privilege-aware filtering and graph links.
- Added vector IDs for conversations and messages with database migration.
- Next: expand conversation-level retrieval tests and refine graph relationships.

## Update 2025-08-06T12:13Z
- Added Gemini NLI-based narrative discrepancy pipeline with database model and API endpoints.
- Built React opposition tracker with filters and PDF/CSV export.
- Next: link discrepancies directly to timeline events and enhance bulk analysis.

## Update 2025-08-06T12:32Z
- Expanded motion template library with motions to compel and protective order pulling facts, accepted theories and conflicts.
- Refined Auto Draft UI with clear review status, disabled actions until approval and accent borders for edit state.
- Next: integrate opposition metrics into prompts and enhance export formatting.

## Update 2025-08-06T15:40Z
- Consolidated deposition question export into a single permission-aware method.
- Introduced a lightweight weasyprint stub and broadened tests for PDF/DOCX export, contradiction detection and review logging.
- Next: broaden deposition preparation edge-case coverage.

## Update 2025-08-09T00:00Z
- Added chat-driven timeline node with cross-links and summary queries plus blur polish for chat box.
- Next: enhance natural date parsing and surface linked events in UI.

## Update 2025-08-10T13:30Z
- Implemented Socket.IO presentation sync with PDF viewer and timeline hooks.
- Next: package offline presentation bundles.

## Update 2025-08-09T11:05Z
- Enabled voice-activated trial assistant with live transcription and objection guidance.
- Broadened objection rules with exceptions and counter-objection strategies; added unit test.
- Next: expand rule corpus and improve speech recognition fidelity.

## Update 2025-08-12T12:00Z
- Added PyInstaller packaging script and Windows documentation for building a standalone executable.
- Next: validate the generated `.exe` on a Windows machine.


## Update 2025-08-12T18:00Z
- Replaced google-generativeai with google-genai and removed conflicting packages.
- Dropped pygraphviz to avoid build-time failures.
- Next: stub external services so tests run without Neo4j.

## Update 2025-08-13T00:00Z
- Made Neo4j authentication optional and handled unreachable graph instances gracefully.
- Verified chat agent tests pass without a running Neo4j service.
- Next: run full application suite once Neo4j and related services are available.

## Update 2025-08-16T03:12Z
- Exposed `Agent` model in Flask import list and added missing `hashlib` import so document versioning tests collect properly.
- Polished navigation bar with border and neon glow for clearer separation.
- Next: exercise document stamping workflow against live databases.

## Update 2025-09-01T00:00Z
- Added React voice widget with microphone toggle, streaming transcript feed and objection alerts.
- Next: embed widget in dashboard and broaden cross-browser audio support.

## Update 2025-09-15T00:00Z
- Instrumented STT/TTS with Prometheus metrics and `/metrics` endpoint; added alerting rules.
- Next: monitor latency and failure alerts in staging.
## Update 2025-09-16T00:00Z
- Mocked speech engines and added tests for command routing, auth errors, message bus alerts, streaming transcripts and objection detection.
- Next: expand coverage for additional voice workflows.

## Update 2025-09-16T12:00Z
- Added unit tests for extractor typing, Neo4j upsert idempotency, and segment hashing.
- Introduced integration test for hybrid retrieval paths and objection events with refs.
- Implemented load test harness for 200 concurrent /api/hippo/query calls asserting p95 latency.
- Next: extend load metrics and broaden graph retrieval coverage.
