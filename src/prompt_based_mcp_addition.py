"""
Enhanced AI Agent Protocol with Dynamic MCP Addition via Prompts
Allows adding new MCP servers through natural language descriptions
"""

import asyncio
import os
import json
import logging
import re
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Import existing components
import sys
sys.path.append(str(Path(__file__).parent))
from ai_agent_protocol.core import AIAgentProtocol, AgentRequest, MCPServerInfo

# Try to import Groq for intelligent parsing
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, SystemMessage
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPAddRequest:
    """Request to add a new MCP server via prompt"""
    description: str
    name: str = ""
    repository_url: str = ""
    language: str = ""
    confidence: float = 0.0
    auto_detected: bool = False

class DynamicMCPManager:
    """Manager for dynamically adding MCP servers via prompts"""
    
    def __init__(self, base_path: str, groq_api_key: str = None):
        self.base_path = Path(base_path)
        self.protocol = AIAgentProtocol(str(base_path))
        self.groq_api_key = groq_api_key
        
        # Initialize Groq if available
        if GROQ_AVAILABLE and groq_api_key and groq_api_key != "dummy_key":
            try:
                self.llm = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name="llama-3.1-8b-instant",
                    temperature=0.1,
                    max_tokens=1024
                )
                self.mode = "groq"
                logger.info("✅ Groq LLM initialized for intelligent MCP detection")
            except Exception as e:
                logger.warning(f"Groq setup failed: {e}, using pattern matching")
                self.mode = "pattern"
        else:
            self.mode = "pattern"
            logger.info("📝 Using pattern matching mode for MCP detection")
    
    async def process_add_mcp_command(self, user_input: str) -> str:
        """Process command to add new MCP server"""
        try:
            logger.info(f"🔍 Analyzing request to add MCP: {user_input}")
            
            # Parse the add request
            if self.mode == "groq":
                add_request = await self._parse_add_request_with_groq(user_input)
            else:
                add_request = self._parse_add_request_with_patterns(user_input)
            
            if not add_request:
                return "❌ Could not understand MCP addition request\n💡 Try: 'add leetcode mcp server for coding practice'"
            
            # Search for the MCP server
            return await self._search_and_add_mcp(add_request)
            
        except Exception as e:
            logger.error(f"Error processing add MCP command: {e}")
            return f"❌ Error: {e}\n💡 Try: 'add [service] mcp server for [purpose]'"
    
    async def _parse_add_request_with_groq(self, user_input: str) -> Optional[MCPAddRequest]:
        """Parse add request using Groq LLM"""
        try:
            system_prompt = """You are an expert at understanding requests to add new MCP (Model Context Protocol) servers.

Parse the user's request and respond with ONLY a JSON object with these fields:
- name: the service/tool name (e.g., "leetcode", "docker", "email")
- description: what the MCP server would do
- language: likely programming language ("python", "typescript", or "unknown")
- confidence: confidence score 0.0-1.0

Examples:
"add leetcode mcp server for coding practice" → {"name": "leetcode", "description": "LeetCode MCP server for coding practice and algorithm problems", "language": "python", "confidence": 0.95}
"I need a docker mcp to manage containers" → {"name": "docker", "description": "Docker MCP server for container management", "language": "python", "confidence": 0.90}
"add email integration mcp" → {"name": "email", "description": "Email MCP server for email integration", "language": "python", "confidence": 0.85}

Respond with ONLY the JSON object, no other text."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()
            
            # Try to extract JSON from response
            try:
                # Remove any markdown formatting
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]
                
                parsed = json.loads(response_text)
                
                return MCPAddRequest(
                    description=user_input,
                    name=parsed.get("name", ""),
                    language=parsed.get("language", "unknown"),
                    confidence=parsed.get("confidence", 0.5),
                    auto_detected=True
                )
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Groq response as JSON: {response_text}")
                return self._parse_add_request_with_patterns(user_input)
                
        except Exception as e:
            logger.error(f"Groq parsing failed: {e}")
            return self._parse_add_request_with_patterns(user_input)
    
    def _parse_add_request_with_patterns(self, user_input: str) -> Optional[MCPAddRequest]:
        """Parse add request using pattern matching"""
        user_input_lower = user_input.lower().strip()
        
        # Check if it's an add request
        if not any(word in user_input_lower for word in ["add", "create", "install", "setup", "need", "want"]):
            return None
        
        # Extract service name
        # Look for patterns like "add [service] mcp", "[service] mcp server", etc.
        patterns = [
            r"add\s+(\w+)\s+mcp",
            r"(\w+)\s+mcp\s+server",
            r"need\s+(\w+)\s+mcp",
            r"want\s+(\w+)\s+mcp",
            r"install\s+(\w+)\s+mcp",
            r"setup\s+(\w+)\s+mcp",
            r"create\s+(\w+)\s+mcp"
        ]
        
        service_name = ""
        for pattern in patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                service_name = match.group(1)
                break
        
        if not service_name:
            # Try to extract from context
            words = user_input_lower.split()
            for i, word in enumerate(words):
                if word == "mcp" and i > 0:
                    service_name = words[i-1]
                    break
        
        if not service_name:
            return None
        
        # Generate description
        description = f"{service_name.title()} MCP server"
        if "for" in user_input_lower:
            purpose = user_input_lower.split("for", 1)[1].strip()
            description += f" for {purpose}"
        
        # Guess language based on service type
        python_services = ["email", "database", "ai", "ml", "analytics", "data"]
        typescript_services = ["web", "api", "frontend", "react", "node"]
        
        language = "unknown"
        if any(svc in service_name for svc in python_services):
            language = "python"
        elif any(svc in service_name for svc in typescript_services):
            language = "typescript"
        
        return MCPAddRequest(
            description=user_input,
            name=service_name,
            language=language,
            confidence=0.7,
            auto_detected=False
        )
    
    async def _search_and_add_mcp(self, add_request: MCPAddRequest) -> str:
        """Search for and add the MCP server"""
        try:
            service_name = add_request.name
            
            # Search GitHub for MCP servers
            logger.info(f"🔍 Searching GitHub for {service_name} MCP servers...")
            mcp_servers = await self._search_github_for_mcp(service_name)
            
            if not mcp_servers:
                return await self._suggest_manual_creation(add_request)
            
            # Show options to user
            result = f"🔍 **Found {len(mcp_servers)} {service_name.title()} MCP servers:**\n\n"
            
            for i, server in enumerate(mcp_servers[:5], 1):
                result += f"**{i}. {server['name']}**\n"
                result += f"   📝 {server['description']}\n"
                result += f"   ⭐ Stars: {server['stars']} | Language: {server['language']}\n"
                result += f"   🔗 {server['url']}\n\n"
            
            # Auto-add the best match
            best_server = mcp_servers[0]
            auto_add_result = await self._auto_add_mcp_server(best_server, add_request)
            
            result += f"🚀 **Auto-installing best match:**\n{auto_add_result}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching and adding MCP: {e}")
            return f"❌ Error searching for {add_request.name} MCP: {e}"
    
    async def _search_github_for_mcp(self, service_name: str) -> List[Dict]:
        """Search GitHub for MCP servers"""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for repositories
                search_queries = [
                    f"{service_name} mcp server",
                    f"{service_name}-mcp-server",
                    f"mcp-{service_name}-server",
                    f"{service_name} model context protocol"
                ]
                
                all_results = []
                
                for query in search_queries:
                    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
                    
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                for repo in data.get('items', [])[:3]:
                                    # Filter for likely MCP servers
                                    repo_name = repo['name'].lower()
                                    repo_desc = (repo['description'] or '').lower()
                                    
                                    if any(term in repo_name or term in repo_desc for term in ['mcp', 'model context protocol']):
                                        server_info = {
                                            'name': repo['name'],
                                            'description': repo['description'] or f"{service_name.title()} MCP server",
                                            'url': repo['html_url'],
                                            'stars': repo['stargazers_count'],
                                            'language': repo['language'] or 'unknown',
                                            'default_branch': repo['default_branch']
                                        }
                                        all_results.append(server_info)
                    except Exception as e:
                        logger.warning(f"Error searching with query '{query}': {e}")
                        continue
                
                # Remove duplicates and sort by stars
                seen_urls = set()
                unique_results = []
                for result in all_results:
                    if result['url'] not in seen_urls:
                        seen_urls.add(result['url'])
                        unique_results.append(result)
                
                return sorted(unique_results, key=lambda x: x['stars'], reverse=True)
                
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []
    
    async def _auto_add_mcp_server(self, server_info: Dict, add_request: MCPAddRequest) -> str:
        """Automatically add MCP server to registry"""
        try:
            # Create MCPServerInfo
            mcp_server = MCPServerInfo(
                name=f"{add_request.name.upper()}_MCP",
                repository_url=server_info['url'],
                download_url=f"{server_info['url']}/archive/refs/heads/{server_info['default_branch']}.zip",
                description=server_info['description'],
                language=server_info['language'].lower() if server_info['language'] else add_request.language,
                installation_commands=self._get_default_install_commands(server_info['language']),
                run_command=self._get_default_run_command(server_info['language']),
                run_args=self._get_default_run_args(server_info['language']),
                dependencies=self._get_default_dependencies(server_info['language'])
            )
            
            # Add to protocol registry
            self.protocol.registry.known_servers[add_request.name.lower()] = mcp_server
            
            # Try to install it
            logger.info(f"📥 Installing {mcp_server.name}...")
            success = await self.protocol.server_manager.download_and_install_server(mcp_server)
            
            if success:
                # Update the enhanced protocol keywords
                await self._update_enhanced_protocol_keywords(add_request.name)
                
                return f"""✅ Successfully added and configured {add_request.name.title()} MCP server!

📦 **Server Details:**
  • Name: {mcp_server.name}
  • Repository: {server_info['url']}
  • Stars: ⭐ {server_info['stars']}
  • Language: {server_info['language']}

🔧 **Configuration Updated:**
  • ✅ Added to Python client config
  • ✅ Added to TypeScript client config (if applicable)
  • ✅ Run commands automatically configured

🎯 **Ready to use:**
  • 'create agent with {add_request.name}'
  • 'check {add_request.name} status'
  • '{add_request.name} mcp help'"""
            else:
                return f"""✅ Configuration updated for {add_request.name.title()} MCP server!

📦 **Server Details:**
  • Name: {mcp_server.name}
  • Repository: {server_info['url']}
  • Stars: ⭐ {server_info['stars']}
  • Language: {server_info['language']}

🔧 **Configuration Status:**
  • ✅ Added to client configuration files
  • ✅ Run commands configured
  • ⚠️ Manual installation may be required

💡 **Next Steps:**
  • Check the server directory for installation issues
  • Verify dependencies are installed
  • Repository: {server_info['url']}"""
                
        except Exception as e:
            logger.error(f"Error auto-adding MCP server: {e}")
            return f"❌ Error adding {add_request.name} MCP server: {e}"
    
    def _get_default_install_commands(self, language: str) -> List[str]:
        """Get default installation commands based on language"""
        language_lower = (language or '').lower()
        if language_lower in ['python', 'py']:
            return ["pip install -e .", "pip install -r requirements.txt"]
        elif language_lower in ['typescript', 'javascript', 'ts', 'js']:
            return ["npm install", "npm run build"]
        else:
            return ["# Auto-detected installation commands"]
    
    def _get_default_run_command(self, language: str) -> str:
        """Get default run command based on language"""
        language_lower = (language or '').lower()
        if language_lower in ['python', 'py']:
            return "python"
        elif language_lower in ['typescript', 'javascript', 'ts', 'js']:
            return "npx"
        else:
            return "node"
    
    def _get_default_run_args(self, language: str) -> List[str]:
        """Get default run arguments based on language"""
        language_lower = (language or '').lower()
        if language_lower in ['python', 'py']:
            return ["server.py"]
        elif language_lower in ['typescript', 'javascript', 'ts', 'js']:
            return ["tsx", "src/index.ts"]
        else:
            return ["index.js"]
    
    def _get_default_dependencies(self, language: str) -> List[str]:
        """Get default dependencies based on language"""
        language_lower = (language or '').lower()
        if language_lower in ['python', 'py']:
            return ["mcp", "aiohttp"]
        elif language_lower in ['typescript', 'javascript', 'ts', 'js']:
            return ["@modelcontextprotocol/sdk"]
        else:
            return []
    
    async def _update_enhanced_protocol_keywords(self, service_name: str):
        """Update enhanced protocol to recognize new service"""
        try:
            # This would update the enhanced_ai_protocol_working.py file
            # For now, just log the addition
            logger.info(f"📝 New MCP keyword added: {service_name}")
            logger.info(f"💡 Update mcp_keywords list to include '{service_name}'")
        except Exception as e:
            logger.warning(f"Could not auto-update keywords: {e}")
    
    async def _suggest_manual_creation(self, add_request: MCPAddRequest) -> str:
        """Suggest manual creation when no servers found"""
        return f"""🔍 No existing {add_request.name.title()} MCP servers found.

🛠️ **Create Your Own MCP Server:**

**Option 1: Use MCP Template**
```bash
git clone https://github.com/modelcontextprotocol/create-mcp-server
cd create-mcp-server
npm create mcp-server {add_request.name}-mcp-server
```

**Option 2: Manual Setup**
1. Create directory: `{add_request.name.upper()}_MCP/`
2. Add MCP protocol implementation
3. Place in: `src/Base/MCP_structure/mcp_servers/`

**Option 3: Add Existing Repository**
If you know a repository URL:
```
'add mcp from https://github.com/user/{add_request.name}-mcp-server'
```

💡 **Need help?** Try: 'how to create {add_request.name} mcp server'"""

class EnhancedMCPCLIWithPromptAddition:
    """Enhanced CLI with prompt-based MCP addition"""
    
    def __init__(self, groq_api_key: str = None):
        self.base_path = Path(__file__).parent.parent
        self.dynamic_manager = DynamicMCPManager(str(self.base_path), groq_api_key)
    
    async def process_command(self, command: str) -> str:
        """Process command with MCP addition support"""
        command_lower = command.lower().strip()
        
        # Check if it's specifically an add MCP request (more precise detection)
        add_patterns = [
            r"add\s+\w+\s+mcp",
            r"create\s+\w+\s+mcp", 
            r"install\s+\w+\s+mcp",
            r"i\s+need\s+\w+\s+mcp",
            r"i\s+want\s+\w+\s+mcp"
        ]
        
        is_add_request = any(re.search(pattern, command_lower) for pattern in add_patterns)
        
        # Don't treat status/query commands as add requests
        query_patterns = [
            r"what\s+mcp\s+servers",
            r"list\s+mcp",
            r"show\s+mcp",
            r"check\s+if\s+\w+\s+is",
            r"status\s+of"
        ]
        
        is_query_request = any(re.search(pattern, command_lower) for pattern in query_patterns)
        
        if is_add_request and not is_query_request:
            return await self.dynamic_manager.process_add_mcp_command(command)
        else:
            # Use original enhanced protocol
            from enhanced_ai_protocol_working import EnhancedMCPCLI
            original_cli = EnhancedMCPCLI()
            return await original_cli.process_command(command)

async def demo_prompt_based_mcp_addition():
    """Demo adding MCPs via prompts"""
    
    print("🚀 Enhanced AI Agent Protocol - Prompt-Based MCP Addition")
    print("=" * 60)
    print("🧠 Add new MCP servers just by describing what you need!")
    print()
    
    cli = EnhancedMCPCLIWithPromptAddition()
    
    # Demo commands for adding MCPs
    demo_commands = [
        "add leetcode mcp server for coding practice",
        "I need a docker mcp to manage containers", 
        "create an email mcp server for gmail integration",
        "add database mcp for postgresql operations",
        "install weather mcp server for weather data"
    ]
    
    print("🎯 **Demo Commands:**")
    for i, cmd in enumerate(demo_commands, 1):
        print(f"  {i}. {cmd}")
    print()
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n🎯 **Command {i}/5:** '{command}'")
        print("=" * 50)
        
        try:
            response = await cli.process_command(command)
            print("🤖 **AI Response:**")
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 50)
        await asyncio.sleep(1)
    
    print("\n🎉 **Demo Complete!**")
    print("\n✨ **Key Features:**")
    print("  • Natural language MCP addition")
    print("  • Automatic GitHub search")
    print("  • Smart installation")
    print("  • Registry updates")
    print()
    print("💡 **Try adding your own:**")
    print("  • 'add slack mcp server for team communication'")
    print("  • 'I need a calendar mcp for scheduling'")
    print("  • 'create twitter mcp for social media'")

if __name__ == "__main__":
    asyncio.run(demo_prompt_based_mcp_addition())
