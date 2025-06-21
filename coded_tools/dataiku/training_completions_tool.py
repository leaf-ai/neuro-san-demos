from pathlib import Path
from typing import Any, Dict, Union
import logging
from neuro_san.interfaces.coded_tool import CodedTool


class TrainingCompletionsTool(CodedTool):
    """Check if a user completed a training."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[bool, str]:
        user_id = str(args.get("user_id", "")).strip()
        training_name = str(args.get("training_name", "")).strip()
        certificate_id = str(args.get("certificate_id", "")).strip()

        logging.info(
            "[TrainingCompletionsTool] Input user_id=%s, training_name=%s, certificate_id=%s",
            user_id,
            training_name,
            certificate_id,
        )

        file_path = Path(__file__).parent / "knowdocs" / "training_completions.md"
        try:
            lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
            rows = [ln for ln in lines if "|" in ln][2:]
            for idx, row in enumerate(rows):
                parts = [p.strip() for p in row.strip("|").split("|")]
                logging.info("[TrainingCompletionsTool] Row %s: %s", idx, parts)
                if len(parts) < 5:
                    continue
                if (
                    parts[0] == user_id
                    and parts[2] == training_name
                    and parts[3] == certificate_id
                ):
                    logging.info("[TrainingCompletionsTool] ✅ Match found.")
                    return True
            logging.info("[TrainingCompletionsTool] ❌ No match found.")
            return False
        except Exception as exc:  # pragma: no cover - simple demo
            logging.error("[TrainingCompletionsTool] ❌ Error verifying completion: %s", exc)
            return False