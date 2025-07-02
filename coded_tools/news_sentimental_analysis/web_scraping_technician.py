import requests
from newspaper import Article
from bs4 import BeautifulSoup
import os
import time
import logging
from typing import Dict, Any
import feedparser
import backoff
    

from neuro_san.interfaces.coded_tool import CodedTool

# Setup logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WebScrapingTechnician(CodedTool):
    """A class to scrape news articles from NYT, Guardian, and Al Jazeera."""

    def __init__(self):
        self.NYT_API_KEY = os.getenv("NYT_API_KEY")
        self.GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")
        self.nyt_sections = [
            "arts", "business", "climate", "education", "health", "jobs", "opinion",
            "politics", "realestate", "science", "technology", "travel", "us", "world"
        ]
        self.aljazeera_feeds = {
            "world": "https://www.aljazeera.com/xml/rss/all.xml"
        }
        logger.info("WebScrapingTechnician initialized")

    def scrape_with_bs4(self, url: str, source: str = "generic") -> str:
        try:
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.content, "html.parser")
            if source == "nyt":
                article_body = soup.find_all("section", {"name": "articleBody"})
                paragraphs = [p.get_text() for section in article_body for p in section.find_all("p")]
            else:
                article_body = soup.find("div", class_="article-body") or soup
                paragraphs = [p.get_text() for p in article_body.find_all("p")]
            return " ".join(paragraphs).strip()
        except Exception as e:
            logger.warning(f"BeautifulSoup failed for {url} ({source}): {e}")
            return ""

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.HTTPError,
        max_tries=10,
        max_time=300,
        giveup=lambda e: e.response is None or e.response.status_code != 429
    )
    def _fetch_nyt_section(self, url: str) -> Dict:
        response = requests.get(url, timeout=15)
        if response.status_code == 429:
            remaining = response.headers.get("X-Rate-Limit-Remaining")
            reset_time = response.headers.get("X-Rate-Limit-Reset")
            if remaining == "0" and reset_time:
                wait = max(0, int(reset_time) - int(time.time())) + 2
                logger.warning(f"Rate limit hit. Waiting {wait} seconds for reset.")
                time.sleep(wait)
                response = requests.get(url, timeout=15)
            elif remaining == "0":
                raise requests.exceptions.HTTPError("Daily quota exhausted", response=response)
        response.raise_for_status()
        return response.json()

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_time=30
    )
    def _fetch_aljazeera_feed(self, feed_url: str) -> Any:
        return feedparser.parse(feed_url)

    def _scrape_article(self, url: str, source: str) -> str:
        try:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text.strip()
            if not content:
                raise ValueError("Empty content")
            return content
        except Exception as e:
            logger.debug(f"Newspaper3k failed for {url}: {e}")
            return self.scrape_with_bs4(url, source)

    def scrape_nyt(self, keywords: list, save_dir: str = "nyt_articles_output") -> Dict[str, Any]:
        logger.info("NYT scraping started")
        keywords = [kw.lower() for kw in keywords]
        os.makedirs(save_dir, exist_ok=True)
        all_articles = []

        for section in self.nyt_sections:
            url = f"https://api.nytimes.com/svc/topstories/v2/{section}.json?api-key={self.NYT_API_KEY}"
            try:
                data = self._fetch_nyt_section(url)
                for article in data.get("results", []):
                    text_check = (article.get("title", "") + " " + article.get("abstract", "")).lower()
                    if any(kw in text_check for kw in keywords):
                        article_url = article.get("url")
                        content = self._scrape_article(article_url, "nyt")
                        if content:
                            all_articles.append(content.replace("\n", " "))
                        time.sleep(0.5)
                time.sleep(6)
            except Exception as e:
                logger.error(f"Error in NYT section '{section}': {e}")

        filename = os.path.join(save_dir, "nyt_articles.txt")
        with open(filename, "w", encoding="utf-8") as f:
            for article in all_articles:
                f.write(article + "\n")

        return {
            "saved_articles": len(all_articles),
            "file": filename,
            "status": "success" if all_articles else "failed"
        }

    def scrape_guardian(self, keywords: list, save_dir: str = "guardian_articles_output", page_size: int = 50) -> Dict[str, Any]:
        logger.info("Guardian scraping started")
        keywords = [kw.lower() for kw in keywords]
        
        os.makedirs(save_dir, exist_ok=True)

        all_articles = []

        for keyword in keywords:
            url = "https://content.guardianapis.com/search"
            params = {"q": keyword, "api-key": self.GUARDIAN_API_KEY, "page-size": page_size, "show-fields": "bodyText"}
            try:
                response = requests.get(url, params=params, timeout=15)
                results = response.json().get("response", {}).get("results", [])
                for article in results:
                    article_url = article.get("webUrl")
                    content = self._scrape_article(article_url, "guardian")
                    if content:
                        all_articles.append(content.replace("\n", " "))
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Guardian error for keyword '{keyword}': {e}")

        filename = os.path.join(save_dir, "guardian_articles.txt")
        with open(filename, "w", encoding="utf-8") as f:
            for article in all_articles:
                f.write(article + "\n")

        return {
            "saved_articles": len(all_articles),
            "file": filename,
            "status": "success" if all_articles else "failed"
        }

    def scrape_aljazeera(self, keywords: list, save_dir: str = "aljazeera_articles_output") -> Dict[str, Any]:
        logger.info("Al Jazeera scraping started")
        keywords = [kw.lower() for kw in keywords]
        os.makedirs(save_dir, exist_ok=True)
        all_articles = []

        for feed_name, feed_url in self.aljazeera_feeds.items():
            try:
                feed = self._fetch_aljazeera_feed(feed_url)
                for entry in feed.entries:
                    url = entry.link
                    text_check = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
                    matches_initial = any(kw in text_check for kw in keywords)
                    content = self._scrape_article(url, "aljazeera")
                    if content:
                        content_lower = content.lower()
                        if matches_initial or any(kw in content_lower for kw in keywords):
                            all_articles.append(content.replace("\n", " "))
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Al Jazeera feed '{feed_name}' error: {e}")

        filename = os.path.join(save_dir, "aljazeera_articles.txt")
        with open(filename, "w", encoding="utf-8") as f:
            for article in all_articles:
                f.write(article + "\n")

        return {
            "saved_articles": len(all_articles),
            "file": filename,
            "status": "success" if all_articles else "failed"
        }

    def scrape_all(self, keywords: list, save_dir: str = "all_articles_output") -> Dict[str, Any]:
        os.makedirs(save_dir, exist_ok=True)

        nyt_result = self.scrape_nyt(keywords, save_dir)
        guardian_result = self.scrape_guardian(keywords, save_dir)
        aljazeera_result = self.scrape_aljazeera(keywords, save_dir)

        # Combine all articles into a single file
        all_articles = []
        for result in [nyt_result, guardian_result, aljazeera_result]:
            file_path = result.get("file")
            if file_path and os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    articles = f.readlines()
                    all_articles.extend([article.strip() for article in articles if article.strip()])

        combined_filename = os.path.join(save_dir, "all_news_articles.txt")
        with open(combined_filename, "w", encoding="utf-8") as f:
            for article in all_articles:
                f.write(article + "\n")

        total_articles = len(all_articles)

        return {
            "saved_articles": total_articles,
            "nyt_file": nyt_result.get("file"),
            "guardian_file": guardian_result.get("file"),
            "aljazeera_file": aljazeera_result.get("file"),
            "combined_file": combined_filename,
            "status": "success" if total_articles else "failed"
        }

    def invoke(self, arguments: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        source = arguments.get("source", "all").lower().strip()
        keywords_str = arguments.get("keywords", "")
        keyword_list = [kw.strip().lower() for kw in keywords_str.split(",") if kw.strip()]
        save_dir = f"{source}_articles_output"

        if not keyword_list:
            return {"error": "Keywords cannot be empty"}

        if source == "nyt":
            return self.scrape_nyt(keyword_list, save_dir)
        elif source == "guardian":
            return self.scrape_guardian(keyword_list, save_dir)
        elif source == "aljazeera":
            return self.scrape_aljazeera(keyword_list, save_dir)
        elif source == "all":
            return self.scrape_all(keyword_list, save_dir)
        else:
            return {"error": f"Invalid source '{source}'. Must be one of: nyt, guardian, aljazeera, all"}

    async def async_invoke(self, arguments: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(arguments, sly_data)