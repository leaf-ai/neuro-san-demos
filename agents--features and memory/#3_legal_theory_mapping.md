⚖️ Legal Theory Mapping (Expanded)
🎯 Problem (Reframed)
Legal professionals are drowning in facts and documents, but litigation isn’t won on facts alone — it’s won on legal theories: persuasive, structured narratives backed by admissible evidence that satisfy the elements of a claim or defense.

Right now, building those theories is:

Manual

Time-consuming

Highly dependent on individual experience

✅ Your Solution Vision
Create a system that auto-generates legal theories grounded in your document corpus and legal knowledge graph, using a mix of:

NLP/embeddings

Ontologies of causes of action and elements

Graph reasoning

Retrieval-augmented generation (RAG)

🧠 System Architecture & Flow
1. Legal Theory Ontology
You need a structured model of legal theories.
This includes:

Causes of action (e.g., breach of contract, fraud, battery)

Required elements for each cause

Possible defenses

Typical factual indicators (e.g., false statement, reliance, damages)

🛠 Data source options:

CA Jury Instructions (CACI)

Cornell's LII

Manual extraction (start with a few causes, expand over time)

2. Fact/Theme Extraction via Embeddings
You already have:

A vector store

A document processor

Chroma/Neo4j in play

Here’s how to leverage that:

Break all docs into semantic chunks

Apply entity recognition and topic modeling to pull:

Parties

Actions

Dates

Causality

Contradictions

Use vector similarity + keyword hybrid queries to tag evidence with likely:

Causes of action

Elements satisfied

Inferred relationships

3. Graph-Based Case Theory Model
Store relationships in Neo4j:

ruby
Copy code
(:Fact)-[:SUPPORTS]->(:Element)-[:BELONGS_TO]->(:CauseOfAction)
(:Fact)-[:DISPUTED_BY]->(:Document)
(:Fact)-[:ORIGINATED_IN]->(:Deposition|:Email|:Message)
(:CauseOfAction)-[:DEFENDED_BY]->(:Defense)
→ This gives you visual, queryable maps of your case theories.

4. Legal Theory Suggestion Engine
Use a multi-step agent process:

Query: For each cause of action in your ontology, check if any elements are satisfied by facts in the evidence.

Aggregate: Build clusters of facts supporting a theory

Rank: Score theories by:

Number of elements satisfied

Strength of factual support

Consistency across documents

Generate Summary: Output a legal theory candidate like:

plaintext
Copy code
Suggested Theory: Intentional Infliction of Emotional Distress

- Extreme & outrageous conduct: Texts from May 3–6 show repeated threats.
- Intent: Language such as “I want you to suffer” (May 4).
- Severe emotional distress: Deposition of Plaintiff, lines 210–232.
You can generate these via RAG + prompt engineering from your Neo4j & Chroma data.

5. Interactive Legal Theory Builder UI
Let the user:

Click a theory (e.g., Fraud)

See how many elements are supported

View documents linked to each element

Manually approve, reject, or comment

Export theory to:

Motion draft

Statement of facts

Pretrial statement

💼 Why This Is Valuable (In Real Life)
User Type	What They Gain
Solo litigant	Confidence in structuring claims or defenses
Plaintiff-side firm	Faster intake + better damage theories
Defense counsel	Early case assessment + trial prep tools
Judges/clerks	(Eventually) structured review of legal sufficiency

🛠 Optional Power-Ups
Timeline overlay: Show when facts supporting each element occurred

Contradiction detector: Flag when supporting facts are undermined by later docs

Jurisdiction-aware theories: Filter elements based on state/federal distinctions

🧪 Prototype MVP Prompt (for now)
Here’s a simple dev prompt to bootstrap a prototype:

“Given this document set, suggest all possible causes of action that may apply, including a list of elements for each and which documents support each element.”

Once that works with 1–2 causes, wire it to Neo4j/Chroma and scale.
Plan for Implementing Legal Theory Mapping in neuro-san-studio-2
Establish Legal Theory Ontology

Create a structured ontology (legal_theory_ontology.json or similar) under coded_tools/legal_discovery/ describing causes of action, required elements, common defenses, and typical factual indicators.

Extend apps/legal_discovery/models.py with relational tables for CauseOfAction, Element, Defense, and Fact, linking facts to source documents and the existing LegalTheory model, which currently only holds a name and description.

Provide helper loaders to expose this ontology to both Flask routes and coded tools while aligning with root instructions for production-ready code and manifest integration.

Implement Fact and Theme Extraction

Introduce coded_tools/legal_discovery/fact_extractor.py that uses NLP (NER, topic modeling) to break ingested documents into semantic chunks, identify parties, actions, dates, causality, and contradictions, then tag candidate causes and elements.

Use existing VectorDatabaseManager for embeddings and hybrid queries; store extracted facts and metadata back into the new Fact table and Neo4j nodes.

Update ingestion pipeline in interface_flask.py to invoke the extractor after each upload, ensuring Flask routes and UI remain synchronized per module guidelines.

Extend Neo4j Graph Model

Augment KnowledgeGraphManager with new methods to persist (:Fact)-[:SUPPORTS]->(:Element)-[:BELONGS_TO]->(:CauseOfAction) and related relationships (e.g., :DISPUTED_BY, :DEFENDED_BY), building on existing node/relationship utilities.

Provide cleanup and subgraph retrieval routines for these new types to maintain visual, queryable case-theory maps.

Build Legal Theory Suggestion Engine

Create coded_tools/legal_discovery/legal_theory_engine.py that:

Loads ontology and queries Neo4j/Chroma for supporting facts.

Evaluates each cause of action by counting satisfied elements and scoring factual strength.

Generates RAG-based summaries for candidate theories.

Expose REST endpoints in apps/legal_discovery/interface_flask.py (e.g., /api/theories/suggest, /api/theories/<id>), returning structured results.

Interactive Legal Theory Builder UI

Add LegalTheorySection.jsx under apps/legal_discovery/src/components/ with a new dashboard tab allowing users to:

View suggested theories, elements, and supporting documents.

Approve/reject theories and export them to motion drafts or statements.

Wire the component to the new Flask endpoints, apply the existing dark theme and design tokens for visual consistency, and ensure responsive behavior.

Registries and Configuration

Register fact_extractor and legal_theory_engine in registries/legal_discovery.hocon so the orchestrator can delegate tasks to these tools.

Update apps/legal_discovery/requirements.txt and Dockerfiles/docker-compose to include new dependencies (e.g., spaCy, graph libraries) while keeping Windows compatibility and documenting any gunicorn changes.

Testing and Documentation

Add unit tests under tests/coded_tools/legal_discovery/ for ontology loading, fact extraction, graph persistence, and theory suggestion logic.

Update apps/legal_discovery/README.md with setup instructions, data-source references (e.g., CACI, LII), and usage examples.

Log progress in both AGENTS.md files before each commit, noting completed steps and next actions.