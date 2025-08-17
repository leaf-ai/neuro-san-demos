from __future__ import annotations

"""Keyword-driven registry for voice commands."""

from typing import Callable, Dict, Optional, Tuple

from coded_tools.legal_discovery.timeline_manager import TimelineManager


CommandResult = Tuple[str, str]
CommandHandler = Callable[[dict], str]


def _timeline_summary(data: dict) -> str:
    """Return a simple timeline summary for the provided case."""
    case_id = data.get("case_id", 1)
    tm = TimelineManager()
    return tm.summarize(case_id)


COMMAND_REGISTRY: Dict[str, CommandHandler] = {
    "timeline summary": _timeline_summary,
}


def match_command(transcript: str) -> Optional[CommandHandler]:
    """Return a handler if the transcript matches a registered command."""
    lower = transcript.lower()
    for keyword, handler in COMMAND_REGISTRY.items():
        if keyword in lower:
            return handler
    return None


def execute_command(transcript: str, data: dict) -> Optional[CommandResult]:
    """Execute the command if found and return its keyword and result."""
    handler = match_command(transcript)
    if not handler:
        return None
    keyword = next(k for k, v in COMMAND_REGISTRY.items() if v is handler)
    result = handler(data)
    return keyword, result


__all__ = ["COMMAND_REGISTRY", "execute_command"]
