# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool


class ManageEval(CodedTool):
    """
    CodedTool implementation manages evaluation score.
    Returns a dictionary mapping the evaluation.
    """

    def __init__(self):
        self.eval_data: Dict[str, Any] = {
            "innovation_score": None,
            "ux_score": None,
            "scalability_score": None,
            "market_potential_score": None,
            "ease_of_implementation_score": None,
            "financial_feasibility_score": None,
            "complexity_score": None,
            # we update the description separately
            # "description": None
        }

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Updates the evaluation scores based on the provided arguments.
        :param args: An empty dictionary (not used)

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
            but whose values are meant to be kept out of the chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool implementation
            adding the data is not invoke()-ed more than once.

            Keys expected for this implementation are essential the evaluation scores:
            - "innovation_score"
            - "ux_score"
            - "scalability_score"
            - "market_potential_score"
            - "ease_of_implementation_score"
            - "financial_feasibility_score"
            - "complexity_score"
            - "description"

        :return:
            A dictionary containing evaluation scores with the above listed keys.
            Note: This method also updates the sly_data dictionary with the new evaluation scores.
        """
        tool_name = self.__class__.__name__
        print(f"========== Calling {tool_name} ==========")
        print(f"\nargs: {args}")
        # Parse the sly data
        print(f"\nsly_data:\n{sly_data}")
        # Get the evaluation from sly_data, if it exists
        if sly_data.get("evaluation") is None:
            updated_evaluation: Dict[str, Any] = self.eval_data
        else:
            # If evaluation data exists, use it
            updated_evaluation: Dict[str, Any] = sly_data.get("evaluation").copy()

        # Update the evaluation scores from the supplied scores
        # Make sure description is handled properly
        if args is not None:
            for key in self.eval_data.keys():
                if key in args:
                    # If the key is in args, update the evaluation score
                    updated_evaluation[key] = args[key]

        # we should append to the text in description instead of replacing it with new values
        if "description" in args:
            if "description" in updated_evaluation:
                updated_evaluation["description"] += f"\n{args['description']}"
            else:
                updated_evaluation["description"] = args.get("description")

        # Finally update the sly_data
        sly_data["evaluation"] = updated_evaluation

        tool_response = {"updated_evaluation": updated_evaluation}
        print("-----------------------")
        print(f"{tool_name} response: ", tool_response)
        print(f"========== Done with {tool_name} ==========")
        return tool_response

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method because it's quick, non-blocking.
        """
        return self.invoke(args, sly_data)
