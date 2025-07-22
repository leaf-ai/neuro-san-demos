import os

from neuro_san.client.agent_session_factory import AgentSessionFactory
from neuro_san.client.streaming_input_processor import StreamingInputProcessor

AGENT_NETWORK_NAME = "legal_discovery"


from .settings import get_user_settings


def set_up_legal_discovery_assistant():
    """Configure these as needed."""
    agent_name = AGENT_NETWORK_NAME
    connection = "direct"
    host = "localhost"
    port = 30011
    local_externals_direct = False
    metadata = {"user_id": os.environ.get("USER")}

    # Get API key from settings
    user_settings = get_user_settings()
    if user_settings:
        if user_settings.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = user_settings.gemini_api_key
        if user_settings.courtlistener_api_key:
            os.environ["COURTLISTENER_API_KEY"] = user_settings.courtlistener_api_key
        if user_settings.california_codes_url:
            os.environ["CALIFORNIA_CODES_URL"] = user_settings.california_codes_url

    # Create session factory and agent session
    factory = AgentSessionFactory()
    session = factory.create_session(connection, agent_name, host, port, local_externals_direct, metadata)
    # Initialize any conversation state here
    legal_discovery_thread = {
        "last_chat_response": None,
        "prompt": "Please enter your response ('quit' to terminate):\n",
        "timeout": 5000.0,
        "num_input": 0,
        "user_input": None,
        "sly_data": None,
        "chat_filter": {"chat_filter_type": "MAXIMAL"},
    }
    return session, legal_discovery_thread


def legal_discovery_thinker(legal_discovery_session, legal_discovery_thread, thoughts):
    """
    Processes a single turn of user input within the legal discovery agent's session.

    This function simulates a conversational turn by:
    1. Initializing a StreamingInputProcessor to handle the input.
    2. Updating the agent's internal thread state with the user's input (`thoughts`).
    3. Passing the updated thread to the processor for handling.
    4. Extracting and returning the agent's response for this turn.

    Parameters:
        legal_discovery_session: An active session object for the legal discovery agent.
        legal_discovery_thread (dict): The agent's current conversation thread state.
        thoughts (str): The user's input or query to be processed.

    Returns:
        tuple:
            - last_chat_response (str or None): The agent's response to the input.
            - legal_discovery_thread (dict): The updated thread state after processing.
    """
    # Use the processor (like in agent_cli.py)
    input_processor = StreamingInputProcessor(
        "DEFAULT",
        "/tmp/agent_thinking.txt",  # Or wherever you want
        legal_discovery_session,
        None,  # Not using a thinking_dir for simplicity
    )
    # Update the conversation state with this turn's input
    legal_discovery_thread["user_input"] = thoughts
    legal_discovery_thread = input_processor.process_once(legal_discovery_thread)
    # Get the agent response for this turn
    last_chat_response = legal_discovery_thread.get("last_chat_response")
    return last_chat_response, legal_discovery_thread


def tear_down_legal_discovery_assistant(legal_discovery_session):
    """Tear down the assistant.

    :param legal_discovery_session: The pointer to the session.
    """
    print("tearing down legal discovery assistant...")
    legal_discovery_session.close()
    # client.assistants.delete(legal_discovery_assistant_id)
    print("legal discovery assistant torn down.")
