import json
from pathlib import Path
from typing import Any, Dict

from neuro_san.interfaces.coded_tool import CodedTool


class TrainingRequirementsTool(CodedTool):
    """Return training requirements for a specific environment."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        env = str(args.get("env", "")).upper()
        file_path = Path(__file__).parent / "knowdocs" / "training_requirements.md"
        try:
            text = file_path.read_text(encoding="utf-8")
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            data = json.loads(text[json_start:json_end])
            return data.get(env, {})
        except Exception:  # pragma: no cover - simple demo
            return {}