from google.adk.agents import Agent
from geo.constants import ADK_MODEL
from geo.tools.geo_service import geo_service
from geo.agent_prompts import CONTENT_MANAGEMENT_LEAD

from .page_ingestor import page_ingestor_agent
from .content_enhancer import content_enhancer_agent
from .seo_specialist import seo_specialist_agent
from .output_generator import output_generator_agent

content_management_lead_agent = Agent(
    name="content_management_lead",
    model=ADK_MODEL,
    description="Top-level orchestrator for the Rabobank SEO pipeline (v2).",
    instruction=CONTENT_MANAGEMENT_LEAD,
    tools=[geo_service],
    sub_agents=[
        page_ingestor_agent
    ],
)