from neo4j import GraphDatabase

from neuro_san.coded_tool import CodedTool


class KnowledgeGraphManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

    def close(self):
        self.driver.close()

    def run_query(self, query: str, parameters: dict = None) -> list:
        """
        Runs a Cypher query against the Neo4j database.

        :param query: The Cypher query to run.
        :param parameters: A dictionary of parameters for the query.
        :return: A list of records returned by the query.
        """
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

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

    def create_relationship(self, start_node_id: int, end_node_id: int, relationship_type: str, properties: dict = None):
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
