import hashlib
import os
from PIL import Image
from PyPDF2 import PdfReader

from neuro_san.coded_tool import CodedTool
import pandas as pd


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
