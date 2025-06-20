
"""Example of MCP server"""
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("BMI", port=8000)


# langchain-mcp-adapter only support mcp tools but not resources or prompts.
# Function's name, docstring, and argument annotation are converted to
# attribute `nanme`, `description`, and `args_schema`, respectively.
@mcp.tool()
def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight / (height ** 2)


if __name__ == "__main__":
    # streamable http is prefered over stdio as transport method.
    mcp.run(transport="streamable-http")
