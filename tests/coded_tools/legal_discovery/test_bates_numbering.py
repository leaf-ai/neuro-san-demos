import fitz

from coded_tools.legal_discovery.bates_numbering import (
    BatesNumberingService,
    stamp_pdf,
)


def create_sample_pdf(path: str) -> None:
    doc = fitz.open()
    doc.new_page()
    doc.save(path)


def test_get_next_bates_number_increments():
    service = BatesNumberingService()
    first = service.get_next_bates_number("TEST")
    second = service.get_next_bates_number("TEST")
    assert first == "TEST_000001"
    assert second == "TEST_000002"
    assert first != second


def test_stamp_pdf(tmp_path):
    input_pdf = tmp_path / "input.pdf"
    output_pdf = tmp_path / "output.pdf"
    create_sample_pdf(str(input_pdf))
    start, end = stamp_pdf(str(input_pdf), str(output_pdf), 1, prefix="TEST")
    assert start == "TEST_000001"
    assert end == "TEST_000001"
    doc = fitz.open(str(output_pdf))
    text = doc[0].get_text()
    assert "TEST_000001" in text
