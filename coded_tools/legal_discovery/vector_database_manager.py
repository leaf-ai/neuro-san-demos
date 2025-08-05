import logging
import os

import chromadb
from neuro_san.interfaces.coded_tool import CodedTool


class VectorDatabaseManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8000"))
        # Use the HTTP client so vector storage can reside on an external
        # Chroma service backed by PostgreSQL for concurrent access.
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection("legal_documents")

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """
        Adds documents to the vector database.

        :param documents: A list of documents to add.
        :param metadatas: A list of metadata dictionaries corresponding to the documents.
        :param ids: A list of unique IDs for the documents.
        """
        # Chroma requires a non-empty metadata dict for every document. Some
        # ingestion paths may supply missing or empty metadata, so normalise the
        # list here to guarantee valid placeholders are present. This protects
        # against `ValueError: Expected metadata to be a non-empty dict` without
        # modifying the upstream library.
        safe_docs: list[str] = []
        safe_metadatas: list[dict] = []
        safe_ids: list[str] = []

        # Pad the metadata list to match documents length if needed
        if len(metadatas) < len(documents):
            metadatas = metadatas + [{}] * (len(documents) - len(metadatas))

        for doc, md, doc_id in zip(documents, metadatas, ids):
            # Skip if ID already exists
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing and existing.get("ids"):
                    continue
            except Exception:  # pragma: no cover - best effort
                pass

            # Similarity check to avoid near-duplicates
            try:
                res = self.collection.query(query_texts=[doc], n_results=1)
                if res.get("ids") and res["ids"][0]:
                    if res.get("distances") and res["distances"][0][0] < 0.1:
                        continue
            except Exception:  # pragma: no cover - best effort
                pass

            safe_docs.append(doc)
            safe_ids.append(doc_id)
            if not isinstance(md, dict) or not md:
                safe_metadatas.append({"source": "unknown", "id": doc_id})
            else:
                cleaned = {k: v for k, v in md.items() if v}
                if cleaned:
                    safe_metadatas.append(cleaned)
                else:
                    safe_metadatas.append({"source": "unknown", "id": doc_id})

        if not safe_docs:
            return

        try:
            self.collection.add(documents=safe_docs, metadatas=safe_metadatas, ids=safe_ids)
        except ValueError as exc:
            logging.warning(
                "Vector add failed (%s); retrying with placeholder metadata", exc
            )
            fallback = [{"source": "unknown", "id": i} for i in safe_ids]
            self.collection.add(documents=safe_docs, metadatas=fallback, ids=safe_ids)

    def query(self, query_texts: list[str], n_results: int = 10) -> dict:
        """
        Queries the vector database.

        :param query_texts: A list of query texts.
        :param n_results: The number of results to return.
        :return: A dictionary containing the query results.
        """
        return self.collection.query(query_texts=query_texts, n_results=n_results)

    def get_document_count(self) -> int:
        """
        Returns the number of documents in the vector database.

        :return: The number of documents.
        """
        return self.collection.count()

    def delete_documents(self, ids: list[str]):
        """
        Deletes documents from the vector database.

        :param ids: A list of document IDs to delete.
        """
        self.collection.delete(ids=ids)
