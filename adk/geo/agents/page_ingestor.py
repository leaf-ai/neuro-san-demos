from google.adk.agents import Agent
from geo.constants import ADK_MODEL
from geo.tools.geo_service import geo_service
from geo.agent_prompts import PAGE_INGESTOR

from .compliance_specialist import compliance_specialist_agent

page_ingestor_agent = Agent(
    name="page_ingestor",
    model=ADK_MODEL,
    description="Extracts Rabobank page content & metadata for downstream agents.",
    instruction=PAGE_INGESTOR,
    tools=[geo_service],
    sub_agents=[compliance_specialist_agent],
)