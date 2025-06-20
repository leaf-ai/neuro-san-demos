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

import asyncio
import json
import webbrowser
from typing import Any
from typing import Dict

from neuro_san.interfaces.coded_tool import CodedTool
from neuro_san.internals.graph.persistence.agent_network_restorer import AgentNetworkRestorer
from pyvis.network import Network


class AgentNetworkHtmlGenerator(CodedTool):
    """
    CodedTool implementation which draw agent_network to html file
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        :param args: An argument dictionary whose keys are the parameters
            to the coded tool and whose values are the values passed for
            them by the calling agent.  This dictionary is to be treated as
            read-only.

            The argument dictionary expects the following keys:
                "agent_name"

        :param sly_data: A dictionary whose keys are defined by the agent
            hierarchy, but whose values are meant to be kept out of the
            chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool
            implementation adding the data is not invoke()-ed more than
            once.

            Keys expected for this implementation are:
                None
        :return: successful sent message ID or error message
        """

        # Extract arguments from the input dictionary
        agent_name: str = args.get("agent_name")

        # Validate presence of required inputs
        if not agent_name:
            return "Error: No agent_name provided."

        print(f"Generating HTML file for {agent_name}")

        # Create dict from hocon
        try:
            network_dict = AgentNetworkRestorer().restore("registries/" + agent_name + ".hocon").get_config()
        except FileNotFoundError as file_not_found_error:
            print(file_not_found_error)
            return f"Trying to load {agent_name}.hocon: {file_not_found_error}."

        # Generate html
        generate_html(agent_name, network_dict)

        # Open it on chrome
        webbrowser.get("open -a 'Google Chrome' %s").open(f"{agent_name}.html")

        return f"{agent_name}.html was successfully generated."

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """Run invoke asynchronously."""
        return await asyncio.to_thread(self.invoke, args, sly_data)


def generate_html(agent_name: str, network_dict: Dict[str, Any]):
    """
    Creat a html file from a dictionary.

    :param network_dict: .

    :return: successful sent message ID or error statement
    """

    net = Network(height="1000px", width="100%", directed=False)

    # Set global styling (without node shape override)
    net.set_options(
        """
    var options = {
    "nodes": {
        "font": { "color": "#ffffff" },
        "borderWidth": 2
    },
    "layout": {
        "improvedLayout": true
    },
    "interaction": {
        "hover": true,
        "dragNodes": true
    },
    "physics": {
        "enabled": true,
        "barnesHut": {
        "gravitationalConstant": -3000,
        "centralGravity": 0.0,
        "springLength": 500
        }
    }
    }
    """
    )

    # Add nodes
    for node in network_dict.get("tools"):
        node_name = node["name"]
        tooltip = json.dumps(node, indent=4)

        # Force rectangular box-shaped nodes
        net.add_node(
            node_name,
            label=node_name,
            color="#4169E1",
            shape="box",
            widthConstraint={"minimum": 180, "maximum": 200},
            heightConstraint={"minimum": 80},
            font={"multi": "html"},
            title=tooltip,
        )

    # Add edges
    for node in [n for n in network_dict.get("tools", []) if "tools" in n]:
        node_name = node["name"]
        tools = node["tools"]
        for tool in tools:
            net.add_edge(node_name, tool)

    # Show the graph
    net.show(f"{agent_name}.html", notebook=False)
