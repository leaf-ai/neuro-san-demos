from __future__ import annotations

import subprocess
from typing import Any

from neuro_san.interfaces.coded_tool import CodedTool


class CommandPrompt(CodedTool):
    """Execute shell commands within a controlled sandbox."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def run(self, command: str, timeout: int = 30) -> str:
        """Run a shell command and return combined stdout/stderr."""
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return (proc.stdout + proc.stderr).strip()
        except Exception as exc:  # pragma: no cover - environment may vary
            return f"Error running command: {exc}"


__all__ = ["CommandPrompt"]
