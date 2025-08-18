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


def _graph_candidates(case_id: str, seeds: List[str], k: int) -> Dict[str, Dict]:
    """Return candidate segments scored by seeded entity matches.

    This function acts as a lightweight stand-in for a Neo4j GDS
    personalised PageRank or HippoRAG query.  When the real services are
    unavailable the in-memory index is scanned and any segment containing
    one of the ``seeds`` is returned with a simple frequency score.
    """

    case_index = INDEX.get(case_id, {})
    scores: Dict[str, Dict] = {}
    seed_set = {s.lower() for s in seeds}
    for seg in (s for docs in case_index.values() for s in docs):
        gscore = len(seed_set.intersection(seg.entities))
        if gscore:
            scores[seg.segment_id] = {"segment": seg, "graph": gscore}
    return dict(
        sorted(scores.items(), key=lambda x: x[1]["graph"], reverse=True)[:k]
    )


def _vector_candidates(case_id: str, query: str, k: int) -> Dict[str, Dict]:
    """Return candidate segments scored by dense similarity.

    In production this would issue a Chroma similarity search.  For the
    offline test environment we simply count query token matches.
    """

    q_tokens = query.lower().split()
    case_index = INDEX.get(case_id, {})
    scores: Dict[str, Dict] = {}
    for seg in (s for docs in case_index.values() for s in docs):
        dscore = sum(seg.text.lower().count(t) for t in q_tokens)
        if dscore:
            scores[seg.segment_id] = {"segment": seg, "dense": dscore}
    return dict(
        sorted(scores.items(), key=lambda x: x[1]["dense"], reverse=True)[:k]
    )


def hippo_query(case_id: str, query: str, k: int = 10) -> Dict[str, object]:
    """Query indexed segments using graph and vector searches.

    The function performs three stages:

    1. **Entity linking** – extract entities from the query.  These seed a
       personalised PageRank style lookup over the Neo4j graph.  When no
       entities are found, or the graph returns no results, we fall back to
       using raw query tokens as seeds.
    2. **Dense retrieval** – issue a similarity search against the vector
        store (Chroma).  In the offline test environment this is simulated
        with token frequency counts.
    3. **Re‑ranking** – merge candidates by ``segment_id`` and compute a
       combined ``hybrid`` score representing a trivial cross‑encoder/LLM
       re‑ranker.
    """

    q_entities = _extract_entities(query)
    q_tokens = query.lower().split()
    seeds = q_entities or q_tokens

    graph_cands = _graph_candidates(case_id, seeds, k)
    if q_entities and not graph_cands:
        graph_cands = _graph_candidates(case_id, q_tokens, k)

    dense_cands = _vector_candidates(case_id, query, k)

    merged: Dict[str, Dict] = {}
    for seg_id, info in {**graph_cands, **dense_cands}.items():
        seg = info["segment"]
        entry = merged.setdefault(seg_id, {"segment": seg, "graph": 0, "dense": 0})
        entry["graph"] += info.get("graph", 0)
        entry["dense"] += info.get("dense", 0)

    results = []
    token_set = set(q_tokens)
    for seg_id, info in merged.items():
        seg = info["segment"]
        graph_score = info["graph"]
        dense_score = info["dense"]
        hybrid_score = graph_score + dense_score
        spans = [
            {"start": m.start(), "end": m.end()}
            for t in token_set
            for m in re.finditer(re.escape(t), seg.text.lower())
        ]
        path = [
            {"type": "Document", "doc_id": seg.doc_id},
            *[{"type": "Entity", "key": ent} for ent in seg.entities],
            {"type": "Segment", "segment_id": seg.segment_id},
        ]
        results.append(
            {
                "doc_id": seg.doc_id,
                "segment_id": seg.segment_id,
                "snippet": seg.text[:200],
                "spans": spans,
                "path": path,
                "scores": {
                    "graph": graph_score,
                    "dense": dense_score,
                    "hybrid": hybrid_score,
                },
            }
        )

    results.sort(key=lambda r: r["scores"]["hybrid"], reverse=True)
    trace_id = hashlib.sha1(query.encode()).hexdigest()
    return {"answer": "", "items": results[:k], "trace_id": trace_id}
