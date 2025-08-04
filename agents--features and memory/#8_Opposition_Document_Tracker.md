✅ Opposition Document Tracker — Technical Plan of Action
1. Document Source Flagging
Goal: Differentiate and tag documents based on their origin.

🔧 DB Schema Updates
Add a source column to the Document model:

python
Copy code
source = db.Column(db.String, default="user")  # values: "user", "opp_counsel", "court"
🖼️ UI Update
During upload:

Dropdown or toggle to set source:

“Uploaded by Us”

“Received from Opposing Counsel”

“Court Issued”

Color-code source in document list (e.g., red = opposing, blue = court)

2. Deduplication & Similarity Detection
Goal: Identify overlap between user and opposing documents.

🔍 Hash-Based Deduplication
On ingest, compute content hash:

python
Copy code
sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
Query DB:

sql
Copy code
SELECT id FROM document WHERE content_hash = :sha256 AND source = 'user'
If match → flag as duplicate

🤖 Embedding-Based Fuzzy Match
Generate vector on ingest (if not already present)

Query ChromaDB for similarity (e.g., cosine sim > 0.90)

Use it to identify “partial duplicates” or paraphrased content

3. Contradiction & Narrative Divergence Detection
Goal: Expose where opposing claims conflict with user evidence.

🧠 NLP Pipeline – contradiction_detector.py
Inputs:

Opposing doc (e.g., claim: “Client never contacted X”)

User docs w/ high similarity

Steps:

Chunk opposing doc

For each chunk:

Query vector DB for top-k similar user docs

Use contradiction detection model:

python
Copy code
from transformers import pipeline
contradiction = pipeline("text-classification", model="ynie/roberta-large-snli")
If label = “contradiction” → flag discrepancy

Store result in NarrativeDiscrepancy table:

sql
Copy code
id | opposing_doc_id | user_doc_id | conflicting_claim | evidence_excerpt | confidence
4. Dashboard: Opposition Evidence Tracker
Goal: Provide visibility and actionable insights on opposing documents.

📊 Dashboard Views
Received Documents section:

Filter by source = opp_counsel

Show status: Duplicate ✅ | Conflict ⚠️ | Untagged ⚪

Narrative Conflicts table:

Opposing claim vs. internal contradiction

Links to source documents

Manual flag for “Request Admission” or “Impeachment Candidate”

Missing Items:

Prompt user if expected discovery categories (e.g., “All contracts from 2022”) are missing from opposing production

📤 Export Options
Summary report (PDF/CSV):

List of opposing documents

Detected duplicates

Highlighted contradictions

5. Optional Enhancements
Timeline overlay: Show which side uploaded which doc first

Compare side-by-side view of similar opposing/user documents

Legal implication analysis (e.g., contradictions involving material facts)

🚀 Why This Wins
This lets litigants:

Track and organize incoming productions

Identify overlaps and missing items

Directly confront opposing narratives with evidence