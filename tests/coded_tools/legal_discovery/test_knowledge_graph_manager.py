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
        self.kg_manager.run_query("MATCH (n) WHERE id(n) = $node_id DETACH DELETE n", {"node_id": node_id})

if __name__ == '__main__':
    unittest.main()
