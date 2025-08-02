export const ClientsConfig: string[] = [
    "MCP_CLIENT_OPENAI",
    "MCP_CLIENT_AZURE_AI",
    "MCP_CLIENT_GEMINI"
]

export const ServersConfig: any[] = [
    {
        server_name: "LEETCODE_MCP",
        command: "node",
        args: [
            "../servers/LEETCODE_MCP/build/index.js"
        ],
        server_features_and_capability: "An MCP server enabling automated access to LeetCode's problems, solutions, and public data with optional authentication for user-specific features, supporting leetcode.com & leetcode.cn sites."
    },
    {
        server_name: "BUGSNAG_MCP",
        command: "node",
        args: [
            "../servers/BUGSNAG_MCP/build/index.js"
        ],
        server_features_and_capability: "A Model Context Protocol (MCP) server for interacting with Bugsnag. This server allows LLM tools like Cursor and Claude to investigate and resolve issues in Bugsnag."
    },
    {
        server_name: "anything-llm",
        command: "node",
        args: [
            "--directory",
            "../servers/anything-llm",
            "index.js"
        ],
        server_features_and_capability: "The all-in-one Desktop & Docker AI application with built-in RAG, AI agents, No-code agent builder, MCP compatibility,  and more."
    },
    {
        server_name: "notion-mcp-server",
        command: "node",
        args: [
            "--directory",
            "../servers/notion-mcp-server",
            "index.js"
        ],
        server_features_and_capability: "Official Notion MCP Server"
    },
    {
        server_name: "mcp-chrome",
        command: "node",
        args: [
            "--directory",
            "../servers/mcp-chrome",
            "index.js"
        ],
        server_features_and_capability: "Chrome MCP Server is a Chrome extension-based Model Context Protocol (MCP) server that exposes your Chrome browser functionality to AI assistants like Claude, enabling complex browser automation, content analysis, and semantic search."
    },
    {
        server_name: "youtube-mcp-server",
        command: "node",
        args: [
            "--directory",
            "../servers/youtube-mcp-server",
            "index.js"
        ],
        server_features_and_capability: "MCP Server for YouTube API, enabling video management, Shorts creation, and advanced analytics"
    }
]
