import json

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
