# servers/mcp/dataiku_mcp_server.py
from flask import Flask, jsonify, request
from docstring_parser import parse
from dataiku_tool_functions import AVAILABLE_MCP_TOOLS

app = Flask(__name__)

@app.route('/dataiku_mcp/tools', methods=['GET'])
def get_tools():
    """Exposes the schema for all available tools."""
    tool_schemas = []
    for name, func in AVAILABLE_MCP_TOOLS.items():
        docstring = parse(func.__doc__)
        # Note: We are not exposing user_id/sly_data params in the schema
        # because the agent shouldn't have to provide them. The adapter handles it.
        params_props = {
            p.arg_name: {"type": "string", "description": p.description}
            for p in docstring.params
        }
        tool_schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": docstring.short_description,
                "parameters": {
                    "type": "object",
                    "properties": params_props,
                    "required": list(params_props.keys())
                }
            }
        })
    return jsonify(tool_schemas)

@app.route('/dataiku_mcp/invoke/<tool_name>', methods=['POST'])
def invoke_tool(tool_name):
    """Invokes a specific tool by name."""
    if tool_name not in AVAILABLE_MCP_TOOLS:
        return jsonify({"error": f"Tool '{tool_name}' not found."}), 404

    try:
        # The adapter will send a payload with both 'args' and 'sly_data'
        payload = request.get_json()
        args = payload.get("args", {})
        sly_data = payload.get("sly_data", {})

        func = AVAILABLE_MCP_TOOLS[tool_name]
        result = func(args=args, sly_data=sly_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run this server on a new port, e.g., 5002
    app.run(port=5002, debug=True)