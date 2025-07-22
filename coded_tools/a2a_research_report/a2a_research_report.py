"""
Example of how to use coded tool as a2a client.

Before running this coded tool
- cloning the repo from https://github.com/google/a2a-python/tree/main
- pip install .
- run A2A server

"""

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

from typing import Any
from typing import Dict
from uuid import uuid4

import httpx

# pylint: disable=import-error
from a2a.client import A2AClient
from a2a.types import SendMessageResponse
from neuro_san.interfaces.coded_tool import CodedTool


class A2aResearchReport(CodedTool):
    """
    CodedTool as an A2A client that connects to a crewAI agents that write
    a report on a given topic in A2A server.
    """

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Write a report on a given topic.

        :param args: Dictionary containing "topic".
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
        :return: A report or error message
        """
        # Extract arguments from the input dictionary
        topic: str = args.get("topic")

        if not topic:
            return "Error: No topic provided."

        # It could take a long time before remote agents response.
        # Adjust the timeout accordingly.
        async with httpx.AsyncClient(timeout=600.0) as httpx_client:
            client = await A2AClient.get_client_from_agent_card_url(
                # Make sure the A2A server is running and the port here
                # matches the one in the server.
                httpx_client,
                "http://localhost:9999",
            )
            # Send the message to server
            send_message_payload: dict[str, Any] = {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": f"{topic}"}],
                    "messageId": uuid4().hex,
                },
            }

            # Get response and parse to dictionary
            response: SendMessageResponse = await client.send_message(payload=send_message_payload)
            result: Dict[str, Any] = response.model_dump(exclude_none=True)

            # Extract text from the response
            report_text = result["result"]["parts"][-1]["text"]

            # Add some example citations
            report_text_with_citations = (
                f"{report_text}\\n\\n"
                f"This is an example citation to a case: [citation: https://www.courtlistener.com/opinion/106387/brown-v-board-of-education/]\\n"
                f"This is an example citation to a statute: [citation: https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=EVID&sectionNum=210.]"
            )

            # Make citations clickable
            import re

            def replace_citations(match):
                url = match.group(1)
                return f'<a href="{url}" target="_blank">[{url}]</a>'

            report_html = re.sub(r'\[citation: (.*?)\]', replace_citations, report_text_with_citations)

            return f"<html><body>{report_html}</body></html>"
