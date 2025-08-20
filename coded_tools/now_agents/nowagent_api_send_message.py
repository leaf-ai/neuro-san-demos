# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
import json
import os
import requests
from typing import Any
from typing import Dict
from typing import Optional

from neuro_san.interfaces.coded_tool import CodedTool

class NowAgentSendMessage(CodedTool):
    """
    A tool to interact with Agentforce agents using the Agentforce API.
    Example usage: See tests/coded_tools/agentforce/test_agentforce_api.py
    """

    def __init__(self):
        """
        Constructs an NowAgentAPI object.
        """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Calls the Agentforce API to get a response to the user's inquiry. If no session was provided in the sly_data,
        a new session is created. Otherwise, the existing session is reused to keep the conversation going.
        WARNING: The AgentforceAdapter constructor reads the AGENTFORCE_CLIENT_ID and AGENTFORCE_CLIENT_SECRET
        environment variables. If they are NOT provided, this `invoke` call will return mock responses.

        
        :return: The response message from ServiceNow. 
        """  # noqa E501
        # Parse the arguments
        servicenow_url: str = self._get_env_variable('SERVICENOW_INSTANCE_URL')
        servicenow_caller_email: str = self._get_env_variable('SERVICENOW_CALLER_EMAIL')
        servicenow_user: str = self._get_env_variable('SERVICENOW_USER')
        servicenow_pwd: str = self._get_env_variable('SERVICENOW_PWD')
        print(f"ServiceNow URL: {servicenow_url}")
        print(f"user:{servicenow_user}")
        print(f"pwd:{servicenow_pwd}")

        print(f"args: {args}")
        inquiry: str = args.get("inquiry")
        agent_id: str = args.get("agent_id")

        # Get the session_id and access_token from the sly_data. Having a session_id means the user has already started
        # a conversation with Agentforce and wants to continue it.
        
        tool_name = self.__class__.__name__
        print(f"========== Calling {tool_name} ==========")

        # Set the request parameters
        url = servicenow_url+'api/sn_aia/agenticai/v1/agent/id/'+agent_id
        # Set proper headers
        headers = {"Content-Type":"application/json","Accept":"application/json"}

        # Do the HTTP request
        response = requests.post(url, auth=(servicenow_user, servicenow_pwd), headers=headers ,data="{\"request_id\":\"56789\",\"metadata\":{\"email_id\":\""+servicenow_caller_email+"\"},\"inputs\":[{\"content_type\":\"text\",\"content\":\""+inquiry+"\"}]}")


        # Check for HTTP codes other than 200
        if response.status_code != 200: 
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
            exit()

        # Decode the JSON response into a dictionary and use the data
        tool_response = response.json()

        print("-----------------------")
        print(f"{tool_name} tool response: ", tool_response)
        print(f"========== Done with {tool_name} ==========")

        sly_data["session_path"] = tool_response["metadata"]["user_id"]+"_"+tool_response["metadata"]["session_id"]
        print(f"Updated sly_data: {sly_data}")

        return tool_response
    
    @staticmethod
    def _get_env_variable(env_variable_name: str) -> str:
        print(f"NowAgent: getting {env_variable_name} from environment variables...")
        env_var = os.getenv(env_variable_name, None)
        if env_var is None:
            print(f"NowAgent: {env_variable_name} is NOT defined")
        else:
            print(f"NowAget: {env_variable_name} FOUND in environment variables")
        print(env_var)
        return env_var

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Delegates to the synchronous invoke method for now.
        """
        return self.invoke(args, sly_data)



