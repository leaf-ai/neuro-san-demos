**Improved Prompt: Comprehensive Technical Plan of Action for Developing an Opposition Document Tracker**

---

**Objective:** Develop a detailed, step-by-step technical plan for creating an Opposition Document Tracker. This tracker must efficiently manage and analyze documents from various sources, identify duplicates, detect contradictions, and provide actionable insights through an intuitive user dashboard.

**Target AI Model:** Codex / ChatGPT

---

### **1. Document Source Flagging**

**Goal:** Implement a robust system to differentiate and tag documents based on their origin.

#### **1.1 Database Schema Updates**
- **Action:** Modify the existing Document model to include a source column.
- **Specification:**
  - **Column Name:** `source`
  - **Data Type:** String
  - **Default Value:** `"user"`
  - **Allowed Values:** `"user"`, `"opp_counsel"`, `"court"`

**Example Code:**
```python
source = db.Column(db.String, default="user")  # values: "user", "opp_counsel", "court"
```

#### **1.2 User Interface Update**
- **Action:** Enhance the document upload interface to allow users to specify the document source.
- **Specification:**
  - **UI Component:** Dropdown or toggle selector during upload.
  - **Options:**
    - “Uploaded by Us”
    - “Received from Opposing Counsel”
    - “Court Issued”
  - **Color Coding:** Implement a color scheme in the document list to visually differentiate sources:
    - Red = Opposing Counsel
    - Blue = Court

---

### **2. Deduplication & Similarity Detection**

**Goal:** Develop mechanisms to identify and manage duplicate documents and similar content.

#### **2.1 Hash-Based Deduplication**
- **Action:** Implement a hashing mechanism on document ingestion.
- **Specification:**
  - **Process:** Compute SHA-256 hash of the document content.
  - **Database Query:** Check for existing hashes in the database.
  
**Example Code:**
```python
import hashlib

sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
# Database Query
SELECT id FROM document WHERE sha256 = :sha256 AND source = 'user'
```
- **Flagging:** If a match is found, flag the document as a duplicate.

#### **2.2 Embedding-Based Fuzzy Matching**
- **Action:** Generate embeddings for documents to facilitate similarity detection.
- **Specification:**
  - **Process:** On document ingestion, generate a vector representation.
  - **Similarity Query:** Use ChromaDB to find similar documents based on cosine similarity (threshold > 0.90).
  
**Example Code:**
```python
from chromadb import Client

client = Client()
embedding = model.encode(document_content)
similar_docs = client.query(embedding, threshold=0.90)
```

---

### **3. Contradiction & Narrative Divergence Detection**

**Goal:** Analyze opposing claims to identify contradictions with user evidence.

#### **3.1 NLP Pipeline Implementation**
- **Action:** Create a pipeline for contradiction detection using NLP techniques.
- **Specification:**
  - **Inputs:**
    - Opposing document (e.g., claim: “Client never contacted X”)
    - User documents with high similarity scores.
  - **Process:**
    - Chunk the opposing document.
    - For each chunk, query the vector database for top-k similar user documents.
    - Use a pre-trained contradiction detection model.

**Example Code:**
```python
from transformers import pipeline

contradiction_detector = pipeline("text-classification", model="ynie/roberta-large-snli")
for chunk in opposing_document_chunks:
    if contradiction_detector(chunk)['label'] == "contradiction":
        # Flag discrepancy
```
- **Data Storage:** Store results in the `NarrativeDiscrepancy` table.

**SQL Schema:**
```sql
CREATE TABLE NarrativeDiscrepancy (
    id SERIAL PRIMARY KEY,
    opposing_doc_id INT,
    user_doc_id INT,
    conflicting_claim TEXT,
    evidence_excerpt TEXT,
    confidence FLOAT
);
```

---

### **4. Dashboard: Opposition Evidence Tracker**

**Goal:** Create an interactive dashboard for tracking and analyzing opposing documents.

#### **4.1 Dashboard Views**
- **Action:** Develop a dashboard with multiple views for document tracking.
- **Specification:**
  - **Received Documents Section:**
    - Filter documents by source = `opp_counsel`.
    - Display status indicators: Duplicate ✅ | Conflict ⚠️ | Untagged ⚪.
  - **Narrative Conflicts Table:**
    - Show opposing claims alongside identified contradictions.
    - Provide links to source documents.
    - Include manual flagging options for “Request Admission” or “Impeachment Candidate.”

#### **4.2 Missing Items Notification**
- **Action:** Prompt users when expected discovery categories are missing.
- **Specification:** Alert users for missing items (e.g., “All contracts from 2022”).

#### **4.3 Export Options**
- **Action:** Enable users to export summaries.
- **Specification:**
  - Format: PDF/CSV.
  - Contents: List of opposing documents, detected duplicates, highlighted contradictions.

---

### **5. Optional Enhancements**

**Goal:** Improve user experience and analytical capabilities.

#### **5.1 Timeline Overlay**
- **Action:** Visual representation of document upload timelines.

#### **5.2 Side-by-Side Document Comparison**
- **Action:** Allow users to compare similar opposing and user documents side-by-side.

#### **5.3 Legal Implication Analysis**
- **Action:** Analyze contradictions involving material facts for legal implications.

---

### **Instructions for AI Model:**
- Provide detailed code snippets and explanations for each step.
- Ensure that the specifications are clear and actionable.
- Use clear formatting for code and SQL schemas to enhance readability.
- Include comments in the code to explain the logic and functionality.
- Suggest best practices for implementation, including error handling and performance optimization.

---

This improved prompt is structured to guide the AI model in generating a comprehensive technical plan with detailed specifications, making it easier for developers to implement the Opposition Document Tracker effectively.
