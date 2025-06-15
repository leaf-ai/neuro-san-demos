"""Tool module for doing RAG from confluence pages"""

# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
# END COPYRIGHT

import inspect
import os
import re
from typing import Any
from typing import Dict
from typing import List

# pylint: disable=import-error
from atlassian.errors import ApiPermissionError
from langchain_community.document_loaders.confluence import ConfluenceLoader
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from neuro_san.interfaces.coded_tool import CodedTool
from requests.exceptions import HTTPError

INVALID_PATH_PATTERN = r"[<>:\"|?*\x00-\x1F]"


class ConfluenceRag(CodedTool):
    """
    CodedTool implementation which provides a way to do RAG on confluence pages
    """

    def __init__(self):
        self.save_vector_store: bool = False
        self.abs_vector_store_path: str = None

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Load confluence pages from URLs, build a vector store, and run a query against it.

        :param args: Dictionary containing:
          "query": search string

        :param sly_data: A dictionary whose keys are defined by the agent
            hierarchy, but whose values are meant to be kept out of the
            chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool implementation
            adding the data is not invoke()-ed more than once.

            Keys expected for this implementation are:
                None
        :return: Text result from querying the built vector store,
            or error message
        """
        # Extract arguments from the input dictionary
        query: str = args.get("query", "")

        # Create a list of parameters of ConfluenceLoader
        # https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.confluence.ConfluenceLoader.html
        confluence_loader_params = [
            name for name in inspect.signature(ConfluenceLoader.__init__).parameters if name != "self"
        ]

        # Filter args from the above list
        confluence_loader_args = {arg: arg_value for arg, arg_value in args.items() if arg in confluence_loader_params}

        # Check the env var for "username" and "api_key"
        confluence_loader_args.setdefault("username", os.getenv("JIRA_USERNAME"))
        confluence_loader_args.setdefault("api_key", os.getenv("JIRA_API_TOKEN"))

        # Validate presence of required inputs
        if not query:
            return "❌ Missing required input: 'query'."
        if not confluence_loader_args.get("url"):
            return (
                "❌ Missing required input: 'url'.\n" "This should look like: https://your-domain.atlassian.net/wiki/"
            )
        if not confluence_loader_args.get("space_key") and not confluence_loader_args.get("page_ids"):
            return (
                "❌ Missing both 'space_key' and 'page_ids'.\n"
                "Provide at least one to locate the Confluence content to load.\n"
                "- 'space_key' is the identifier of the Confluence space (e.g., 'DAI').\n"
                "- 'page_ids' should be a list of page IDs you want to load, e.g., ['123456', '7891011'].\n\n"
                "Tip: You can find these values in a page URL like:\n"
                "https://your-domain.atlassian.net/wiki/spaces/<space_key>/pages/<page_id>/<title>"
            )

        # Save the generated vector store as a JSON file if True
        self.save_vector_store = args.get("save_vector_store", False)

        vector_store_path: str = args.get("vector_store_path", "")

        if vector_store_path:
            # Check for obviously invalid characters in filenames (basic check)
            if re.search(INVALID_PATH_PATTERN, vector_store_path):
                raise ValueError(f"Invalid vector_store_path: '{vector_store_path}'")

            # Check file extension
            if not vector_store_path.endswith(".json"):
                raise ValueError(f"vector_store_path must be a .json file, got: '{vector_store_path}'")

            if os.path.isabs(vector_store_path):
                # It's already an absolute path — use it directly
                self.abs_vector_store_path = vector_store_path
            else:
                # Combine to relative path to base path to make absolute path
                base_path: str = os.path.dirname(__file__)
                self.abs_vector_store_path = os.path.abspath(os.path.join(base_path, vector_store_path))

        # Build the vector store and run the query
        vectorstore: InMemoryVectorStore = await self.generate_vector_store(confluence_loader_args)
        return await self.query_vectorstore(vectorstore, query)

    async def generate_vector_store(self, confluence_loader_args: Dict[str, Any]) -> InMemoryVectorStore:
        """
        Asynchronously loads confluence documents from a given confluence URL, split them into
        chunks, and build an in-memory vector store using OpenAI embeddings
        or load vectorstore if it is available.

        :param confluence_loader_args: Dictionary of arguments for ConfluenceLoader containing a confluence URL
        :return: In-memory vector store containing the embedded document chunks
        """

        url = confluence_loader_args.get("url")

        # If vector store file path is provided (abs_vector_store_path is not None), try to load vector store first.
        if self.abs_vector_store_path:
            try:
                vectorstore = InMemoryVectorStore.load(path=self.abs_vector_store_path, embedding=OpenAIEmbeddings())
                print(f"Loaded vector store from: {self.abs_vector_store_path}")
                return vectorstore
            except FileNotFoundError:
                print(f"Vector store not found. Creating from confluence pages: {url}")

        docs: List[Document] = []
        try:
            loader = ConfluenceLoader(**confluence_loader_args)
            docs = await loader.aload()
            print(f"Successfully load confluence pages from {url}")
        except HTTPError as http_error:
            print(f"HTTP error: {http_error}")
        except ApiPermissionError as api_error:
            print(f"API Permission error: {api_error}")

        # Split documents into smaller chunks for better embedding and retrieval
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=50)
        doc_chunks: List[Document] = text_splitter.split_documents(docs)

        # Create an in-memory vector store with embeddings
        vectorstore: InMemoryVectorStore = await InMemoryVectorStore.afrom_documents(
            documents=doc_chunks,
            collection_name="rag-in-memory",
            embedding=OpenAIEmbeddings(),
        )

        if self.save_vector_store and self.abs_vector_store_path:
            os.makedirs(os.path.dirname(self.abs_vector_store_path), exist_ok=True)
            vectorstore.dump(path=self.abs_vector_store_path)
            print(f"Vector store saved to: {self.abs_vector_store_path}")

        return vectorstore

    async def query_vectorstore(self, vectorstore: InMemoryVectorStore, query: str) -> str:
        """
        Query the given vector store using the provided query string
        and return the combined content of retrieved documents.

        :param vectorstore: The in-memory vector store to query
        :param query: The user query to search for relevant documents
        :return: Concatenated text content of the retrieved documents
        """
        # Create a retriever interface from the vector store
        retriever: VectorStoreRetriever = vectorstore.as_retriever()

        # Perform an asynchronous similarity search
        results: List[Document] = await retriever.ainvoke(query)

        if results:
            print("Retrieval completed!")

        # Concatenate the content of all retrieved documents
        return "\n\n".join(doc.page_content for doc in results)
