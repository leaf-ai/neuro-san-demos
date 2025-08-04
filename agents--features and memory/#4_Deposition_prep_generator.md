**Improved Prompt:**

---

**🗂️ Comprehensive Exhibit & Trial Binder Creator Development Plan**

⚖️ **Objective:**
Create a meticulous, step-by-step implementation guide for developing a trial-ready exhibit binder system. This system should include functionality for cover sheets, Bates numbering, privilege management, and chain-of-custody documentation, ensuring legal integrity throughout the process. 

---

### **System Design Overview:**

**1. Core Components:**
   - **Document Model Extension:** Enhance the existing SQL Document model to support exhibit-specific attributes.
   - **Exhibit Manager Service:** Develop a dedicated service for managing exhibit-related operations.
   - **User Interface Integration:** Create an intuitive UI for tagging, organizing, and exporting exhibits.
   - **Binder Generation Logic:** Implement functionality for generating binders in PDF/ZIP formats.
   - **Compliance Checks:** Integrate a cross-checking system for legal compliance before export.

---

### **Detailed Implementation Steps:**

#### **Step 1: Document Model Extension**

1. **Database Schema Updates:**
   - Modify the existing Document SQL model to include the following fields:
     ```python
     class Document(db.Model):
         ...
         is_exhibit = db.Column(db.Boolean, default=False)
         exhibit_number = db.Column(db.String, unique=True)
         exhibit_title = db.Column(db.String)
     ```

2. **Neo4j Node Update:**
   - Update the corresponding Neo4j node structure to reflect these new fields.

---

#### **Step 2: Exhibit Manager Service Development**

1. **Service File Creation:**
   - Create a new service file named `exhibit_manager.py`.

2. **Function for Assigning Exhibit Numbers:**
   - Implement a function to assign exhibit numbers:
     ```python
     def assign_exhibit_number(document_id, title=None):
         next_num = get_next_exhibit_counter()
         doc = Document.query.get(document_id)
         doc.exhibit_number = f"EX_{next_num:04}"
         doc.exhibit_title = title or doc.name
         doc.is_exhibit = True
         db.session.commit()
     ```

3. **Exhibit Counter Table:**
   - Create a new SQL table `exhibit_counter` to manage the next available exhibit number per case.

---

#### **Step 3: User Interface Integration**

1. **Document View Modifications:**
   - Add a checkbox labeled “Mark as Exhibit” in the document view.
   - Implement an AJAX call to `assign_exhibit_number` when the checkbox is selected.

2. **Exhibit Organizer View:**
   - Develop a new tab titled "Exhibits" featuring:
     - A sortable table with columns for Exhibit Number, Title, Bates Start, Page Count, and Privilege Flag.
     - Functionality to reorder, retitle, and remove exhibit status.

---

#### **Step 4: PDF Binder Generation**

1. **Cover Sheet Renderer Implementation:**
   - Utilize libraries like ReportLab or PyMuPDF to create cover sheets for each exhibit:
     ```python
     def create_cover_sheet(exhibit):
         ...
     ```

2. **PDF Merging Logic:**
   - Implement a function to merge cover sheets with exhibit files:
     ```python
     def generate_binder(case_id):
         ...
         for exhibit in exhibits:
             cover_sheet = create_cover_sheet(exhibit)
             merge_pdf(cover_sheet, exhibit.file_path)
         save_final_binder(case_id)
     ```

---

#### **Step 5: Export Options Implementation**

1. **Export Binder Button:**
   - Create an "Export Binder" button in the UI with options for:
     - Full PDF binder.
     - ZIP of all exhibits with a JSON metadata file.

2. **Export Format Structures:**
   - Define the directory structure for TrialPad and OnCue exports:
     ```
     TrialPad_Exhibits/
       EX_0001_Title.pdf
       manifest.json
     ```

---

#### **Step 6: Validation & Safety Checks**

1. **Compliance Checks Before Export:**
   - Implement validation functions to ensure:
     - All exhibits have Bates numbers.
     - Privileged documents are flagged appropriately.

2. **Audit Logging:**
   - Create an `exhibit_audit_log` table to track:
     - User actions on exhibits.
     - Timestamps and modifications made.

---

### **Expected Outcome:**
By following this implementation plan, you will achieve:
- A streamlined and legally compliant exhibit preparation process.
- An organized output suitable for court presentation.
- A robust backend infrastructure supporting trial workflows.

---

**Please provide a complete step-by-step implementation plan, including code snippets and clear instructions for each component outlined above. Focus on technical accuracy and clarity to facilitate development.** 

**Desired Outcome:** A comprehensive, highly detailed, and technical plan for execution with clear steps and sub-steps.  
**Target Model:** Codex/ChatGPT.
