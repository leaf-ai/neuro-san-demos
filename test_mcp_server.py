#!/usr/bin/env python3
"""
End-to-end tests for the GEO FastMCP server (streamable-http, session-aware).

Run with:
    python test_mcp_server.py

Requires:
    pip install fastmcp>=2.2
"""

import asyncio
from fastmcp import Client
from pathlib import Path

SERVER_URL = "http://127.0.0.1:8001/mcp"   # trailing slash not required


async def main() -> None:
    async with Client(SERVER_URL, timeout=60) as client:
        # ------------------------------------------------------------------ #
        # 0. Health-check
        # ------------------------------------------------------------------ #
        tools = await client.list_tools()
        print("✅  Server healthy – tools exposed:", [t.name for t in tools])

        # ------------------------------------------------------------------ #
        # 1. hello_world
        # ------------------------------------------------------------------ #
        hello = await client.call_tool("hello_world", {"name": "Test User"})
        print("✅  hello_world →", hello.data.result)

        # ------------------------------------------------------------------ #
        # 2. rabobank_scrape (default URL)
        # ------------------------------------------------------------------ #
        scrape_default = await client.call_tool("rabobank_scrape")
        # md_default = scrape_default.data.result
        # print("✅  rabobank_scrape(default) length:", len(md_default))
        # print("   Preview:", md_default[:120].replace("\n", " "), "…\n")
        assert scrape_default.data.result is True, "Default scrape failed"
        default_md_path = Path("servers/mcp/knowdocs/finance-my-business.md")
        print(
            f"✅  rabobank_scrape(default) cached to: {default_md_path}"
        )

        # ------------------------------------------------------------------ #
        # 3. rabobank_scrape (custom URL)
        # ------------------------------------------------------------------ #
        scrape_custom = await client.call_tool(
            "rabobank_scrape",
            {
                "url": "https://www.rabobank.com/products/expand-my-business",
                "retries": 10,
                "delay_seconds": 1.0,
            },
        )
        # md_custom = scrape_custom.data.result
        # print("✅  rabobank_scrape(custom) length:", len(md_custom))
        # print("   Preview:", md_custom[:120].replace("\n", " "), "…")
        assert scrape_custom.data.result is True, "Custom scrape failed"
        custom_path = Path("servers/mcp/knowdocs/expand-my-business.md")
        print(
            f"✅  rabobank_scrape(custom) cached to: {custom_path}"
        )

        # ------------------------------------------------------------------ #
        # 4. get_markdown / save_markdown
        # ------------------------------------------------------------------ #
        target_url = "https://www.rabobank.com/products/expand-my-business"

        # -- get_markdown --------------------------------------------------- #
        md_resp = await client.call_tool("get_markdown", {"url": target_url})
        markdown = md_resp.data.result
        assert markdown, "get_markdown returned empty text"
        print(f"✅  get_markdown → {len(markdown):,} chars")

        # -- save_markdown -------------------------------------------------- #
        updated = markdown + "\n<!-- test update -->\n"
        save_resp = await client.call_tool(
            "save_markdown",
            {"url": target_url, "markdown": updated},
        )
        assert save_resp.data.result is True, "save_markdown failed"
        saved_path = Path("servers/mcp/knowdocs/expand-my-business.md")
        print(f"✅  save_markdown → wrote to: {saved_path.resolve()}")
if __name__ == "__main__":
    asyncio.run(main())
