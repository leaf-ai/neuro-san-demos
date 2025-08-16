import os
from pathlib import Path

from google import genai

from coded_tools.legal_discovery.auto_drafter import AutoDrafter
from coded_tools.legal_discovery.template_library import TemplateLibrary


class DummyClient:
    class Models:
        
        def generate_content(*args, **kwargs):
            class R:
                text = "Sample draft"
            return R()
    models = Models()

def test_template_library_available():
    lib = TemplateLibrary()
    available = lib.available()
    assert "motion_to_dismiss" in available
    assert "motion_in_limine" in available
    assert "motion_to_compel" in available
    assert "motion_for_protective_order" in available


def test_auto_drafter_generate(monkeypatch):
    monkeypatch.setattr(genai, "Client", lambda *a, **k: DummyClient())
    drafter = AutoDrafter()
    text = drafter.generate("motion_to_dismiss")
    assert isinstance(text, str) and text


def test_auto_drafter_export(tmp_path, monkeypatch):
    monkeypatch.setattr(genai, "Client", lambda *a, **k: DummyClient())
    drafter = AutoDrafter()
    path_docx = tmp_path / "draft.docx"
    drafter.export("hello", str(path_docx))
    assert path_docx.exists()
    path_pdf = tmp_path / "draft.pdf"
    drafter.export("hello", str(path_pdf))
    assert path_pdf.exists()
