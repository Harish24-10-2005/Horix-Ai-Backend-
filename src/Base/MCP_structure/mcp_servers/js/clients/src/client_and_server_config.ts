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
    }
]
