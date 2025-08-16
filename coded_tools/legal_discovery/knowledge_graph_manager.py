import os
import time

import logging

from neo4j import GraphDatabase
try:  # pragma: no cover - allows tests without neo4j package
    from neo4j.exceptions import AuthError, ServiceUnavailable
except Exception:  # pragma: no cover - fallback when exceptions module missing
    AuthError = ServiceUnavailable = Exception
from neuro_san.interfaces.coded_tool import CodedTool
from pyvis.network import Network


class KnowledgeGraphManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD")
        db = os.environ.get("NEO4J_DATABASE", "neo4j")

        self.database = db
        auth = (user, pwd) if pwd else None
        try:
            self.driver = GraphDatabase.driver(
                uri,
                auth=auth,
                max_connection_lifetime=60,
                connection_timeout=10,
                max_connection_pool_size=50,
                keep_alive=True,
            )
            self._verify_with_backoff()
        except Exception as exc:  # pragma: no cover - network path
            logging.warning("Neo4j unavailable: %s", exc)
            self.driver = None

    def _verify_with_backoff(self, attempts: int = 5, base_sleep: float = 0.5) -> None:
        for i in range(attempts):
            try:
                with self.driver.session(database=self.database) as s:
                    s.run("RETURN 1").consume()
                return
            except (ServiceUnavailable, AuthError) as exc:
                if i == attempts - 1:
                    raise RuntimeError(f"Neo4j connectivity/auth failed: {exc}") from exc
                time.sleep(base_sleep * (2**i))

    def close(self):
        if self.driver:
            self.driver.close()

    def run_query(self, query: str, params: dict | None = None) -> list[dict]:
        """Run a Cypher query and return all records as dictionaries."""
        if not self.driver:
            raise RuntimeError("Neo4j driver unavailable")
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, params or {})
                return [r.data() for r in result]
        except Exception as exc:  # pragma: no cover - driver errors can vary
            raise RuntimeError("Neo4j query failed") from exc

    def create_node(self, label: str, properties: dict) -> int:
        """
        Creates a new node in the knowledge graph.

        :param label: The label for the new node.
        :param properties: A dictionary of properties for the new node.
        :return: The ID of the newly created node.
        """
        query = f"CREATE (n:{label} $props) RETURN id(n) AS id"
        return self.run_query(query, {"props": properties})[0]["id"]

    def create_relationship(
        self, start_node_id: int, end_node_id: int, relationship_type: str, properties: dict = None
    ):
        """
        Creates a new relationship between two nodes in the knowledge graph.

        :param start_node_id: The ID of the start node.
        :param end_node_id: The ID of the end node.
        :param relationship_type: The type of the new relationship.
        :param properties: A dictionary of properties for the new relationship.
        """
        query = (
            f"MATCH (a) WHERE id(a)=$a "
            f"MATCH (b) WHERE id(b)=$b "
            f"CREATE (a)-[r:{relationship_type} $props]->(b) RETURN id(r) AS id"
        )
        return self.run_query(
            query,
            {"a": start_node_id, "b": end_node_id, "props": properties or {}},
        )[0]["id"]

    def add_fact(self, case_node_id: int, document_node_id: int, fact: dict) -> int:
        """Create a Fact node and link it to case and document nodes."""
        fact_props = {
            "text": fact.get("text", ""),
            "parties": fact.get("parties", []),
            "dates": fact.get("dates", []),
            "actions": fact.get("actions", []),
        }
        fact_id = self.create_node("Fact", fact_props)
        if case_node_id is not None:
            self.create_relationship(case_node_id, fact_id, "HAS_FACT")
        if document_node_id is not None:
            self.create_relationship(document_node_id, fact_id, "HAS_FACT")
        return fact_id

    def _get_or_create_by_name(self, label: str, name: str) -> int:
        """Return the ID of a node with the given name, creating it if needed."""
        query = f"MATCH (n:{label} {{name: $name}}) RETURN id(n) as id"
        result = self.run_query(query, {"name": name})
        if result:
            return result[0]["id"]
        return self.create_node(label, {"name": name})

    def add_legal_reference(
        self,
        category: str,
        title: str,
        text: str,
        url: str,
        retrieved_at: str,
        theories: list[str] | None = None,
    ) -> int:
        """Create a ``LegalReference`` node and link to theories and timeline."""

        ref_props = {
            "category": category,
            "title": title,
            "text": text,
            "url": url,
            "retrieved_at": retrieved_at,
        }
        ref_id = self.create_node("LegalReference", ref_props)
        # Link to timeline
        timeline_id = self.create_node(
            "TimelineEvent", {"date": retrieved_at, "description": title}
        )
        self.create_relationship(ref_id, timeline_id, "OCCURRED_ON")
        # Link to legal theories
        for theory in theories or []:
            theory_id = self._get_or_create_by_name("LegalTheory", theory)
            self.create_relationship(ref_id, theory_id, "RELATES_TO")
        return ref_id

    def search_legal_references(self, query: str) -> list[dict]:
        """Simple full-text search over legal references."""
        cypher = (
            "MATCH (r:LegalReference) "
            "WHERE toLower(r.text) CONTAINS toLower($q) "
            "OR toLower(r.title) CONTAINS toLower($q) "
            "RETURN r.category AS category, r.title AS title, r.url AS url, r.retrieved_at AS retrieved_at"
        )
        return [dict(record) for record in self.run_query(cypher, {"q": query})]

    def link_fact_to_element(
        self,
        fact_id: int,
        cause: str,
        element: str,
        weight: float | None = None,
        relation: str = "SUPPORTS",
    ) -> None:
        """Link an existing fact to an element and cause of action.

        Parameters
        ----------
        fact_id:
            ID of the ``Fact`` node.
        cause:
            Name of the cause of action.
        element:
            Name of the element to link.
        weight:
            Optional confidence weight stored on the relationship.
        relation:
            Relationship type, either ``SUPPORTS`` or ``CONTRADICTS``.

        The method ensures the ``Element`` is connected to the
        ``CauseOfAction`` via ``BELONGS_TO`` and then creates the specified
        relationship from the fact to the element with the provided weight.
        """

        relation = relation.upper()
        if relation not in {"SUPPORTS", "CONTRADICTS"}:
            raise ValueError("relation must be SUPPORTS or CONTRADICTS")

        cause_id = self._get_or_create_by_name("CauseOfAction", cause)
        element_id = self._get_or_create_by_name("Element", element)
        self.create_relationship(element_id, cause_id, "BELONGS_TO")
        props = {"weight": weight} if weight is not None else None
        self.create_relationship(fact_id, element_id, relation, props)

    def relate_facts(
        self,
        source_fact_id: int,
        target_fact_id: int,
        relation: str = "SUPPORTS",
        weight: float | None = None,
    ) -> None:
        """Create a relationship between two existing ``Fact`` nodes."""

        relation = relation.upper()
        if relation not in {"SUPPORTS", "CONTRADICTS"}:
            raise ValueError("relation must be SUPPORTS or CONTRADICTS")
        props = {"weight": weight} if weight is not None else None
        self.create_relationship(source_fact_id, target_fact_id, relation, props)

    def link_document_dispute(self, fact_id: int, document_node_id: int) -> None:
        """Link a fact to a document that disputes it."""
        self.create_relationship(fact_id, document_node_id, "DISPUTED_BY")

    def link_fact_origin(self, fact_id: int, origin_label: str, origin_name: str) -> None:
        """Link a fact to its origin source such as Deposition or Email."""
        origin_id = self._get_or_create_by_name(origin_label, origin_name)
        self.create_relationship(fact_id, origin_id, "ORIGINATED_IN")

    def relate_fact_to_element(self, fact_node_id: int, element_node_id: int) -> None:
        """Create a SUPPORTS relationship between an existing Fact and Element."""
        query = "MATCH (f:Fact), (e:Element) " "WHERE id(f) = $fid AND id(e) = $eid " "MERGE (f)-[:SUPPORTS]->(e)"
        self.run_query(query, {"fid": fact_node_id, "eid": element_node_id})

    def get_node(self, node_id: int) -> dict:
        """
        Retrieves a node from the knowledge graph.

        :param node_id: The ID of the node to retrieve.
        :return: A dictionary representing the node.
        """
        query = "MATCH (n) WHERE id(n) = $node_id RETURN n"
        result = self.run_query(query, {"node_id": node_id})
        return dict(result[0]["n"]) if result else None

    def get_relationships(self, node_id: int) -> list:
        """
        Retrieves all relationships for a given node.

        :param node_id: The ID of the node.
        :return: A list of dictionaries representing the relationships.
        """
        query = "MATCH (n)-[r]->() WHERE id(n) = $node_id RETURN r"
        result = self.run_query(query, {"node_id": node_id})
        return [dict(record["r"]) for record in result]

    def export_graph(self, output_path: str = "graph.html") -> str:
        """
        Exports the entire graph as an interactive HTML file.

        :param output_path: The path to save the HTML file to.
        :return: The path to the generated HTML file.
        """
        nodes_query = "MATCH (n) RETURN id(n) as id, labels(n) as labels, properties(n) as properties"
        nodes_result = self.run_query(nodes_query)

        relationships_query = (
            "MATCH ()-[r]->() RETURN id(startNode(r)) as source, id(endNode(r)) as target, "
            "type(r) as type, properties(r) as properties"
        )
        relationships_result = self.run_query(relationships_query)

        net = Network(notebook=True)
        for record in nodes_result:
            node_id = record["id"]
            labels = record["labels"]
            properties = record["properties"]
            title = "\\n".join([f"{k}: {v}" for k, v in properties.items()])
            net.add_node(node_id, label=labels[0], title=title)

        for record in relationships_result:
            source = record["source"]
            target = record["target"]
            rel_type = record["type"]
            properties = record["properties"]
            title = "\\n".join([f"{k}: {v}" for k, v in properties.items()])
            net.add_edge(source, target, label=rel_type, title=title)

        net.save_graph(output_path)
        return output_path

    def get_cause_subgraph(self, cause: str):
        """Retrieve nodes and edges connected to a cause of action."""
        nodes_query = (
            "MATCH (c:CauseOfAction {name:$cause}) "
            "OPTIONAL MATCH (c)<-[:BELONGS_TO]-(e:Element) "
            "OPTIONAL MATCH (e)<-[:SUPPORTS]-(f:Fact) "
            "OPTIONAL MATCH (f)-[:DISPUTED_BY]->(d:Document) "
            "OPTIONAL MATCH (f)-[:ORIGINATED_IN]->(o) "
            "WITH collect(DISTINCT c) + collect(DISTINCT e) + collect(DISTINCT f) + "
            "collect(DISTINCT d) + collect(DISTINCT o) as nodes "
            "UNWIND nodes as n RETURN DISTINCT id(n) as id, labels(n) as labels, properties(n) as properties"
        )

        edges_query = (
            "MATCH (e:Element)-[r:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
            "RETURN id(e) as source, id(c) as target, 'BELONGS_TO' as type, properties(r) as properties "
            "UNION "
            "MATCH (f:Fact)-[r:SUPPORTS]->(e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
            "RETURN id(f) as source, id(e) as target, 'SUPPORTS' as type, properties(r) as properties "
            "UNION "
            "MATCH (f:Fact)-[r:CONTRADICTS]->(e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
            "RETURN id(f) as source, id(e) as target, 'CONTRADICTS' as type, properties(r) as properties "
            "UNION "
            "MATCH (f:Fact)-[s:SUPPORTS]->(e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}), "
            "(f)-[r:DISPUTED_BY]->(d:Document) "
            "RETURN id(f) as source, id(d) as target, 'DISPUTED_BY' as type, properties(r) as properties "
            "UNION "
            "MATCH (f:Fact)-[s:SUPPORTS]->(e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}), "
            "(f)-[r:ORIGINATED_IN]->(o) "
            "RETURN id(f) as source, id(o) as target, 'ORIGINATED_IN' as type, properties(r) as properties"
        )

        nodes = [
            {
                "id": record["id"],
                "labels": record["labels"],
                "properties": record["properties"],
            }
            for record in self.run_query(nodes_query, {"cause": cause})
        ]

        edges = [
            {
                "source": record["source"],
                "target": record["target"],
                "type": record["type"],
                "properties": record.get("properties", {}),
            }
            for record in self.run_query(edges_query, {"cause": cause})
        ]

        return nodes, edges

    def cause_support_scores(self) -> list[dict]:
        """Return satisfaction counts and confidence for each cause of action."""
        query = (
            "MATCH (c:CauseOfAction)<-[:BELONGS_TO]-(e:Element) "
            "OPTIONAL MATCH (e)<-[:SUPPORTS]-(f:Fact) "
            "WITH c, e, COUNT(f) as fact_count "
            "WITH c, COUNT(DISTINCT e) as total_elements, "
            "COUNT(DISTINCT CASE WHEN fact_count > 0 THEN e END) as satisfied_elements "
            "RETURN c.name as cause, total_elements, satisfied_elements, "
            "CASE WHEN total_elements=0 THEN 0 ELSE toFloat(satisfied_elements)/total_elements END as confidence"
        )
        return [dict(record) for record in self.run_query(query)]

    def get_subgraph(self, label: str):
        """Retrieve a subgraph for nodes with a given label."""
        nodes_query = f"MATCH (n:{label}) RETURN id(n) as id, labels(n) as labels, properties(n) as properties"
        relationships_query = (
            f"MATCH (n:{label})-[r]->(m) RETURN id(startNode(r)) as source, id(endNode(r)) as target, type(r) as type"
        )

        nodes = [
            {
                "id": record["id"],
                "labels": record["labels"],
                "properties": record["properties"],
            }
            for record in self.run_query(nodes_query)
        ]

        edges = [
            {
                "source": record["source"],
                "target": record["target"],
                "type": record["type"],
            }
            for record in self.run_query(relationships_query)
        ]

        return nodes, edges

    def delete_node(self, node_id: int) -> None:
        """Delete a node and any attached relationships."""
        query = "MATCH (n) WHERE id(n) = $node_id DETACH DELETE n"
        self.run_query(query, {"node_id": node_id})

    def delete_relationship(self, start_node_id: int, end_node_id: int, relationship_type: str) -> None:
        """Delete a specific relationship between two nodes."""
        query = ("MATCH (a)-[r:{rtype}]->(b) " "WHERE id(a) = $start AND id(b) = $end DELETE r").format(
            rtype=relationship_type
        )
        self.run_query(query, {"start": start_node_id, "end": end_node_id})
