from google.adk.agents import Agent
from geo.constants import ADK_MODEL
from geo.agent_prompts import OUTPUT_GENERATOR

output_generator_agent = Agent(
    name="output_generator",
    model=ADK_MODEL,
    description="Formats final Markdown and JSON-LD output.",
    instruction=OUTPUT_GENERATOR,
)