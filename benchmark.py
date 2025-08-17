"""Simple benchmarking script for vector and graph queries."""
import asyncio
import time

from coded_tools.legal_discovery.vector_database_manager import VectorDatabaseManager
from coded_tools.legal_discovery.knowledge_graph_manager import KnowledgeGraphManager


async def bench_vector():
    mgr = VectorDatabaseManager()
    mgr.add_documents(["doc"], [{}], ["1"])
    start = time.time()
    for _ in range(5):
        await mgr.aquery(["doc"])
    return time.time() - start


async def bench_graph():
    mgr = KnowledgeGraphManager()
    if not mgr.driver:
        return None
    start = time.time()
    for _ in range(5):
        await mgr.arun_query("RETURN 1")
    return time.time() - start


async def main():
    v = await bench_vector()
    g = await bench_graph()
    print(f"vector: {v:.4f}s")
    if g is not None:
        print(f"graph: {g:.4f}s")
    else:
        print("graph: driver unavailable")


if __name__ == "__main__":
    asyncio.run(main())
