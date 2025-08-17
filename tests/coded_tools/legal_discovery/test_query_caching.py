import asyncio
from unittest.mock import MagicMock

from coded_tools.legal_discovery.vector_database_manager import VectorDatabaseManager
from coded_tools.legal_discovery.knowledge_graph_manager import KnowledgeGraphManager


def test_vector_query_cache_invalidation():
    mgr = VectorDatabaseManager()
    mgr.collection = MagicMock()
    mgr.collection.query.return_value = {"documents": [["d"]], "metadatas": [[{}]], "ids": [["1"]]}
    mgr.collection.get.return_value = {"ids": []}
    mgr.collection.add.return_value = None

    mgr.query(["hello"])
    mgr.query(["hello"])
    assert mgr.collection.query.call_count == 1
    mgr.collection.query.reset_mock()
    mgr.add_documents(["hello"], [{}], ["1"])
    mgr.collection.query.reset_mock()
    mgr.collection.query.return_value = {"documents": [["d2"]], "metadatas": [[{}]], "ids": [["1"]]}
    mgr.query(["hello"])
    assert mgr.collection.query.call_count == 1

    asyncio.run(mgr.aquery(["hello"]))
    assert mgr.collection.query.call_count == 1


def test_graph_query_cache_invalidation():
    mgr = KnowledgeGraphManager()
    session = MagicMock()

    def make_record(data):
        rec = MagicMock()
        rec.data.return_value = data
        return rec

    session.run.side_effect = [
        [make_record({})],
        [make_record({"id": 1})],
        [make_record({})],
    ]

    driver = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    mgr.driver = driver

    mgr.run_query("MATCH (n) RETURN n")
    mgr.run_query("MATCH (n) RETURN n")
    assert session.run.call_count == 1

    mgr.create_node("Test", {"name": "a"})
    mgr.run_query("MATCH (n) RETURN n")
    assert session.run.call_count == 3

    asyncio.run(mgr.arun_query("MATCH (n) RETURN n"))
    assert session.run.call_count == 3
