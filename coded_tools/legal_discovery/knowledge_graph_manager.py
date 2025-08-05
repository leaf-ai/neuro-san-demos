import os

from neo4j import GraphDatabase
from neuro_san.interfaces.coded_tool import CodedTool
from pyvis.network import Network


class KnowledgeGraphManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verify connection
            with self.driver.session() as session:
                session.run("RETURN 1")
        except Exception as exc:  # pragma: no cover - connection may fail in tests
            raise RuntimeError(f"Failed to connect to Neo4j at {uri}. Is the server running?") from exc

    def close(self):
        self.driver.close()

    def run_query(self, query: str, parameters: dict = None) -> list:
        """
        Runs a Cypher query against the Neo4j database.

        :param query: The Cypher query to run.
        :param parameters: A dictionary of parameters for the query.
        :return: A list of records returned by the query.
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [record for record in result]
        except Exception as exc:
            raise RuntimeError("Neo4j query failed") from exc

    def create_node(self, label: str, properties: dict) -> int:
        """
        Creates a new node in the knowledge graph.

        :param label: The label for the new node.
        :param properties: A dictionary of properties for the new node.
        :return: The ID of the newly created node.
        """
        query = f"CREATE (n:{label} $props) RETURN id(n)"
        result = self.run_query(query, {"props": properties})
        return result[0][0]

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
            f"MATCH (a), (b) "
            f"WHERE id(a) = $start_node_id AND id(b) = $end_node_id "
            f"CREATE (a)-[r:{relationship_type} $props]->(b)"
        )
        self.run_query(query, {"start_node_id": start_node_id, "end_node_id": end_node_id, "props": properties or {}})

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

    def link_fact_to_element(
        self, fact_id: int, cause: str, element: str, weight: float = 1.0
    ) -> None:
        """Link an existing fact to an element and cause with a weighted relationship."""
        cause_id = self._get_or_create_by_name("CauseOfAction", cause)
        element_id = self._get_or_create_by_name("Element", element)
        self.create_relationship(element_id, cause_id, "BELONGS_TO")
        self.create_relationship(fact_id, element_id, "SUPPORTS", {"weight": weight})
    def link_fact_to_element(self, fact_id: int, cause: str, element: str) -> None:
        """Link an existing fact to an element and cause of action."""
        cause_id = self._get_or_create_by_name("CauseOfAction", cause)
        element_id = self._get_or_create_by_name("Element", element)
        self.create_relationship(element_id, cause_id, "BELONGS_TO")
        self.create_relationship(fact_id, element_id, "SUPPORTS")

    def link_document_dispute(self, fact_id: int, document_node_id: int) -> None:
        """Link a fact to a document that disputes it."""
        self.create_relationship(fact_id, document_node_id, "DISPUTED_BY")

    def link_fact_origin(self, fact_id: int, origin_label: str, origin_name: str) -> None:
        """Link a fact to its origin source such as Deposition or Email."""
        origin_id = self._get_or_create_by_name(origin_label, origin_name)
        self.create_relationship(fact_id, origin_id, "ORIGINATED_IN")

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
            "MATCH (e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
            "RETURN id(e) as source, id(c) as target, 'BELONGS_TO' as type "
            "UNION "
            "MATCH (f:Fact)-[:SUPPORTS]->(e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
            "RETURN id(f) as source, id(e) as target, 'SUPPORTS' as type "
            "UNION "
            "MATCH (f:Fact)-[:SUPPORTS]->(e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}), "
            "(f)-[:DISPUTED_BY]->(d:Document) "
            "RETURN id(f) as source, id(d) as target, 'DISPUTED_BY' as type "
            "UNION "
            "MATCH (f:Fact)-[:SUPPORTS]->(e:Element)-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}), "
            "(f)-[:ORIGINATED_IN]->(o) "
            "RETURN id(f) as source, id(o) as target, 'ORIGINATED_IN' as type"
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
            }
            for record in self.run_query(edges_query, {"cause": cause})
        ]

        return nodes, edges

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

    def delete_relationship(
        self, start_node_id: int, end_node_id: int, relationship_type: str
    ) -> None:
        """Delete a specific relationship between two nodes."""
        query = (
            "MATCH (a)-[r:{rtype}]->(b) "
            "WHERE id(a) = $start AND id(b) = $end DELETE r"
        ).format(rtype=relationship_type)
        self.run_query(query, {"start": start_node_id, "end": end_node_id})
