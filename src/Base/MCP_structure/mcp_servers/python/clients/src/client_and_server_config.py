ClientsConfig = [
    "MCP_CLIENT_AZURE_AI",
    "MCP_CLIENT_OPENAI",
    "MCP_CLIENT_GEMINI"
]

ServersConfig = [
    {
        "server_name": "LANGSMITH_MCP",
        "command": "uvx",
        "args": [
            "langsmith-mcp-server"
        ],
        "env": {
            "LANGSMITH_API_KEY": "lsv2_demo_key_for_testing"
        }
    },
    {
        "server_name": "mcp-context-forge",
        "command": "uv",
        "args": [
            "--directory",
            "../servers/mcp-context-forge",
            "run",
            "main.py"
        ],
        "env": {}
    },
    {
        "server_name": "youtube-mcp-server",
        "command": "node",
        "args": [
            "../servers/youtube-mcp-server/build/index.js"
        ],
        "env": {}
    },
    {
        "server_name": "1Panel",
        "command": "node",
        "args": [
            "../servers/1Panel/build/index.js"
        ],
        "env": {}
    },
    {
        "server_name": "mcp-server-docker",
        "command": "uv",
        "args": [
            "--directory",
            "../servers/mcp-server-docker",
            "run",
            "main.py"
        ],
        "env": {}
    }
]
