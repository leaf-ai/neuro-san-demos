from __future__ import annotations

from typing import Any, Dict, List

from neuro_san.interfaces.coded_tool import CodedTool

from .internet_search import InternetSearch
from .code_editor import CodeEditor
from .command_prompt import CommandPrompt


class SandboxedVM(CodedTool):
    """Sandboxed Linux environment providing browser, editor and terminal."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.internet = InternetSearch(**kwargs)
        self.editor = CodeEditor(**kwargs)
        self.terminal = CommandPrompt(**kwargs)

    # Internet capabilities -------------------------------------------------
    def search(self, query: str, **params: Any) -> List[Dict[str, Any]]:
        """Perform an internet search inside the sandbox."""
        return self.internet.search(query, **params)

    # File editing ----------------------------------------------------------
    def read_file(self, path: str) -> str:
        """Read file contents using the sandbox editor."""
        return self.editor.read_file(path)

    def write_file(self, path: str, content: str) -> str:
        """Write ``content`` to ``path`` using the sandbox editor."""
        return self.editor.write_file(path, content)

    # Command execution -----------------------------------------------------
    def run(self, command: str, timeout: int = 30) -> str:
        """Execute a shell command within the sandbox."""
        return self.terminal.run(command, timeout=timeout)


__all__ = ["SandboxedVM"]
