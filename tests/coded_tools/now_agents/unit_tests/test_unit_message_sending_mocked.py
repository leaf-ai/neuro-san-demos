# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#

import os
import unittest
from unittest.mock import patch, Mock

from coded_tools.now_agents.nowagent_api_send_message import NowAgentSendMessage


# Mock response data for testing
MOCK_SEND_RESPONSE = {
    "metadata": {
        "user_id": "test_user_123",
        "session_id": "session_456"
    },
    "status": "message_sent"
}


class TestNowAgentSendMessage(unittest.TestCase):
    """
    Unit tests for NowAgentSendMessage class.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tool = NowAgentSendMessage()
        self.test_args = {
            "inquiry": "Help me with my laptop issue",
            "agent_id": "12345678-1234-1234-1234-123456789abc"
        }
        self.test_sly_data = {}

    @patch.dict(os.environ, {
        'SERVICENOW_INSTANCE_URL': 'https://test.service-now.com/',
        'SERVICENOW_CALLER_EMAIL': 'test@example.com',
        'SERVICENOW_USER': 'test_user',
        'SERVICENOW_PWD': 'test_password'
    })
    @patch('coded_tools.now_agents.nowagent_api_send_message.requests.post')
    def test_invoke_success(self, mock_post):
        """
        Test successful message sending to ServiceNow agent.
        
        This test verifies that the tool correctly sends a message to a ServiceNow AI agent
        and properly manages session data.
        """
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_SEND_RESPONSE
        mock_post.return_value = mock_response

        # Execute the tool
        result = self.tool.invoke(self.test_args, self.test_sly_data)

        # Verify the result
        self.assertEqual(result, MOCK_SEND_RESPONSE)
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["user_id"], "test_user_123")

        # Verify session_path was set in sly_data
        expected_session_path = "test_user_123_session_456"
        self.assertEqual(self.test_sly_data["session_path"], expected_session_path)

        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        expected_url = "https://test.service-now.com/api/sn_aia/agenticai/v1/agent/id/12345678-1234-1234-1234-123456789abc"
        self.assertEqual(call_args[0][0], expected_url)
        self.assertEqual(call_args[1]["auth"], ("test_user", "test_password"))

        # Verify request payload structure
        import json
        payload = json.loads(call_args[1]["data"])
        self.assertEqual(payload["metadata"]["email_id"], "test@example.com")
        self.assertEqual(payload["inputs"][0]["content"], "Help me with my laptop issue")

    @patch.dict(os.environ, {
        'SERVICENOW_INSTANCE_URL': 'https://test.service-now.com/',
        'SERVICENOW_CALLER_EMAIL': 'test@example.com',
        'SERVICENOW_USER': 'test_user',
        'SERVICENOW_PWD': 'test_password'
    })
    @patch('coded_tools.now_agents.nowagent_api_send_message.requests.post')  
    @patch('coded_tools.now_agents.nowagent_api_send_message.exit')
    @patch('builtins.print')
    def test_invoke_authentication_failure(self, mock_print, mock_exit, mock_post):
        """
        Test handling of authentication failure.
        
        This test verifies that the tool properly handles 401 authentication errors
        from the ServiceNow API and prints error information.
        """
        # Mock 401 authentication error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "error": {"message": "User Not Authenticated"}
        }
        mock_post.return_value = mock_response
        
        # Mock exit to prevent actual exit
        mock_exit.side_effect = SystemExit()

        # Execute the tool and expect SystemExit due to authentication failure
        with self.assertRaises(SystemExit):
            self.tool.invoke(self.test_args, self.test_sly_data)
        
        # Verify error information was printed
        mock_exit.assert_called_once()
        error_calls = [call for call in mock_print.call_args_list 
                      if 'Status: 401' in str(call) or 'Error Response:' in str(call)]
        self.assertTrue(len(error_calls) >= 2, "Error messages should be printed")

    @patch.dict(os.environ, {
        'SERVICENOW_INSTANCE_URL': 'https://test.service-now.com/',
        'SERVICENOW_CALLER_EMAIL': 'test@example.com',
        'SERVICENOW_USER': 'test_user',
        'SERVICENOW_PWD': 'test_password'
    })
    @patch('coded_tools.now_agents.nowagent_api_send_message.requests.post')
    def test_invoke_missing_agent_id(self, mock_post):
        """
        Test handling of missing agent_id parameter.
        
        This test verifies that the tool handles missing required parameters gracefully.
        """
        # Test with missing agent_id
        args_missing_agent = {"inquiry": "Help me"}
        
        # The tool should still attempt the call but with None agent_id
        # This will result in an invalid URL, but we're testing parameter handling
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not Found"}
        mock_post.return_value = mock_response

        with self.assertRaises(SystemExit):
            self.tool.invoke(args_missing_agent, self.test_sly_data)

    @patch('builtins.print')
    def test_get_env_variable(self, mock_print):
        """
        Test environment variable retrieval.
        
        This test verifies that the _get_env_variable helper method correctly
        retrieves environment variables.
        """
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = self.tool._get_env_variable('TEST_VAR')
            self.assertEqual(result, 'test_value')

        # Test missing environment variable - should print NOT defined message
        result = self.tool._get_env_variable('NONEXISTENT_VAR')
        self.assertIsNone(result)
        
        # Verify the "NOT defined" message was printed
        not_defined_calls = [call for call in mock_print.call_args_list 
                           if 'NONEXISTENT_VAR is NOT defined' in str(call)]
        self.assertTrue(len(not_defined_calls) >= 1, "NOT defined message should be printed")

    @patch.dict(os.environ, {
        'SERVICENOW_INSTANCE_URL': 'https://test.service-now.com/',
        'SERVICENOW_CALLER_EMAIL': 'test@example.com',
        'SERVICENOW_USER': 'test_user',
        'SERVICENOW_PWD': 'test_password'
    })
    @patch('coded_tools.now_agents.nowagent_api_send_message.requests.post')
    def test_async_invoke(self, mock_post):
        """
        Test asynchronous invoke method.
        
        This test verifies that the async_invoke method delegates correctly
        to the synchronous invoke method.
        """
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_SEND_RESPONSE
        mock_post.return_value = mock_response

        # Execute the async tool
        import asyncio
        result = asyncio.run(self.tool.async_invoke(self.test_args, self.test_sly_data))

        # Verify the result matches synchronous behavior
        self.assertEqual(result, MOCK_SEND_RESPONSE)


if __name__ == '__main__':
    unittest.main()