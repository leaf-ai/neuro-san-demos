from pathlib import Path
from typing import Any, Dict, Union
import logging

from neuro_san.interfaces.coded_tool import CodedTool


class UserVerificationTool(CodedTool):
    """Verify a user's identity from the users table."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[bool, str]:
        # user_id = str(args.get("user_id", "")).strip()
        # dataiku_id = str(args.get("dataiku_id", "")).strip()
        user_id = sly_data.get("user_id", "").strip()
        dataiku_id = sly_data.get("dataiku_id", "").strip()

        logging.info(f"[UserVerificationTool] Input user_id={user_id}, dataiku_id={dataiku_id}")

        file_path = Path(__file__).parent / "knowdocs" / "users.md"

        try:
            lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
            rows = [ln for ln in lines if "|" in ln][2:]  # Skip header + separator

            for idx, row in enumerate(rows):
                parts = [p.strip() for p in row.strip("|").split("|")]

                logging.info(f"[UserVerificationTool] Row {idx}: {parts}")

                if len(parts) < 5:
                    logging.warning(f"[UserVerificationTool] Skipping row {idx} due to insufficient columns.")
                    continue

                log_message = (
                    f"Comparing: user_id: {parts[0]} == {user_id}, "
                    f"dataiku_id: {parts[2]} == {dataiku_id}, "
                    f"status: {parts[4]} == A"
                )
                logging.info(f"[UserVerificationTool] {log_message}")

                if (
                    parts[0] == user_id and
                    parts[2] == dataiku_id and
                    parts[4].upper() == "A"
                ):
                    logging.info(f"[UserVerificationTool] ✅ Match found.")
                    return True

            logging.warning(f"[UserVerificationTool] ❌ No match found in users.md")
            return False

        except Exception as exc:
            logging.error(f"[UserVerificationTool] ❌ Error reading file or verifying user: {exc}")
            return f"Error: {exc}"
