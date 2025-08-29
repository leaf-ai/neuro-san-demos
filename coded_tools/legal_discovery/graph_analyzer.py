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

    def _count_rel(self, kg: KnowledgeGraphManager, rel: str) -> int:
        rows = kg.run_query(f"MATCH ()-[r:{rel}]->() RETURN count(r) AS c", {})
        return int(rows[0]["c"]) if rows else 0

    def enrich_relationships(self) -> dict:
        """Run robust Cypher passes and return per-relationship deltas."""
        kg = KnowledgeGraphManager()
        deltas: dict[str, int] = {}

        def run_with_delta(name: str, merge_cypher: str) -> None:
            before = self._count_rel(kg, name)
            kg.run_query(merge_cypher, {}, cache=False)
            after = self._count_rel(kg, name)
            deltas[name] = max(0, after - before)

        run_with_delta(
            "RELATED_TO",
            (
                "MATCH (f1:Fact)-[:HAS_FACT]-(d1:Document), (f2:Fact)-[:HAS_FACT]-(d2:Document) "
                "WHERE id(f1) < id(f2) AND d1.case_id = d2.case_id AND any(p IN f1.parties WHERE p IN f2.parties) "
                "MERGE (f1)-[:RELATED_TO {reason:'party_cooccurrence'}]->(f2)"
            ),
        )
        run_with_delta(
            "CO_SUPPORTS",
            (
                "MATCH (f1:Fact)-[:SUPPORTS]->(e:Element)<-[:SUPPORTS]-(f2:Fact) "
                "WHERE id(f1) < id(f2) "
                "MERGE (f1)-[:CO_SUPPORTS {element:e.name}]->(f2)"
            ),
        )
        run_with_delta(
            "TEMPORALLY_NEAR",
            (
                "MATCH (f1:Fact), (f2:Fact) "
                "WHERE id(f1) < id(f2) AND any(p IN f1.parties WHERE p IN f2.parties) "
                "AND size(f1.dates) > 0 AND size(f2.dates) > 0 "
                "WITH f1, f2, date(f1.dates[0]) AS d1, date(f2.dates[0]) AS d2 "
                "WHERE abs(duration.between(d1, d2).days) <= 14 "
                "MERGE (f1)-[:TEMPORALLY_NEAR {days:abs(duration.between(d1,d2).days)}]->(f2)"
            ),
        )
        run_with_delta(
            "SAME_OCCURRENCE",
            (
                "MATCH (f1:Fact), (f2:Fact) "
                "WHERE id(f1) < id(f2) AND any(a IN f1.actions WHERE a IN f2.actions) "
                "AND any(p IN f1.parties WHERE p IN f2.parties) "
                "AND size(f1.dates) > 0 AND size(f2.dates) > 0 "
                "WITH f1, f2, date(f1.dates[0]) AS d1, date(f2.dates[0]) AS d2 "
                "WHERE abs(duration.between(d1, d2).days) <= 1 "
                "MERGE (f1)-[:SAME_OCCURRENCE]->(f2)"
            ),
        )
        run_with_delta(
            "POTENTIAL_CONTRADICTION",
            (
                "MATCH (f1:Fact), (f2:Fact) "
                "WHERE id(f1) < id(f2) AND any(a IN f1.actions WHERE a IN f2.actions) "
                "AND ((toLower(f1.text) CONTAINS ' not ' OR toLower(f1.text) STARTS WITH 'no ' OR toLower(f1.text) CONTAINS ' never ') XOR "
                "     (toLower(f2.text) CONTAINS ' not ' OR toLower(f2.text) STARTS WITH 'no ' OR toLower(f2.text) CONTAINS ' never ')) "
                "MERGE (f1)-[:POTENTIAL_CONTRADICTION]->(f2)"
            ),
        )
        run_with_delta(
            "EVIDENCES",
            (
                "MATCH (f:Fact),(t:TimelineEvent) WHERE size(f.dates) > 0 AND exists(t.date) "
                "WITH f, t, date(f.dates[0]) AS df, date(t.date) AS dt "
                "WHERE abs(duration.between(df, dt).days) <= 3 "
                "MERGE (f)-[:EVIDENCES]->(t)"
            ),
        )
        kg.close()
        return deltas

    def analyze_timeline_paths(self) -> dict:
        kg = KnowledgeGraphManager()
        out: dict = {}
        try:
            rows = kg.run_query(
                "MATCH p=(f:Fact)-[:SUPPORTS]->(:Element)-[:BELONGS_TO]->(:CauseOfAction) RETURN count(p) AS c"
            )
            out["fact_to_cause_paths"] = int(rows[0]["c"]) if rows else 0
        except Exception:
            out["fact_to_cause_paths"] = 0
        finally:
            kg.close()
        return out
