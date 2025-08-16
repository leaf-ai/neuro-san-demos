
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

import asyncio
import inspect
import logging
from typing import Any
from typing import Dict
from typing import List

import requests
from langchain_community.document_loaders import WikipediaLoader
from langchain_core.documents import Document
from neuro_san.interfaces.coded_tool import CodedTool

from .base_rag import BaseRag

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WikipediaRag(CodedTool, BaseRag):
    """
    CodedTool implementation which provides a way to do RAG on Wikipedia articles.
    """

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Load Wikipedia articles based on queries, build a vector store, and run a query against it.

        :param args: Dictionary containing:
          "query": search string
          "wiki_queries": list of Wikipedia topics or a single topic string
          "lang": language code for Wikipedia articles (default is "en")
          "load_max_docs": maximum number of documents to load (default is 10)
          "doc_content_chars_max": maximum number of characters to keep in each document (default is 1000)
          "save_vector_store": boolean flag to save the vector store to a file
          "vector_store_path": relative path to this file
        
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
            or an error message.
        """
        # Extract arguments from the input dictionary
        query: str = args.get("query", "")
        wiki_queries: List[str] = args.get("wiki_queries") or []

        # Validate presence of required inputs
        if not query:
            logger.error("Missing required input: 'query' (retrieval question).")
            return "❌ Missing required input: 'query'."
        if not wiki_queries:
            logger.error("Missing required input: 'wiki_queries' (Wikipedia topics).")
            return "❌ Missing required input: 'wiki_queries' (list)."

        wikipedia_loader_params = [
            name for name in inspect.signature(WikipediaLoader.__init__).parameters if name != "self"
        ]
        loader_args: Dict[str, Any] = {k: v for k, v in args.items() if k in wikipedia_loader_params}
        loader_args["wiki_queries"] = wiki_queries

        # Save the generated vector store as a JSON file if True
        self.save_vector_store = bool(args.get("save_vector_store", False))

        # Configure the vector store path
        self.configure_vector_store_path(args.get("vector_store_path"))

        # Prepare the vector store
        vectorstore = await self.generate_vector_store(loader_args=loader_args)

        # Run the query against the vector store
        return await self.query_vectorstore(vectorstore, query)

    async def load_documents(self, loader_args: Dict[str, Any]) -> List[Document]:
        """
        Load Wikipedia articles based on provided queries.

        :param loader_args: Dictionary containing 'wiki_queries' (list of Wikipedia topics)
        :return: List of loaded Wikipedia documents
        """
        docs: List[Document] = []
        wiki_queries: List[str] = loader_args.pop("wiki_queries", [])

        for topic in wiki_queries:
            try:
                logger.info("Loading Wikipedia docs for query: '%s'", topic)

                per_topic_args = dict(loader_args)
                per_topic_args["query"] = topic

                loader = WikipediaLoader(**per_topic_args)
                loaded = await loader.aload() if hasattr(loader, "aload") else loader.load()

                docs.extend(loaded)
                logger.info("Successfully loaded %d Wikipedia docs for '%s'", len(loaded), topic)

            except ValueError as e:
                logger.error("Invalid Wikipedia query '%s': %s", topic, e)
            except requests.exceptions.RequestException as e:
                logger.error("Network error while fetching '%s': %s", topic, e)
            except asyncio.TimeoutError:
                logger.error("Timed out while loading Wikipedia docs for '%s'", topic)

        if not docs:
            logger.warning("No Wikipedia documents were loaded for the provided queries: %s", wiki_queries)

        return docs
