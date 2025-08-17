ClientsConfig = [
    "MCP_CLIENT_AZURE_AI",
    "MCP_CLIENT_OPENAI",
    "MCP_CLIENT_GEMINI"
]

ServersConfig = [
    {
        "server_name": "manim-mcp",
        "command": "python",
        "args": ["-m", "manim-mcp"],
        "env": {}
    },
    {
        "server_name": "mcp-git-ingest",
        "command": "python",
        "args": ["-m", "mcp-git-ingest"],
        "env": {}
    },
    {
        "server_name": "youtube_video_mcp",
        "command": "uv",
        "args": ["--directory", "../servers/youtube_video_mcp", "run", "python", "-m", "youtube_video_mcp"],
        "env": {}
    },
    {
        "server_name": "mcp-wikipedia",
        "command": "python",
        "args": ["main.py"],
        "env": {}
    },
]

