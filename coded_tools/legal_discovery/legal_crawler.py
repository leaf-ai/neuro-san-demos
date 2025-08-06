import datetime
import os
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from neuro_san.interfaces.coded_tool import CodedTool

from .knowledge_graph_manager import KnowledgeGraphManager


class LegalCrawler(CodedTool):
    """Crawl legal resources and store them in Neo4j."""

    def __init__(self, kg: Optional[KnowledgeGraphManager] = None, **kwargs):
        super().__init__(**kwargs)
        self.kg = kg or KnowledgeGraphManager()
        self.sources: Dict[str, Optional[str]] = {
            "bench_cards": os.environ.get("BENCH_CARDS_URL"),
            "jury_instructions": os.environ.get("JURY_INSTRUCTIONS_URL"),
            "statutes": os.environ.get("STATUTES_URL"),
            "case_law": os.environ.get("CASE_LAW_URL"),
        }

    def _fetch_text(self, url: str) -> str:
        """Return normalized text content for a URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text(" ", strip=True)

    def crawl_category(self, category: str) -> List[Dict[str, str]]:
        """Crawl a configured category and return references."""
        base_url = self.sources.get(category)
        if not base_url:
            raise RuntimeError(f"{category} URL not configured")
        text = self._fetch_text(base_url)
        retrieved = datetime.datetime.utcnow().isoformat()
        return [
            {
                "category": category,
                "title": base_url,
                "url": base_url,
                "text": text,
                "retrieved_at": retrieved,
            }
        ]

    def crawl_all(self) -> List[Dict[str, str]]:
        """Crawl all configured categories."""
        results: List[Dict[str, str]] = []
        for category in self.sources:
            try:
                results.extend(self.crawl_category(category))
            except Exception as exc:  # pragma: no cover - network issues
                results.append({"category": category, "error": str(exc)})
        return results

    def store(self, references: List[Dict[str, str]], theories: Optional[List[str]] = None) -> None:
        """Store crawled references in the knowledge graph."""
        for ref in references:
            if ref.get("error"):
                continue
            self.kg.add_legal_reference(
                category=ref["category"],
                title=ref["title"],
                text=ref["text"],
                url=ref["url"],
                retrieved_at=ref["retrieved_at"],
                theories=theories or [],
            )

__all__ = ["LegalCrawler"]
