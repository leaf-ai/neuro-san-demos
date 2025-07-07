"""Generic MCP Tool Adapter for connecting to MCP servers"""

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

from typing import Any, Dict, List, Union
import logging

from langchain_mcp_adapters.client import MultiServerMCPClient
from neuro_san.interfaces.coded_tool import CodedTool


class MCPToolAdapter(CodedTool):
    """
    Generic adapter for connecting to MCP servers and dynamically exposing their tools.
    
    This adapter discovers tools from an MCP server at runtime and makes them available
    to the neuro-san agent system without requiring individual tool definitions.
    """

    async def _get_client(self, base_url: str, server_name: str = "mcp_server") -> MultiServerMCPClient:
        """Get or create the MCP client connection."""
        client = MultiServerMCPClient(
            {
                server_name: {
                    "url": base_url,
                    "transport": "streamable_http",
                }
            }
        )
        return client

    async def _get_tools(self, client: MultiServerMCPClient) -> List[Any]:
        """Get the list of available tools from the MCP server."""
        tools = await client.get_tools()
        logging.info(f"[MCPToolAdapter] Discovered {len(tools)} tools from MCP server")
        return tools

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Any:
        """
        Dynamically invoke MCP server tools.
        
        This method expects the args to contain:
        - 'tool_name': The name of the MCP tool to invoke
        - 'base_url': The URL of the MCP server (from configuration)
        - Other parameters as required by the specific tool
        
        :param args: Dictionary containing tool_name, base_url, and tool parameters
        :param sly_data: Context data (passed through to tools that need it)
        :return: Result from the MCP tool
        """
        tool_name = args.get("tool_name")
        if not tool_name:
            return "Error: tool_name parameter is required"

        # Get configuration from args
        base_url = args.get("base_url", "http://localhost:8000/mcp/")
        server_name = args.get("server_name", "mcp_server")

        logging.info(f"[MCPToolAdapter] Invoking MCP tool: {tool_name} at {base_url}")

        try:
            # Get MCP client and tools
            client = await self._get_client(base_url, server_name)
            tools = await self._get_tools(client)
            
            # Find the requested tool
            target_tool = None
            for tool in tools:
                if hasattr(tool, 'name') and tool.name == tool_name:
                    target_tool = tool
                    break
            
            if not target_tool:
                available_tools = [tool.name for tool in tools if hasattr(tool, 'name')]
                return f"Error: Tool '{tool_name}' not found. Available tools: {available_tools}"

            # Prepare parameters for the MCP tool
            tool_params = {k: v for k, v in args.items() if k not in ["tool_name", "base_url", "server_name"]}
            
            # Add sly_data parameters if the tool expects them
            # For tools like user_verification and training_completions that need user context
            if tool_name in ["user_verification", "training_completions"]:
                user_id = sly_data.get("user_id", "").strip()
                dataiku_id = sly_data.get("dataiku_id", "").strip()
                
                if tool_name == "user_verification":
                    tool_params.update({
                        "user_id": user_id,
                        "dataiku_id": dataiku_id
                    })
                elif tool_name == "training_completions":
                    tool_params["user_id"] = user_id

            # Invoke the MCP tool
            result = await target_tool.ainvoke(tool_params)
            
            logging.info(f"[MCPToolAdapter] Tool '{tool_name}' returned: {type(result).__name__}")
            return result

        except Exception as e:
            logging.error(f"[MCPToolAdapter] Error invoking tool '{tool_name}': {e}")
            return f"Error: {e}"

    async def list_available_tools(self, base_url: str = "http://localhost:8000/mcp/") -> List[str]:
        """
        List all available tools from the MCP server.
        
        :param base_url: The URL of the MCP server
        :return: List of tool names
        """
        try:
            client = await self._get_client(base_url)
            tools = await self._get_tools(client)
            return [tool.name for tool in tools if hasattr(tool, 'name')]
        except Exception as e:
            logging.error(f"[MCPToolAdapter] Error listing tools: {e}")
            return [] 