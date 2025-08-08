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

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from openai import OpenAIError

DEFAULT_OPENAI_MODEL = "gpt-4o-2024-08-06"


# pylint: disable=too-few-public-methods
class OpenAITool:
    """
    An implementation for invoking OpenAI built-in tools using LangChain's ChatOpenAI.

    Supported tools include (but are not limited to):
        - "code_interpreter"
        - "web_search_preview"
        - "file_search"
        - "image_generation"
        - "mcp"

    Only "code_interpreter" and "web_search_preview" have been tested.

    See https://platform.openai.com/docs/guides/tools?api-mode=responses
    """

    logger = logging.getLogger(__name__)

    @staticmethod
    async def arun(
        query: str,
        builtin_tool: str,
        openai_model: str | None = DEFAULT_OPENAI_MODEL,
        **additional_kwargs: dict[str, Any],
    ) -> list[dict[str, Any]] | str:
        """
        :param query: Request from the user prompt.
        :param builtin_tool: The name of the built-in OpenAI tool to invoke.
        :param openai_model: The OpenAI model to use when calling the tool.
            Defaults to "gpt-4o-2024-08-06" if not provided.
        :param additional_kwargs: Additional keyword arguments to pass to the selected tool.
            Tool-specific requirements:
                - "web_search_preview": no additional kwargs needed.
                - "code_interpreter": requires "container" to be set.
            Refer to https://python.langchain.com/docs/integrations/chat/openai/#responses-api

        :return:
            In case of successful execution:
                Tool results
            otherwise:
                a text string an error message in the format:
                "OpenAI Error: <error message>"
        """

        if not openai_model:
            openai_model = DEFAULT_OPENAI_MODEL

        OpenAITool.logger.info(">>>>>>>>>> Invoking OpenAI Tool <<<<<<<<<<")
        OpenAITool.logger.info("Query: %s", query)
        OpenAITool.logger.info("OpenAI Model: %s", openai_model)
        OpenAITool.logger.info("Built-in Tool: %s", builtin_tool)
        OpenAITool.logger.info("Additional Keyword Arguments: %s", additional_kwargs)

        try:
            # Instantiate the chat model using specified model.
            # The "output_version" key format output from built-in tool invocations into
            # the message’s content field, rather than additional_kwargs.
            openai_llm = ChatOpenAI(model=openai_model, output_version="responses/v1")
            tool: dict[str, Any] = {"type": builtin_tool} | additional_kwargs

            # Invoke with the provided query and tool,
            # "tool_choice" is set to "required" to force the model to use tool.
            result: AIMessage = await openai_llm.ainvoke(query, tools=[tool], tool_choice="required")
            content: list[dict[str, Any]] = result.content
            OpenAITool.logger.info("Result from OpenAI Tool: %s", content)
            return content

        except OpenAIError as openai_error:
            OpenAITool.logger.error("OpenAI Error: %s", openai_error)
            return f"OpenAI Error: {openai_error}"
