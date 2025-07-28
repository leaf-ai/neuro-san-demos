import fitz
from neuro_san.interfaces.coded_tool import CodedTool


class DocumentModifier(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def redact_text(self, filepath: str, text_to_redact: str):
        """
        Redacts text from a PDF file.

        :param filepath: The path to the PDF file.
        :param text_to_redact: The text to redact.
        """
        doc = fitz.open(filepath)
        for page in doc:
            areas = page.search_for(text_to_redact)
            for area in areas:
                page.add_redact_annot(area)
            page.apply_redactions()
        doc.save(f"{filepath}_redacted.pdf")

    def bates_stamp(self, filepath: str, prefix: str):
        """
        Adds a Bates stamp to a PDF file.

        :param filepath: The path to the PDF file.
        :param prefix: The prefix for the Bates stamp.
        """
        doc = fitz.open(filepath)
        for i, page in enumerate(doc):
            page.insert_text((10, 10), f"{prefix}-{i+1:06d}", fontsize=10)
        doc.save(f"{filepath}_stamped.pdf")
