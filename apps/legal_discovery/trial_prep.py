"""Trial Prep Academy core modules."""
from __future__ import annotations

import hashlib
import logging
import os
import textwrap
from dataclasses import dataclass
from typing import Iterable, List

import chromadb
import requests
import spacy
from spacy.cli import download as spacy_download
from bs4 import BeautifulSoup
from chromadb.config import Settings
from neo4j import GraphDatabase

from .database import db
from .models import LegalResource, Lesson, LessonProgress


def _load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:  # pragma: no cover - environment specific
        spacy_download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


@dataclass
class CandidateResource:
    """Simple container used by the scout and quality gate."""

    url: str
    title: str | None = None
    jurisdiction: str | None = None


class ResourceScout:
    """Scans configured feeds for candidate legal materials."""

    def __init__(self, feeds: Iterable[str] | None = None) -> None:
        self.feeds = list(
            feeds
            or [
                "https://www.courts.ca.gov/opinions-slip.htm",
                "https://www.justice.gov/usao/resources",
            ]
        )

    def scan(self) -> List[CandidateResource]:
        candidates: List[CandidateResource] = []
        for feed in self.feeds:
            try:
                resp = requests.get(feed, timeout=10)
                resp.raise_for_status()
            except Exception as exc:  # pragma: no cover - network failures
                logging.warning("feed %s unreachable: %s", feed, exc)
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = requests.compat.urljoin(feed, link["href"])
                if href.lower().endswith((".pdf", ".html", ".htm")):
                    candidates.append(CandidateResource(url=href, title=link.text.strip()))
        return candidates


class ResourceScraper:
    """Fetch and parse legal resources into raw text."""

    def fetch(self, url: str) -> str:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "pdf" in content_type or url.lower().endswith(".pdf"):
            return self._parse_pdf(resp.content)
        return self._parse_html(resp.text)

    @staticmethod
    def _parse_pdf(data: bytes) -> str:
        import fitz  # PyMuPDF

        text = []
        with fitz.open(stream=data, filetype="pdf") as doc:
            for page in doc:
                text.append(page.get_text())
        return "\n".join(text)

    @staticmethod
    def _parse_html(text: str) -> str:
        soup = BeautifulSoup(text, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(" ")


class QualityGate:
    """Scores resources to determine indexing suitability."""

    KEYWORDS = ["evidence", "motion", "trial", "rule"]

    def score(self, text: str, jurisdiction: str | None = None) -> float:
        score = 0.0
        lowered = text.lower()
        for kw in self.KEYWORDS:
            if kw in lowered:
                score += 1
        if jurisdiction and jurisdiction.lower() in lowered:
            score += 1
        return score / (len(self.KEYWORDS) + 1)

    def passes(self, score: float) -> bool:
        return score >= 0.2


class KnowledgeBase:
    """Stores resource embeddings using ChromaDB with an in-memory fallback."""

    def __init__(self) -> None:
        self.nlp = _load_spacy_model()
        try:
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
            self.collection = self.client.get_or_create_collection("trial_prep_resources")
            self.use_chroma = True
        except Exception:  # pragma: no cover - environment specific
            self.client = None
            self.collection = {}
            self.use_chroma = False

    def index(self, resource: LegalResource) -> None:
        doc = self.nlp(resource.content)
        if self.use_chroma:
            self.collection.add(
                ids=[str(resource.id)],
                embeddings=[doc.vector.tolist()],
                documents=[resource.content],
                metadatas=[{"title": resource.title}],
            )
        else:
            self.collection[str(resource.id)] = doc.vector

    def search(self, query: str, limit: int = 5) -> List[int]:
        doc = self.nlp(query)
        if self.use_chroma:
            result = self.collection.query(query_embeddings=[doc.vector.tolist()], n_results=limit)
            return [int(rid) for rid in result.get("ids", [[]])[0]]
        import numpy as np

        q = doc.vector
        scores = []
        for rid, vec in self.collection.items():
            denom = float(np.linalg.norm(q) * np.linalg.norm(vec)) or 1.0
            scores.append((rid, float(np.dot(q, vec) / denom)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [int(rid) for rid, _ in scores[:limit]]


class GraphManager:
    """Links resources to topics and related materials in Neo4j."""

    def __init__(self, uri: str | None = None, user: str | None = None, password: str | None = None) -> None:
        uri = uri or os.environ.get("NEO4J_URL", "bolt://localhost:7687")
        user = user or os.environ.get("NEO4J_USER", "neo4j")
        password = password or os.environ.get("NEO4J_PASSWORD", "neo4jPass123")
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.session = self.driver.session()
        except Exception:  # pragma: no cover - external service
            self.driver = None
            self.session = None

    def link(self, resource: LegalResource, topic: str) -> None:
        if self.session is None:  # pragma: no cover - network path
            return
        try:
            self.session.run(
                "MERGE (r:Resource {id:$id, title:$title})"
                " MERGE (t:Topic {name:$topic})"
                " MERGE (r)-[:BELONGS_TO]->(t)",
                id=resource.id,
                title=resource.title,
                topic=topic,
            )
        except Exception:  # pragma: no cover - external service
            pass

    def close(self) -> None:
        if self.session:
            self.session.close()
        if self.driver:
            self.driver.close()


class LessonBuilder:
    """Transforms resources into lessons with summaries and quizzes."""

    def __init__(self) -> None:
        self.nlp = _load_spacy_model()

    def _summarize(self, text: str) -> str:
        summary = textwrap.shorten(text, width=400, placeholder="...")
        return summary

    def _quiz(self, text: str) -> List[dict]:
        doc = self.nlp(text)
        questions = []
        for sent in list(doc.sents)[:3]:
            words = sent.text.split()
            if len(words) < 6:
                continue
            idx = len(words) // 2
            answer = words[idx]
            question = " ".join(words[:idx] + ["____"] + words[idx + 1 :])
            questions.append({"question": question, "answer": answer})
        return questions

    def build_from_resource(self, resource: LegalResource, topic: str) -> Lesson:
        summary = self._summarize(resource.content)
        quiz = self._quiz(resource.content)
        lesson = Lesson(topic=topic, title=resource.title, resource_id=resource.id, summary=summary, quiz=quiz)
        db.session.add(lesson)
        db.session.commit()
        return lesson


class CurriculumManager:
    """CRUD operations for lessons and progress tracking."""

    def list_lessons(self, topic: str | None = None) -> List[Lesson]:
        query = Lesson.query
        if topic:
            query = query.filter_by(topic=topic)
        return query.all()

    def record_progress(
        self, lesson_id: int, completed: bool, quiz_score: float | None, thumbs_up: bool | None
    ) -> LessonProgress:
        progress = LessonProgress.query.filter_by(lesson_id=lesson_id, user_id="default").first()
        if progress is None:
            progress = LessonProgress(lesson_id=lesson_id, user_id="default")
            db.session.add(progress)
        progress.completed = completed
        if quiz_score is not None:
            progress.quiz_score = float(quiz_score)
        progress.thumbs_up = thumbs_up
        db.session.commit()
        return progress


class ResourceManager:
    """Orchestrates resource acquisition and indexing."""

    def __init__(self) -> None:
        self.scout = ResourceScout()
        self.scraper = ResourceScraper()
        self.gate = QualityGate()
        self.kb = KnowledgeBase()
        self.graph = GraphManager()

    def ingest(self) -> List[LegalResource]:  # pragma: no cover - network heavy
        resources = []
        for candidate in self.scout.scan():
            try:
                text = self.scraper.fetch(candidate.url)
                score = self.gate.score(text, candidate.jurisdiction)
                if not self.gate.passes(score):
                    continue
                sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
                existing = LegalResource.query.filter_by(sha256=sha).first()
                if existing:
                    continue
                resource = LegalResource(
                    title=candidate.title or candidate.url,
                    url=candidate.url,
                    jurisdiction=candidate.jurisdiction,
                    content=text,
                    metadata_json={"score": score},
                    sha256=sha,
                )
                db.session.add(resource)
                db.session.commit()
                self.kb.index(resource)
                if candidate.jurisdiction:
                    self.graph.link(resource, candidate.jurisdiction)
                resources.append(resource)
            except Exception as exc:
                logging.warning("failed to ingest %s: %s", candidate.url, exc)
        return resources

    def add_manual_resource(self, title: str, url: str, jurisdiction: str, content: str) -> LegalResource:
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        resource = LegalResource(
            title=title,
            url=url,
            jurisdiction=jurisdiction,
            content=content,
            metadata_json={},
            sha256=sha,
        )
        db.session.add(resource)
        db.session.commit()
        self.kb.index(resource)
        if jurisdiction:
            self.graph.link(resource, jurisdiction)
        return resource

    def search(self, query: str) -> List[LegalResource]:
        ids = self.kb.search(query)
        if not ids:
            return []
        return LegalResource.query.filter(LegalResource.id.in_(ids)).all()
