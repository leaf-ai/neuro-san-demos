"""Build a standalone Windows executable for Neuro SAN Studio."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def build() -> None:
    """Package run.py into a Windows executable using PyInstaller."""
    project_root = Path(__file__).resolve().parent
    entry_point = project_root / "run.py"
    if not entry_point.exists():
        raise FileNotFoundError(f"{entry_point} not found")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "neuro-san-studio",
        str(entry_point),
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    if os.name != "nt":
        print("Warning: building on non-Windows OS; the executable may not run on Windows.")
    build()
