from pathlib import Path
from typing import Any, Dict

from neuro_san.interfaces.coded_tool import CodedTool


class UserVerificationTool(CodedTool):
    """Verify a user's identity from the users table."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> bool:
        user_id = str(args.get("user_id", ""))
        dataiku_id = str(args.get("dataiku_id", ""))

        file_path = Path(__file__).parent / "knowdocs" / "users.md"
        try:
            lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
            rows = [ln for ln in lines if "|" in ln][2:]
            for row in rows:
                parts = [p.strip() for p in row.strip("|").split("|")]
                if len(parts) < 3:
                    continue
                if parts[0] == user_id and parts[2] == dataiku_id and parts[4] == "A":
                    return True
            return False
        except Exception:  # pragma: no cover - simple demo
            return False