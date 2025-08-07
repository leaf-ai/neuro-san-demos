import os
from neuro_san.interfaces.coded_tool import CodedTool
from langchain_google_genai import ChatGoogleGenerativeAI

from .web_scraper import WebScraper

try:
    from .courtlistener_client import CourtListenerClient
except Exception:  # pragma: no cover - optional
    CourtListenerClient = None


class ResearchTools(CodedTool):
    """Perform legal research using CourtListener and California Codes."""

    def search(self, query: str, source: str = "all"):
        """Return combined research results and a Gemini 2.5 summary."""
        results: dict[str, object] = {}

        if source in ("all", "cases") and CourtListenerClient:
            client = CourtListenerClient()
            try:
                results["cases"] = client.search_opinions(query)
            except Exception as exc:  # pragma: no cover - network may fail
                results["cases_error"] = str(exc)

        if source in ("all", "statutes"):
            scraper = WebScraper()
            try:
                results["statutes"] = scraper.scrape_california_codes(query)
            except Exception as exc:  # pragma: no cover - network may fail
                results["statutes_error"] = str(exc)

        try:
            llm = ChatGoogleGenerativeAI(
                model=os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
            )
            prompt = (
                "Summarize the following legal research results in concise bullet points:\n"
                + str(results)
            )
            summary = llm.invoke(prompt, timeout=60).content
            results["summary"] = summary
        except Exception:  # pragma: no cover - optional LLM failure
            pass

        return results
