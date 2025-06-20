import uuid
from typing import Any, Dict

from neuro_san.interfaces.coded_tool import CodedTool


class ONSTicketCreatorTool(CodedTool):
    """Generate a mock ServiceNow ticket number."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        return f"SNOW-{uuid.uuid4().hex[:8]}"