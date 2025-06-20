from pathlib import Path
from typing import Any, Dict

from neuro_san.interfaces.coded_tool import CodedTool


class TrainingCompletionsTool(CodedTool):
    """Check if a user completed a training."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> bool:
        user_id = str(args.get("user_id", ""))
        training_name = args.get("training_name", "")
        certificate_id = args.get("certificate_id", "")

        file_path = Path(__file__).parent / "knowdocs" / "training_completions.md"
        try:
            lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
            rows = [ln for ln in lines if "|" in ln][2:]
            for row in rows:
                parts = [p.strip() for p in row.strip("|").split("|")]
                if len(parts) < 5:
                    continue
                if parts[0] == user_id and parts[2] == training_name and parts[3] == certificate_id:
                    return True
            return False
        except Exception:  # pragma: no cover - simple demo
            return False