import os
import json
import logging
from typing import Dict, List, Tuple, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk import sent_tokenize
import tiktoken

from neuro_san.interfaces.coded_tool import CodedTool

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    import nltk
    nltk.download('punkt', quiet=True)
except Exception as e:
    logger.error(f"Failed to download NLTK data: {e}")

class SentimentAnalysis(CodedTool):
    """
    A CodedTool that analyzes sentiment for sentences containing specific keywords
    across text files stored in a predefined directory.
    """

    def safe_any(self, iterable) -> bool:
        try:
            return any(iterable)
        except NameError as e:
            logger.error(f"NameError for 'any': {e}. Falling back to manual iteration.")
            for item in iterable:
                if item:
                    return True
            return False

    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        try:
            tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            tokenizer = tiktoken.get_encoding("cl100k_base")
        return len(tokenizer.encode(text))
    
    def analyze_keyword_sentiment(self, text: str, keywords: List[str]) -> Tuple[List[Dict], bool]:
        try:
            sentences = sent_tokenize(text)
            results = []
            found_keywords = False

            for sentence in sentences:
                if self.safe_any(kw in sentence.lower() for kw in keywords):
                    found_keywords = True
                    scores = self.analyzer.polarity_scores(sentence)
                    results.append({
                        "sentence": sentence,
                        "compound": scores["compound"],
                        "positive": scores["pos"],
                        "negative": scores["neg"],
                        "neutral": scores["neu"]
                    })
            return results, found_keywords
        except Exception as e:
            logger.error(f"Error analyzing keyword sentiment: {e}")
            return [], False

    def invoke(self, arguments: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        self.input_dir = os.path.abspath("all_articles_output")
        self.output_dir = os.path.abspath("sentiment_output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.analyzer = SentimentIntensityAnalyzer()
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")

        source = arguments.get("source", "all").lower()
        keywords_str = arguments.get("keywords", "")
        keywords_list = [kw.strip().lower() for kw in keywords_str.split(",") if kw.strip()]

        target_sources = None if source == "all" else {s.strip().lower() for s in source.split(",") if s.strip()}

        results = {
            "source": source,
            "total_analyzed": 0,
            "total_matched": 0,
            "articles": [],
            "avg_compound": 0.0,
            "avg_positive": 0.0,
            "avg_negative": 0.0,
            "avg_neutral": 0.0,
            "file_analytics": {}
        }

        total_compound = total_positive = total_negative = total_neutral = 0.0
        file_stats = {}

        try:
            txt_files = [f for f in os.listdir(self.input_dir) if f.endswith(".txt")]

            for file_name in txt_files:
                if file_name.startswith("aljazeera_articles"):
                    source_name = "aljazeera"
                elif file_name.startswith("guardian_articles"):
                    source_name = "guardian"
                elif file_name.startswith("nyt_articles"):
                    source_name = "nyt"
                elif file_name.startswith("all_news_articles"):
                    source_name = "all"
                else:
                    source_name = "unknown"

                if target_sources is not None and source_name.lower() not in target_sources:
                    continue

                file_path = os.path.join(self.input_dir, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        continue

                if file_name not in file_stats:
                    file_stats[file_name] = {
                        "analyzed": 0,
                        "matched": 0,
                        "compound_sum": 0.0,
                        "positive_sum": 0.0,
                        "negative_sum": 0.0,
                        "neutral_sum": 0.0,
                        "articles": []
                    }

                sentence_results, matched = self.analyze_keyword_sentiment(content, keywords_list)
                results["total_analyzed"] += 1
                file_stats[file_name]["analyzed"] += 1

                if matched:
                    snippet = content[:200] + ("..." if len(content) > 200 else "")
                    avg_scores = {
                        "avg_compound": sum(r["compound"] for r in sentence_results) / len(sentence_results),
                        "avg_positive": sum(r["positive"] for r in sentence_results) / len(sentence_results),
                        "avg_negative": sum(r["negative"] for r in sentence_results) / len(sentence_results),
                        "avg_neutral": sum(r["neutral"] for r in sentence_results) / len(sentence_results)
                    }

                    article_data = {
                        "file": file_name,
                        "snippet": snippet,
                        "sentences": sentence_results,
                        **avg_scores
                    }

                    file_stats[file_name]["articles"].append(article_data)
                    file_stats[file_name]["matched"] += 1
                    file_stats[file_name]["compound_sum"] += avg_scores["avg_compound"]
                    file_stats[file_name]["positive_sum"] += avg_scores["avg_positive"]
                    file_stats[file_name]["negative_sum"] += avg_scores["avg_negative"]
                    file_stats[file_name]["neutral_sum"] += avg_scores["avg_neutral"]

                    if file_name != "all_news_articles.txt":
                        results["articles"].append(article_data)
                        results["total_matched"] += 1
                        total_compound += avg_scores["avg_compound"]
                        total_positive += avg_scores["avg_positive"]
                        total_negative += avg_scores["avg_negative"]
                        total_neutral += avg_scores["avg_neutral"]

            matched = results["total_matched"]
            if matched:
                results["avg_compound"] = total_compound / matched
                results["avg_positive"] = total_positive / matched
                results["avg_negative"] = total_negative / matched
                results["avg_neutral"] = total_neutral / matched

            for file_name, stats in file_stats.items():
                file_matched = stats["matched"]
                results["file_analytics"][file_name] = {
                    "total_analyzed": stats["analyzed"],
                    "total_matched": file_matched,
                    "articles_count": len(stats["articles"]),
                    "avg_compound": stats["compound_sum"] / file_matched if file_matched else 0.0,
                    "avg_positive": stats["positive_sum"] / file_matched if file_matched else 0.0,
                    "avg_negative": stats["negative_sum"] / file_matched if file_matched else 0.0,
                    "avg_neutral": stats["neutral_sum"] / file_matched if file_matched else 0.0
                }

            output_path = os.path.join(self.output_dir, f"sentiment_{source}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

            logger.info(f"Sentiment analysis saved to {output_path}")
            return {"status": "success", "output_file": output_path, **results}

        except Exception as e:
            logger.error(f"Error in processing: {e}")
            return {"status": "failed", "error": str(e)}

    async def async_invoke(self, arguments: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(arguments, sly_data)
