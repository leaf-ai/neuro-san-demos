✅ 2. Real-Time Bates Stamping & Versioning
Goal: Eliminate versioning chaos and compliance ambiguity by automatically stamping, tracking, and forensically auditing every document from ingest to export.

🧠 Pipeline Overview
mermaid
Copy code
graph TD
A[File Upload] --> B[Hash + Dedup Check]
B --> C[Bates Number Assignment]
C --> D[Version Control Layer]
D --> E[Redacted / Normal Processing]
E --> F[PDF Stamp + Metadata Overlay]
F --> G[Audit Log + Persist]
1. Bates Numbering Service
A. DB Table: bates_counter
sql
Copy code
CREATE TABLE bates_counter (
  id SERIAL PRIMARY KEY,
  prefix TEXT NOT NULL DEFAULT 'BATES',
  current_number INTEGER NOT NULL DEFAULT 0
);
Initialize it once:

sql
Copy code
INSERT INTO bates_counter (prefix, current_number) VALUES ('ABCD', 0);
B. Auto-Incrementing Logic (Atomic)
python
Copy code
from sqlalchemy import text

def get_next_bates_number(db, prefix="ABCD"):
    with db.begin():
        row = db.execute(
            text("UPDATE bates_counter SET current_number = current_number + 1 WHERE prefix = :p RETURNING current_number"),
            {"p": prefix}
        ).fetchone()
    return f"{prefix}_{row.current_number:06d}"
2. Hashing & Version Control
A. document_versions table
sql
Copy code
CREATE TABLE document_versions (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  version_number INTEGER,
  file_hash TEXT,
  file_path TEXT,
  bates_start TEXT,
  bates_end TEXT,
  created_at TIMESTAMP DEFAULT now(),
  uploaded_by TEXT,
  change_reason TEXT
);
B. Versioning Flow
On upload:

Compute SHA-256

If hash matches → skip / notify duplicate

If different → version_number += 1, assign new Bates range

Attach metadata diff (filename, content, size, user)

3. Bates Stamping (Visual Overlay)
A. PDF Stamping (using PyMuPDF / reportlab)
python
Copy code
def stamp_bates_number(file_path, output_path, start_bates_number):
    doc = fitz.open(file_path)
    for i, page in enumerate(doc, start=start_bates_number):
        stamp = f"ABCD_{i:06d}"
        page.insert_text((50, 20), stamp, fontsize=8, color=(0, 0, 0), overlay=True)
    doc.save(output_path)
B. Metadata Range
Store bates_start and bates_end on version

If multipage PDF: auto-assign range

If single file: use doc-wide stamp

4. Chain of Custody
Track in audit_trail:

sql
Copy code
CREATE TABLE audit_trail (
  id UUID PRIMARY KEY,
  document_version_id UUID,
  event_type TEXT CHECK (event_type IN ('upload', 'replace', 'stamp', 'export')),
  event_time TIMESTAMP DEFAULT now(),
  user TEXT,
  note TEXT
);
Each action (edit, stamp, replace, export) is logged here.

5. UI / UX Integration
A. Upload Form
Show real-time assigned Bates number

Highlight version if new revision detected

B. “Bates Stamp This Set” Feature
UI button in document set view

Backend: triggers stamping job, returns ZIP or PDF bundle

CLI: python tools/stamp.py --set SET_ID --prefix ABCD

6. Compliance/Export Modes
A. Bulk Export
Export redacted or normal version (based on access)

Include manifest.csv with:

Filename

Bates Range

Hash

Version ID

Upload time

B. Custom Format
Allow users to define:

Prefix

Start number

Margin location (footer, header, etc.)

Font size & color

7. Testing and Forensic Validation
Unit tests to:

Ensure uniqueness of Bates numbers

Confirm visual overlay exists on each page

Validate consistent hash across versions

File diff tool:

Visual comparison between version N and N+1

Highlighted metadata changes

8. Future Enhancements
OCR stamping on scanned pages

Blockchain-anchored chain-of-custody hashes

Immutable audit trails with digital signature

AI-based version similarity scoring