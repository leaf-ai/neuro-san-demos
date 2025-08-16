import unittest

from coded_tools.legal_discovery.knowledge_graph_manager import KnowledgeGraphManager


class TestLegalCrawlerIntegration(unittest.TestCase):
    def setUp(self):
        self.kg = KnowledgeGraphManager()
        if self.kg.driver is None:
            self.skipTest("Neo4j driver unavailable")

    def tearDown(self):
        self.kg.close()

    def test_add_and_search_legal_reference(self):
        ref_id = self.kg.add_legal_reference(
            category="statute",
            title="Test Statute",
            text="Example statute text about contracts",
            url="http://example.com/statute",
            retrieved_at="2025-01-01",
            theories=["Contracts"],
        )
        results = self.kg.search_legal_references("statute")
        self.assertTrue(any(r["title"] == "Test Statute" for r in results))
        self.kg.delete_node(ref_id)
        # Clean up related nodes
        self.kg.run_query(
            "MATCH (n:LegalTheory {name:$name}) DETACH DELETE n",
            {"name": "Contracts"},
        )
        self.kg.run_query(
            "MATCH (n:TimelineEvent {description:$d}) DETACH DELETE n",
            {"d": "Test Statute"},
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
