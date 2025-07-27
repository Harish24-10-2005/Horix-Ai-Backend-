ClientsConfig =[
    "MCP_CLIENT_AZURE_AI",
    "MCP_CLIENT_OPENAI",
	"MCP_CLIENT_GEMINI"
]
ServersConfig = [
{
        "server_name": "LANGSMITH_MCP",
        "command": "uv",
        "args": ["--directory", "../servers/LANGSMITH_MCP", "--directory", "langsmith-mcp-server/langsmith_mcp_server", "run", "server.py",
    {
        "server_name": "DATABASE_MCP",
        "command": "node",
        "args": ["--directory", "../../js/servers/DATABASE_MCP", "index.js",
    {
        "server_name": "WHAT_MCP",
        "command": "node",
        "args": ["--directory", "../../js/servers/WHAT_MCP", "index.js",
    {
        "server_name": "WHAT_MCP",
        "command": "node",
        "args": ["--directory", "../../js/servers/WHAT_MCP", "index.js"]
    }
]
    }
]
    }
]
    },
    {
		"server_name": "REDHAT_MCP",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/REDHAT_MCP/redhat-api-mcp",
			"run",
			"redhat_mcp_server.py"
		]
	},
    {
		"server_name": "PAGERDUTY_MCP",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/PAGERDUTY_MCP/pagerduty-mcp-server/src/pagerduty_mcp_server",
			"run",
            "python",
            "-m",
			"pagerduty_mcp_server"
		]
	},
    {
		"server_name": "BLENDER_MCP",
		"command":"uv",
		"args": [
			"--directory",
			"../servers/BLENDER_MCP/blender-mcp",
			"run",
            "python",
			"main.py"
		]
	}
]