import fitz
from coded_tools.legal_discovery.privilege_detector import PrivilegeDetector


def test_detect_and_redact_text():
    detector = PrivilegeDetector()
    text = "This is confidential legal advice from your attorney."
    privileged, spans = detector.detect(text)
    assert privileged and spans
    redacted = detector.redact_text(text, spans)
    assert "[REDACTED]" in redacted
    assert "confidential" not in redacted.lower()


def test_redact_pdf(tmp_path):
    input_pdf = tmp_path / "in.pdf"
    output_pdf = tmp_path / "out.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "privileged memo")
    doc.save(str(input_pdf))
    PrivilegeDetector.redact_pdf(str(input_pdf), str(output_pdf), ["privileged"])
    out_doc = fitz.open(str(output_pdf))
    text = out_doc.load_page(0).get_text().lower()
    assert "privileged" not in text
