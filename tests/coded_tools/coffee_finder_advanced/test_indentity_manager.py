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

from coded_tools.coffee_finder_advanced.identity_manager import IdentityManagerAPI


class TestIdentityManagerAPI(TestCase):
    """
    Unit tests for the IdentityManagerAPI class.
    """

    # @unittest.skip("Not a unit test: this is an integration test that starts a server and requires user input.")
    def test_invoke(self):
        """
        Tests the invoke method of the OrderAPI CodedTool.
        Checks the response is correctly generated when all params are provided and valid.
        """
        id_manager = IdentityManagerAPI()
        response_1 = id_manager.invoke(args={}, sly_data={})
        expected_username = "Olivier"
        expected_resp_1 = f"User logged in successfully as: {expected_username}"
        self.assertEqual(expected_resp_1, response_1)

    def test_invoke_sly_data(self):
        """
        Tests the invoke method of the OrderAPI CodedTool.
        Checks the response is correctly generated when all params are provided and valid.
        """
        id_manager = IdentityManagerAPI()
        expected_username = "Olivier"
        sly_data = {"username": expected_username}
        response_1 = id_manager.invoke(args={}, sly_data=sly_data)
        expected_resp_1 = f"Username is: {expected_username}"
        self.assertEqual(expected_resp_1, response_1)