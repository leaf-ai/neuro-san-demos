import os

import requests
from bs4 import BeautifulSoup
from neuro_san.interfaces.coded_tool import CodedTool


class WebScraper(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.california_codes_url = os.environ.get("CALIFORNIA_CODES_URL")

    def scrape_california_codes(self, query: str) -> str:
        """
        Scrapes the California Codes website for a given query.

        :param query: The search query.
        :return: The text content of the search results.
        """
        if not self.california_codes_url:
            return "California Codes URL not configured."

        # This is a simplified example. A real implementation would need to handle the search form submission.
        url = f"{self.california_codes_url}/search/codes.xhtml?query={query}"
        return self.scrape_website(url)

    def scrape_website(self, url: str) -> str:
        """
        Scrapes a website and returns the text content.

        :param url: The URL of the website to scrape.
        :return: The text content of the website.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            return soup.get_text()
        except Exception as e:
            return f"Error scraping website '{url}': {e}"

    def scrape_sitemap(self, url: str) -> list:
        """
        Scrapes a sitemap and returns a list of URLs.

        :param url: The URL of the sitemap.
        :return: A list of URLs found in the sitemap.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
            urls = [loc.text for loc in soup.find_all("loc")]
            return urls
        except Exception as e:
            return f"Error scraping sitemap '{url}': {e}"
