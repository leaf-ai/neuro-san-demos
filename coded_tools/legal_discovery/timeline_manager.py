import json
import re
from datetime import datetime

from flask import render_template_string
from neuro_san.interfaces.coded_tool import CodedTool


class TimelineManager(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timelines = {}

    def create_timeline(self, timeline_id: str, timeline_items: list):
        """
        Creates a new timeline.

        :param timeline_id: A unique ID for the timeline.
        :param timeline_items: A list of items to add to the timeline.
        """
        self.timelines[timeline_id] = timeline_items

    def get_timeline_items(self, timeline_id: str) -> list:
        """
        Retrieves the items for a given timeline.

        :param timeline_id: The ID of the timeline to retrieve.
        :return: A list of timeline items.
        """
        return self.timelines.get(timeline_id, [])

    def add_timeline_item(self, timeline_id: str, item: dict):
        """
        Adds an item to a timeline.

        :param timeline_id: The ID of the timeline to add the item to.
        :param item: The item to add to the timeline.
        """
        if timeline_id not in self.timelines:
            self.timelines[timeline_id] = []
        self.timelines[timeline_id].append(item)

    def render_timeline(self, timeline_items: list) -> str:
        """
        Renders a timeline as an HTML page.

        :param timeline_items: A list of items to render in the timeline.
        :return: The rendered HTML.
        """
        with open("apps/legal_discovery/templates/timeline.html") as f:
            template_str = f.read()
        return render_template_string(template_str, timeline_items=timeline_items)

    def get_timeline(self, case_id: str) -> list:
        """Retrieve timeline events for a case from the database."""
        try:
            from apps.legal_discovery.models import TimelineEvent
        except Exception:  # pragma: no cover - optional DB dependency
            return []

        events = TimelineEvent.query.filter_by(case_id=case_id).order_by(TimelineEvent.event_date).all()
        result = []
        for event in events:
            result.append(
                {
                    "id": event.id,
                    "date": event.event_date.isoformat(),
                    "description": event.description,
                    "links": event.links or {},
                }
            )
        return result

    def upsert_event_from_text(self, text: str, case_id: int = 1):
        """Parse chat text and upsert a timeline event.

        Expected format: "YYYY-MM-DD description [dep:ID] [ex:ID] [theory:ID]".
        A prefix like "case:ID" may specify the case.
        """
        if m := re.match(r"case:(\d+)\s+(.*)", text.strip(), re.I):
            case_id = int(m.group(1))
            text = m.group(2)
        m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(.*)", text.strip())
        if not m:
            return None
        date_str, rest = m.groups()
        try:
            date = datetime.fromisoformat(date_str)
        except ValueError:
            return None
        links = {"depositions": [], "exhibits": [], "legal_theories": []}
        for kind, val in re.findall(r"\[(dep|ex|theory):(\d+)\]", rest, re.I):
            if kind.lower() == "dep":
                links["depositions"].append(int(val))
            elif kind.lower() == "ex":
                links["exhibits"].append(int(val))
            else:
                links["legal_theories"].append(int(val))
        description = re.sub(r"\[(dep|ex|theory):(\d+)\]", "", rest).strip()
        try:
            from apps.legal_discovery.models import TimelineEvent, db
        except Exception:  # pragma: no cover
            return None
        event = (
            TimelineEvent.query.filter_by(case_id=case_id, event_date=date).first()
        )
        if event:
            event.description = description
            event.links = links
        else:
            event = TimelineEvent(
                case_id=case_id, event_date=date, description=description, links=links
            )
            db.session.add(event)
        db.session.commit()
        return {
            "id": event.id,
            "date": event.event_date.isoformat(),
            "description": event.description,
            "links": event.links or {},
        }

    def summarize(self, case_id: int) -> str:
        """Return a simple string summary of timeline events."""
        try:
            from apps.legal_discovery.models import TimelineEvent
        except Exception:  # pragma: no cover
            return ""
        events = (
            TimelineEvent.query.filter_by(case_id=case_id)
            .order_by(TimelineEvent.event_date)
            .all()
        )
        return "; ".join(
            f"{e.event_date.date()}: {e.description}" for e in events
        )
