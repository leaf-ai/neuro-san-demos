from typing import Dict, List

from apps.legal_discovery.hippo import (
    _segment_hash,
    chunk_text,
    make_doc_id,
    upsert_document_and_segments,
    upsert_graph,
)


def test_entity_extractor_typing_accepts_list_and_dict():
    doc_id = make_doc_id("case", "path.txt")
    text = "Alice met Bob."

    def list_extractor(t: str) -> List[str]:
        return ["alice", "bob"]

    segs = chunk_text(text, doc_id, entity_extractor=list_extractor)
    assert segs[0].entities == ["alice", "bob"]
    assert segs[0].facts == []

    def dict_extractor(t: str) -> Dict[str, object]:
        return {"entities": ["carol"], "facts": [("k", "s", "o")]}  # type: ignore[arg-type]

    segs2 = chunk_text(text, doc_id, entity_extractor=dict_extractor)
    assert segs2[0].entities == ["carol"]
    assert segs2[0].facts == [("k", "s", "o")]


def test_segment_hashing_deterministic_and_unique():
    h1 = _segment_hash("some text")
    h2 = _segment_hash("some text")
    h3 = _segment_hash("other text")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 16


def test_chunk_text_segment_ids_deterministic():
    doc_id = make_doc_id("case", "doc.txt")
    text = "foo bar baz"
    segs1 = chunk_text(text, doc_id)
    segs2 = chunk_text(text, doc_id)
    assert [s.segment_id for s in segs1] == [s.segment_id for s in segs2]


def test_upsert_document_and_segments_idempotent():
    segs = [
        {"hash": "h1", "text": "seg", "page": 1, "para": 0, "entities": [], "facts": []}
    ]
    cypher1, params1 = upsert_document_and_segments("d1", "c1", "p.txt", segs)
    cypher2, params2 = upsert_document_and_segments("d1", "c1", "p.txt", segs)
    assert cypher1 == cypher2
    assert params1 == params2
    assert "MERGE (d:Document" in cypher1
    assert "MERGE (s:Segment" in cypher1


def test_upsert_graph_returns_expected_cypher_and_params():
    edges = [
        {"src": "h1", "dst": "h2", "type": "REL", "weight": 0.5},
        {"src": "h2", "dst": "h3", "type": "CITES", "weight": 1.0},
    ]
    cypher, params = upsert_graph(edges)
    expected_cypher = "\n".join(
        [
            "UNWIND $edges AS edge",
            "MATCH (s:Segment {hash: edge.src})",
            "MATCH (t:Segment {hash: edge.dst})",
            "MERGE (s)-[r:EDGE {type: edge.type}]->(t)",
            "SET r.weight=edge.weight",
        ]
    )
    assert cypher == expected_cypher
    assert params == {"edges": edges}
    assert "MATCH (s:Segment {hash: edge.src})" in cypher
    assert "MERGE (s)-[r:EDGE {type: edge.type}]->(t)" in cypher
