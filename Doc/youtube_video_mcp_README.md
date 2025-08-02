<!-- AUTO-GENERATED MCP README -->
<!-- Generated on: 2025-08-03 00:13:40 -->
<!-- Source: D:\Horix AI\Backend\src\Base\MCP_structure\mcp_servers\python\servers\youtube_video_mcp\ReadMe.md -->

# MCP Server: youtube_video_mcp

**🔧 Language:** Python  
**📦 Server Type:** MCP (Model Context Protocol)  
**📅 Added to Collection:** 2025-08-03 00:13:40  
**🔗 Repository:** https://github.com/yug-space/youtube_video_mcp  
**📍 Source Location:** `D:\Horix AI\Backend\src\Base\MCP_structure\mcp_servers\python\servers\youtube_video_mcp\ReadMe.md`

---

## Original README Content

# YouTube Transcript MCP Server

This is a Model Control Protocol (MCP) server that provides a tool to fetch transcripts from YouTube videos.

## Features

- Extracts video ID from any valid YouTube URL
- Returns plain-text transcripts (without timestamps)
- Uses the `youtube-transcript-api` library

## Installation

```bash
# Install dependencies
pip install youtube-transcript-api "mcp[fastmcp]"
```

## Usage

Run the server:

```bash
python main.py
```

The server exposes a single tool:

- `get_transcript`: Takes a YouTube URL and returns the video ID and transcript

## Example

Using the MCP client:

```python
from mcp.client import Client

client = Client(transport="stdio")
response = client.call("get_transcript", {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
print(f"Video ID: {response['video_id']}")
print(f"Transcript: {response['transcript'][:100]}...")  # First 100 chars
```

## Error Handling

The server handles these error cases:
- Invalid YouTube URLs
- Videos without available transcripts


---

## Integration Notes

This MCP server has been automatically integrated into the Enhanced AI Agent Protocol system.

### Quick Access
- **Configuration Location:** `src/Base/MCP_structure/mcp_servers/python/servers/youtube_video_mcp/`
- **Language:** Python
- **Status:** ✅ Integrated

### Usage in System
You can interact with this MCP server through:
1. **Interactive Mode:** `python final_demo.py` → Option 2
2. **Natural Language:** Describe what you need and the system will use appropriate MCPs
3. **Direct Access:** Use the AI Agent Protocol to call specific MCP functions

### Management Commands
```bash
# Check server status
python -c "from src.ai_agent_protocol.core import AIAgentProtocol; import asyncio; protocol = AIAgentProtocol('.'); asyncio.run(protocol.list_available_mcp_servers())"

# Validate configuration
python src/config_validator.py
```

---
*This README was automatically collected and enhanced by the Enhanced AI Agent Protocol system.*
