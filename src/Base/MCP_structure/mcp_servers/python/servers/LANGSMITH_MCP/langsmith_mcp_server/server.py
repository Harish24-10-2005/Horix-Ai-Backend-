"""
MCP server for LangSmith SDK integration.
This server exposes methods to interact with LangSmith's observability platform:
- get_thread_history: Fetch conversation history for a specific thread
- get_prompts: Fetch prompts from LangSmith with optional filtering
- pull_prompt: Pull a specific prompt by its name
"""

import os

from mcp.server.fastmcp import FastMCP

from langsmith_mcp_server.langsmith_client import LangSmithClient
from langsmith_mcp_server.services import (
    register_prompts,
    register_resources,
    register_tools,
)

# Create MCP server
mcp = FastMCP("LangSmith API MCP Server")

# Default API key (will be overridden in main or by direct assignment)
# default_api_key = os.environ.get("LANGSMITH_API_KEY")
# default_api_key = "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"
# langsmith_client = LangSmithClient(default_api_key) if default_api_key else None

# Register all tools with the server using simplified registration modules
register_tools(mcp, langsmith_client= None)
register_prompts(mcp, langsmith_client = None)
register_resources(mcp, langsmith_client = None)


def main() -> None:
    """Run the LangSmith MCP server."""
    print("Starting LangSmith MCP server!")
    # Run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
