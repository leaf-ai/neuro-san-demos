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
import time
import requests
from typing import Any
from typing import Dict
from typing import Optional

from neuro_san.interfaces.coded_tool import CodedTool

class NowAgentRetrieveMessage(CodedTool):
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
        url = servicenow_url+'api/now/table/sn_aia_external_agent_execution?sysparm_query=direction%3DOUTBOUND%5Esession_path%3D'+sly_data["session_path"]
        # Set proper headers
        headers = {"Content-Type":"application/json","Accept":"application/json"}

        print("URL ==========="+url)
        # Do the HTTP request
        response = requests.get(url, auth=(servicenow_user, servicenow_pwd), headers=headers )

        # Decode the JSON response into a dictionary and use the data
        tool_response = response.json()

        for attempt in range(1, 6):
            print(f"Attempt {attempt}...")
            response = requests.get(url, auth=(servicenow_user, servicenow_pwd), headers=headers )
            tool_response = response.json()
            print(f"Response: {tool_response}")
            if isinstance(tool_response, dict) and "result" in tool_response:
                if isinstance(tool_response["result"], list) and tool_response["result"]:
                    print("Non-empty result found.")
                    break
            if attempt < 5:
                time.sleep(5)
            print("Max attempts reached without finding a non-empty result.")

        print("-----------------------")
        print(f"{tool_name} tool response: ", tool_response)
        print(f"========== Done with {tool_name} ==========")

        

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



