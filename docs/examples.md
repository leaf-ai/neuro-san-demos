# Examples

Here are a few examples ordered by level of complexity.

<!-- TOC -->
* [Examples](#examples)
  * [🔰 Basic Examples](#-basic-examples)
    * [Music Nerd](#music-nerd)
    * [Music Nerd Pro](#music-nerd-pro)
    * [Music Nerd Local](#music-nerd-local)
    * [Music Nerd Pro Local](#music-nerd-pro-local)
    * [Music Nerd Pro Sly](#music-nerd-pro-sly)
    * [Music Nerd Pro Sly Local](#music-nerd-pro-sly-local)
  * [🧰 Tool Integration Examples](#-tool-integration-examples)
    * [Gmail Assistant](#gmail-assistant)
    * [Agentforce](#agentforce)
    * [Agentspace](#agentspace)
    * [MCP BMI STREAMABLE HTTP](#mcp-bmi-streamable-http)
    * [A2A RESEARCH REPORT](#a2a-research-report)
    * [PDF RAG Assistant](#pdf-rag-assistant)
    * [Confluence RAG Assistant](#confluence-rag-assistant)
    * [Agentic RAG Assistant](#agentic-rag-assistant)
  * [🏢 Industry-Specific Examples](#-industry-specific-examples)
    * [Intranet Agents](#intranet-agents)
    * [Intranet Agents With Tools](#intranet-agents-with-tools)
    * [Airline Policy 360 Assistant](#airline-policy-360-assistant)
    * [Real Estate Agent](#real-estate-agent)
    * [Consumer Decision Assistant Agents](#consumer-decision-assistant-agents)
    * [Therapy Vignette Supervision](#therapy-vignette-supervision)
  * [🧪 Experimental and Research](#-experimental-and-research)
    * [Agent Network Designer](#agent-network-designer)
    * [KWIK Agents](#kwik-agents)
    * [CRUSE](#cruse)
    * [Conscious Assistant](#conscious-assistant)
    * [Log Analyzer](#log-analyzer)
<!-- TOC -->

## 🔰 Basic Examples

Introductory examples designed to help users get started with Neuro SAN.

### Music Nerd

[Music Nerd](./examples/music_nerd.md) is a basic agent network with a single agent,
used as a "Hello world!" example. It can also be used to test for follow-up questions and deterministic answers.

### Music Nerd Pro

[Music Nerd Pro](./examples/music_nerd_pro.md) is a simple agent network with a frontman agent and a "Coded Tool."
This is a good way to learn about how to call Python code from an agent.

**Tags:** `tool`

### Music Nerd Local

[Music Nerd Local](./examples/music_nerd_local.md) is an exact copy of
[Music Nerd](./examples/music_nerd.md) that uses an LLM that runs locally with Ollama.

**Tags:** `llm_config`

### Music Nerd Pro Local

[Music Nerd Pro Local](./examples/music_nerd_pro_local.md) is an exact copy
of [Music Nerd Pro](./examples/music_nerd_pro.md) that uses a **tool-calling** LLM that runs locally with Ollama.

**Tags:** `tool`, `llm_config`

### Music Nerd Pro Sly

[Music Nerd Pro Sly](./examples/music_nerd_pro_sly.md) is a copy of
[Music Nerd Pro](./examples/music_nerd_pro.md) that uses `sly_data` to keep track of a variable.
This is a good way to learn about how to manage a state in a conversation.

**Tags:** `tool`, `sly_data`

### Music Nerd Pro Sly Local

[Music Nerd Pro Sly Local](./examples/music_nerd_pro_sly_local.md) is a copy of
[Music Nerd Pro Sly](./examples/music_nerd_pro_sly.md) that uses
a **tool-calling** LLM that runs locally with Ollama.

**Tags:** `tool`, `sly_data`, `llm_config`

## 🧰 Tool Integration Examples

Examples that demonstrate how to integrate external tools and services.

### Gmail Assistant
[Gmail Assistant](./examples/gmail.md) is a conversational agent that helps users manage their Gmail inbox using natural language. It can search, read, draft, and send emails by delegating tasks to specialized tools in the Gmail Toolkit.

**Tags:** `tool`, `Gmail`, `API`

### Agentforce

[Agentforce](./examples/agentforce.md) is an agent network that delegates to a Salesforce Agentforce agent
to interact with a CRM system.

**Tags:** `tool`, `API`

### Agentspace

[Agentspace](./examples/agentspace_adapter.md) is an agent network that delegates to a Google Agentspace agent to
interact with different datastore connectors on Google Cloud.

**Tags:** `tool`, `API`

### MCP BMI STREAMABLE HTTP

[MCP BMI STREAMABLE HTTP](./examples/mcp_bmi_streamable_http.md) is an agent that calls a tool in MCP server via streamable http to
calculate BMI. It serves as an example of how to connect to MCP servers in coded tools.

**Tags:** `tool`, `MCP`

### A2A RESEARCH REPORT

[A2A RESEARCH REPORT](./examples/a2a_research_report.md) is an agent that uses a coded tool as an A2A client to connect
to crewAI agents in an A2A server to write a report on a provided topic. This is an example of how to link
neuro-san with other agentic frameworks.

**Tags:** `tool`, `A2A`, `CrewAI`

### PDF RAG Assistant

[PDF RAG Assistant](./examples/pdf_rag.md) is an agent-based system that answers user queries by retrieving information
from specified PDF files using Retrieval-Augmented Generation (RAG). It processes input through a frontman agent and a
PDF retrieval tool, enabling accurate responses from static documents.

**Tags:** `tool`, `RAG`

### Confluence RAG Assistant

[Confluence RAG Assistant](./examples/confluence_rag.md) answers user queries using RAG over Confluence pages by loading page content (and optional attachments), building a vector store, and retrieving relevant info to respond.

**Tags** `tool`, `RAG`

### Agentic RAG Assistant

[Agentic RAG Assistant](./examples/agentic_rag.md) is a modular multi-agent system that answers user queries by
retrieving information from the web, PDF documents, and Slack channels. It mimics a smart assistant that delegates tasks
to specialized tools and compiles responses into clear, helpful answers.

**Tags:** `tool`, `API`, `RAG`

## 🏢 Industry-Specific Examples

Examples tailored to specific industry applications.

### Intranet Agents

[Intranet Agents](examples/intranet_agents.md) is a multi-agent system that mimics the intranet of a major corporation.
It allows you to interact and get information from various departments such as IT, Finance, Legal, HR, etc.

**Tags:** `AAOSA`

### Intranet Agents With Tools

[Intranet Agents With Tools](examples/intranet_agents_with_tools.md) is a multi-agent system that mimics the intranet of
a major corporation. It allows you to interact and get information from various departments such as IT, Finance, Legal,
HR, etc. Some of the down-chain agents call coded tools.

**Tags:** `tool`, `API`, `AAOSA`

### Airline Policy 360 Assistant

[Airline Policy 360 Assistant](./examples/airline_policy.md) is a sophisticated multi-agent system designed to manage
and respond to customer inquiries by referring to related airline policies with structured delegation. It mimics a
real-world helpdesk with specialized teams, each handling a specific domain of airline policies such as baggage,
flights, international travel, and more.

**Tags:** `tool`, `API`, `AAOSA`

### Real Estate Agent

[Real Estate Agent](examples/real_estate.md) is a multi-agent system that provides help with real estate transaction
inquiries. The top-level "front-man" agent receives a question, and in coordination with down-chain agents, provides an
answer. Some of the down-chain agents call coded tools.

**Tags:** `tool`, `AAOSA`, `external_network`

### Consumer Decision Assistant Agents

[Consumer Decision Assistant](examples/consumer_decision_assistant.md) is a multi-agent system that calls other (B2C)
multi-agent systems that are not necessarily aligned.

**Tags:** `tool`, `AAOSA`,  `external_network`

### Therapy Vignette Supervision

[Therapy Vignette Supervision](examples/therapy_vignette_supervision.md) is an agentic therapy supervision group. Give
it a therapy vignette, and it will produce a consensus treatment plan after the various therapy experts offer their
opinion.

**Tags:** `AAOSA`

## 🧪 Experimental and Research

Cutting-edge examples for research and experimentation.

### Agent Network Designer

[Agent Network Designer](examples/agent_network_designer.md) is a multi-agent system to create multi-agent systems.
Enter the name of an organization or describe the use-case and will create an agent network hocon for you and save it to
your registries directory and give you some usage examples.

**Tags:** `tool`

### KWIK Agents

[KWIK_agents](examples/kwik_agents.md) is a basic multi-agent system with memory.

**Tags:** `tool`, `memory`

### CRUSE

[CRUSE](examples/cruse.md) is an agent that can dynamically attach to any agent in your registry and make it run with a context reactive user experience. This is a good example of how to switch down-chain agents dynamically using coded tools and sly_data.

**Tags:** `tool`, `ui`, `app`

### Conscious Assistant

[Conscious Agent](examples/conscious_agent.md) is a multi-agent system used within the conscious assistant and
serves as a good example of how to run an agent permanently.

**Tags:** `tool`, `memory`, `app`

### Log Analyzer

[Log Analyzer](examples/log_analyzer.md) is a multi-agent system used within the log analyzer app and serves as a
good example of how to run an agent network on an agent network log for various validations.

**Tags:** `AAOSA`, `app`