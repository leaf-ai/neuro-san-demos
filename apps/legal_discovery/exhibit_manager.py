"""Exhibit management utilities for the legal discovery module."""

import json
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

from .database import db
from .models import Document, ExhibitCounter, ExhibitAuditLog


class ExhibitExportError(Exception):
    """Raised when exhibits fail validation prior to export."""


def _get_or_create_counter(case_id: int) -> ExhibitCounter:
    """Return the exhibit counter for a case, creating it if needed."""
    counter = ExhibitCounter.query.filter_by(case_id=case_id).first()
    if counter is None:
        counter = ExhibitCounter(case_id=case_id, next_num=1)
        db.session.add(counter)
        db.session.commit()
    return counter


def get_next_exhibit_counter(case_id: int) -> int:
    """Increment and return the next exhibit number for a case."""
    counter = _get_or_create_counter(case_id)
    value = counter.next_num
    counter.next_num += 1
    db.session.commit()
    return value


def log_action(
    case_id: int,
    document_id: int | None,
    action: str,
    user: str | None = None,
    details: dict | None = None,
) -> None:
    """Persist an audit log entry for exhibit operations."""
    log = ExhibitAuditLog(
        case_id=case_id,
        document_id=document_id,
        user=user,
        action=action,
        details=details or {},
    )
    db.session.add(log)
    db.session.commit()


def assign_exhibit_number(
    document_id: int, title: str | None = None, user: str | None = None
) -> str:
    """Mark a document as an exhibit and assign the next sequential number.

    Repeated calls on an already-assigned document simply return the existing
    exhibit number, keeping the operation idempotent.
    """
    doc = Document.query.get(document_id)
    if doc is None:
        raise ValueError("Document not found")
    if doc.is_exhibit and doc.exhibit_number:
        return doc.exhibit_number
    next_num = get_next_exhibit_counter(doc.case_id)
    doc.exhibit_number = f"EX_{next_num:04}"
    doc.exhibit_title = title or doc.name
    doc.is_exhibit = True
    doc.exhibit_order = next_num
    db.session.commit()
    log_action(doc.case_id, doc.id, "ASSIGN", user, {"exhibit_number": doc.exhibit_number})
    return doc.exhibit_number


def create_cover_sheet(exhibit: Document) -> BytesIO:
    """Render a simple PDF cover sheet for an exhibit."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, f"Exhibit {exhibit.exhibit_number}")
    c.setFont("Helvetica", 14)
    if exhibit.exhibit_title:
        c.drawString(100, 720, exhibit.exhibit_title)
    y = 700
    c.setFont("Helvetica", 12)
    if exhibit.probative_value is not None:
        c.drawString(100, y, f"Probative: {exhibit.probative_value:.2f}")
        y -= 18
    if exhibit.admissibility_risk is not None:
        c.drawString(100, y, f"Admissibility Risk: {exhibit.admissibility_risk:.2f}")
        y -= 18
    if exhibit.narrative_alignment is not None:
        c.drawString(100, y, f"Narrative Align: {exhibit.narrative_alignment:.2f}")
        y -= 18
    if exhibit.score_confidence is not None:
        c.drawString(100, y, f"Confidence: {exhibit.score_confidence:.2f}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def _text_page(title: str, text: str) -> BytesIO:
    """Create a simple PDF page with a title and body text."""
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(80, 760, title)
    c.setFont("Helvetica", 12)
    text_obj = c.beginText(80, 740)
    for line in text.splitlines():
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def merge_pdf(cover: BytesIO, exhibit_path: str, writer: PdfWriter) -> None:
    """Append a cover sheet and exhibit file to the provided PDF writer."""
    if not Path(exhibit_path).exists():
        raise FileNotFoundError(exhibit_path)
    writer.append(PdfReader(cover))
    writer.append(PdfReader(exhibit_path))


def validate_exhibits(case_id: int) -> None:
    """Ensure all exhibits for a case satisfy export requirements."""
    exhibits = Document.query.filter_by(case_id=case_id, is_exhibit=True).all()
    for ex in exhibits:
        if not ex.bates_number:
            raise ExhibitExportError(f"Missing Bates number for {ex.exhibit_number}")
        if ex.is_privileged:
            raise ExhibitExportError(f"Exhibit {ex.exhibit_number} is marked privileged")


def generate_binder(case_id: int, output_path: str | None = None) -> str:
    """Combine exhibits with cover sheets into a single PDF binder."""
    validate_exhibits(case_id)
    exhibits = (
        Document.query.filter_by(case_id=case_id, is_exhibit=True, is_privileged=False)
        .order_by(Document.exhibit_order, Document.exhibit_number)
        .all()
    )
    writer = PdfWriter()
    for exhibit in exhibits:
        cover = create_cover_sheet(exhibit)
        merge_pdf(cover, exhibit.file_path, writer)
        meta = {m.schema: m.data for m in exhibit.metadata_entries}
        if (dep := meta.get("deposition_excerpt")) and dep.get("text"):
            writer.append(PdfReader(_text_page("Deposition Excerpt", dep["text"])))
        if (theory := meta.get("theory_reference")) and theory.get("text"):
            writer.append(PdfReader(_text_page("Theory Reference", theory["text"])))
    if output_path is None:
        output_path = Path(tempfile.gettempdir()) / f"case_{case_id}_binder.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)
    log_action(case_id, None, "EXPORT_BINDER", details={"path": str(output_path)})
    return str(output_path)


def export_zip(case_id: int, output_path: str | None = None) -> str:
    """Package exhibits and a manifest into a zip archive."""
    validate_exhibits(case_id)
    exhibits = (
        Document.query.filter_by(case_id=case_id, is_exhibit=True, is_privileged=False)
        .order_by(Document.exhibit_order, Document.exhibit_number)
        .all()
    )
    if output_path is None:
        output_path = Path(tempfile.gettempdir()) / f"case_{case_id}_exhibits.zip"
    manifest = []
    with zipfile.ZipFile(output_path, "w") as z:
        for ex in exhibits:
            name = f"{ex.exhibit_number}_{(ex.exhibit_title or '').replace(' ', '_')}.pdf"
            z.write(ex.file_path, name)
            meta = {m.schema: m.data for m in ex.metadata_entries}
            entry = {
                "exhibit_number": ex.exhibit_number,
                "title": ex.exhibit_title,
                "path": name,
                "bates_number": ex.bates_number,
            }
            if (dep := meta.get("deposition_excerpt")) and dep.get("text"):
                dep_name = f"{ex.exhibit_number}_deposition.txt"
                z.writestr(dep_name, dep["text"])
                entry["deposition_excerpt"] = dep_name
            if (theory := meta.get("theory_reference")) and theory.get("text"):
                theory_name = f"{ex.exhibit_number}_theory.txt"
                z.writestr(theory_name, theory["text"])
                entry["theory_reference"] = theory_name
            if score := meta.get("evidence_scorecard"):
                entry["evidence_scorecard"] = score
            if sanctions := meta.get("sanctions_risk"):
                entry["sanctions_risk"] = sanctions
            manifest.append(entry)
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
    log_action(case_id, None, "EXPORT_ZIP", details={"path": str(output_path)})
    return str(output_path)

