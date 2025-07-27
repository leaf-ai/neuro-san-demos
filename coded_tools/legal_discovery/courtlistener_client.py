import os

import requests
from neuro_san.interfaces.coded_tool import CodedTool


class CourtListenerClient(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = os.environ.get("COURTLISTENER_API_KEY")
        self.base_url = "https://www.courtlistener.com/api/rest/v3"

    def search_opinions(self, query: str) -> dict:
        """
        Searches for opinions on CourtListener.

        :param query: The search query.
        :return: A dictionary containing the search results.
        """
        headers = {"Authorization": f"Token {self.api_key}"}
        params = {"q": query}
        response = requests.get(f"{self.base_url}/search/", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_opinion(self, opinion_id: int) -> dict:
        """
        Retrieves a specific opinion from CourtListener.

        :param opinion_id: The ID of the opinion to retrieve.
        :return: A dictionary containing the opinion data.
        """
        headers = {"Authorization": f"Token {self.api_key}"}
        response = requests.get(f"{self.base_url}/opinions/{opinion_id}/", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_docket(self, docket_id: int) -> dict:
        """
        Retrieves a specific docket from CourtListener.

        :param docket_id: The ID of the docket to retrieve.
        :return: A dictionary containing the docket data.
        """
        headers = {"Authorization": f"Token {self.api_key}"}
        response = requests.get(f"{self.base_url}/dockets/{docket_id}/", headers=headers)
        response.raise_for_status()
        return response.json()
