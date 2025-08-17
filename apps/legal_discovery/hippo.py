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
import re
from typing import Dict, List


# ---------------------------------------------------------------------------
# Dataclasses


@dataclass
class Segment:
    """Text segment with deterministic identifier."""

    doc_id: str
    segment_id: str
    text: str
    page: int
    para: int
    tok_start: int
    tok_end: int
    entities: List[str]


# In-memory index: {case_id: {doc_id: [Segment, ...]}}
INDEX: Dict[str, Dict[str, List[Segment]]] = {}


# ---------------------------------------------------------------------------
# Helpers


def make_doc_id(case_id: str, path: str) -> str:
    """Return a stable 128-bit hex id for a document."""

    return hashlib.sha256(f"{case_id}:{path}".encode()).hexdigest()[:32]


def _segment_hash(doc_id: str, start: int, end: int) -> int:
    h = hashlib.sha256(f"{doc_id}:{start}:{end}".encode()).hexdigest()
    # first 16 hex = 64 bits
    return int(h[:16], 16)


def chunk_text(text: str, doc_id: str, page: int = 1, tokens_per_chunk: int = 200) -> List[Segment]:
    """Deterministically split ``text`` into segments.

    Each segment id follows the ``doc_id:page:para:start-end`` pattern and a
    64-bit ``segment_hash`` is derived from these values.  Tokens are simple
    whitespace splits which is adequate for the unit tests.
    """

    tokens = text.split()
    segments: List[Segment] = []
    para = 0
    t = 0
    while t < len(tokens):
        chunk_tokens = tokens[t : t + tokens_per_chunk]
        start = t
        end = t + len(chunk_tokens)
        segment_id = f"{doc_id}:{page}:{para}:{start}-{end}"
        seg_text = " ".join(chunk_tokens)
        entities = _extract_entities(seg_text)
        segments.append(
            Segment(
                doc_id=doc_id,
                segment_id=segment_id,
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


def ingest_document(case_id: str, text: str, path: str = "") -> str:
    """Index ``text`` for ``case_id`` and return the generated ``doc_id``."""

    doc_id = make_doc_id(case_id, path or "inline")
    segments = chunk_text(text, doc_id)
    case_index = INDEX.setdefault(case_id, {})
    case_index[doc_id] = segments
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
