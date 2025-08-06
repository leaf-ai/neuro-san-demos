"""Tests for linking facts to elements and scoring causes of action."""

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
        self.assertEqual(node["name"], properties["name"])
        self.assertEqual(node["value"], properties["value"])

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

    def test_linking_and_cause_subgraph(self):
        try:
            doc_id = self.kg_manager.create_node("Document", {"name": "Doc"})
            fact_id = self.kg_manager.create_node("Fact", {"text": "A fact"})
        except RuntimeError as exc:
            self.skipTest(str(exc))

        self.kg_manager.link_fact_to_element(fact_id, "Fraud", "Misrepresentation", weight=0.7)
        self.kg_manager.link_document_dispute(fact_id, doc_id)
        self.kg_manager.link_fact_origin(fact_id, "Email", "Email1")
        nodes, edges = self.kg_manager.get_cause_subgraph("Fraud")
        labels = {tuple(n["labels"]) for n in nodes}
        self.assertIn(("CauseOfAction",), labels)
        edge_types = {e["type"] for e in edges}
        self.assertIn("SUPPORTS", edge_types)
        self.assertIn("BELONGS_TO", edge_types)
        self.assertIn("DISPUTED_BY", edge_types)
        self.assertIn("ORIGINATED_IN", edge_types)
        support_edge = next(e for e in edges if e["type"] == "SUPPORTS")
        self.assertAlmostEqual(support_edge.get("properties", {}).get("weight"), 0.7)
        self.kg_manager.delete_node(fact_id)
        self.kg_manager.delete_node(doc_id)
        self.kg_manager.run_query("MATCH (n:Email {name:'Email1'}) DETACH DELETE n")
        self.kg_manager.run_query("MATCH (n:Element {name:'Misrepresentation'}) DETACH DELETE n")
        self.kg_manager.run_query("MATCH (n:CauseOfAction {name:'Fraud'}) DETACH DELETE n")

    def test_cause_support_scores(self):
        try:
            cause_id = self.kg_manager.create_node("CauseOfAction", {"name": "Negligence"})
            element_id = self.kg_manager.create_node("Element", {"name": "Duty"})
            self.kg_manager.create_relationship(element_id, cause_id, "BELONGS_TO")
            fact_id = self.kg_manager.create_node("Fact", {"text": "There was a duty"})
            self.kg_manager.relate_fact_to_element(fact_id, element_id)
            scores = self.kg_manager.cause_support_scores()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        negligence = next(s for s in scores if s["cause"] == "Negligence")
        self.assertEqual(negligence["total_elements"], 1)
        self.assertEqual(negligence["satisfied_elements"], 1)
        self.assertEqual(negligence["confidence"], 1.0)
        self.kg_manager.delete_node(fact_id)
        self.kg_manager.delete_node(element_id)
        self.kg_manager.delete_node(cause_id)

    def test_fact_relationship_with_weight(self):
        try:
            a_id = self.kg_manager.create_node("Fact", {"text": "A"})
            b_id = self.kg_manager.create_node("Fact", {"text": "B"})
        except RuntimeError as exc:
            self.skipTest(str(exc))

        self.kg_manager.relate_facts(a_id, b_id, relation="CONTRADICTS", weight=0.4)
        rel = self.kg_manager.run_query(
            "MATCH (a:Fact)-[r:CONTRADICTS]->(b:Fact) WHERE id(a)=$a AND id(b)=$b RETURN r.weight AS w",
            {"a": a_id, "b": b_id},
        )
        self.assertAlmostEqual(rel[0]["w"], 0.4)
        self.kg_manager.delete_node(a_id)
        self.kg_manager.delete_node(b_id)


