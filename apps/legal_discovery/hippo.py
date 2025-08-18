"""Minimal HippoRAG-style indexing and retrieval utilities.

This module provides deterministic document chunking, a very light-weight
entity extraction, and in-memory storage so that the Flask endpoints can
index and search documents without requiring external services. The goal is
not to be feature complete but to exercise the expected control flow for
indexing and retrieval.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
import re
from typing import Callable, Dict, Iterable, List, Optional

try:  # pragma: no cover - allows tests without neo4j package
    from neo4j import GraphDatabase, Driver
except Exception:  # pragma: no cover - fallback when driver unavailable
    GraphDatabase = Driver = None


# ---------------------------------------------------------------------------
# Dataclasses


@dataclass
class Segment:
    """Text segment with deterministic identifier."""

    doc_id: str
    segment_id: str
    segment_hash: str
    text: str
    page: int
    para: int
    tok_start: int
    tok_end: int
    entities: List[str]


# In-memory index: {case_id: {doc_id: [Segment, ...]}}
INDEX: Dict[str, Dict[str, List[Segment]]] = {}


# ---------------------------------------------------------------------------
# Neo4j schema
# ---------------------------------------------------------------------------

SCHEMA_QUERIES: Iterable[str] = (
    "CREATE CONSTRAINT hippo_document_doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.doc_id IS UNIQUE",
    "CREATE CONSTRAINT hippo_segment_hash IF NOT EXISTS FOR (s:Segment) REQUIRE s.hash IS UNIQUE",
    "CREATE CONSTRAINT hippo_entity_key IF NOT EXISTS FOR (e:Entity) REQUIRE e.key IS UNIQUE",
    "CREATE TEXT INDEX hippo_segment_text IF NOT EXISTS FOR (s:Segment) ON EACH [s.text]",
)


def setup_neo4j_schema(driver: Driver, database: str | None = None) -> None:
    """Ensure Neo4j constraints and indexes exist."""

    if not driver:  # pragma: no cover - driver not installed
        return
    db = database or os.environ.get("NEO4J_DATABASE", "neo4j")
    with driver.session(database=db) as session:  # pragma: no cover - network path
        for q in SCHEMA_QUERIES:
            session.run(q)


def ensure_graph_constraints() -> None:
    """Best-effort schema bootstrap using environment variables."""

    if not GraphDatabase:  # pragma: no cover - driver not installed
        return
    uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    pwd = os.environ.get("NEO4J_PASSWORD")
    auth = (user, pwd) if pwd else None
    db = os.environ.get("NEO4J_DATABASE", "neo4j")
    try:  # pragma: no cover - external dependency
        driver = GraphDatabase.driver(uri, auth=auth)
        setup_neo4j_schema(driver, db)
    except Exception:
        pass
    finally:  # pragma: no cover - ensure closure
        try:
            driver.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Helpers


def make_doc_id(case_id: str, path: str) -> str:
    """Return a stable 128-bit hex id for a document."""

    return hashlib.sha256(f"{case_id}:{path}".encode()).hexdigest()[:32]


def _segment_hash(doc_id: str, start: int, end: int) -> str:
    """Return a 64-bit hex hash for a text segment."""

    h = hashlib.sha256(f"{doc_id}:{start}:{end}".encode()).hexdigest()
    # first 16 hex = 64 bits
    return h[:16]


def chunk_text(
    text: str,
    doc_id: str,
    page: int = 1,
    tokens_per_chunk: int = 200,
    entity_extractor: Optional[Callable[[str], List[str]]] = None,
) -> List[Segment]:
    """Deterministically split ``text`` into segments.

    Each segment id follows the ``doc_id:page:para:start-end`` pattern and a
    64-bit ``segment_hash`` is derived from these values.  Tokens are simple
    whitespace splits which is adequate for the unit tests.  The ``entity_extractor``
    parameter allows callers to plug in a richer legal information extraction
    routine.  When omitted, a tiny built-in extractor is used.
    """

    tokens = text.split()
    segments: List[Segment] = []
    para = 0
    t = 0
    extractor = entity_extractor or _extract_entities
    while t < len(tokens):
        chunk_tokens = tokens[t : t + tokens_per_chunk]
        start = t
        end = t + len(chunk_tokens)
        segment_id = f"{doc_id}:{page}:{para}:{start}-{end}"
        seg_text = " ".join(chunk_tokens)
        seg_hash = _segment_hash(doc_id, start, end)
        entities = extractor(seg_text)
        segments.append(
            Segment(
                doc_id=doc_id,
                segment_id=segment_id,
                segment_hash=seg_hash,
                text=seg_text,
                page=page,
                para=para,
                tok_start=start,
                tok_end=end,
                entities=entities,
            )
        )
        para += 1
        t = end
    return segments


def _extract_entities(text: str) -> List[str]:
    """Very small NER extractor.

    We flag capitalised words as entities and normalise them to lower case to
    act as stable keys.  This keeps the implementation light-weight while
    allowing unit tests to exercise entity seeded queries.
    """

    ents = set()
    for match in re.findall(r"\b([A-Z][a-zA-Z]+)\b", text):
        ents.add(match.lower())
    return sorted(ents)


# ---------------------------------------------------------------------------
# Ingestion / Query


def upsert_document_and_segments(
    doc_id: str, case_id: str, path: str, segments: List[dict]
) -> tuple[str, dict]:
    """Return Cypher and parameters to upsert document segments."""

    cypher = (
        "MERGE (d:Document {doc_id: $doc_id}) "
        "SET d.case_id=$case_id, d.path=$path "
        "WITH d UNWIND $segments AS seg "
        "MERGE (s:Segment {hash: seg.hash}) "
        "SET s.text=seg.text, s.page=seg.page, s.para=seg.para "
        "MERGE (d)-[:HAS_SEGMENT]->(s) "
        "FOREACH (e IN seg.entities | MERGE (ent:Entity {key:e}) MERGE (s)-[:MENTIONS]->(ent))"
    )
    params = {
        "doc_id": doc_id,
        "case_id": case_id,
        "path": path,
        "segments": segments,
    }
    return cypher, params


def upsert_graph(edges: Iterable[dict]) -> tuple[str, dict]:
    """Return Cypher and parameters to upsert generic edges."""

    cypher = (
        "UNWIND $edges AS edge "
        "MATCH (s:Segment {hash: edge.src}) "
        "MATCH (t:Segment {hash: edge.dst}) "
        "MERGE (s)-[r:EDGE {type: edge.type}]->(t) "
        "SET r.weight=edge.weight"
    )
    return cypher, {"edges": list(edges)}


def ingest_document(
    case_id: str,
    text: str,
    path: str = "",
    *,
    entity_extractor: Optional[Callable[[str], List[str]]] = None,
    graph_db: Optional[object] = None,
    vector_db: Optional[object] = None,
) -> str:
    """Index ``text`` for ``case_id`` and return the generated ``doc_id``.

    The function accepts optional ``graph_db`` and ``vector_db`` managers to
    perform bulk upserts to Neo4j and Chroma respectively.  Callers may also
    supply a custom ``entity_extractor`` for legal information extraction.
    """

    doc_id = make_doc_id(case_id, path or "inline")
    case_index = INDEX.setdefault(case_id, {})
    if doc_id in case_index:
        return doc_id
    segments = chunk_text(text, doc_id, entity_extractor=entity_extractor)

    # In-memory index -----------------------------------------------------------------
    case_index[doc_id] = segments

    # Bulk vector upsert ---------------------------------------------------------------
    if vector_db:
        try:  # pragma: no cover - best effort
            vector_db.add_documents(
                documents=[s.text for s in segments],
                metadatas=[
                    {
                        "doc_id": doc_id,
                        "case_id": case_id,
                        "segment_id": s.segment_id,
                        "segment_hash": s.segment_hash,
                        "path": path,
                    }
                    for s in segments
                ],
                ids=[s.segment_hash for s in segments],
            )
        except Exception:
            pass

    # Bulk graph upsert ----------------------------------------------------------------
    if graph_db and segments:
        try:  # pragma: no cover - best effort
            seg_dicts = [
                {
                    "hash": s.segment_hash,
                    "text": s.text,
                    "page": s.page,
                    "para": s.para,
                    "entities": s.entities,
                }
                for s in segments
            ]
            graph_db.run_query(
                *upsert_document_and_segments(doc_id, case_id, path, seg_dicts),
                cache=False,
            )
        except Exception:
            pass

    # Postgres ingestion log ----------------------------------------------------------
    try:  # pragma: no cover - external dependency
        from .database import log_ingestion

        log_ingestion(
            case_id=case_id,
            path=path,
            doc_id=doc_id,
            segment_hashes=[s.segment_hash for s in segments],
        )
    except Exception:
        pass

    return doc_id


def hippo_query(case_id: str, query: str, k: int = 10) -> Dict[str, object]:
    """Perform a naïve retrieval over the in-memory index.

    Scores are a simple count of query token occurrences.  Paths include the
    originating entities for demonstrative purposes.
    """

    results = []
    q_tokens = query.lower().split()
    case_index = INDEX.get(case_id, {})
    for doc_segments in case_index.values():
        for seg in doc_segments:
            score = sum(seg.text.lower().count(t) for t in q_tokens)
            if score:
                spans = [
                    {"start": m.start(), "end": m.end()}
                    for t in q_tokens
                    for m in re.finditer(re.escape(t), seg.text.lower())
                ]
                path = [{"type": "Segment", "segment_id": seg.segment_id}]
                for ent in seg.entities:
                    path.insert(0, {"type": "Entity", "key": ent})
                results.append(
                    {
                        "doc_id": seg.doc_id,
                        "segment_id": seg.segment_id,
                        "snippet": seg.text[:200],
                        "spans": spans,
                        "path": path,
                        "scores": {"graph": score, "dense": score, "hybrid": score},
                    }
                )
    results.sort(key=lambda r: r["scores"]["hybrid"], reverse=True)
    return {"answer": "", "items": results[:k], "trace_id": hashlib.sha1(query.encode()).hexdigest()}
