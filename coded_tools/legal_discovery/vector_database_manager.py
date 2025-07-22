import chromadb
from neuro_san.coded_tool import CodedTool


class VectorDatabaseManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("legal_documents")

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """
        Adds documents to the vector database.

        :param documents: A list of documents to add.
        :param metadatas: A list of metadata dictionaries corresponding to the documents.
        :param ids: A list of unique IDs for the documents.
        """
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

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
