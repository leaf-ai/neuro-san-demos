from __future__ import annotations

"""Automated motion drafting using Gemini models."""

from datetime import datetime
from pathlib import Path

import google.generativeai as genai
from docx import Document as DocxDocument
from weasyprint import HTML

from neuro_san.interfaces.coded_tool import CodedTool

from .template_library import TemplateLibrary


class AutoDrafter(CodedTool):
    """Generate legal motion drafts and export them."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.templates = TemplateLibrary()

    def generate(self, motion_type: str) -> str:
        """Generate a draft for the given motion type using Gemini."""
        prompt = self.templates.build_prompt(motion_type)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt, generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        return response.text

    def export(self, content: str, file_path: str) -> str:
        """Export reviewed content to DOCX or PDF."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".pdf":
            html = f"<pre>{content}</pre>"
            HTML(string=html).write_pdf(str(path))
        else:
            doc = DocxDocument()
            for line in content.splitlines():
                doc.add_paragraph(line)
            doc.save(str(path))
        return str(path)
