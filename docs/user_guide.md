# User guide

<!--TOC-->

- [User guide](#user-guide)
  - [Simple agent network](#simple-agent-network)
  - [Hocon files](#hocon-files)
    - [Import and Substitution](#import-and-substitution)
    - [Manifest](#manifest)
    - [Agent network](#agent-network)
      - [Agent specifications](#agent-specifications)
      - [Tool specifications](#tool-specifications)
      - [LLM specifications](#llm-specifications)
  - [LLM configuration](#llm-configuration)
    - [OpenAI](#openai)
    - [AzureOpenAI](#azureopenai)
    - [Ollama](#ollama)
  - [Multi-agent networks](#multi-agent-networks)
  - [Coded tools](#coded-tools)
    - [Simple tool](#simple-tool)
    - [API calling tool](#api-calling-tool)
    - [Sly data](#sly-data)
  - [Toolbox](#toolbox)
  - [Logging and debugging](#logging-and-debugging)
  - [Advanced](#advanced)
    - [Subnetworks](#subnetworks)
    - [AAOSA](#aaosa)
  - [Connect with other agent frameworks](#connect-with-other-agent-frameworks)

<!--TOC-->

## Simple agent network

The `music_nerd` agent network is the simplest agent network possible: it contains a single agent
that answers questions about music since the 60s. See its description here: [docs/examples/music_nerd.md](../docs/examples/music_nerd.md).

The steps to start the server and the client are described in the [README](../README.md).
When starting, the first thing the server will do is load the agent network configurations
from the "manifest" file. The manifest file is specified by the `AGENT_MANIFEST_FILE` environment variable:
```
AGENT_MANIFEST_FILE="./registries/manifest.hocon"
```
Open [./registries/manifest.hocon](../registries/manifest.hocon) and look at its contents. It should look something like this:
```hocon
{
    # ... other agent networks ... #
    "music_nerd.hocon": true,
    # ... other agent networks ... #
}
```
This tells the server to load the `music_nerd.hocon` file from the same `/registries` folder.

Setting the value to `false` would make the server ignore this agent network.

Open [../registries/music_nerd.hocon](../registries/hello_world.hocon) and have a look at it.
For now just note that it contains:
- an `llm_config` section that specifies which LLM to use by default for the agents in this file
- a `tools` section that contains a single agent, the "frontman", called `MusicNerd`

Read the instructions of the agent to see what it does.
Feel free to modify the instructions to see how it affects the agent's behavior.
See if you can make it a soccer expert for instance!

We'll describe the structure of agent networks' `.hocon` files in next section.

## Hocon files

### Import and Substitution

HOCON files support importing content from other HOCON files using the unquoted keyword `include`, followed by whitespace and the path to the imported file as a quoted string:
```hocon
include "config.hocon"
```
> **Note**: The file path in include should be an **absolute path** to ensure it can be resolved correctly.

HOCON supports value substitution by referencing previously defined configuration values. This allows constants to be defined once and reused throughout the file.

To substitute a value, wrap the referenced key in `${}`:
```hocon
"function": ${aaosa_call}
```

To substitute a nested value inside an object or dictionary, use dot notation:
```hocon
"name": ${info.name}
```

Note that substitutions are **not parsed inside quoted strings**. If you need to include a substitution within a string, you can quote only the non-substituted parts:
```hocon
"instructions": ${instruction_prefix} "main instruction" ${instruction_suffix}
```
You can see a working example here: [../registries/smart_home_include.hocon](../registries/smart_home_include.hocon).

For more details, please see [https://github.com/lightbend/config/blob/main/HOCON.md#substitutions](https://github.com/lightbend/config/blob/main/HOCON.md#substitutions)

### Manifest

A manifest file is a list of agent network configurations that the server will load.

It's simple dictionary where the keys are the names of the agent network configuration files
and the values are booleans. For instance:
```hocon
{
    "agent_network_A.hocon": true,
    "agent_network_B.hocon": false,
    "agent_network_C.hocon": true,
}
```
In this example the server will load agent networks A and C but not B.

When you start the server, you can see which agent networks have been loaded by looking at the logs:
```
> python -m neuro_san.service.agent_main_loop --port 30011

tool_registries found: ['agent_network_A', 'agent_network_C']
```

For more details, please check the [Agent Manifest HOCON File Reference](https://github.com/cognizant-ai-lab/neuro-san/blob/main/docs/manifest_hocon_reference.md) documentation.

### Agent network

#### Agent specifications

| **Field**    | **Description**                                                                                                                              |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| agent_name   | text handle for other agent specs and hosting system to refer to                                                                             |
| function     | Open AI function spec (standard) that formally describes the various inputs that the agent expects                                           |
| instructions | text that sets up the agent in detail for its task                                                                                           |
| command      | text that sets the agent in motion after it receives all its inputs                                                                          |
| tools        | optional list of references to other agents that this agent is allowed to call in the course of working through their input and instructions |
| llm_config   | optional agent-specification for different LLMs for different purposes such as specialization, costs, etc.                                   |

#### Tool specifications

| **Field**     | **Description**                                                                                   |
|---------------|---------------------------------------------------------------------------------------------------|
| agent_name    | text handle for other agent specs to refer to                                                     |
| function      | Open AI function spec (standard) that formally describes the various inputs that the tool expects |
| method        | Code reference to the function that is to be invoked when the tool is called.                     |

#### LLM specifications

| **Field**   | **Description**                                                                                                                       |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------|
| model_name  | name of the model to use (i.e. “gpt-4o”, “claude-3-haiku”)                                                                            |
| *_api_key   | api key value or environment variable to reference to allow access to the LLM provider if different from hosting environment default. |
| temperature | optional level of randomness 0.0-1.0 to use for LLM results                                                                           |

See next section for more information about how to specify the LLM(s) to use.

For a full description of the fields, please refer to the [Agent Network HOCON File Reference](https://github.com/cognizant-ai-lab/neuro-san/blob/main/docs/agent_hocon_reference.md) documentation.

## LLM configuration

The `llm_config` section of the agent network configuration file specifies which LLM to use
for the agents in this file. It can be specified:
- at the agent network level, to apply to all agents in this file
- at the agent level, to apply to a specific agent

For a full description of the fields, please refer to the [LLM config](https://github.com/cognizant-ai-lab/neuro-san/blob/main/docs/agent_hocon_reference.md#llm_config) documentation.

For instructions about how to extend the default LLM descriptions shipped with the `neuro-san` library,
please refer to the [LLM Info HOCON File Reference](https://github.com/cognizant-ai-lab/neuro-san/blob/main/docs/llm_info_hocon_reference.md) documentation.

### OpenAI

To use an OpenAI LLM, set the `OPENAI_API_KEY` environment variable to your OpenAI API key
and specify which model to use in the `model_name` field:
```hocon
    "llm_config": {
        "model_name": "gpt-4o",
    },
```

See [./examples/music_nerd.md](./examples/music_nerd.md) for an example.

### AzureOpenAI

If you are using Azure OpenAI in your hocon file, you might need to set the `llm_config` to use the right model.<br>

For example:
```hocon
"llm_config": {
        "model_name": "azure-gpt-4o",
        "openai_api_version": "your_api_version",
        "azure_endpoint": "your_end_point",
        "deployment_name": "your_deployment_name"
},
```

You can set some of these as environment variables or add them in your .env file in order to use Azure OpenAI:  
AZURE_OPENAI_ENDPOINT="https://your_base_url.openai.azure.com"  
OPENAI_API_VERSION="<your Azure OpenAI API version e.g. 2024-12-01-preview>"  
OPENAI_API_KEY="your Azure OpenAI API key"  

> **Note**: Some Azure OpenAI deployments may have a lower `max_tokens` limit than the default associated with the `model_name` in Neuro-San.
If the `max_tokens` value in your `llm_config` exceeds the actual limit of the model specified by `deployment_name`, the LLM will fail to return a response — even if the prompt itself is within limits. To fix this, explicitly set a `max_tokens` value in your `llm_config` that matches the deployed model’s actual capacity.

See [Azure OpenAI Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=keyless%2Ctypescript-keyless%2Cpython-new%2Ccommand-line&pivots=programming-language-python) for more information.


### Ollama

To use an LLM that runs locally with [Ollama](https://ollama.com/):
- Make sure the Ollama server is running
- Make sure the model is downloaded, up to date and available in the Ollama server. For instance, `ollama run llama3.1`
  will download the model and make it available for use. `ollama pull llama3.1`
  will update the model to the latest version if needed.
- If the agent network contains tools, make sure the model can call tools:
  see [Ollama's documentation for models that support tools](https://ollama.com/search?c=tools)
- Set the `class` and `model_name` fields in the `llm_config` section of the agent network configuration file:
```hocon
    "llm_config": {
        "class": "ollama",
        "model_name": "llama3.1",
    },
```

See [./examples/music_nerd_pro_local.md](./examples/music_nerd_pro_local.md) for an example.

For more information about how to use Ollama with LangChain,
see [this page](https://python.langchain.com/docs/integrations/chat/ollama/)


## Multi-agent networks

## Coded tools

Coded tools are coded functionalities that extend agent's capabilities beyond its core reasoning capabilities and allow it to interact with databases, APIs, and external services.

### Simple tool

[music_nerd_pro](https://github.com/cognizant-ai-lab/neuro-san-studio/blob/main/docs/examples.md#music-nerd-pro) is a simple agent that helps with music-related inquiries. It uses a simple coded tool which is implemented in Python -- The coded tool does not call an API.

### API calling tool

[intranet_agents_with_tools](https://github.com/cognizant-ai-lab/neuro-san-studio/blob/main/docs/examples.md#intranet-agents-with-tools) is a multi-agent system that mimics the intranet of a major corporation. It allows you to interact with and get information from various departments such as IT, Finance, Legal, HR, etc. The HR agent calls a coded tool implemented in Python that calls HCM APIs.

### Sly data

A `sly_data` dictionary can be passed along with the `ChatRequest` from the client side.
The `sly_data` will not be seen by the LLMs, and by default, will not leave the agent network.
Within the agent network the `sly_data` is visible to the coded tools and can be used as a
bulletin-board between coded tools.

This policy is one of security-by-default, whereby no `sly_data` gets out of the agent network
at all unless otherwise specified. It's only when a boundary is crossed that the question of
what goes through arises. There are 3 boundaries:

1.  What goes out to external networks (`to_downstream`). For instance, you may not want to send
    credentials to an agent network that lives on another server.
2.  What comes in from external networks (`from_upstream`). For instance, you might not trust what's
    coming from an agent network that lives on another server.
3.  What goes back to the client (`to_upstream`). For instance, you might not want secrets from
    the server side to be shared with the clients that connect to it.

So by default nothing is shared, and you have to explicitly state what goes through.

Suppose you have an agent network that takes in two numbers,
the name of an operation (say, addition/subtraction/multiplication/division), and asks another
agent network to perform the operation on the numbers. To pass the numbers as `sly_data` to the
downstream agent network you must specify the following in the .hocon file of the agent that
is connecting to the downstream agent network:

```hocon
"allow": {
    "to_downstream": {
        # Specifying this allows specific sly_data
        # keys from this agent network to be sent
        # to downstream agent networks
        "sly_data": ["x", "y"]
   }
}
```

To get `sly_data` coming back from a downstream agent network, i.e., to get the result of
adding two numbers, you must specify the following in the .hocon file of the agent that is
connecting to the downstream agent network:

```hocon
"allow": {
    "from_downstream": {
        # Specifying this allows specific sly_data
        # keys to be ingested from downstream agent
        # networks as sly_data for this agent network
        "sly_data": ["equals"]
    }
}
```

To allow frontman agent to return `sly_data` to the client, you must specify the following in
the .hocon file of the frontman (the only agent that is connected to the client):

```hocon
"allow": {
    "to_upstream": {
        # Specifying this allows sly_data keys
        # from this network to be passed back
        # to the calling client
        "sly_data": ["equals"]
    }
}
```

All the above .hocon "allow" blocks can be combined in a single "allow" block. An example
is given [here](https://github.com/cognizant-ai-lab/neuro-san/blob/main/neuro_san/registries/math_guy_passthrough.hocon#L54)

For a full reference, please check the [neuro-san documentation](https://github.com/cognizant-ai-lab/neuro-san/blob/main/docs/agent_hocon_reference.md#allow)

## Toolbox

The **Toolbox** is a flexible and extensible system for managing tools that can be used by agents. It simplifies the integration of **LangChain** and **custom-coded tools** in a agent network configuration.

### Default tools in toolbox

#### Langchain tools

| Name               | Description                                           |
| ------------------ | ----------------------------------------------------- |
| `bing_search`      | Web search via Bing. Requires `BingSearchAPIWrapper`. |
| `tavily_search`    | Web search via Tavily. |
| `requests_get`     | HTTP GET requests.                                    |
| `requests_post`    | HTTP POST requests.                                   |
| `requests_patch`   | HTTP PATCH requests.                                  |
| `requests_put`     | HTTP PUT requests.                                    |
| `requests_delete`  | HTTP DELETE requests.                                 |
| `requests_toolkit` | Bundle of all above request tools.                    |

#### Coded tools

| Name             | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| `website_search` | Searches the internet via DuckDuckGo. |
| `rag_retriever`  | Performs RAG (retrieval-augmented generation) from given URLs. |



### Usage in agent network config

To use tools from toolbox in your agent network, simply call them with field `toolbox`:
```json
    {
        "name": "name_of_the_agent",
        "toolbox": "name_of_the_tool_from_toolbox"
    }
```

### Adding tools in toolbox
1. Create the toolbox configuration file. This can be either HOCON or JSON files.
2. Define the tools
    - langchain tools
        - Each tool or toolkit must have a `class` key.
        - The specified class must be available in the server's `PYTHONPATH`.
        - Additional dependencies (outside of `langchain_community`) must be installed separately.
        
        Example:
        ```hocon
            "bing_search": {
                # Fully qualified class path of the tool to be instantiated.
                "class": "langchain_community.tools.bing_search.BingSearchResults",

                # (Optional) URL for reference documentation about this tool.
                "base_tool_info_url": "https://python.langchain.com/docs/integrations/tools/bing_search/",

                # Arguments for the tool's constructor.
                "args": {
                    "api_wrapper": {
                        # If the argument should be instantiated as a class, specify it using the "class" key.
                        # This tells the system to create an instance of the provided class instead of passing it as-is.
                        "class": "langchain_community.utilities.BingSearchAPIWrapper"
                    },
                }
            }
        ```
    - coded tools
        - Similar to how one can define it in agent network config file
        - `description` let the agent know what the tool does.
        - `parameters` are arguments' definitions and types. This is optional.
        - `class` specifies the tool's implementation as **module.ClassName** where the module can be found in `AGENT_TOOL_PATH`.

        Example:
        ```json
            "rag_retriever": {
                "class": "rag.Rag",
                "description": "Retrieve information on the given urls",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "urls": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of url to retrieve info from"
                        },
                        "query": {
                            "type": "string",
                            "description": "Query for retrieval"
                        }
                    },
                    "required": ["urls", "query"]
                },
            }
        ```

        For more examples, please see [https://github.com/cognizant-ai-lab/neuro-san/blob/main/neuro_san/internals/run_context/langchain/toolbox/toolbox_info.hocon](https://github.com/cognizant-ai-lab/neuro-san/blob/main/neuro_san/internals/run_context/langchain/toolbox/toolbox_info.hocon)

3. Point to the config file by setting the environment variable `AGENT_TOOLBOX_INFO_FILE` to your custom config:

    ```bash
    export AGENT_TOOLBOX_INFO_FILE=/path/to/my_toolbox_config.hocon
    ```

## Logging and debugging

To debug your code, set up your environment per instructions [here](https://github.com/cognizant-ai-lab/neuro-san-studio).
Furthermore, please install the build requirements in your virtual environment via the following commands:

```
. ./venv/bin/activate
pip install -r requirements-build.txt
```

2. Suppose you want to debug the coded tool for `music_nerd_pro` agent network. Add the following lines of code to the `music_nerd_pro`'s coded tool Python file (E.g., to the first line of `invoke` method in `Accountant` [class](https://github.com/cognizant-ai-lab/neuro-san-studio/blob/main/coded_tools/music_nerd_pro/accounting.py)

```
import pytest
pytest.set_trace()
```

3. Start the client and server via `python3 -m run`, select `music_berd_pro` agent network, and ask a question like `Where was John Lennon born?`.
The code execution stops at the line where you added `pytest.set_trace` statement. You can step through the code, view variable values, etc. by typing commands in the terminal. For all the debugger options, please refer to pdb documentation [here](https://ugoproto.github.io/ugo_py_doc/pdf/Python-Debugger-Cheatsheet.pdf)

The client and server logs will be saved to `logs/nsflow.log` and `logs/server.log` respectively.

## Advanced

- Tools' arguments can be overidden in the agent network config file using the `args` key.
Example:
```hocon
{
    "name": "web_searcher",
    "toolbox": "bing_search",
    "args": {
                # This will override the number of search results to 3
                "num_results": 3
            }
}
```


### Subnetworks

### AAOSA

AAOSA stands for **A**daptive **A**gent **O**riented **S**oftware **A**rchitecture.

In this architecture, agents decide if they can answer inquiries or if they need to call other agents to help them.

Reference:
[Iterative Statistical Language Model Generation for Use with an
Agent-Oriented Natural Language Interface ](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=3004005f1e736815b367be83f2f90cc0fa9e0411)

<!-- (https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=011fb718658d611294613286c0f4b143aed40f43) -->

Look at [../registries/smart_home.hocon](../registries/smart_home.hocon) and in particular:
- aaosa_instructions
- aaosa_call
- aaosa_command

## Connect with other agent frameworks

- MCP: [MCP BMI SSE](./examples/mcp_bmi_sse.md) is an example of an agent network that uses [MCP](https://www.anthropic.com/news/model-context-protocol)
to call an agent that calculates the body mass index (BMI).
- A2A: [A2A research report](./examples/a2a_research_report.md) is an example of an agent network that uses a coded tool as an A2A client to
connect to CrewAI agents running in an A2A server to write a report on a provided topic.
- CrewAI: see the A2A example above.
- Agentforce: [Agentforce](./examples/agentforce.md) is an agent network that delegates queries to a [Salesforce Agentforce](https://www.salesforce.com/agentforce/)
agent to interact with a CRM system.
- Agentspace: [Agentspace_adapter](./examples/agentspace_adapter.md) is an agent network adapter that delegates queries to a [Google Agentspace](https://cloud.google.com/agentspace/agentspace-enterprise/docs/overview) agent to interact with different data store connectors on google cloud.
