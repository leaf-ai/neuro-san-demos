import networkx as nx
from neuro_san.interfaces.coded_tool import CodedTool
from .knowledge_graph_manager import KnowledgeGraphManager


class GraphAnalyzer(CodedTool):
    """Analyze relationships in the knowledge graph."""

    def analyze_centrality(self, subnet: str | None = None) -> list[dict]:
        kg = KnowledgeGraphManager()
        nodes, edges = kg.get_subgraph(subnet or "*")
        kg.close()

        graph = nx.DiGraph()
        for n in nodes:
            graph.add_node(n["id"], label=n.get("labels", [""])[0])
        for e in edges:
            graph.add_edge(e["source"], e["target"], type=e.get("type"))

        centrality = nx.degree_centrality(graph)
        ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{"id": nid, "score": round(score, 3)} for nid, score in ranked]
