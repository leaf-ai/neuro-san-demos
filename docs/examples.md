# Examples

Here are a few examples ordered by level of complexity.

## Music Nerd

[Music Nerd](./examples/music_nerd.md) is a very simple agent network with a single agent,
used as a "Hello world!" example. It can also be used to test for follow-up questions and deterministic answers.

## Music Nerd Pro

[Music Nerd Pro](./examples/music_nerd_pro.md) is a simple agent network with a frontman agent and a "Coded Tool".
This is a good way to learn about how to call Python code from an agent.

## Music Nerd Local

[Music Nerd Local](./examples/music_nerd_local.md) is an exact copy of
[Music Nerd](./examples/music_nerd.md) that uses an LLM that runs locally with Ollama.

## Music Nerd Pro Local

[Music Nerd Pro Local](./examples/music_nerd_pro_local.md) is an exact copy of
[Music Nerd Pro](./examples/music_nerd_pro.md) that uses
a **tool-calling** LLM that runs locally with Ollama.

## Music Nerd Pro Sly

[Music Nerd Pro Sly](./examples/music_nerd_pro_sly.md) is a copy of
[Music Nerd Pro](./examples/music_nerd_pro.md) that uses `sly_data` to keep track of a variable.
This is a good way to learn about how to manage a state in a conversation.

## Music Nerd Pro Sly Local

[Music Nerd Pro Sly Local](./examples/music_nerd_pro_sly_local.md) is a copy of
[Music Nerd Pro Sly](./examples/music_nerd_pro_sly.md) that uses
a **tool-calling** LLM that runs locally with Ollama.

## CrewAI Research Report

[CrewAI Research Report](./examples/crewai_research_report.md) is an agentic system that calls CrewAI to do website search and write a report. It serves as an example of how to connect to CrewAI in coded tools.

## MCP BMI SSE

[MCP BMI SSE](./examples/mcp_bmi_sse.md) is an agent that calls a tool in MCP server via server-sent events (sse) to calculate BMI. It serves as an example of how to connect to mcp servers in coded tools.

## Agentic RAG Assistant

[Agentic RAG Assistant](./examples/agentic_rag.md) is a modular multi-agent system that answers user queries by retrieving information from the web, PDF documents, and Slack channels. It mimics a smart assistant that delegates tasks to specialized tools and compiles responses into clear, helpful answers.

## Airline Policy 360 Assistant

[Airline Policy 360 Assistant](./examples/airline_policy.md) is a sophisticated multi-agent system designed to manage and respond to customer inquiries by referring to related airline policies with structured delegation. It mimics a real-world helpdesk with specialized teams, each handling a specific domain of airline policies such as baggage, flights, international travel, and more.

## Intranet Agents

[Intranet Agents](examples/intranet_agents.md) is a multi-agent system that mimics the intranet of a major corporation. It allows you to interact and get information from various departments such as IT, Finance, Legal, HR, etc.

## Intranet Agents With Tools

[Intranet Agents With Tools](examples/intranet_agents_with_tools.md) is a multi-agent system that mimics the intranet of a major corporation. It allows you to interact and get information from various departments such as IT, Finance, Legal, HR, etc. Some of the down-chain agents call coded tools.

## Agentforce

[Agentforce](./examples/agentforce.md) is an agent network that delegates to a Salesforce Agentforce agent
to interact with a CRM system.

## Agent Network Designer

[Agent Network Designer](examples/agent_network_designer.md) is a multi-agent system to create multi-agent systems. Enter the name of an organization or describe the use-case and will create a agent network hocon for you and save it to your registries directory and give you some usage examples.

## KWIK Agents

[kwik_agents.md](examples/kwik_agents.md) is a basic multi-agent system with memory.

