✅ Forensic Chain of Custody Dashboard — Technical Implementation Plan
1. Data Capture & Logging Layer
Goal: Ensure all events in a document’s lifecycle are logged in a forensically sound, tamper-evident way.

🧱 Schema Additions
chain_of_custody_log table:

sql
Copy code
id (UUID)
document_id (FK)
event_type (ENUM): [INGESTED, HASHED, REDACTED, STAMPED, VERSIONED, DELETED]
timestamp (UTC)
user_id (FK or string)
event_metadata (JSONB): {
    "hash": "abc123",
    "duration": "2.5s",
    "source_path": "...",
    ...
}
Enable append-only behavior:

Use database triggers to forbid UPDATEs/DELETEs.

Optionally export to a WORM storage file (write once, read many) or Merkle-tree ledger for evidentiary integrity.

🎯 Events to Log
Log entries at these stages:

Event Type	Metadata Captured
INGESTED	Filename, uploader, time, file path
HASHED	SHA-256 hash, file size, time taken
REDACTED	Redaction spans, rules triggered
BATES_STAMPED	Bates range, user, template used
VERSIONED	Old hash, new hash, diff summary
FAILED	Error traceback, stage, timestamp

2. Logging Implementation
Wrap each ingestion and processing stage with a logger utility:

python
Copy code
from forensic_logger import log_event

log_event(doc_id, "HASHED", user_id=current_user.id, metadata={"sha256": hash_val})
Store raw logs in PostgreSQL and optionally serialize them to:

doc_path + ".chainlog.json"

External immutable storage for audit assurance

3. Dashboard Backend API
Build a REST endpoint:

http
Copy code
GET /api/chain-of-custody?document_id=123
Returns:

json
Copy code
{
  "document_id": 123,
  "events": [
    {
      "type": "INGESTED",
      "timestamp": "2025-08-03T20:10Z",
      "user": "manny",
      "metadata": {
        "path": "...",
        "size": 2134421
      }
    },
    ...
  ]
}
Support filters by:

Case ID

Date Range

Hash delta

Event type

4. Dashboard Frontend UI
📊 Components
Timeline View (vertical progression of events)

Event Details Modal (on-click → show metadata)

Hash Diff View (compare two versions of a doc)

Error Log View for failed processing or timeouts

🔍 Filters
User

Date

Processing step (dropdown)

Document ID

📤 Export Button
Generate PDF or CSV chain-of-custody report:

Document name

Each step (timestamp, action, hash, user)

Flag any inconsistencies (e.g., mismatched hash on reprocess)

5. Chain-of-Custody Compliance
Each event is:

Time-stamped

Linked to a user ID (from session or audit context)

Immutable once written

Export log with notarized hash:

Add "chain_hash": sha256(log_dump) to end of exported report

🚀 Bonus Ideas
Visual diff of redacted vs. original

Timeline of all document events case-wide

Export to .LEDES or .OPT for trial mgmt software

