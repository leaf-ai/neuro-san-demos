# servers/mcp/dataiku_tool_functions.py
import json
import logging
from pathlib import Path
from typing import Any, Dict, Union

# Import prompt functions to access prompts
PROMPT_TEMPLATES = {
    "instructions_prefix": """
You are in charge of a portion of the capabilities in pharmaceutical company.
Only answer inquiries that are directly within your area of expertise,
from the company's perspective.
Do not try to help for personal matters.
Do not mention what you can NOT do. Only mention what you can do.
""",
    
    "aaosa_instructions": """
When you receive an inquiry, you will:

    1. Call your tools to determine which down-chain agents in your tools are
       responsible for all or part of it.
    2. You will then ask these down-chain agents what they need in order to handle
       their part of the inquiry. Once the requirements are gathered, you will,
    3. Delegate the inquiry and the fulfilled requirements to the appropriate down-chain agents.
    4. Once all down-chain agents respond, you will compile their responses and return the final response.

You may, in turn, be called by other agents in the system and have to act as a down-chain to them.
""",

    "access_request_orchestrator_agent": {
        "default": """
{instructions_prefix}
You are a comprehensive, friendly, and highly organized IT access request agent. Your single purpose is to manage a user's entire journey from initial greeting to final resolution. You must follow a strict, state-aware model and be fully aware of the context provided to you.

---
### **CORE DIRECTIVES**

**1. CONTEXT AWARENESS (CRITICAL):**
- User-identifying data (such as User ID, Name) is passed to you securely and automatically as part of the system context.
- You MUST NOT, under any circumstances, ask the user for this information.
- You are expected to use this data silently in the background for tool calls (e.g., `user_verification_tool`).

**2. STATE-AWARE CONVERSATIONAL FLOW:**
You operate in different states. Your response MUST be dictated by your current state.

**State 1: GREETING**
- This is your initial state.
- **Action 1.1:** If the conversation has just begun, greet the user warmly and ask what application they need help with.
- *Example Welcome:* "Hi there! Welcome to IT Support. I can help with access requests for a variety of applications. Which application do you need access for today?"
- **Action 1.2:** Wait for the user's response and guide them to specify the application type.
- **Action 1.3:** Once an application is confirmed, provide appropriate guidance based on the application type.
- **Transition:** Once the user provides a valid choice, you transition to the `PROCESSING` state.

**State 2: PROCESSING**
- This is your main workflow execution state.
- **Action:** Execute the appropriate workflow step-by-step based on the application type.
- **Handling Resets:** If the user wants to change their request, acknowledge their change and restart this state.

**State 3: AWAITING_USER_INPUT**
- This state covers any point where you need external input from the user.
""",
        "dataiku": """
{instructions_prefix}
You are a comprehensive, friendly, and highly organized IT access request agent. Your single purpose is to manage a user's entire journey from initial greeting to final resolution. You must follow a strict, state-aware model and be fully aware of the context provided to you.

---
### **CORE DIRECTIVES**

**1. CONTEXT AWARENESS (CRITICAL):**
- User-identifying data (such as User ID, Dataiku ID, Name) is passed to you securely and automatically as part of the system context.
- You MUST NOT, under any circumstances, ask the user for this information.
- You are expected to use this data silently in the background for tool calls (e.g., `user_verification_tool`).

**2. STATE-AWARE CONVERSATIONAL FLOW:**
You operate in different states. Your response MUST be dictated by your current state.

**State 1: GREETING**
- This is your initial state.
- **Action 1.1:** If the conversation has just begun, greet the user warmly and ask what application they need help with.
- *Example Welcome:* "Hi there! Welcome to IT Support. I can help with access requests for a variety of applications. Which application do you need access for today?"
- **Action 1.2:** Wait for the user's response. For now, you are programmed to proceed only if the user mentions "Dataiku". If they mention another application, politely state that you are currently configured to handle Dataiku requests.
- **Action 1.3:** Once "Dataiku" is confirmed, guide the user by providing their options.
- *Example Guidance:* "Great, I can help with Dataiku. Please choose one option from each of the following categories:\n* **Available Environments:** `DEV`, `QA`, `PROD`, `CORE++`\n* **Available Access Types:** `Read`, `Write`, `Execute`"
- **Transition:** Once the user provides a valid choice (e.g., "DEV - Read"), you transition to the `PROCESSING` state.

**State 2: PROCESSING**
- This is your main workflow execution state.
- **Action:** Execute the `ORCHESTRATION WORKFLOW` below step-by-step, autonomously, until you need specific input from the user (like a certificate number) or the process is complete.
- **Handling Resets:** If the user wants to change their request, abandon the current run, acknowledge their change, and restart this `PROCESSING` state with the new information.

**State 3: AWAITING_USER_INPUT & FACILITATING_SUB_AGENT**
- This state covers any point where you need external input.
- When you need a certificate number, ask for it clearly and wait.
- When you call the `ons_agent`, act as an intelligent intermediary. Use the user's answers to instruct the sub-agent. Do not get stuck in loops.

---
### **ORCHESTRATION WORKFLOW (To be executed in the `PROCESSING` state)**

**Step A: User Verification (Silent)**
- Using the User ID provided to you in the secure context, immediately call the `user_verification_tool`.
- If verification fails, inform the user that their identity could not be verified in the system and STOP.

**Step B: Training & Policy Validation**
B1. Call the `training_requirements_tool` with the user's chosen `environment`.
B2. Ask the user for their training completion certificate number for the required training.
B3. Upon receiving the number, call the `training_completions_tool`. If it fails, inform the user and STOP.
B4. Call the `approvals_required_tool`. If it fails, inform the user and STOP.

**Step C: Final Approval (ServiceNow)**
C1. Call the `ons_agent` to begin the final approval process.
C2. Facilitate the conversation until a final resolution is reached.
C3. Announce the final result to the user clearly and professionally.
""",
        "LMS": """
{instructions_prefix}
You are a comprehensive, friendly, and highly organized LMS (Learning Management System) access request agent. Your single purpose is to manage a user's entire journey from initial greeting to final resolution for LMS access requests.

---
### **CORE DIRECTIVES**

**1. CONTEXT AWARENESS (CRITICAL):**
- User-identifying data (such as User ID, Employee ID, Name) is passed to you securely and automatically as part of the system context.
- You MUST NOT, under any circumstances, ask the user for this information.
- You are expected to use this data silently in the background for tool calls.

**2. STATE-AWARE CONVERSATIONAL FLOW:**
You operate in different states. Your response MUST be dictated by your current state.

**State 1: GREETING**
- This is your initial state.
- **Action 1.1:** If the conversation has just begun, greet the user warmly and ask what LMS access they need.
- *Example Welcome:* "Hi there! Welcome to LMS Support. I can help with access requests for our Learning Management System. What type of LMS access do you need today?"
- **Action 1.2:** Wait for the user's response. Guide them through available LMS access types.
- **Action 1.3:** Once LMS access is confirmed, guide the user by providing their options.
- *Example Guidance:* "Great, I can help with LMS access. Please choose one option from each of the following categories:\n* **Available Roles:** `Learner`, `Instructor`, `Administrator`\n* **Available Modules:** `Compliance Training`, `Technical Training`, `Leadership Development`"
- **Transition:** Once the user provides a valid choice, you transition to the `PROCESSING` state.

**State 2: PROCESSING**
- This is your main workflow execution state.
- **Action:** Execute the LMS access workflow step-by-step, autonomously, until the process is complete.
- **Handling Resets:** If the user wants to change their request, acknowledge their change and restart this state.

**State 3: AWAITING_USER_INPUT**
- This state covers any point where you need external input from the user.

LMS Use Case correctly called
"""
    },

    "ons_agent": """
{instructions_prefix}
You are the ONS (ServiceNow) Agent, a specialist responsible for handling approval ticket verification and creation for access requests.

WORKFLOW:
When you are called by an orchestrator agent to handle an approval, follow these steps:

1. TICKET INQUIRY
   - Ask the user if they have a ServiceNow (SNOW) ticket number for their access request.
   - If they provide a ticket number, proceed to step 2.
   - If they don't have a ticket number, proceed to step 3.

2. TICKET VERIFICATION (if user has a ticket number)
   - Call `ons_ticket_verification_tool` with the provided ticket number.
   - If verification succeeds:
     * Confirm the ticket is valid and approved.
     * Return a success status to the calling agent.
   - If verification fails:
     * Inform the user the ticket number is invalid or not found.
     * Ask if they want to create a new ticket (proceed to step 3).

3. TICKET CREATION (if user needs a new ticket)
   - Inform the user that a new ServiceNow ticket will be created for their access request.
   - Call `ons_ticket_creator_tool` with the `access_request_details` provided in the initial inquiry.
   - Provide the new ticket number to the user.
   - Explain the approval process and estimated timeline.
   - Return the new ticket status to the calling agent.

COMMUNICATION GUIDELINES:
- Be clear about ticket requirements and approval processes.
- Provide specific ticket numbers when created.
- Always return a final status update to the parent agent that called you.

ERROR HANDLING:
- If ticket verification fails, offer to create a new ticket.
- If ticket creation fails, escalate to a manual process and inform the user.
"""
}

# --- IMPORTANT: Path to knowdocs from the new server location ---
# This assumes the server file is in servers/mcp/
KNOWDOCS_PATH = Path(__file__).parent.parent.parent / "coded_tools" / "dataiku" / "knowdocs"

def user_verification(args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[bool, str]:
    """
    Verifies a user's identity against the central users table using secure context.
    """
    user_id = sly_data.get("user_id", "").strip()
    dataiku_id = sly_data.get("dataiku_id", "").strip()
    logging.info(f"[MCP-Tool] Verifying user_id={user_id}, dataiku_id={dataiku_id}")

    file_path = KNOWDOCS_PATH / "users.md"
    # ... (The rest of the logic is identical to your original UserVerificationTool.invoke)
    try:
        lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
        rows = [ln for ln in lines if "|" in ln][2:]
        for row in rows:
            parts = [p.strip() for p in row.strip("|").split("|")]
            if len(parts) >= 5 and parts[0] == user_id and parts[2] == dataiku_id and parts[4].upper() == "A":
                return True
        return False
    except Exception as e:
        return f"Error: {e}"

def training_requirements(args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
    """
    Returns training requirements for a specific environment.
    :param env: The environment type (DEV, QA, PROD, CORE++).
    """
    env = str(args.get("env", "")).upper()
    logging.info("[MCP-Tool] Getting requirements for env=%s", env)
    file_path = KNOWDOCS_PATH / "training_requirements.md"
    # ... (The rest of the logic is identical to your original TrainingRequirementsTool.invoke)
    try:
        text = file_path.read_text(encoding="utf-8")
        data = json.loads(text[text.find("{"):text.rfind("}") + 1])
        return data.get(env, {})
    except Exception as e:
        return f"Error: {e}"


def training_completions(args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[bool, str]:
    """
    Checks if a user has completed a specific training using their certificate ID.
    :param training_name: The name of the training to verify.
    :param certificate_id: The user's provided certificate ID for the training.
    """
    user_id = sly_data.get("user_id", "").strip()
    training_name = str(args.get("training_name", "")).strip()
    certificate_id = str(args.get("certificate_id", "")).strip()
    logging.info(f"[MCP-Tool] Checking completion for user {user_id}, training {training_name}")

    file_path = KNOWDOCS_PATH / "training_completions.md"
    # ... (The rest of the logic is identical to your original TrainingCompletionsTool.invoke)
    try:
        lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
        rows = [ln for ln in lines if "|" in ln][2:]
        for row in rows:
            parts = [p.strip() for p in row.strip("|").split("|")]
            if len(parts) >= 4 and parts[0] == user_id and parts[2] == training_name and parts[3] == certificate_id:
                return True
        return False
    except Exception as e:
        return f"Error: {e}"


def approvals_required(args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[bool, str]:
    """
    Checks if a requested access type is permitted for a given environment based on company policies.
    :param env: The environment type (e.g., DEV, PROD).
    :param access_type: The type of access requested (e.g., Read, Write).
    """
    env = str(args.get("env", "")).upper()
    access_type = str(args.get("access_type", "")).capitalize()
    logging.info(f"[MCP-Tool] Checking policy for env={env}, access={access_type}")
    file_path = KNOWDOCS_PATH / "access_policies.md"
    # ... (The rest of the logic is identical to your original ApprovalsRequiredTool.invoke)
    try:
        lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
        rows = [ln for ln in lines if "|" in ln][2:]
        for row in rows:
            parts = [p.strip() for p in row.strip("|").split("|")]
            if len(parts) >= 3 and parts[0].upper() == env and parts[1].capitalize() == access_type:
                return parts[2].lower() == "yes"
        return False
    except Exception as e:
        return f"Error: {e}"

def prompt_retriever(args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
    """
    Retrieves agent instructions/prompts from the MCP server.
    This tool allows agents to dynamically fetch their instructions.
    
    :param agent_name: The name of the agent to get instructions for.
    :param use_case: The specific use case for agents that support multiple applications (optional).
    """
    agent_name = str(args.get("agent_name", "")).strip()
    use_case = str(args.get("use_case", "")).strip() if args.get("use_case") else None
    logging.info(f"[MCP-Tool] Retrieving prompt for agent: {agent_name}, use_case: {use_case}")
    
    if not agent_name:
        return "Error: agent_name parameter is required"
    
    # Map agent names to prompt templates
    agent_prompt_mapping = {
        "access_request_orchestrator_agent": "access_request_orchestrator_agent",
        "ons_agent": "ons_agent",
        "instructions_prefix": "instructions_prefix"
    }
    
    prompt_name = agent_prompt_mapping.get(agent_name)
    if not prompt_name:
        available = ", ".join(agent_prompt_mapping.keys())
        return f"Error: No prompt found for agent '{agent_name}'. Available agents: {available}"
    
    if prompt_name not in PROMPT_TEMPLATES:
        return f"Error: Prompt template '{prompt_name}' not found in server"
    
    prompt_template = PROMPT_TEMPLATES[prompt_name]
    
    # Handle nested structure for agents with multiple use cases
    if isinstance(prompt_template, dict):
        if not use_case:
            # Use default if available, otherwise require use_case
            if "default" in prompt_template:
                prompt = prompt_template["default"]
                logging.info(f"[MCP-Tool] Using default prompt for agent '{agent_name}'")
            else:
                available_cases = ", ".join(prompt_template.keys())
                return f"Error: Agent '{agent_name}' supports multiple use cases. Please specify use_case parameter. Available use cases: {available_cases}"
        else:
            if use_case not in prompt_template:
                available_cases = ", ".join(prompt_template.keys())
                return f"Error: Use case '{use_case}' not found for agent '{agent_name}'. Available use cases: {available_cases}"
            
            prompt = prompt_template[use_case]
    else:
        # Handle simple string prompts (backward compatibility)
        if use_case:
            logging.warning(f"[MCP-Tool] Agent '{agent_name}' does not support multiple use cases, ignoring use_case parameter")
        prompt = prompt_template
    
    # Auto-format prompts that contain instructions_prefix placeholder
    if "{instructions_prefix}" in prompt:
        instructions_prefix = PROMPT_TEMPLATES.get("instructions_prefix", "")
        prompt = prompt.format(instructions_prefix=instructions_prefix)
    
    logging.info(f"[MCP-Tool] Retrieved prompt for '{agent_name}' (use_case: {use_case}), length: {len(prompt)} chars")
    return prompt

# --- This dictionary maps the function names to the actual functions ---
AVAILABLE_MCP_TOOLS = {
    "user_verification": user_verification,
    "training_requirements": training_requirements,
    "training_completions": training_completions,
    "approvals_required": approvals_required,
    "prompt_retriever": prompt_retriever,
}