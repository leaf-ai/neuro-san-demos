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
import time
import logging
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from .cache import invalidate_prefix

try:  # pragma: no cover - allows tests without neo4j package
    from neo4j import GraphDatabase, Driver
except Exception:  # pragma: no cover - fallback when driver unavailable
    GraphDatabase = Driver = None

try:  # pragma: no cover - optional chroma dependency
    import chromadb  # type: ignore
except Exception:  # pragma: no cover - chroma not installed
    chromadb = None

try:  # pragma: no cover - optional cross-encoder dependency
    from sentence_transformers import CrossEncoder  # type: ignore
except Exception:  # pragma: no cover - transformer library not installed
    CrossEncoder = None

try:  # pragma: no cover - optional LLM scoring dependency
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - OpenAI not installed
    OpenAI = None

CROSS_ENCODER_MODEL = os.environ.get("CROSS_ENCODER_MODEL")
if CrossEncoder and CROSS_ENCODER_MODEL:
    try:  # pragma: no cover - model loading path
        CROSS_ENCODER = CrossEncoder(CROSS_ENCODER_MODEL)
    except Exception:  # pragma: no cover - model load failures
        CROSS_ENCODER = None
else:  # pragma: no cover - environment did not request a model
    CROSS_ENCODER = None

LLM_SCORER_MODEL = os.environ.get("LLM_SCORER_MODEL")
if OpenAI and LLM_SCORER_MODEL and os.environ.get("OPENAI_API_KEY"):
    try:  # pragma: no cover - network path
        _openai_client = OpenAI()
    except Exception:  # pragma: no cover - client init failures
        _openai_client = None
else:  # pragma: no cover - no LLM scoring
    _openai_client = None


logger = logging.getLogger(__name__)


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
    facts: List[Tuple[str, str, str]]


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


# ---------------------------------------------------------------------------
# Helpers


def make_doc_id(case_id: str, path: str) -> str:
    """Return a stable 128-bit hex id for a document."""

    return hashlib.sha256(f"{case_id}:{path}".encode()).hexdigest()[:32]


def _segment_hash(text: str) -> str:
    """Return a 64-bit hex hash for a text segment based on its contents."""

    return hashlib.sha256(text.encode()).hexdigest()[:16]


def chunk_text(
    text: str,
    doc_id: str,
    page: int = 1,
    tokens_per_chunk: int = 200,
    entity_extractor: Optional[Callable[[str], List[str] | Dict[str, object]]] = None,
) -> List[Segment]:
    """Deterministically split ``text`` into segments.

    Each segment id follows the ``doc_id:hash`` pattern where ``hash`` is a
    64-bit digest of the segment text. Tokens are simple whitespace splits
    which is adequate for the unit tests.  The ``entity_extractor``
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
        seg_text = " ".join(chunk_tokens)
        seg_hash = _segment_hash(seg_text)
        segment_id = f"{doc_id}:{seg_hash}"
        result = extractor(seg_text)
        if isinstance(result, dict):
            entities = result.get("entities", [])
            facts = result.get("facts", [])
        else:
            entities = result
            facts = []
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
                facts=facts,
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
    """Return Cypher and parameters to upsert document segments.

    The statement merges ``Document`` and ``Segment`` nodes alongside
    related ``Entity`` and ``Fact`` nodes using the Neo4j 5.23 templates.
    """

    cypher = (
        "\n".join(
            [
                "MERGE (d:Document {doc_id: $doc_id})",
                "SET d.case_id=$case_id, d.path=$path",
                "WITH d UNWIND $segments AS seg",
                "MERGE (s:Segment {hash: seg.hash})",
                "SET s.text=seg.text, s.page=seg.page, s.para=seg.para",
                "MERGE (d)-[:HAS_SEGMENT]->(s)",
                (
                    "FOREACH (e IN seg.entities | MERGE (ent:Entity {key:e}) "
                    "MERGE (s)-[:MENTIONS]->(ent))"
                ),
                (
                    "FOREACH (f IN seg.facts | "
                    "MERGE (sub:Entity {key:f.subject}) "
                    "MERGE (obj:Entity {key:f.object}) "
                    "MERGE (fact:Fact {key:f.key, predicate:f.predicate}) "
                    "MERGE (fact)-[:SUBJECT]->(sub) "
                    "MERGE (fact)-[:OBJECT]->(obj) "
                    "MERGE (s)-[:ASSERTS]->(fact))"
                ),
            ]
        )
    )
    params = {
        "doc_id": doc_id,
        "case_id": case_id,
        "path": path,
        "segments": segments,
    }
    return cypher, params


def upsert_graph(edges: Iterable[dict]) -> tuple[str, dict]:
    """Return Cypher and parameters to upsert generic edges between segments."""

    cypher = "\n".join(
        [
            "UNWIND $edges AS edge",
            "MATCH (s:Segment {hash: edge.src})",
            "MATCH (t:Segment {hash: edge.dst})",
            "MERGE (s)-[r:EDGE {type: edge.type}]->(t)",
            "SET r.weight=edge.weight",
        ]
    )
    return cypher, {"edges": list(edges)}


def ingest_document(
    case_id: str,
    text: str,
    path: str = "",
    *,
    entity_extractor: Optional[Callable[[str], List[str] | Dict[str, object]]] = None,
    graph_db: Optional[object] = None,
    vector_db: Optional[object] = None,
) -> str:
    """Index ``text`` for ``case_id`` and return the generated ``doc_id``.

    The function accepts optional ``graph_db`` and ``vector_db`` managers to
    perform bulk upserts to Neo4j and Chroma respectively.  Callers may also
    supply a custom ``entity_extractor`` for legal information extraction.
    """

    start = time.perf_counter()
    errors: List[str] = []
    doc_id = make_doc_id(case_id, path or "inline")
    segments = chunk_text(text, doc_id, entity_extractor=entity_extractor)
    segment_hashes = [s.segment_hash for s in segments]

    try:  # pragma: no cover - best effort
        from .database import ingestion_matches

        if ingestion_matches(doc_id, segment_hashes):
            return doc_id
    except Exception as exc:
        logger.exception("failed to check ingestion match", exc_info=exc)

    case_index = INDEX.setdefault(case_id, {})
    case_index[doc_id] = segments
    invalidate_prefix("hippo_query")
    invalidate_prefix("vector_search")

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
        except Exception as e:
            errors.append(f"vector: {e}")

    if graph_db and segments:
        try:  # pragma: no cover - best effort
            seg_dicts = []
            for s in segments:
                fact_dicts = [
                    {
                        "key": hashlib.sha256(f"{sub}:{pred}:{obj}".encode()).hexdigest()[:32],
                        "subject": sub,
                        "predicate": pred,
                        "object": obj,
                    }
                    for sub, pred, obj in s.facts
                ]
                seg_dicts.append(
                    {
                        "hash": s.segment_hash,
                        "text": s.text,
                        "page": s.page,
                        "para": s.para,
                        "entities": s.entities,
                        "facts": fact_dicts,
                    }
                )
            graph_db.run_query(
                *upsert_document_and_segments(doc_id, case_id, path, seg_dicts),
                cache=False,
            )
        except Exception as e:
            errors.append(f"graph: {e}")

    elapsed_ms = (time.perf_counter() - start) * 1000
    try:  # pragma: no cover - external dependency
        from .database import log_ingestion

        log_ingestion(
            case_id=case_id,
            path=path,
            doc_id=doc_id,
            segment_hashes=segment_hashes,
            status="failed" if errors else "ingested",
            duration_ms=elapsed_ms,
            error="; ".join(errors) if errors else None,
        )
    except Exception as exc:
        logger.exception("failed to log ingestion", exc_info=exc)

    return doc_id


def _graph_candidates(case_id: str, seeds: List[str], k: int) -> Dict[str, Dict]:
    """Return candidate segments scored by personalised PageRank.

    The routine prefers a real Neo4j GDS or HippoRAG lookup when the
    ``neo4j`` driver is available and environment variables point to a
    running service.  Failing that, it falls back to a tiny in-memory
    scorer that simply counts overlapping entities.
    """

    case_index = INDEX.get(case_id, {})
    lookup = {s.segment_id: s for docs in case_index.values() for s in docs}

    if GraphDatabase and seeds:
        uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD")
        auth = (user, pwd) if pwd else None
        db = os.environ.get("NEO4J_DATABASE", "neo4j")
        driver: Driver | None = None
        try:  # pragma: no cover - external dependency
            driver = GraphDatabase.driver(uri, auth=auth)
            with driver.session(database=db) as session:
                cypher = (
                    "CALL { MATCH (e:Entity) WHERE e.key IN $seeds RETURN collect(e) AS seed } "
                    "CALL gds.pageRank.stream({"
                    " nodeProjection:'Segment',"
                    " relationshipProjection:{MENTIONS:{type:'MENTIONS',orientation:'REVERSE'}},"
                    " sourceNodes: seed }) "
                    "YIELD nodeId, score "
                    "WITH gds.util.asNode(nodeId) AS s, score "
                    "MATCH (d:Document)-[:HAS_SEGMENT]->(s) "
                    "WHERE d.case_id=$case_id "
                    "RETURN s.segment_id AS segment_id, score "
                    "ORDER BY score DESC LIMIT $k"
                )
                records = session.run(
                    cypher,
                    {"seeds": seeds, "case_id": case_id, "k": k},
                )
                results: Dict[str, Dict] = {}
                for rec in records:
                    seg_id = rec.get("segment_id")
                    seg = lookup.get(seg_id)
                    if seg:
                        results[seg_id] = {
                            "segment": seg,
                            "graph": float(rec.get("score", 0.0)),
                        }
                if results:
                    return results
        except Exception as exc:
            logger.exception("graph candidate retrieval failed", exc_info=exc)
        finally:  # pragma: no cover - ensure closure
            if driver:
                try:
                    driver.close()
                except Exception as exc:
                    logger.exception("driver close failed", exc_info=exc)

    # Fallback to deterministic entity overlap scoring
    scores: Dict[str, Dict] = {}
    seed_set = {s.lower() for s in seeds}
    for seg in lookup.values():
        gscore = len(seed_set.intersection(seg.entities))
        if gscore:
            scores[seg.segment_id] = {"segment": seg, "graph": gscore}
    return dict(
        sorted(scores.items(), key=lambda x: x[1]["graph"], reverse=True)[:k]
    )


def _vector_candidates(case_id: str, query: str, k: int) -> Dict[str, Dict]:
    """Return candidate segments scored by dense similarity.

    A real deployment would use a Chroma collection.  When the ``chromadb``
    package or service is missing we degrade to a bag-of-words overlap which
    keeps the unit tests hermetic.
    """

    case_index = INDEX.get(case_id, {})
    lookup = {s.segment_id: s for docs in case_index.values() for s in docs}

    if chromadb:
        try:  # pragma: no cover - external dependency
            client = chromadb.Client()
            coll = client.get_collection(case_id)
            res = coll.query(query_texts=[query], n_results=k)
            scores: Dict[str, Dict] = {}
            ids = res.get("ids", [[]])[0]
            dists = res.get("distances", [[]])[0]
            for seg_id, dist in zip(ids, dists):
                seg = lookup.get(seg_id)
                if seg:
                    scores[seg_id] = {"segment": seg, "dense": float(dist)}
            if scores:
                return scores
        except Exception as exc:
            logger.exception("vector candidate retrieval failed", exc_info=exc)

    # Fallback token frequency approach
    q_tokens = query.lower().split()
    scores: Dict[str, Dict] = {}
    for seg in lookup.values():
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
    3. **Cross‑encoder/LLM re‑ranking** – merge candidates by ``segment_id``
       and compute a combined ``hybrid`` score incorporating the cross
       encoder or an LLM scoring model when available.
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

    cross_scores: List[float]
    if CROSS_ENCODER and merged:
        try:  # pragma: no cover - external dependency
            pairs = [(query, info["segment"].text) for info in merged.values()]
            cross_scores = list(CROSS_ENCODER.predict(pairs))
        except Exception:
            cross_scores = [0.0] * len(merged)
    elif _openai_client and LLM_SCORER_MODEL and merged:
        cross_scores = []
        for info in merged.values():
            try:  # pragma: no cover - network path
                prompt = (
                    "Rate the relevance of the passage to the query on a 0-1 scale.\n"
                    f"Query: {query}\nPassage: {info['segment'].text}\nScore:"
                )
                resp = _openai_client.responses.create(
                    model=LLM_SCORER_MODEL,
                    input=prompt,
                    temperature=0,
                )
                out = resp.output[0].content[0].text  # type: ignore[index]
                cross_scores.append(float(out.strip()))
            except Exception:
                cross_scores.append(0.0)
    else:
        cross_scores = [0.0] * len(merged)

    results = []
    token_set = set(q_tokens)
    for (seg_id, info), cross_score in zip(merged.items(), cross_scores):
        seg = info["segment"]
        graph_score = info.get("graph", 0)
        dense_score = info.get("dense", 0)
        cross_score = float(cross_score)
        hybrid_score = graph_score + dense_score + cross_score
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
                    "cross": cross_score,
                    "hybrid": hybrid_score,
                },
            }
        )

    results.sort(key=lambda r: r["scores"]["hybrid"], reverse=True)
    trace_id = hashlib.sha1(query.encode()).hexdigest()
    return {"answer": "", "items": results[:k], "trace_id": trace_id}
