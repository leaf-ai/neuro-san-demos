import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from neuro_san.coded_tool import CodedTool


class DocumentProcessor(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extract_text_from_pdf(self, filepath: str) -> str:
        """
        Extracts text from a PDF file.

        :param filepath: The path to the PDF file.
        :return: The extracted text.
        """
        try:
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            return f"Error extracting text from PDF '{filepath}': {e}"

    def ocr_image(self, filepath: str) -> str:
        """
        Performs OCR on an image file.

        :param filepath: The path to the image file.
        :return: The extracted text.
        """
        try:
            return pytesseract.image_to_string(Image.open(filepath))
        except Exception as e:
            return f"Error performing OCR on image '{filepath}': {e}"

    def extract_text(self, filepath: str) -> str:
        """
        Extracts text from a file, performing OCR if necessary.

        :param filepath: The path to the file.
        :return: The extracted text.
        """
        if filepath.lower().endswith(".pdf"):
            return self.extract_text_from_pdf(filepath)
        elif filepath.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")):
            return self.ocr_image(filepath)
        else:
            try:
                with open(filepath, "r") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file '{filepath}': {e}"
