import requests
from bs4 import BeautifulSoup

from neuro_san.coded_tool import CodedTool


class WebScraper(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
