from google.adk.agents import Agent
from geo.constants import ADK_MODEL
from geo.agent_prompts import SEO_SPECIALIST

from .output_generator import output_generator_agent

seo_specialist_agent = Agent(
    name="seo_specialist",
    model=ADK_MODEL,
    description="Optimises content for SEO before final output.",
    instruction=SEO_SPECIALIST,
    sub_agents=[output_generator_agent],
)