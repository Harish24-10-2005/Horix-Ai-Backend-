# 🤖 MCP Auto-Configuration Agent

An intelligent AI agent built with LangChain and Groq API that automatically configures MCP (Model Context Protocol) servers by reading and understanding their README files.

## 🌟 Features

- **🧠 AI-Powered Analysis**: Uses Groq/OpenAI to understand README files and extract configuration requirements
- **🔧 Automatic Configuration**: Generates proper configuration entries for both Python and JavaScript MCP servers
- **📝 Smart Parsing**: Extracts installation commands, environment variables, dependencies, and run configurations
- **🔍 Validation**: Validates configurations after creation to ensure they're correct
- **💾 Backup System**: Automatically backs up existing configurations before making changes
- **📊 Comprehensive Logging**: Detailed logs and error reporting for debugging
- **🔄 Integration Ready**: Seamlessly integrates with the existing MCP download system

## 📋 Prerequisites

1. **API Key**: Get a Groq API key from [console.groq.com](https://console.groq.com/) (recommended) or OpenAI API key
2. **Python 3.8+**: Make sure you have Python 3.8 or higher installed
3. **Dependencies**: Install required packages (see Installation section)

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The agent requires these packages:
- `langchain-groq` - For Groq LLM integration
- `langchain-core` - Core LangChain functionality  
- `langchain-openai` - OpenAI fallback support
- `python-dotenv` - Environment variable management
- `aiohttp` - Async HTTP client
- `pydantic` - Data validation

### 2. Set Up Environment Variables

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your API key
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Verify Installation

```bash
python demo_mcp_agent.py
```

## 💻 Usage

### Command Line Interface

#### Configure a Specific MCP Server
```bash
python src/mcp_auto_config_agent.py --mcp-name youtube-mcp-server
```

#### Configure All MCP Servers
```bash
python src/mcp_auto_config_agent.py --configure-all
```

#### Validate Configurations
```bash
python src/mcp_auto_config_agent.py --validate
```

#### Configure with Custom README
```bash
python src/mcp_auto_config_agent.py --mcp-name my-server --readme-path /path/to/README.md
```

### Python API

```python
from src.mcp_auto_config_agent import MCPAutoConfigAgent
import asyncio

async def main():
    # Initialize the agent
    agent = MCPAutoConfigAgent()
    
    # Configure a specific MCP server
    success = await agent.auto_configure_new_mcp("youtube-mcp-server")
    
    # Configure all MCP servers
    results = await agent.configure_all_mcps()
    
    # Validate configurations
    validation = await agent.validate_configuration()

asyncio.run(main())
```

### Integration with Existing System

The agent automatically integrates with the existing MCP download system. When a new MCP server is downloaded, it will be automatically configured:

```python
# This happens automatically after MCP download
await self._auto_configure_downloaded_mcp(server_info)
```

## 🧠 How It Works

### 1. README Analysis
The agent uses AI to analyze README files and extract:
- **Installation commands** (pip install, npm install, etc.)
- **Run commands** (python main.py, node index.js, etc.)
- **Environment variables** required by the server
- **Dependencies** and package requirements
- **Build steps** if needed
- **Port configurations**

### 2. Configuration Generation
Based on the analysis, it generates appropriate configuration entries:

**Python Configuration (client_and_server_config.py)**:
```python
{
    "server_name": "example-mcp",
    "command": "python",
    "args": ["main.py"],
    "env": {"API_KEY": "your_api_key_here"}
}
```

**JavaScript Configuration (client_and_server_config.ts)**:
```typescript
{
    server_name: "example-mcp",
    command: "node",
    args: ["build/index.js"],
    server_features_and_capability: "Description of server capabilities"
}
```

### 3. Validation & Backup
- Creates automatic backups of existing configurations
- Validates the new configuration
- Logs all changes for audit trail

## 📊 Example Analysis

**Input README**:
```markdown
# YouTube Transcript MCP Server

## Installation
```bash
pip install youtube-transcript-api "mcp[fastmcp]"
```

## Usage
```bash
python main.py
```

The server exposes a single tool for getting YouTube transcripts.
```

**AI Analysis Result**:
```json
{
  "server_name": "youtube-mcp-server",
  "command": "python",
  "args": ["main.py"],
  "env_vars": {},
  "install_method": "pip",
  "dependencies": ["youtube-transcript-api", "mcp[fastmcp]"],
  "language": "python",
  "build_required": false,
  "description": "YouTube Transcript MCP Server for getting video transcripts"
}
```

## 🔧 Configuration Files

The agent updates these configuration files:

### Python Servers
- **File**: `src/Base/MCP_structure/mcp_servers/python/clients/src/client_and_server_config.py`
- **Format**: Python dictionary with server configurations

### JavaScript/TypeScript Servers  
- **File**: `src/Base/MCP_structure/mcp_servers/js/clients/src/client_and_server_config.ts`
- **Format**: TypeScript array with server configurations

### Backup Files
- **Location**: `config_backups/`
- **Format**: `{language}_config_{timestamp}.{ext}`

## 📝 Logging

The agent provides comprehensive logging:

### Configuration Log
- **File**: `mcp_config_log.json`
- **Content**: All configuration events with timestamps
- **Purpose**: Audit trail and debugging

### Console Output
- Real-time progress updates
- Success/failure notifications
- Detailed error messages
- Validation results

## 🔍 Troubleshooting

### Common Issues

#### "No LLM available"
**Problem**: API key not set or invalid  
**Solution**: 
1. Check your `.env` file
2. Verify API key is correct
3. Test with: `echo $GROQ_API_KEY`

#### "README not found"
**Problem**: No README file for MCP server  
**Solution**: 
1. Check if MCP server has a README.md file
2. Use `--readme-path` to specify custom location
3. Create a basic README with installation instructions

#### "Configuration update failed"
**Problem**: Cannot write to configuration files  
**Solution**:
1. Check file permissions
2. Ensure files exist and are writable
3. Check for syntax errors in existing configs

#### "Invalid JSON in AI response"
**Problem**: AI returned malformed JSON  
**Solution**:
1. Try again (AI responses can vary)
2. Check if README has clear instructions
3. Switch to pattern matching mode

### Debug Mode

Enable verbose logging:
```bash
export MCP_VERBOSE_LOGGING=true
python src/mcp_auto_config_agent.py --configure-all
```

### Validation

Always validate after configuration:
```bash
python src/mcp_auto_config_agent.py --validate
```

## 🧪 Testing

### Run Demo
```bash
python demo_mcp_agent.py
```

### Test Individual Components
```python
# Test README analysis
agent = MCPAutoConfigAgent()
config = await agent._analyze_readme_with_ai("test-server", readme_content)

# Test configuration update
success = await agent._apply_configuration(config)

# Test validation
validation = await agent.validate_configuration("test-server")
```

## 🔄 Integration Points

### With Existing MCP Download System
The agent integrates automatically with `ai_agent_protocol/core.py`:

```python
# Added to download_and_install_server method
await self._auto_configure_downloaded_mcp(server_info)
```

### With MCP Integration Layer
Use the integration layer for custom workflows:

```python
from src.mcp_integration import MCPDownloadIntegration

integration = MCPDownloadIntegration()
await integration.on_mcp_downloaded("new-mcp-server")
```

## 📚 API Reference

### MCPAutoConfigAgent

#### `auto_configure_new_mcp(mcp_name: str, readme_path: str = None) -> bool`
Configure a specific MCP server.

#### `configure_all_mcps() -> Dict[str, bool]`
Configure all MCP servers found in the servers directory.

#### `validate_configuration(mcp_name: str = None) -> Dict[str, Any]`
Validate MCP server configurations.

### MCPConfiguration

Data class representing extracted configuration:
- `server_name`: Name of the MCP server
- `command`: Command to run the server
- `args`: Command line arguments
- `env_vars`: Environment variables
- `install_method`: Installation method (pip, npm, etc.)
- `dependencies`: Required packages
- `language`: Programming language
- `build_required`: Whether build step is needed
- `description`: Server description

## 🛡️ Security Considerations

- **API Keys**: Store in `.env` file, never commit to version control
- **File Permissions**: Agent modifies configuration files - ensure proper permissions
- **Backup**: Always backup configurations before changes
- **Validation**: Always validate configurations after changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- **Enhanced AI Agent Protocol**: Main project this agent integrates with
- **MCP Structure**: Base MCP server management system
- **LangChain**: Framework for LLM applications
- **Groq**: Fast LLM inference platform

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the main project README
- **API Reference**: See inline code documentation
- **Discord**: Join the community Discord for real-time help

---

*Built with ❤️ using LangChain and Groq API*
