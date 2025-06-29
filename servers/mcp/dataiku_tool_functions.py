# servers/mcp/dataiku_tool_functions.py
import json
import logging
from pathlib import Path
from typing import Any, Dict, Union

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


# --- This dictionary maps the function names to the actual functions ---
AVAILABLE_MCP_TOOLS = {
    "user_verification": user_verification,
    "training_requirements": training_requirements,
    "training_completions": training_completions,
    "approvals_required": approvals_required,
}