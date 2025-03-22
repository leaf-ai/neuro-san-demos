from typing import Any
from typing import Dict
from typing import Optional
import json

from neuro_san.interfaces.coded_tool import CodedTool

from coded_tools.agentforce.agentforce_adapter import AgentforceAdapter

MOCK_SESSION_ID = "06518755-b897-4311-afea-2aab1df77314"
MOCK_SECRET = "1234567890"
MOCK_RESPONSE_MESSAGE_1 = \
"""
{"messages": [{"type": "Inform", "id": "04d35a5d-6011-4eb9-88a9-2897f49a6bdc", "feedbackId": "7d92a297-dc95-4306-b638-42f6e36ddfab", "planId": "7d92a297-dc95-4306-b638-42f6e36ddfab", "isContentSafe": true, "message": "Sure, I can help with that. Could you please provide Lauren Bailey's email address to look up her cases?", "result": [], "citedReferences": []}], "_links": {"self": null, "messages": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/06518755-b897-4311-afea-2aab1df77314/messages"}, "messagesStream": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/06518755-b897-4311-afea-2aab1df77314/messages/stream"}, "session": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/agents/0XxKc000000kvtXKAQ/sessions"}, "end": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/06518755-b897-4311-afea-2aab1df77314"}}}
"""
MOCK_RESPONSE_MESSAGE_2 = \
"""
{"messages": [{"type": "Inform", "id": "caf90c84-a150-4ccd-8430-eb29189696ac", "feedbackId": "e24505db-1edd-4b76-b5f5-908be083fc67", "planId": "e24505db-1edd-4b76-b5f5-908be083fc67", "isContentSafe": true, "message": "It looks like there are no recent cases associated with Lauren Bailey's email address. Is there anything else I can assist you with?", "result": [], "citedReferences": []}], "_links": {"self": null, "messages": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/06518755-b897-4311-afea-2aab1df77314/messages"}, "messagesStream": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/06518755-b897-4311-afea-2aab1df77314/messages/stream"}, "session": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/agents/0XxKc000000kvtXKAQ/sessions"}, "end": {"href": "https://api.salesforce.com/einstein/ai-agent/v1/sessions/06518755-b897-4311-afea-2aab1df77314"}}}
"""
MOCK_RESPONSE_1 = {
    "session_id": MOCK_SESSION_ID,
    "access_token": MOCK_SECRET,
    "response": json.loads(MOCK_RESPONSE_MESSAGE_1)
}
MOCK_RESPONSE_2 = {
    "session_id": MOCK_SESSION_ID,
    "access_token": MOCK_SECRET,
    "response": json.loads(MOCK_RESPONSE_MESSAGE_2)
}


class AgentforceAPI(CodedTool):
    """
    A tool to interact with Agentforce agents using the Agentforce API.
    """

    def __init__(self):
        """
        Constructs an AgentforceAPI object.
        """
        # Construct an AgentforceAdapter object using environment variables
        self.agentforce = AgentforceAdapter(None, None)

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        :param args: A dictionary with the following keys:
                    "inquiry": the user request to the Agentforce API, as a string.
                    "session_id": (optional) the ID of the session to reuse to keep the conversation going, if any.
                     If None, a new session is created which means a new conversation is started.
                    "access_token": (optional) the access token corresponding to the session_id. Can only be None if
                    session_id is None.


        :param sly_data: A dictionary containing parameters that should be kept out of the chat stream.
                         Keys expected for this implementation are:
                         None

        :return: A dictionary containing:
                 "session_id": the session id to use to continue the conversation,
                 "access_token": the corresponding access_token
                 "response": the response message from Agentforce.
        """
        # Parse the arguments
        inquiry: str = args.get("inquiry")
        session_id: Optional[str] = args.get("session_id", None)
        access_token: Optional[str] = args.get("access_token", None)

        tool_name = self.__class__.__name__
        print(f"========== Calling {tool_name} ==========")
        print(f"    Inquiry: {inquiry}")
        print(f"    Session ID: {session_id}")

        if self.agentforce.is_configured:
            print("AgentforceAdapter is configured. Fetching response...")
            response = self.agentforce.post_message(inquiry, session_id, access_token)
        else:
            print("WARNING: AgentforceAdapter is NOT configured. Using a mock response")
            if session_id in (None, "None"):
                # No session yet. This is the first request the user makes
                response = MOCK_RESPONSE_1
            else:
                # The user has a session. This is a follow-up request
                response = MOCK_RESPONSE_2
        tool_response = {
            "session_id": response["session_id"],
            "access_token": response["access_token"],
            "response": response["response"]["messages"][0]["message"]
        }
        print("-----------------------")
        print(f"{tool_name} tool response: ", tool_response)
        print(f"========== Done with {tool_name} ==========")
        return tool_response


# Example usage:
if __name__ == "__main__":
    agentforce_tool = AgentforceAPI()
    # Ask a first question
    af_inquiry_1 = "Can you give me a list of Lauren Bailey's most recent cases?"
    print(f"USER: {af_inquiry_1}")
    # Get the response
    af_response_1 = agentforce_tool.invoke(args={"inquiry": af_inquiry_1}, sly_data={})
    print(f"AGENTFORCE: {af_response_1["response"]}")
    # Follow up with what Agentforce asked for. Session exists now, reuse it to continue the conversation instead
    # of starting a new one
    af_inquiry_2 = "lbailey@example.com"
    print(f"USER: {af_inquiry_2}")
    params = {"inquiry": af_inquiry_2,
              "session_id": af_response_1["session_id"],
              "access_token": af_response_1["access_token"]}
    af_response_2 = agentforce_tool.invoke(args=params, sly_data={})
    print(f"AGENTFORCE: {af_response_2["response"]}")
    # Close the session
    agentforce_tool.agentforce.close_session(af_response_2["session_id"], af_response_2["access_token"])
