from __future__ import annotations
import os
from typing import Any, Optional

# Import the correct client library
from fastmcp import Client
from google.adk.tools import FunctionTool

# Base URL for the MCP server
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost:8001/mcp")
# Timeout for the client connection
TIMEOUT_S = float(os.getenv("MCP_TIMEOUT_S", "60"))

async def _geo_service_impl(
    tool_name: str,
    url: Optional[str] = None,
    enhanced: Optional[bool] = None,
    markdown: Optional[str] = None,
    retries: Optional[int] = None,
    delay_seconds: Optional[float] = None
) -> Any:
    """
    Calls a specific tool on the MCP server with structured arguments.

    Args:
        tool_name: The exact name of the tool to call (e.g., 'rabobank_scrape').
        url: The target URL for scraping or saving.
        enhanced: Flag for enhanced markdown processing.
        markdown: The markdown content to save.
        retries: Number of retries for scraping.
        delay_seconds: Delay between scrape retries.
    """
    tool_args = {
        "url": url,
        "enhanced": enhanced,
        "markdown": markdown,
        "retries": retries,
        "delay_seconds": delay_seconds,
    }
    final_args = {k: v for k, v in tool_args.items() if v is not None}

    async with Client(MCP_BASE_URL, timeout=TIMEOUT_S) as client:
        try:
            response = await client.call_tool(tool_name, final_args)

            # 👇 THE CORRECTED ERROR HANDLING
            # First, check if the 'error' attribute exists on the response data.
            # This handles cases where the call is successful and there is no error object.
            if hasattr(response.data, 'error') and response.data.error:
                error = response.data.error
                raise RuntimeError(f"MCP error: {error.message} (Code: {error.code})")

            # If there's no error, return the result from the successful response.
            return response.data.result

        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool '{tool_name}': {e}")

# Create the FunctionTool from the final, polished implementation
geo_service = FunctionTool(_geo_service_impl)