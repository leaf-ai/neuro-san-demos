import os
from neuro_san.interfaces.coded_tool import CodedTool

class CodeEditor(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def read_file(self, filepath: str) -> str:
        """
        Reads the content of a file.

        :param filepath: The path to the file to read.
        :return: The content of the file, or an error message.
        """
        try:
            with open(filepath, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file '{filepath}': {e}"

    def write_file(self, filepath: str, content: str) -> str:
        """
        Writes content to a file.

        :param filepath: The path to the file to write to.
        :param content: The content to write to the file.
        :return: A message indicating success or failure.
        """
        try:
            with open(filepath, "w") as f:
                f.write(content)
            return f"File '{filepath}' written successfully."
        except Exception as e:
            return f"Error writing to file '{filepath}': {e}"
