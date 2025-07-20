from docx import Document

from neuro_san.coded_tool import CodedTool


class SubpoenaManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subpoenas = {}

    def create_subpoena(self, subpoena_id: str, content: str):
        """
        Creates a new subpoena.

        :param subpoena_id: A unique ID for the subpoena.
        :param content: The content of the subpoena.
        """
        self.subpoenas[subpoena_id] = content

    def get_subpoena(self, subpoena_id: str) -> str:
        """
        Retrieves a subpoena.

        :param subpoena_id: The ID of the subpoena to retrieve.
        :return: The content of the subpoena.
        """
        return self.subpoenas.get(subpoena_id, "")

    def draft_subpoena_document(self, filepath: str, content: str):
        """
        Drafts a subpoena document.

        :param filepath: The path to the new document.
        :param content: The content to add to the document.
        """
        document = Document()
        document.add_paragraph(content)
        document.save(filepath)
