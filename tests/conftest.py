"""Test configuration and helpers."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path so `apps` package imports succeed
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
