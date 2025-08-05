from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from neuro_san.interfaces.coded_tool import CodedTool

from apps.legal_discovery.chain_logger import ChainEventType, log_event
from apps.legal_discovery.database import db
from apps.legal_discovery.models import (
    Conversation,
    Document,
    Message,
    MessageVisibility,
)

from .knowledge_graph_manager import KnowledgeGraphManager
from .privilege_detector import PrivilegeDetector
from .vector_database_manager import VectorDatabaseManager


class RetrievalChatAgent(CodedTool):
    """Query vector and graph stores with privilege filtering and audit logging."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.vector_db = VectorDatabaseManager(**kwargs)
        self.graph_db = KnowledgeGraphManager(**kwargs)
        self.detector = PrivilegeDetector()

    def _ensure_conversation(self, conversation_id: Optional[str], sender_id: int) -> Conversation:
        if conversation_id:
            convo = Conversation.query.get(conversation_id)
            if convo:
                if sender_id not in convo.participants:
                    convo.participants.append(sender_id)
                    db.session.commit()
                return convo
        convo = Conversation(participants=[sender_id])
        db.session.add(convo)
        db.session.commit()
        return convo

    def store_message(
        self,
        conversation_id: Optional[str],
        sender_id: int,
        content: str,
        document_ids: Optional[List[int]] = None,
        reply_to: Optional[str] = None,
    ) -> Message:
        convo = self._ensure_conversation(conversation_id, sender_id)
        privileged, spans = self.detector.detect(content)
        visibility = MessageVisibility.ATTORNEY_ONLY if privileged else MessageVisibility.PUBLIC
        text = self.detector.redact_text(content, spans) if privileged else content
        message = Message(
            conversation_id=convo.id,
            sender_id=sender_id,
            content=text,
            document_ids=document_ids or [],
            reply_to_id=reply_to,
            visibility=visibility,
        )
        db.session.add(message)
        db.session.commit()
        return message

    def query(
        self,
        question: str,
        sender_id: int = 0,
        conversation_id: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        message = self.store_message(conversation_id, sender_id, question)
        vec = self.vector_db.query([question], n_results=top_k)
        documents: List[Dict[str, Any]] = []
        for doc_id, meta in zip(vec.get("ids", [[]])[0], vec.get("metadatas", [[]])[0]):
            doc = Document.query.filter_by(id=int(meta.get("id", doc_id))).first()
            if not doc or doc.is_privileged:
                continue
            log_event(doc.id, ChainEventType.ACCESSED, metadata={"message_id": message.id})
            documents.append({"id": doc.id, "name": doc.name})
        try:
            records = self.graph_db.run_query(
                "MATCH (f:Fact) WHERE toLower(f.text) CONTAINS toLower($q) RETURN f.text AS text LIMIT $k",
                {"q": question, "k": top_k},
            )
            facts = [r["text"] for r in records]
        except Exception as exc:  # pragma: no cover - best effort
            logging.warning("graph query failed: %s", exc)
            facts = []
        return {"message_id": message.id, "documents": documents, "facts": facts}


__all__ = ["RetrievalChatAgent"]
