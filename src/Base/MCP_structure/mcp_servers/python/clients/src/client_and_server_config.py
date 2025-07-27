ClientsConfig = [
    "MCP_CLIENT_AZURE_AI",
    "MCP_CLIENT_OPENAI",
    "MCP_CLIENT_GEMINI"
]

ServersConfig = [
    {
        "server_name": "LANGSMITH_MCP",
        "command": "uvx",
        "args": ["langsmith-mcp-server"],
        "env": {"LANGSMITH_API_KEY": "lsv2_demo_key_for_testing"}
    },
]
