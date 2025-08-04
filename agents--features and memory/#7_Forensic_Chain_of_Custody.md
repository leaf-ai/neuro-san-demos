**Improved Prompt:**

---

**Forensic Chain of Custody Dashboard — Comprehensive Technical Implementation Plan**

**Objective:** Generate a detailed, step-by-step technical implementation plan for a Forensic Chain of Custody Dashboard. The plan must ensure that all events in a document’s lifecycle are logged in a forensically sound and tamper-evident manner. It should provide technical specifications, clear steps, and sub-steps for each component of the system.

### Instructions for AI Model (Codex/ChatGPT):
- Focus on generating a highly detailed implementation plan that adheres to best practices in software development and forensic integrity.
- Ensure clarity and specificity in each section, including code snippets, data structures, and API specifications.
- Use structured formatting (e.g., bullet points, tables) to enhance readability.
- Consider potential security and compliance requirements throughout the implementation.

### Implementation Plan Structure:

---

### 1. Data Capture & Logging Layer

**Goal:** Ensure all events in a document's lifecycle are logged in a forensically sound, tamper-evident manner.

**1.1 Schema Design**
- **Create a `chain_of_custody_log` table with the following structure:**
    ```sql
    CREATE TABLE chain_of_custody_log (
        id UUID PRIMARY KEY,
        document_id UUID REFERENCES documents(id),
        event_type ENUM('INGESTED', 'HASHED', 'REDACTED', 'STAMPED', 'VERSIONED', 'DELETED') NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        user_id UUID REFERENCES users(id),
        event_metadata JSONB
    );
    ```

- **1.2 Event Metadata Structure:**
    - Define the `event_metadata` JSONB structure for each event type:
        - **INGESTED:** { "filename": string, "uploader": string, "time": timestamp, "file_path": string }
        - **HASHED:** { "sha256": string, "file_size": integer, "time_taken": duration }
        - **REDACTED:** { "redaction_spans": array, "rules_triggered": array }
        - **STAMPED:** { "bates_range": string, "user": string, "template_used": string }
        - **VERSIONED:** { "old_hash": string, "new_hash": string, "diff_summary": string }
        - **DELETED:** { "error_traceback": string, "stage": string, "timestamp": timestamp }

**1.3 Append-Only Behavior**
- **Implement database triggers** to prevent UPDATEs/DELETEs on the `chain_of_custody_log` table.
- **Optionally, export logs** to WORM (Write Once, Read Many) storage or a Merkle-tree ledger to ensure evidentiary integrity.

### 2. Logging Implementation

**2.1 Logger Utility**
- **Create a Python logger utility** to encapsulate logging for each document processing stage:
    ```python
    from forensic_logger import log_event

    def process_document(doc_id, user_id):
        # Example of logging the HASHED event
        log_event(doc_id, "HASHED", user_id=user_id, metadata={"sha256": hash_val})
    ```

**2.2 Storage of Logs**
- **Store raw logs** in PostgreSQL.
- **Optionally serialize logs** to external files:
    - Save as `doc_path + ".chainlog.json"` for audit assurance.

### 3. Dashboard Backend API

**3.1 REST API Endpoint**
- **Create a RESTful API endpoint** to retrieve chain of custody events:
    ```http
    GET /api/chain-of-custody?document_id=123
    ```

**3.2 API Response Structure**
- **Define the JSON response structure:**
    ```json
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
        }
      ]
    }
    ```

**3.3 Filtering Options**
- **Support filters** by:
    - Case ID
    - Date Range
    - Hash delta
    - Event type

### 4. Dashboard Frontend UI

**4.1 UI Components**
- **Design the following components:**
    - **Timeline View:** Vertical progression of events
    - **Event Details Modal:** On-click to display detailed metadata
    - **Hash Diff View:** Compare two versions of a document
    - **Error Log View:** Display failed processing or timeouts

**4.2 Filters and Export Options**
- **Implement filters** for:
    - User
    - Date
    - Processing step (dropdown)
    - Document ID
- **Export Button:** Generate PDF or CSV chain-of-custody reports including:
    - Document name
    - Each step (timestamp, action, hash, user)
    - Flag any inconsistencies (e.g., mismatched hash on reprocess)

### 5. Chain-of-Custody Compliance

**5.1 Compliance Features**
- Ensure each event is:
    - Time-stamped
    - Linked to a user ID (from session or audit context)
    - Immutable once written
- **Export log with notarized hash:** Add `"chain_hash": sha256(log_dump)` to the end of the exported report.

### 6. Bonus Ideas

- **Visual Diff:** Implement a visual diff of redacted vs. original documents.
- **Case-wide Timeline:** Provide a timeline of all document events across a case.
- **Export Formats:** Support export to .LEDES or .OPT formats for trial management software.

---

**Desired Outcome:** A step-by-step, highly detailed, and comprehensive technical plan of execution, including specifications, clearly defined steps, and sub-steps for each component of the Forensic Chain of Custody Dashboard.

**Target AI Model:** Codex/ChatGPT

---

This improved prompt emphasizes clarity, structure, and the need for comprehensive technical details while ensuring that the AI model generates a response that meets the user's expectations effectively.
