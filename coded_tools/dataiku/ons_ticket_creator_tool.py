import uuid
from typing import Any, Dict, Union
import logging
from neuro_san.interfaces.coded_tool import CodedTool


class ONSTicketCreatorTool(CodedTool):
    """Generate a mock ServiceNow ticket number."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        ticket = f"SNOW-{uuid.uuid4().hex[:8]}"
        logging.info("[ONSTicketCreatorTool] Generated ticket %s", ticket)
        return ticket