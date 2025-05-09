"""
Example of how to use crewai with neuro-san
To run this tool:
`pip install crewai`
"""

# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

from typing import Any
from typing import Dict
from typing import Type

from crewai import Agent
from crewai import Crew
from crewai import LLM
from crewai import Task
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel
from pydantic import Field

from neuro_san.interfaces.coded_tool import CodedTool


class CrewaiResearchReport(CodedTool):
    """
    CodedTool implementation which calculate BMI using a tool from mcp server
    """

    async def async_invoke(
            self,
            args: Dict[str, Any],
            sly_data: Dict[str, Any]
    ) -> float:
        """
        Use CrewAI to perform research via web search and generate a report.

        This example is adapted from https://docs.crewai.com/quickstart,
        but replaces the original SerperDevTool from crewai_tools with
        LangChain's DuckDuckGoSearchResults.

        :param args: Dictionary containing 'topic'.
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
        :return: BMI or error message
        """
        # Extract arguments from the input dictionary
        topic: str = args.get("topic")

        if not topic:
            return "Error: No topic provided."

        # LLM for agents
        llm = LLM(model="gpt-4o-mini")

        # Agents are researcher and reporting_analyst
        researcher = Agent(
            role="{topic} Senior Data Researcher",
            goal="Uncover cutting-edge developments in {topic}",
            backstory=(
                "You're a seasoned researcher with a knack for uncovering the "
                "latest developments in {topic}. Known for your ability to "
                "find the most relevant information and present it in a clear "
                "and concise manner."
            ),
            llm=llm,
            verbose=False
        )

        reporting_analyst = Agent(
            role="{topic} Reporting Analyst",
            goal=(
                "Create detailed reports based on {topic} data analysis and "
                "research findings"
            ),
            backstory=(
                "You're a meticulous analyst with a keen eye for detail. "
                "You're known for your ability to turn complex data into "
                "clear and concise reports, making it easy for others to "
                "understand and act on the information you provide."
            ),
            llm=llm,
            verbose=False
        )

        # researcher conducts research with DuckDuckGo while reporting_analyst
        # write a report
        research_task = Task(
            description=(
                "Conduct a thorough research about {topic}"
                "Make sure you find any interesting and relevant information "
                "given the current year is 2025."
            ),
            expected_output=(
                "A list with 10 bullet points of the most relevant information"
                " about {topic}"
            ),
            tools=[MyCustomDuckDuckGoTool()],
            agent=researcher
        )

        reporting_task = Task(
            description=(
                "Review the context you got and expand each topic into a full "
                "section for a report. Make sure the report is detailed and "
                "contains any and all relevant information."
            ),
            expected_output=(
                "A fully fledge reports with the mains topics, each with a "
                "full section of information. Formatted as markdown "
                "without '```'"
            ),
            agent=reporting_analyst
        )

        # Put agents and tasks into crew
        crew = Crew(
            agents=[researcher, reporting_analyst],
            tasks=[research_task, reporting_task],
            verbose=True
        )

        # Kick off the async run
        inputs = {'topic': topic}
        result = await crew.kickoff_async(inputs=inputs)

        return result.raw


class MyCustomDuckDuckGoToolInput(BaseModel):
    """Input schema for MyCustomDuckDuckGoTool."""
    query: str = Field(..., description="URL to search for.")


class MyCustomDuckDuckGoTool(BaseTool):
    """
    Convert DuckDuckGo LangChain tool into a CrewAI-compatible tool.

    See:
    - https://docs.crewai.com/concepts/tools
    - https://stackoverflow.com/questions/79226122/
    """
    name: str = "DuckDuckGo Search Tool"
    description: str = "Search the web for a given query."
    args_schema: Type[BaseModel] = MyCustomDuckDuckGoToolInput

    def _run(self, *args: Any, **kwargs: Any) -> str:
        query = kwargs.get("query") or (args[0] if args else None)
        if not query:
            raise ValueError("Missing required 'query' argument.")
        duckduckgo_tool = DuckDuckGoSearchResults()
        return duckduckgo_tool.invoke(query)
