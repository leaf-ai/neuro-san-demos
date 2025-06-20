from typing import Any, Dict

from neuro_san.interfaces.coded_tool import CodedTool


class ONSTicketVerificationTool(CodedTool):
    """Simple validator for ServiceNow ticket numbers."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> bool:
        ticket_number = args.get("ticket_number", "")
        return bool(ticket_number) and str(ticket_number).startswith("SNOW-")