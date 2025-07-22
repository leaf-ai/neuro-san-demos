from google.adk.agents import Agent
from geo.constants import ADK_MODEL
from geo.agent_prompts import COMPLIANCE_SPECIALIST

from .content_enhancer import content_enhancer_agent

compliance_specialist_agent = Agent(
    name="compliance_specialist",
    model=ADK_MODEL,
    description="Validates content against brand and legal guidelines.",
    instruction=COMPLIANCE_SPECIALIST,
    sub_agents=[content_enhancer_agent],
)