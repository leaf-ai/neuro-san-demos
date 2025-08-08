# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
# END COPYRIGHT

import logging
from typing import Any

from anthropic import AnthropicError
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage

DEFAULT_ANTHROPIC_MODEL = "claude-3-7-sonnet-20250219"


# pylint: disable=too-few-public-methods
class AnthropicTool:
    """
    An implementation for invoking Anthropic built-in tools using LangChain's ChatAnthropic.

    Supported tools include (but are not limited to):
        - "code_execution"
        - "web_search"

    Only "code_execution" and "web_search" have been tested.

    See https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
    """

    logger = logging.getLogger(__name__)

    @staticmethod
    async def arun(
        query: str,
        tool_type: str,
        tool_name: str,
        anthropic_model: str | None = DEFAULT_ANTHROPIC_MODEL,
        betas: list[str] | None = None,
        **additional_kwargs: dict[str, Any],
    ) -> list[dict[str, Any]] | str:
        """
        :param query: Request from the user prompt.
        :param builtin_tool: The name of the built-in OpenAI tool to invoke.
        :param anthropic_model: The Anthropic model to use when calling the tool.
            Defaults to "claude-3-7-sonnet-20250219" if not provided.
        :param betas: Some tools are still in beta and requires this parameter.
        :param additional_kwargs: Additional keyword arguments to pass to the selected tool.
            Refer to https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview

        :return:
            In case of successful execution:
                Tool results
            otherwise:
                a text string an error message in the format:
                "Anthropic Error: <error message>"
        """

        if not anthropic_model:
            anthropic_model = DEFAULT_ANTHROPIC_MODEL

        AnthropicTool.logger.info(">>>>>>>>>> Invoking Anthropic Tool <<<<<<<<<<")
        AnthropicTool.logger.info("Query: %s", query)
        AnthropicTool.logger.info("Anthropic Model: %s", anthropic_model)
        AnthropicTool.logger.info("Built-in Tool Type: %s", tool_type)
        AnthropicTool.logger.info("Built-in Tool Name: %s", tool_name)
        AnthropicTool.logger.info("Additional Keyword Arguments: %s", additional_kwargs)

        try:
            # Instantiate the chat model using specified model.
            anthropic_llm = ChatAnthropic(model=anthropic_model)

            tool: dict[str, Any] = {"type": tool_type, "name": tool_name} | additional_kwargs

            # Invoke with the provided query and tool,
            # "tool_choice" is set to {"type": "any"} to force the model to use tool.
            result: AIMessage = await anthropic_llm.ainvoke(
                query, betas=betas, tools=[tool], tool_choice={"type": "any"}
            )
            content: list[dict[str, Any]] = result.content
            AnthropicTool.logger.info("Result from Anthropic Tool: %s", content)
            return content

        except AnthropicError as anthropic_error:
            AnthropicTool.logger.error("Anthropic Error: %s", anthropic_error)
            return f"Anthropic Error: {anthropic_error}"
