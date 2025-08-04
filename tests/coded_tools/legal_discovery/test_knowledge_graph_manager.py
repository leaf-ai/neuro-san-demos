import unittest
from coded_tools.legal_discovery.knowledge_graph_manager import KnowledgeGraphManager

class TestKnowledgeGraphManager(unittest.TestCase):
    def setUp(self):
        try:
            self.kg_manager = KnowledgeGraphManager()
        except RuntimeError as exc:  # Neo4j not running
            self.skipTest(str(exc))

    def tearDown(self):
        self.kg_manager.close()

    def test_create_and_get_node(self):
        # Create a node
        label = "TestNode"
        properties = {"name": "Test Name", "value": 123}
        node_id = self.kg_manager.create_node(label, properties)
        self.assertIsInstance(node_id, int)

        # Get the node
        node = self.kg_manager.get_node(node_id)
        self.assertIsNotNone(node)
        self.assertEqual(node['name'], properties['name'])
        self.assertEqual(node['value'], properties['value'])

        # Clean up
        self.kg_manager.delete_node(node_id)

    def test_add_fact(self):
        doc_id = self.kg_manager.create_node("Document", {"name": "Doc"})
        case_id = self.kg_manager.create_node("Case", {"id": 1})
        fact = {
            "text": "Alice signed a contract",
            "parties": ["Alice", "Bob"],
            "dates": ["2024-05-05"],
            "actions": ["sign"],
        }
        fact_id = self.kg_manager.add_fact(case_id, doc_id, fact)
        self.assertIsInstance(fact_id, int)
        rel = self.kg_manager.run_query(
            "MATCH (d:Document)-[:HAS_FACT]->(f:Fact) WHERE id(d)=$d AND id(f)=$f RETURN f",
            {"d": doc_id, "f": fact_id},
        )
        self.assertTrue(rel)
        self.kg_manager.delete_node(fact_id)
        self.kg_manager.delete_node(doc_id)
        self.kg_manager.delete_node(case_id)

if __name__ == '__main__':
    unittest.main()
