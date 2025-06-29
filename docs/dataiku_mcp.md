# Dataiku MCP Migration 

This documentation is for the migrated implementation of the Dataiku-based application to MCP architecture.


## Structure

```bash
neuro-san-demos_root/
├── servers/
│   └── mcp/
│       ├── dataiku_tool_functions.py
│       └── dataiku_mcp_server.py
├── coded_tools/
│   └── dataiku/
│       └── knowdocs/
│           ├── users.md
│           ├── training_requirements.md
│           ├── training_completions.md
│           └── access_policies.md
├── registries/
│   └── dataiku.hocon
├── run.py
└── README.md
```

## Migration Details

### Stage 1: Analysis & Planning

Identified the optimal logical grouping for migration:

- **Migrated Tools** (Dataiku Validation Service):
  - `UserVerificationTool`
  - `TrainingRequirementsTool`
  - `TrainingCompletionsTool`
  - `ApprovalsRequiredTool`

- **Local Tools** (not migrated):
  - `ONSTicketCreatorTool`
  - `ONSTicketVerificationTool`

### Stage 2: Build the MCP Server

Implemented the new MCP server hosting the decoupled validation logic:

- **Server Logic** (`dataiku_tool_functions.py`): Contains refactored tool logic as Python functions.
- **Server Application** (`dataiku_mcp_server.py`): Flask API server exposing validation endpoints.

### Stage 3: HOCON Refactor

The Neuro SAN agent (`access_request_orchestrator_agent`) is reconfigured to use the MCP service:

- Defined MCP adapter (`dataiku_validation_service_mcp`) for communicating with the MCP server.
- Retained local configuration for ServiceNow (ONS) integration.


### Running Instructions

1. **Launch MCP Server:**

```bash
python servers/mcp/dataiku_mcp_server.py
```

The MCP server starts on port `5002`.

2. **Launch Neuro SAN Application:**

```bash
python -m run.py
```

3. **Interact with the Application:**

Use the web UI to interact with the `access_request_orchestrator_agent`. Provide minimal input, and the agent handles validation via the MCP server.

#### Example Interaction:

- **User Message:**
  ```
  Hi, I need Read access to the DEV environment for Dataiku.
  ```

- **Session Context:**
  ```json
  {
    "sly_data": {
      "user_id": "100",
      "dataiku_id": "300",
      "name": "Gordon Banks"
    }
  }
  ```

