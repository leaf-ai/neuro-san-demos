🗂️ 5. Exhibit & Trial Binder Creator
⚖️ Goal:
Streamline the creation of trial-ready exhibit binders with cover sheets, numbering, and seamless export — while maintaining legal integrity (Bates, privilege, chain-of-custody).

🛠️ SYSTEM DESIGN OVERVIEW
Core Components:

Document model extension (add is_exhibit, exhibit_number, exhibit_title)

Exhibit manager service (exhibit_binder.py)

UI integration with tagging, reorder, and export actions

Binder generation logic (PDF/ZIP + optional integration exports)

Privilege/Bates enforcement cross-checker

🧱 DATABASE & BACKEND SETUP
1. Schema Updates
Extend the Document SQL model and Neo4j node:

python
Copy code
is_exhibit = db.Column(db.Boolean, default=False)
exhibit_number = db.Column(db.String)
exhibit_title = db.Column(db.String)
2. Exhibit Index Service
New table: exhibit_counter

Tracks the next number available per case or binder set.

Auto-increments on each new tag or export.

Service function:

```
python
Copy code
{
	def assign_exhibit_number(document_id, title=None):
		next_num = get_next_exhibit_counter()
		doc = Document.query.get(document_id)
		doc.exhibit_number = f"EX_{next_num:04}"
		doc.exhibit_title = title or doc.name
		doc.is_exhibit = True
		db.session.commit()
}
```
		
		
🖥️ UI INTEGRATION
3. Tagging in Document View
Add checkbox: “Mark as Exhibit”

On select:

Call backend to assign number + title

Toggle metadata state visually

4. Exhibit Organizer View
New tab: Exhibits

List all marked docs in sortable table

Columns: Exhibit Number, Title, Bates Start, Page Count, Privilege Flag

Allow user to:

Reorder

Retitle

Remove exhibit status

Preview PDF

📄 PDF BINDER GENERATION
5. Cover Sheet Renderer
Generate per-exhibit cover sheet:

Exhibit No.

Title

Document Metadata (Bates, Pages, Source)

Auto-generated via reportlab or PyMuPDF (fast)

6. PDF Merger
For each exhibit:

Generate cover sheet

Merge with the exhibit file (ensure redactions, Bates are in place)

Append to final output binder

Save PDF binder to /exports/binders/{case_id}/{timestamp}_exhibit_binder.pdf

📤 EXPORT OPTIONS
7. User Actions
Button: “Export Binder”

Options:

📎 Full PDF binder (merged with cover sheets)

📁 ZIP of all exhibits with JSON metadata

🔄 TrialPad/OnCue export (optional)

8. TrialPad/OnCue Export Format
TrialPad uses folder structure + naming conventions:

pgsql
Copy code
TrialPad_Exhibits/
  EX_0001_Title.pdf
  EX_0002_Title.pdf
manifest.json
OnCue uses CSV manifest with titles + file paths.

🔒 VALIDATION & SAFETY CHECKS
9. Cross-Checks
Enforce:

Bates numbers must exist before export

Block inclusion of any Document.privileged == True unless user overrides

Include hash + audit log entry for each exhibit

📚 AUDIT TRAIL
10. Logging
Track:

Who marked document as exhibit

Timestamps

Edits to titles or order

Export time and format

Store in exhibit_audit_log table

✅ OUTCOME
You’ve now:

Made exhibit preparation painless

Created legally clean, organized output for opposing counsel or court

Built reusable infrastructure for pretrial and trial presentation workflows