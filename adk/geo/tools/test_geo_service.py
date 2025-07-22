"""test_geo_service.py – pytest suite for GeoService wrapper

This test file uses **pytest-asyncio** and **respx** (an httpx mock router)
so engineers can unit‑test the `GeoService` FunctionTool without spinning up
a real FastMCP instance.

Install extra deps:
    pip install pytest pytest-asyncio respx[httpx]

Run:
    pytest -q
"""
from __future__ import annotations

import os
from typing import Any

import pytest
from httpx import Response
import respx

# Import the artefacts under test
from tools.geo_service import GeoService, GeoArgs  # adjust import if needed

###############################################################################
# Test helpers                                                                 #
###############################################################################

TEST_BASE_URL = "http://mcp.local/mcp/"

# --------------------------------------------------------------------------- #
# 1) Happy path: JSON response                                                 #
# --------------------------------------------------------------------------- #

@pytest.mark.anyio
async def test_invoke_json_success():
    """GeoService returns parsed JSON when MCP responds with application/json."""
    os.environ["MCP_BASE_URL"] = TEST_BASE_URL  # override for this test
    geo_service = GeoService()
    args = GeoArgs(tool_name="hello_world", url="https://example.com")

    with respx.mock(assert_all_called=True) as router:
        router.post("http://mcp.local/mcp/").mock(
            return_value=Response(200, json={"result": "Hello, World!"})
        )
        result: Any = await geo_service.invoke(args, ctx=None)  # type: ignore[arg-type]

    assert result == {"result": "Hello, World!"}

# --------------------------------------------------------------------------- #
# 2) Happy path: text/plain fallback                                           #
# --------------------------------------------------------------------------- #

@pytest.mark.anyio
async def test_invoke_text_success():
    """GeoService returns raw text when MCP returns text/plain."""
    os.environ["MCP_BASE_URL"] = TEST_BASE_URL
    geo_service = GeoService()
    args = GeoArgs(tool_name="hello_world", url="https://example.com")

    with respx.mock(assert_all_called=True) as router:
        router.post("http://mcp.local/mcp/").mock(
            return_value=Response(200, text="OK", headers={"Content-Type": "text/plain"})
        )
        result = await geo_service.invoke(args, ctx=None)  # type: ignore[arg-type]

    assert result == "OK"

# --------------------------------------------------------------------------- #
# 3) Validation error on extra fields                                          #
# --------------------------------------------------------------------------- #

from pydantic import ValidationError


def test_geoargs_validation_error():
    """GeoArgs should reject unexpected keys thanks to extra='forbid'."""
    with pytest.raises(ValidationError):
        GeoArgs(tool_name="hello_world", url="https://example.com", unexpected="x")
