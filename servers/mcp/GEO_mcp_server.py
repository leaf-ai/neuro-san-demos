# geo_mcp_server.py  –  GEO MCP Server (streamable-http, session-aware)
# Python ≥ 3.12 • FastMCP ≥ 0.3 • Crawl4AI ≥ 0.7

import asyncio, platform, logging
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from mcp.server.fastmcp import FastMCP

# --- Windows event-loop fix (safe on Linux/macOS) --------------------------
if platform.system() == "Windows":
    maj, minor = map(int, platform.python_version_tuple()[:2])
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy() if (maj, minor) >= (3, 12)
        else asyncio.WindowsSelectorEventLoopPolicy()
    )

# -------------------------------------------------------------------------- #
# Constants
# -------------------------------------------------------------------------- #
DEFAULT_URL   = "https://www.rabobank.com/products/finance-my-business"
MAX_RETRIES   = 10
RETRY_DELAY_S = 2

COOKIE_JS = r"""
(async () => {
  try {
    const sels = ['#onetrust-accept-btn-handler',
                  'button[title="Accept all cookies"]'];
    for (let i = 0; i < 50; i++) {
      const btn = sels.map(s => document.querySelector(s)).find(Boolean);
      if (btn) { btn.click(); break; }
      await new Promise(r => setTimeout(r, 100));
    }
  } catch(e) {}
})();
"""

# -------------------------------------------------------------------------- #
# Helper – crawl Rabobank product pages once
# -------------------------------------------------------------------------- #
async def _crawl_once(url: str) -> str:
    md_gen = DefaultMarkdownGenerator(options={"ignore_links": True, "body_width": 0})

    run_cfg = CrawlerRunConfig(
        css_selector="header, main, section.intro",
        wait_for="css:main",          # wait until body copy is injected
        word_count_threshold=0,
        js_code=COOKIE_JS,
        excluded_tags=["nav", "header", "footer", "aside", "script", "style"],
        markdown_generator=md_gen,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=run_cfg)

    md_obj = result.markdown
    return (getattr(md_obj, "fit_markdown", None) or md_obj.raw_markdown or "").strip()


# -------------------------------------------------------------------------- #
# FastMCP server & tools
# --------------------------------------------------
# ------------------------ #
mcp = FastMCP("GEO", port=8001, auto_initialize=True)     # <<< SINGLE INSTANCE

@mcp.tool()
async def hello_world(name: str = "World") -> str:
    """Connectivity test."""
    logging.info("[MCP-Tool] hello_world called")
    return f"Hello, {name}! GEO MCP Server is up."

@mcp.tool()
async def rabobank_scrape(
    url: str = DEFAULT_URL,
    retries: int = MAX_RETRIES,
    delay_seconds: float = RETRY_DELAY_S,
) -> str:
    """Return markdown for any Rabobank `/products/*` page."""
    logging.info("[MCP-Tool] Scraping URL => %s", url)
    for attempt in range(1, retries + 1):
        markdown = await _crawl_once(url)
        if markdown:
            if attempt > 1:
                logging.info("[MCP-Tool] Succeeded on retry %d/%d", attempt, retries)
            return markdown
        logging.warning("[MCP-Tool] Empty result on try %d/%d", attempt, retries)
        await asyncio.sleep(delay_seconds)
    return f"No content found after {retries} retries."


# -------------------------------------------------------------------------- #
# Run the server  (streamable-http keeps SSE / token streaming capability)
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    mcp.run(transport="streamable-http")   # single call, no duplicate
