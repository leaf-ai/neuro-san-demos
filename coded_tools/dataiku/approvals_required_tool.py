from pathlib import Path
from typing import Any, Dict

from neuro_san.interfaces.coded_tool import CodedTool


class ApprovalsRequiredTool(CodedTool):
    """Check if access is permitted based on policies."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> bool:
        env = str(args.get("env", "")).upper()
        access_type = str(args.get("access_type", "")).capitalize()

        file_path = Path(__file__).parent / "knowdocs" / "access_policies.md"
        try:
            lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
            rows = [ln for ln in lines if "|" in ln][2:]
            for row in rows:
                parts = [p.strip() for p in row.strip("|").split("|")]
                if len(parts) < 3:
                    continue
                if parts[0].upper() == env and parts[1].capitalize() == access_type:
                    return parts[2].lower() == "yes"
            return False
        except Exception:  # pragma: no cover - simple demo
            return False