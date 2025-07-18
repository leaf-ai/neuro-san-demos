"""Test cases for the LLM Auditor."""

import textwrap

import dotenv
import pytest
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
from llm_auditor.agent import root_agent

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_happy_path():
    """Runs the agent on a simple input and expects a normal response."""
    user_input = textwrap.dedent("""
        Double check this:
        Question: Why is the sky blue?
        Answer: Becauase the water is blue.
    """).strip()

    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = UserContent(parts=[Part(text=user_input)])
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        print(event)
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text

    # The answer in the input is wrong, so we expect the agent to provided a
    # revised answer, and the correct answer should mention scattering.
    assert "scattering" in response.lower()