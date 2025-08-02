# Download the CSV file from Google Drive and save it in default folder to load it into the database.
# mkdir -p load_files
# gdown "https://drive.google.com/uc?id=10xBXPa3L0X5CAwOAkFrAg2Q9frExr9oy" -O load_files/arxiv_papers.csv
import os
import uuid
import logging
from typing import Dict, Any
import pandas as pd

from sentence_transformers import SentenceTransformer

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ArxivRAG(CodedTool):
    """
    A tool for processing documents from CSV files, embedding them using SentenceTransformer,
    and storing them in a Qdrant vector database for retrieval.
    """
    def __init__(self):
        try:
            self.model = SentenceTransformer('sentence-transformers/all-roberta-large-v1')
            self.qdrant = QdrantClient(host="localhost", port=6333)
            self.collection_name = "papers"
            self.vector_size = self.model.get_sentence_embedding_dimension()
            self._ensure_collection()
            logger.info("Initialized DocumentProcessor with Qdrant")
        except Exception as e:
            logger.error("Initialization failed: %s", e)
            raise

    def _ensure_collection(self):
        """
        Ensure that the Qdrant collection exists, creating it if necessary.
        """
        collections = [c.name for c in self.qdrant.get_collections().collections]
        if self.collection_name not in collections:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )
            logger.info("Created Qdrant collection: %s", self.collection_name)
        else:
            logger.info("Qdrant collection '%s' already exists", self.collection_name)

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Any:
        """
        Invoke the tool with the provided arguments and state data.
        :param args: Dictionary containing the action and parameters.
        :param sly_data: Additional state data, if any.
        :return: A dictionary with the status and results of the operation.
        """
        action = args.get("action")

        if action == "load_csv":
            folder_path = args.get("folder_path", os.getenv("FOLDER_PATH", "load_files/"))
            return self.load_csv(folder_path)

        if action == "query_documents":
            query = args.get("query", "")
            return self.query_documents(query)

        return {"status": "failed", "error": f"Unknown action: {action}"}

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Any:
        return self.invoke(args, sly_data)

    def load_csv(self, folder_path: str) -> Dict[str, Any]:
        """       
        Load CSV files from the specified folder, process them to create embeddings,
        and store them in the Qdrant vector database.
        :param folder_path: Path to the folder containing CSV files.
        :return: A dictionary with the status and results of the operation.
        """
        if not os.path.isdir(folder_path):
            return {"status": "failed", "error": f"Folder not found: {folder_path}"}

        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        if not csv_files:
            return {"status": "failed", "error": f"No CSV files found in: {folder_path}"}

        results = []
        for file in csv_files:
            df = pd.read_csv(os.path.join(folder_path, file))
            df = df.drop_duplicates(subset=["title", "summary"])

            if 'title' not in df.columns or 'summary' not in df.columns:
                logger.warning("Skipping %s, missing 'title' or 'summary'", file)
                continue

            points = []
            for _, row in df.iterrows():
                title, summary = row['title'], row['summary']
                if pd.isna(title) or pd.isna(summary):
                    continue
                text = f"{title} {summary}"
                embedding = self.model.encode(text)
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "title": title,
                        "summary": summary,
                        "source_file": file
                    }
                )
                points.append(point)

            for i in range(0, len(points), 100):
                self.qdrant.upsert(collection_name=self.collection_name, points=points[i:i+100])

            logger.info("Inserted %d vectors from %s", len(points), file)
            results.extend(points)

        return {
            "status": "success",
            "output": self.collection_name,
            "results": {
                "document_count": len(results),
                "documents": [p.payload for p in results[:7]]
            }
        }

    def query_documents(self, query: str, limit: int = 7) -> Dict[str, Any]:
        """
        Query the Qdrant vector database for documents similar to the provided query.
        :param query: The search query string.
        :param limit: The maximum number of results to return.
        :return: A dictionary with the status and results of the query.
        """
        if not query:
            return {"status": "failed", "error": "Empty query provided"}

        try:
            query_vector = self.model.encode(query).tolist()
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )
            return {
                "status": "success",
                "output": self.collection_name,
                "results": {
                    "document_count": len(results),
                    "documents": [
                        {
                            "title": r.payload.get("title"),
                            "summary": r.payload.get("summary"),
                            "source_file": r.payload.get("source_file"),
                            "score": r.score
                        }
                        for r in results
                    ]
                }
            }

        except ValueError as ve:
            logger.error("Value error: %s", ve)
            return {"status": "failed", "error": str(ve)}

        except ConnectionError as ce:
            logger.error("Connection error: %s", ce)
            return {"status": "failed", "error": str(ce)}
