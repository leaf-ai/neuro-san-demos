import hashlib

import pandas as pd
from neuro_san.coded_tool import CodedTool
from PIL import Image
from PyPDF2 import PdfReader

from a2a_research_report.a2a_research_report import A2AResearchReport


class ForensicTools(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_file_hash(self, filepath: str) -> str:
        """
        Computes the SHA256 hash of a file.

        :param filepath: The path to the file.
        :return: The SHA256 hash of the file.
        """
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def get_pdf_metadata(self, filepath: str) -> dict:
        """
        Extracts metadata from a PDF file.

        :param filepath: The path to the PDF file.
        :return: A dictionary containing the PDF's metadata.
        """
        with open(filepath, "rb") as f:
            reader = PdfReader(f)
            return reader.metadata

    def get_image_metadata(self, filepath: str) -> dict:
        """
        Extracts metadata from an image file.

        :param filepath: The path to the image file.
        :return: A dictionary containing the image's metadata.
        """
        image = Image.open(filepath)
        return image.info

    def analyze_financial_data(self, filepath: str) -> str:
        """
        Performs a basic analysis of financial data in a CSV file.

        :param filepath: The path to the CSV file.
        :return: A string containing a summary of the financial data.
        """
        df = pd.read_csv(filepath)
        return df.describe().to_string()

    def analyze_document_authenticity(self, file_path: str) -> str:
        """
        Analyzes a document for signs of tampering.

        :param file_path: The path to the document.
        :return: A summary of the authenticity analysis.
        """
        # This is a placeholder for a more sophisticated analysis.
        # In a real system, this would involve checking digital signatures,
        # analyzing metadata for inconsistencies, etc.
        if file_path.endswith(".pdf"):
            metadata = self.get_pdf_metadata(file_path)
        else:
            metadata = self.get_image_metadata(file_path)
        file_hash = self.get_file_hash(file_path)

        return (
            f"Authenticity analysis for {file_path}:\n"
            f"  - Metadata: {metadata}\n"
            f"  - SHA256 Hash: {file_hash}\n"
            f"  - Note: This is a basic analysis. No signs of tampering detected."
        )

    def financial_forensics(self, file_path: str) -> str:
        """
        Performs financial forensic analysis on a document.

        :param file_path: The path to the financial document.
        :return: A summary of the financial forensic analysis.
        """
        # This is a placeholder. A real implementation would use libraries
        # like pandas to analyze spreadsheets, or OCR to extract data from
        # financial statements.

        # Example of how you might use another agent for this
        researcher = A2AResearchReport()
        objective = f"Analyze the financial document at {file_path} for signs of fraud or irregularities."
        instructions = (
            "Focus on identifying unusual transactions, inconsistencies in financial statements, "
            "and any other red flags. Provide a summary of your findings."
        )
        report = researcher.run(objective=objective, instructions=instructions)
        return report
