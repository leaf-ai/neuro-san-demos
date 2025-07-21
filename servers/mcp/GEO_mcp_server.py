# geo_mcp_server.py  –  GEO MCP Server (streamable-http, session-aware)
# Python ≥ 3.12 • FastMCP ≥ 0.3 • Crawl4AI ≥ 0.7
##############################################################################
# ─────────────────────────────────────────────────────────────────────────── #
# 1. Imports & global logging
# ─────────────────────────────────────────────────────────────────────────── #
##############################################################################
import asyncio
import logging
import platform
from pathlib import Path
from typing import Optional

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from fastapi import FastAPI, Request, Response
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware

from cache_utils import (
    KNOWDOCS_PATH,
    markdown_path,
    page_exists,
    read_markdown,
    write_markdown,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("GEO-MCP")

##############################################################################
# 2. Middleware – raise the request-body limit to 10 MB
##############################################################################
MAX_BODY_BYTES = 10 * 1024 * 1024  # 10 MB


class BodySizeLimiter(BaseHTTPMiddleware):
    """Return HTTP 413 if the incoming body exceeds MAX_BODY_BYTES."""

    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        if len(body) > MAX_BODY_BYTES:
            log.warning("413 Payload too large: %d bytes (limit=%d)",
                        len(body), MAX_BODY_BYTES)
            return Response("Payload too large", status_code=413)
        # Re-inject the body for downstream consumers
        request._body = body
        return await call_next(request)


def _find_fastapi_app(mcp_obj) -> Optional[FastAPI]:
    """
    Return the underlying FastAPI instance no matter which attribute
    name FastMCP uses (public, private or renamed in forks).
    """
    # 1 – common public / private names
    for attr in ("app", "_app", "asgi_app", "_fastapi", "_api"):
        fastapi_app = getattr(mcp_obj, attr, None)
        if isinstance(fastapi_app, FastAPI):
            return fastapi_app
    # 2 – brute-force scan of all attributes
    for val in vars(mcp_obj).values():
        if isinstance(val, FastAPI):
            return val
    return None


def _attach_middleware(mcp_obj, mw_cls):
    """Add `mw_cls` to the FastAPI app, if we can locate it."""
    fastapi_app = _find_fastapi_app(mcp_obj)
    if fastapi_app is None:
        log.warning("⚠ Cannot locate FastAPI app inside FastMCP – "
                    "BodySizeLimiter not installed!")
        return
    fastapi_app.add_middleware(mw_cls)
    log.debug("✅ BodySizeLimiter installed on FastAPI app")


##############################################################################
# 3. Platform fixes (Windows ≤3.11 selector vs. ≥3.12 proactor change)
##############################################################################
if platform.system() == "Windows":
    maj, minor = map(int, platform.python_version_tuple()[:2])
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy() if (maj, minor) >= (3, 12)
        else asyncio.WindowsSelectorEventLoopPolicy()
    )

##############################################################################
# 4. Crawl constants & helper
##############################################################################
DEFAULT_URL = "https://www.rabobank.com/products/finance-my-business"
MAX_RETRIES = 10
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


async def _crawl_once(url: str) -> str:
    """Return a Markdown snapshot of the given Rabobank product URL."""
    md_gen = DefaultMarkdownGenerator(options={"ignore_links": True,
                                               "body_width": 0})
    run_cfg = CrawlerRunConfig(
        css_selector="header, main, section.intro",
        wait_for="css:main",
        word_count_threshold=0,
        js_code=COOKIE_JS,
        excluded_tags=["nav", "header", "footer", "aside",
                       "script", "style"],
        markdown_generator=md_gen,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=run_cfg)
    md_obj = result.markdown
    return (getattr(md_obj, "fit_markdown", None)
            or md_obj.raw_markdown or "").strip()

##############################################################################
# 5. FastMCP instance  +  tools
##############################################################################
mcp = FastMCP("GEO", port=8001, auto_initialize=True)
# 👉 make sure the FastAPI object is actually built
if hasattr(mcp, "initialize"):          # present on every FastMCP release
    mcp.initialize()                    # no-op if already initialised
# 👉 attach the BodySizeLimiter middleware to the FastAPI app
_attach_middleware(mcp, BodySizeLimiter)        # << installs the 10 MB limit


@mcp.tool()
async def hello_world(name: str = "World") -> str:
    log.info("[hello_world] called")
    return f"Hello, {name}! GEO MCP Server is up."


@mcp.tool()
async def rabobank_scrape(
    url: str = DEFAULT_URL,
    retries: int = MAX_RETRIES,
    delay_seconds: float = RETRY_DELAY_S,
) -> bool:
    log.info("[rabobank_scrape] URL=%s", url)
    if page_exists(url):
        log.info("[rabobank_scrape] cached copy exists – skip crawl")
        return True

    for attempt in range(1, retries + 1):
        markdown = await _crawl_once(url)
        if markdown:
            if attempt > 1:
                log.info("[rabobank_scrape] succeeded on retry %d/%d",
                         attempt, retries)
            write_markdown(url, markdown, enhanced=False)
            log.debug("[rabobank_scrape] saved → %s", markdown_path(url))
            return True
        log.warning("[rabobank_scrape] empty result on try %d/%d",
                    attempt, retries)
        await asyncio.sleep(delay_seconds)
    return False


@mcp.tool()
async def get_markdown(url: str = DEFAULT_URL, enhanced: bool = False) -> str:
    log.info("[get_markdown] URL=%s enhanced=%s", url, enhanced)
    return read_markdown(url, enhanced=enhanced)


@mcp.tool()
async def save_markdown(
    url: str = DEFAULT_URL,
    markdown: str = "",
    enhanced: bool = False,
) -> bool:
    log.debug("[save_markdown] URL=%s enhanced=%s payload_chars=%d",
              url, enhanced, len(markdown))
    if not markdown:
        log.error("[save_markdown] empty payload – abort")
        return False
    write_markdown(url, markdown, enhanced=enhanced)
    log.info("[save_markdown] written → %s",
             markdown_path(url, enhanced=enhanced))
    return True


##############################################################################
# 6. Run the server (streamable-http → SSE / token streaming capable)
##############################################################################
if __name__ == "__main__":
    log.info("Starting GEO-MCP on :8001  (body-limit=%.1f MB)",
             MAX_BODY_BYTES / 1024 / 1024)
    mcp.run(transport="streamable-http")
