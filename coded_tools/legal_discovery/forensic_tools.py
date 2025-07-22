import hashlib
import json
import os

import numpy as np
import pandas as pd
import requests
from neuro_san.interfaces.coded_tool import CodedTool
from PIL import Image
from PyPDF2 import PdfReader



class ForensicTools(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("ForensicTools instantiated")

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

        # Calculate descriptive statistics for numerical columns
        numerical_summary = df.describe().to_string()

        # Calculate the median for each numerical column
        median_values = df.median(numeric_only=True).to_string()

        # Calculate the standard deviation for each numerical column
        std_dev_values = df.std(numeric_only=True).to_string()

        # Benford's Law Analysis
        # Extract the first digit of each number in the first numerical column
        first_column = df.select_dtypes(include=np.number).columns[0]
        first_digits = df[first_column].astype(str).str[0].astype(int)
        benford_dist = first_digits.value_counts(normalize=True).sort_index()

        benford_summary = benford_dist.to_string()


        return (
            f"Financial Analysis Summary for {filepath}:\n\n"
            f"**Descriptive Statistics**\n{numerical_summary}\n\n"
            f"**Median Values**\n{median_values}\n\n"
            f"**Standard Deviation**\n{std_dev_values}\n\n"
            f"**Benford's Law Distribution**\n{benford_summary}\n"
        )

    def analyze_document_authenticity(self, file_path: str) -> str:
        """
        Analyzes a document for signs of tampering.

        :param file_path: The path to the document.
        :return: A summary of the authenticity analysis.
        """
        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            metadata = reader.metadata

            report = f"Authenticity analysis for {file_path}:\n"
            report += f"  - SHA256 Hash: {self.get_file_hash(file_path)}\n"
            report += f"  - Metadata: {metadata}\n"

            # Check for multiple versions
            if reader.trailer.get("/Prev"):
                report += "  - Warning: Multiple versions of this PDF were found. This may indicate modification.\n"

            # Check for inconsistencies in metadata
            if metadata.get("/Author") and metadata.get("/Creator"):
                if metadata.get("/Author") != metadata.get("/Creator"):
                    report += (
                        f"  - Warning: Author and Creator metadata do not match.\n"
                        f"  - Author: {metadata.get('/Author')}\n"
                        f"  - Creator: {metadata.get('/Creator')}\n"
                    )

            # Check for hidden content (e.g., text with the same color as the background)
            hidden_text = []
            for page in reader.pages:
                for content in page.get_contents():
                    if content.get("/Filter") == "/FlateDecode":
                        data = content.decompress()
                        if b"BT" in data and b"ET" in data:
                            # This is a very basic check and may not be accurate
                            if b" 0 0 0 rg" in data or b" 1 1 1 rg" in data:
                                hidden_text.append(data)

            if hidden_text:
                report += f"  - Warning: Potential hidden text found on {len(hidden_text)} pages.\n"

            # If any warnings were found, call the VerifyPDF API
            if "Warning" in report:
                report += "\n\n**VerifyPDF API Analysis**\n"
                verifypdf_result = self.call_verifypdf_api(file_path)
                report += json.dumps(verifypdf_result, indent=2)

            return report

        elif file_path.endswith((".jpg", ".jpeg", ".png", ".gif")):
            metadata = self.get_image_metadata(file_path)
            return (
                f"Authenticity analysis for {file_path}:\n"
                f"  - Metadata: {metadata}\n"
                f"  - SHA256 Hash: {self.get_file_hash(file_path)}\n"
                f"  - Note: This is a basic analysis. No signs of tampering detected."
            )
        else:
            return f"Unsupported file type for authenticity analysis: {file_path}"

    def call_verifypdf_api(self, file_path: str) -> dict:
        """Call the VerifyPDF API for additional PDF analysis."""
        url = "https://api.verifypdf.com/v1/verify"
        api_key = os.environ.get("VERIFYPDF_API_KEY")
        if not api_key:
            raise RuntimeError("VERIFYPDF_API_KEY environment variable is not set")

        headers = {"Authorization": f"Bearer {api_key}"}
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=headers, files=files, timeout=30)

        response.raise_for_status()
        return response.json()

    def financial_forensics(self, file_path: str) -> str:
        """
        Performs financial forensic analysis on a document.

        :param file_path: The path to the financial document.
        :return: A summary of the financial forensic analysis.
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-pro")

        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            document_content = ""
            for page in reader.pages:
                document_content += page.extract_text()
        else:
            with open(file_path, "r") as f:
                document_content = f.read()

        prompt = f"""
        Analyze the following financial document for signs of fraud or irregularities.
        Focus on identifying unusual transactions, inconsistencies in financial statements,
        and any other red flags. Provide a summary of your findings.

        Document Content:
        {document_content}
        """

        result = llm.invoke(prompt, timeout=60)
        return result.content
