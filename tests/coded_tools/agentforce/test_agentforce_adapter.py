# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
from unittest import TestCase

from dotenv import load_dotenv  # type: ignore

from coded_tools.agentforce.agentforce_adapter import AgentforceAdapter


class TestAgentforceAdapter(TestCase):
    """
    Unit tests for the AgentforceAdapter class.
    """

    def test_post_message(self):
        """
        Tests the post_message method of the AgentforceAdapter class.
        Loads the environment variables from the .env file if any.
        """
        # Load environment variables from the .env file, if any
        load_dotenv(verbose=True)
        # Instantiate an AgentforceAdapter.
        # Client id and client secret are read from the environment variables.
        agentforce = AgentforceAdapter()
        # message = "Can you help me find training resources for Salesforce?"
        first_message = "Can you give me a list of Jane Doe's most recent cases?"
        print(f"USER: {first_message}")
        # Post the message to the Agentforce API
        first_response = agentforce.post_message(first_message)
        # Keep track of the session_id and access_token to continue the conversation
        session_id = first_response["session_id"]
        access_token = first_response["access_token"]
        response_message = first_response["response"]["messages"][0]["message"]
        print(f"AGENTFORCE: {response_message}")
        second_message = "jdoe@example.com"
        print(f"USER: {second_message}")
        # Continue the conversation by using the session_id and access_token
        a_second_response = agentforce.post_message(second_message, session_id, access_token)
        a_second_response_message = a_second_response["response"]["messages"][0]["message"]
        print(f"AGENTFORCE: {a_second_response_message}")
        # Close the session
        agentforce.close_session(session_id, access_token)
        print("Done!")
