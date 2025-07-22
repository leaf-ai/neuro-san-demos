from google.adk.agents import Agent
from geo.constants import ADK_MODEL
from geo.tools.geo_service import geo_service
from geo.agent_prompts import CONTENT_ENHANCER

from .seo_specialist import seo_specialist_agent

content_enhancer_agent = Agent(
    name="content_enhancer",
    model=ADK_MODEL,
    description="Enhances Rabobank Markdown while preserving structure.",
    instruction=CONTENT_ENHANCER,
    tools=[geo_service],
    sub_agents=[seo_specialist_agent],
)