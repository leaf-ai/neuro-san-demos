import os

from neuro_san.interfaces.coded_tool import CodedTool


class FileManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_file(self, filepath: str, content: str) -> str:
        """
        Creates a new file with the given content.

        :param filepath: The path to the file to create.
        :param content: The content to write to the file.
        :return: A message indicating success or failure.
        """
        try:
            with open(filepath, "w") as f:
                f.write(content)
            return f"File '{filepath}' created successfully."
        except Exception as e:
            return f"Error creating file '{filepath}': {e}"

    def overwrite_file(self, filepath: str, content: str) -> str:
        """
        Overwrites an existing file with the given content.

        :param filepath: The path to the file to overwrite.
        :param content: The new content for the file.
        :return: A message indicating success or failure.
        """
        try:
            with open(filepath, "w") as f:
                f.write(content)
            return f"File '{filepath}' overwritten successfully."
        except Exception as e:
            return f"Error overwriting file '{filepath}': {e}"

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

    def delete_file(self, filepath: str) -> str:
        """
        Deletes a file.

        :param filepath: The path to the file to delete.
        :return: A message indicating success or failure.
        """
        try:
            os.remove(filepath)
            return f"File '{filepath}' deleted successfully."
        except Exception as e:
            return f"Error deleting file '{filepath}': {e}"

    def list_files(self, directory: str) -> str:
        """
        Lists all files and directories in a given directory.

        :param directory: The directory to list.
        :return: A string containing the list of files and directories.
        """
        try:
            return "\n".join(os.listdir(directory))
        except Exception as e:
            return f"Error listing files in '{directory}': {e}"
