<!-- AUTO-GENERATED MCP README -->
<!-- Generated on: 2025-08-17 20:53:38 -->
<!-- Source: D:\Horix AI\Backend\src\Base\MCP_structure\mcp_servers\python\servers\mcp-wikipedia\ReadMe.md -->

# MCP Server: mcp-wikipedia

**🔧 Language:** Python  
**📦 Server Type:** MCP (Model Context Protocol)  
**📅 Added to Collection:** 2025-08-17 20:53:38  
**🔗 Repository:** https://github.com/algonacci/mcp-wikipedia  
**📍 Source Location:** `D:\Horix AI\Backend\src\Base\MCP_structure\mcp_servers\python\servers\mcp-wikipedia\ReadMe.md`

---

## Original README Content

# mcp-wikipedia

MCP server to give client the ability to access Wikipedia pages

# Usage

```json
{
  "mcpServers": {
    "wikipedia": {
      "command": "uv",
      "args": [
        "--directory",
        "%USERPROFILE%/Documents/GitHub/mcp-wikipedia",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```


---

## Integration Notes

This MCP server has been automatically integrated into the Enhanced AI Agent Protocol system.

### Quick Access
- **Configuration Location:** `src/Base/MCP_structure/mcp_servers/python/servers/mcp-wikipedia/`
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
