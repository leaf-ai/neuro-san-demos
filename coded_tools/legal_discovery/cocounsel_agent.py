from __future__ import annotations

import logging
import os
import uuid
from typing import Any, Callable, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from neuro_san.interfaces.coded_tool import CodedTool

from .command_prompt import CommandPrompt
from .document_fetcher import DocumentFetcher
from .internet_search import InternetSearch
from .knowledge_graph_manager import KnowledgeGraphManager
from .sanctions_risk_analyzer import SanctionsRiskAnalyzer
from .vector_database_manager import VectorDatabaseManager
from .code_editor import CodeEditor


EventHandler = Callable[[Dict[str, Any]], None]


class CocounselAgent(CodedTool):
    """Gemini powered co-counsel agent with rich tool integration."""

    def __init__(
        self,
        vector_db: VectorDatabaseManager | None = None,
        graph_db: KnowledgeGraphManager | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.vector_db = vector_db or VectorDatabaseManager(**kwargs)
        self.graph_db = graph_db or KnowledgeGraphManager(**kwargs)
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash-lite-preview-06-17")
        )
        self.embedder = GoogleGenerativeAIEmbeddings()

        # Tools
        self.internet_search = InternetSearch()
        self.code_editor = CodeEditor()
        self.command_prompt = CommandPrompt()
        self.sanctions_analyzer = SanctionsRiskAnalyzer()
        self.document_fetch = DocumentFetcher()

        # Event hooks registry
        self._hooks: Dict[str, List[EventHandler]] = {}

    # ------------------------------------------------------------------
    # Event hook system
    def register_hook(self, event: str, handler: EventHandler) -> None:
        """Register a callback for a named event."""
        self._hooks.setdefault(event, []).append(handler)

    def _emit(self, event: str, payload: Dict[str, Any]) -> None:
        for handler in self._hooks.get(event, []):
            try:
                handler(payload)
            except Exception as exc:  # pragma: no cover - best effort
                logging.warning("event handler failed for %s: %s", event, exc)

    # ------------------------------------------------------------------
    # External ingestion
    def _ingest_external(self, source: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        meta = metadata or {}
        doc_id = f"{source}-{uuid.uuid4()}"
        try:
            self.vector_db.add_documents([text], [meta], [doc_id])
        except Exception as exc:  # pragma: no cover - best effort
            logging.warning("vector ingest failed: %s", exc)
        try:
            self.graph_db.create_node(source.capitalize(), {"id": doc_id, "text": text, **meta})
        except Exception as exc:  # pragma: no cover - best effort
            logging.warning("graph ingest failed: %s", exc)
        self._emit(f"{source}_output", {"id": doc_id, "text": text, "metadata": meta})

    def ingest_forensic_output(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Ingest findings from forensic teams."""
        self._ingest_external("forensic", text, metadata)

    def ingest_research_output(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Ingest findings from research teams."""
        self._ingest_external("research", text, metadata)

    # ------------------------------------------------------------------
    def ask(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Answer a question using vector and graph stores with Gemini."""
        vec = self.vector_db.query([question], n_results=top_k)
        documents = vec.get("documents", [[]])[0]
        metadatas = vec.get("metadatas", [[]])[0]
        try:
            records = self.graph_db.run_query(
                "MATCH (f:Fact) WHERE toLower(f.text) CONTAINS toLower($q) RETURN f.text AS text LIMIT $k",
                {"q": question, "k": top_k},
            )
            facts = [r["text"] for r in records]
        except Exception as exc:  # pragma: no cover - best effort
            logging.warning("graph query failed: %s", exc)
            facts = []

        search_results = self.internet_search.search(question)[:3]

        context = "".join([f"Document: {d}\n" for d in documents]) + "\n" + "\n".join(facts)
        if search_results:
            context += "\n" + "\n".join(sr["snippet"] for sr in search_results if sr.get("snippet"))

        prompt = f"Question: {question}\n\nContext:\n{context}\n\nAnswer:"  # noqa: E501
        answer = self.llm.invoke(prompt, timeout=120).content
        risk = self.sanctions_analyzer.assess(answer)

        result = {
            "answer": answer,
            "documents": metadatas,
            "facts": facts,
            "search_results": search_results,
            "sanctions_risk": risk,
        }
        self._emit("analysis_complete", result)
        return result


__all__ = ["CocounselAgent"]
