ClientsConfig = [
    "MCP_CLIENT_AZURE_AI",
    "MCP_CLIENT_OPENAI",
    "MCP_CLIENT_GEMINI"
]

ServersConfig = [
    {
        "server_name": "REDHAT_MCP",
        "command": "uv",
        "args": [
            "--directory",
            "../servers/REDHAT_MCP/redhat-api-mcp",
            "run",
            "redhat_mcp_server.py"
        ]
    },
    {
        "server_name": "LANGSMITH_MCP",
        "command": "uv",
        "args": [
            "--directory",
            "../servers/LANGSMITH_MCP",
            "run",
            "python",
            "main.py"
        ]
    }
]
