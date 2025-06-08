import logging
import os
from typing import Any
from typing import Dict
from typing import Union

import requests
from neuro_san.interfaces.coded_tool import CodedTool


class BraveSearch(CodedTool):
    """
    CodedTool implementation which provides a way to search the web using Brave search API
    For info on Brave search, and to get a Brave search API key, go to https://brave.com/search/api/
    """

    def __init__(self):
        self.top_n = 5
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        if self.brave_api_key is None:
            logging.error("BRAVE_API_KEY is not set!")
        self.brave_url = os.getenv("BRAVE_URL", "https://api.search.brave.com/res/v1/web/search?q=")
        self.brave_timeout = os.getenv("BRAVE_TIMEOUT", "30")

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent.  This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "app_name" the name of the One Cognizant app for which the URL is needed.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

                This dictionary is largely to be treated as read-only.
                It is possible to add key/value pairs to this dict that do not
                yet exist as a bulletin board, as long as the responsibility
                for which coded_tool publishes new entries is well understood
                by the agent chain implementation and the coded_tool implementation
                adding the data is not invoke()-ed more than once.

                Keys expected for this implementation are:
                    None

        :return:
            In case of successful execution:
                The URL to the app as a string.
            otherwise:
                a text string an error message in the format:
                "Error: <error message>"
        """
        search_terms: str = args.get("search_terms", "")
        if search_terms == "":
            return "Error: No search terms provided."

        logger = logging.getLogger(self.__class__.__name__)
        logger.info(">>>>>>>>>>>>>>>>>>>BraveSearch>>>>>>>>>>>>>>>>>>")
        logger.info("BraveSearch Terms: %s", str(search_terms))
        results = self.brave_search(search_terms, self.top_n)

        links_str = ""
        index = 1
        for result in results.get("web", {}).get("results", []):
            the_link = result.get("url")
            links_str += f"{index}. {the_link} ; "
            logger.info("%s. %s", str(index), str(the_link))
            index += 1

        return links_str

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return self.invoke(args, sly_data)

    def brave_search(self, query: str, num_results: int = 5) -> list:
        """
        Search the web for a given query using Brave Search API
        and return a list of result URLs.

        :param query: The search query (e.g., "10.5 white men sneakers").
        :param num_results: Number of links to retrieve (default=5).
        :return: List of hyperlink strings.
        """
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.brave_api_key,
        }

        url = self.brave_url + f"{query}&count={num_results}"
        response = requests.get(url, headers=headers, timeout=int(self.brave_timeout))
        results = response.json()
        return results
