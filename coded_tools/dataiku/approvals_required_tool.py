from pathlib import Path
from typing import Any, Dict, Union
import logging
from neuro_san.interfaces.coded_tool import CodedTool


class ApprovalsRequiredTool(CodedTool):
    """Check if access is permitted based on policies."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[bool, str]:
        env = str(args.get("env", "")).upper()
        access_type = str(args.get("access_type", "")).capitalize()
        logging.info(
            "[ApprovalsRequiredTool] Input env=%s, access_type=%s", env, access_type
        )
        file_path = Path(__file__).parent / "knowdocs" / "access_policies.md"
        try:
            lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
            rows = [ln for ln in lines if "|" in ln][2:]
            for idx, row in enumerate(rows):
                parts = [p.strip() for p in row.strip("|").split("|")]
                logging.info("[ApprovalsRequiredTool] Row %s: %s", idx, parts)
                if len(parts) < 3:
                    continue
                if parts[0].upper() == env and parts[1].capitalize() == access_type:
                    result = parts[2].lower() == "yes"
                    logging.info("[ApprovalsRequiredTool] Result: %s", result)
                    return result
            logging.info("[ApprovalsRequiredTool] ❌ No matching policy found.")
            return False
        except Exception as exc:  # pragma: no cover - simple demo
            logging.error("[ApprovalsRequiredTool] ❌ Error reading policies: %s", exc)
            return False