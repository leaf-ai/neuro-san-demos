1. Automated Privilege Detection & Redaction
Model Choice & Data Pipeline

Use a legal-domain NER model (e.g. spaCy's “en_legal_ner_md”) fine-tuned for attorney-client patterns.

Pipeline: ingest → chunk → NER → privilege classifier → redact → persist redacted versions.

Redaction Layer

Implement redaction helpers (redaction.py) that take spans flagged as privileged and insert placeholders (e.g., “[REDACTED: Attorney-Client]”) in a copy of the text/PDF.

Keep a mapping of redactions to original text for internal use, but never export the original text when redactions are active.

Review & Audit

Add a “privileged?” flag in the document table.

Provide an interface for attorneys to override AI decisions and maintain an audit log (who/when/what).

2. Real-Time Bates Stamping & Versioning
Bates Number Service

Implement a monotonic counter in the DB (e.g., bates_counter table).

Upon ingest, assign Bates numbers to each page or doc.

Support custom prefixes/formatting (“ABCD_000001”).

Version Control

For each uploaded revision, hash the file and store as a new version.

Show diff/metadata between versions; maintain a chain-of-custody record (hash, ingest time, user).

Export & Compliance

PDF overlays with Bates numbers placed in margin headers/footers.

Command-line utility or UI action for “Bates stamp this set” to reprocess existing docs.

3. Legal Theory Mapping (Core)
(You already have the plan; here’s the integration note.)

Complete ontology creation, fact extraction, graph persistence, suggestion engine, and UI per the prior roadmap.

Make sure privilege tags and Bates numbers flow into the Fact records so that theories respect privilege and can reference stamped pages.

4. Deposition Prep Generator
Witness–Document Linking

Enhance fact extraction to tag documents with participant names and roles (e.g., witness, party).

Maintain a Witness model tied to documents/facts in the DB and Neo4j.

Question Generation

Implement deposition_prep.py which:

For each witness, retrieves associated facts.

Prompts a language model to generate question clusters (background, event chronology, contradictions, damages).

Allows manual edits/approval in the UI.

UI/Export

New tab “Deposition Prep” with witness selector.

Export to PDF/Word outlines with question numbering, Bates references, and doc links.

5. Exhibit & Trial Binder Creator
Tagging & Management

Add “Exhibit” tag to documents; maintain order/index.

UI checkbox “Mark as Exhibit” in document view.

Binder Generation

Tool to compile exhibits into a binder:

Adds cover sheets with exhibit number and title.

Ensures Bates numbers are visible; cross-check for privilege.

Integration

Provide export options (PDF binder, zip of files).

Optional integration hooks for TrialPad/OnCue formats.

6. Live Co‑Counsel Chat + AI Memory
Conversation Store

Add Conversation and Message models with user identity and time stamps.

Maintain context windows referencing doc IDs and facts.

AI Agent

Implement a retrieval-augmented LLM interface that can pull from the vector store/Neo4j and reference prior chat messages.

Commands: “search docs”, “summarize facts”, “suggest theories”, etc.

Team Collaboration

Real‑time WebSocket-based chat with typing indicators and shared context.

Option to mark messages as private or shared.

7. Forensic Chain of Custody Dashboard
Data Collection

Expand logging to capture:

Ingest time, user, file hash, processing steps, redactions, Bates numbers, versions.

Store logs in a tamper‑evident format (append-only log table or external ledger).

Dashboard UI

Visual timeline of each document’s lifecycle.

Filters by user, date range, hash changes, processing outcome.

Export

Generate chain-of-custody reports per doc or per case, including all events and hashes.

8. Opposition Document Tracker
Flagging Opposing Docs

Add a “source” field on docs (user, opp_counsel, court, etc.).

On ingest, user marks doc as “Received from Opposing Counsel.”

Duplicate & Narrative Analysis

Deduplicate against existing docs by hash/embedding similarity.

Compare conflicting narratives; highlight discrepancies (contradiction_detector.py).

Dashboard View

Section to show what opposing counsel has produced, duplicates, missing items, and conflicting statements.

Bonus Moonshots (Outline)
Court Filing Auto-Drafter

Template-based drafting system that pulls facts/elements/theories and populates motion outlines.

Manual review step before final export.

Pretrial Statement Generator

Use existing facts and theory approval data to auto-build stipulations, contested issues, witness lists, etc.

Evidence Scorecard

Heuristic/ML model scoring docs by probative value, admissibility risk, narrative alignment (tie into LTM).

Display scores and sorting features in doc review.

Chat-Style Timeline Builder

Interactive timeline node where users chat to insert events or ask for chronological summaries.

Integration with deposition prep and exhibits.

Implementation Guidelines & Sequencing
Infrastructure First

Build core DB tables, versioning, privilege/redaction pipeline.

Extend logging to support chain-of-custody.

Legal Theory Mapping

Implement ontology, fact extraction, graph model, and theory engine (as previously outlined).

Deliver initial UI for theory review.

Privilege, Bates, and Versioning

Integrate with ingestion process and document viewer.

Ensure all downstream features respect these annotations.

Deposition Prep & Exhibit Binder

Leverage extracted facts and Bates tags to produce questions and exhibit lists.

Provide export features.

Collaboration & Dashboards

Add real-time chat with memory, chain-of-custody UI, and opposition tracker.

Moonshot Features

Once core features are stable, layer in court-filing drafter, pretrial statement generator, evidence scorecard, and timeline chatbot.

Testing & Documentation

Unit tests for each module; integration tests for pipelines.

Update README.md and new feature docs; maintain AGENTS.md logs per repo policies.

By following this roadmap, you move from a powerful document processor to a fully integrated Legal Discovery Intelligence & Strategy Assistant, addressing core litigation pain points and offering the workflow enhancements legal teams will pay for.