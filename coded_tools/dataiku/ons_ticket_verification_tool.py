from typing import Any, Dict, Union
import logging
from neuro_san.interfaces.coded_tool import CodedTool


class ONSTicketVerificationTool(CodedTool):
    """Simple validator for ServiceNow ticket numbers."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[str, bool]:
        ticket_number = str(args.get("ticket_number", "")).strip()
        logging.info(
            "[ONSTicketVerificationTool] Input ticket_number=%s", ticket_number
        )
        result = bool(ticket_number) and ticket_number.startswith("SNOW-")
        logging.info("[ONSTicketVerificationTool] Result: %s", result)
        return result