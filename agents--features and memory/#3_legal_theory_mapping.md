# Enhanced Prompt for Legal Theory Mapping System

## ⚖️ Legal Theory Mapping (Expanded)

### 🎯 Problem Statement
Legal professionals are inundated with facts and documents, yet litigation success hinges on crafting compelling legal theories. These theories are persuasive, structured narratives supported by admissible evidence that address the elements of a claim or defense. Currently, the process of developing these theories is:

- **Manual**
- **Time-consuming**
- **Highly dependent on individual experience**

### ✅ Solution Vision
Develop a system that can automatically generate legal theories grounded in your document corpus and legal knowledge graph. This system will leverage:

- **Natural Language Processing (NLP) and embeddings**
- **Ontologies of causes of action and elements**
- **Graph reasoning**
- **Retrieval-augmented generation (RAG)**

### 🧠 System Architecture & Flow

#### 1. Legal Theory Ontology
Create a structured model of legal theories, including:

- **Causes of Action** (e.g., breach of contract, fraud, battery)
- **Required Elements** for each cause
- **Possible Defenses**
- **Typical Factual Indicators** (e.g., false statement, reliance, damages)

**Data Source Options:**
- California Jury Instructions (CACI)
- Cornell's Legal Information Institute (LII)
- Manual extraction (begin with a few causes, expand over time)

#### 2. Fact/Theme Extraction via Embeddings
Utilize existing resources such as a vector store and a document processor with Chroma/Neo4j. Implement the following steps:

- Break documents into semantic chunks.
- Apply entity recognition and topic modeling to extract:
  - Parties
  - Actions
  - Dates
  - Causality
  - Contradictions
- Use vector similarity and keyword hybrid queries to tag evidence with:
  - Likely causes of action
  - Elements satisfied
  - Inferred relationships

#### 3. Graph-Based Case Theory Model
Store and visualize relationships in Neo4j:

```plaintext
(:Fact)-[:SUPPORTS]->(:Element)-[:BELONGS_TO]->(:CauseOfAction)
(:Fact)-[:DISPUTED_BY]->(:Document)
(:Fact)-[:ORIGINATED_IN]->(:Deposition|:Email|:Message)
(:CauseOfAction)-[:DEFENDED_BY]->(:Defense)
```

This provides visual, queryable maps of case theories.

#### 4. Legal Theory Suggestion Engine
Implement a multi-step agent process:

- **Query**: For each cause of action, verify if any elements are satisfied by facts in the evidence.
- **Aggregate**: Cluster facts supporting a theory.
- **Rank**: Score theories based on:
  - Number of elements satisfied
  - Strength of factual support
  - Consistency across documents
- **Generate Summary**: Produce a legal theory candidate such as:

```plaintext
Suggested Theory: Intentional Infliction of Emotional Distress
- Extreme & outrageous conduct: Texts from May 3–6 show repeated threats.
- Intent: Language such as “I want you to suffer” (May 4).
- Severe emotional distress: Deposition of Plaintiff, lines 210–232.
```

Generate these via RAG and prompt engineering from your Neo4j & Chroma data.

#### 5. Interactive Legal Theory Builder UI
Enable users to:

- Click a theory (e.g., Fraud)
- See supported elements
- View linked documents
- Approve, reject, or comment on theories
- Export theories to:
  - Motion drafts
  - Statement of facts
  - Pretrial statements

### 💼 Value Proposition
| User Type         | Benefit                                    |
|-------------------|--------------------------------------------|
| Solo Litigant     | Confidence in structuring claims or defenses |
| Plaintiff-Side Firm | Faster intake and better damage theories  |
| Defense Counsel   | Early case assessment and trial preparation |
| Judges/Clerks     | Structured review of legal sufficiency      |

### 🛠 Optional Enhancements
- **Timeline Overlay**: Display when facts supporting each element occurred.
- **Contradiction Detector**: Flag supporting facts contradicted by later documents.
- **Jurisdiction-Aware Theories**: Filter elements based on state/federal distinctions.

### 🧪 Prototype MVP Prompt
For initial development, use the following prompt:

"Given this document set, suggest all possible causes of action that may apply, including a list of elements for each and which documents support each element."

### Implementation Plan for Legal Theory Mapping in `neuro-san-studio-2`

#### 1. Establish Legal Theory Ontology
- Create a structured ontology file (`legal_theory_ontology.json`) under `coded_tools/legal_discovery/`.
- Extend `apps/legal_discovery/models.py` with relational tables.
- Provide helper loaders to expose ontology to Flask routes and coded tools.

#### 2. Implement Fact and Theme Extraction
- Develop `fact_extractor.py` using NLP for semantic chunking and tagging.
- Utilize `VectorDatabaseManager` for embeddings and store extracted data.

#### 3. Extend Neo4j Graph Model
- Enhance `KnowledgeGraphManager` for new relationship types.
- Provide cleanup and subgraph retrieval routines.

#### 4. Build Legal Theory Suggestion Engine
- Create `legal_theory_engine.py` for ontology loading and Neo4j/Chroma querying.
- Expose REST endpoints for structured results.

#### 5. Interactive Legal Theory Builder UI
- Develop `LegalTheorySection.jsx` for user interaction.
- Integrate with new Flask endpoints.

### Configuration and Testing
- Register new tools in `registries/legal_discovery.hocon`.
- Update dependencies and Docker configurations.
- Add unit tests and documentation.

Log progress in `AGENTS.md` files with completed steps and next actions.

This comprehensive plan ensures the development of a robust, automated legal theory mapping system that enhances efficiency and accuracy in legal proceedings.
