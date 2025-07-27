"""
Working Enhanced AI Agent Protocol with Natural Language Processing
Simplified version that works with Groq LLM for MCP setup commands
"""

import asyncio
import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Import existing protocol
import sys
sys.path.append(str(Path(__file__).parent))
from ai_agent_protocol.core import AIAgentProtocol, AgentRequest

# Try to import Groq
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, SystemMessage
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ Groq not available, using pattern matching")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPCommand:
    """Parsed MCP command structure"""
    action: str  # setup, check, list, create_agent, status
    mcp_name: str
    agent_type: str = ""
    confidence: float = 0.0
    raw_input: str = ""

class NaturalLanguageMCPProcessor:
    """Natural language processor for MCP commands"""
    
    def __init__(self, base_path: str, groq_api_key: str = None):
        self.base_path = Path(base_path)
        self.protocol = AIAgentProtocol(str(base_path))
        self.groq_api_key = groq_api_key
        
        # Initialize Groq if available
        if GROQ_AVAILABLE and groq_api_key and groq_api_key != "dummy_key":
            try:
                self.llm = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name="mixtral-8x7b-32768",
                    temperature=0.1,
                    max_tokens=1024
                )
                self.mode = "groq"
                logger.info("✅ Groq LLM initialized")
            except Exception as e:
                logger.warning(f"Groq setup failed: {e}, using pattern matching")
                self.mode = "pattern"
        else:
            self.mode = "pattern"
            logger.info("📝 Using pattern matching mode")
    
    async def process_command(self, user_input: str) -> str:
        """Process natural language command"""
        try:
            logger.info(f"🤖 Processing: {user_input}")
            
            # Parse the command
            if self.mode == "groq":
                command = await self._parse_with_groq(user_input)
            else:
                command = self._parse_with_patterns(user_input)
            
            # Execute the command
            return await self._execute_command(command)
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"❌ Error: {e}\n💡 Try commands like 'setup github mcp server'"
    
    async def _parse_with_groq(self, user_input: str) -> MCPCommand:
        """Parse command using Groq LLM"""
        try:
            system_prompt = """You are an expert at parsing natural language commands for MCP (Model Context Protocol) server management.

Parse the user's command and respond with ONLY a JSON object with these fields:
- action: one of "setup", "check", "list", "create_agent", "status"
- mcp_name: the MCP server name (github, langsmith, filesystem, etc.) or empty string
- agent_type: type of agent to create (monitoring_agent, devops_agent, etc.) or empty string
- confidence: confidence score 0.0-1.0

Examples:
"setup github mcp server" → {"action": "setup", "mcp_name": "github", "agent_type": "", "confidence": 0.95}
"check if langsmith is available" → {"action": "check", "mcp_name": "langsmith", "agent_type": "", "confidence": 0.90}
"create monitoring agent with langsmith" → {"action": "create_agent", "mcp_name": "langsmith", "agent_type": "monitoring_agent", "confidence": 0.92}
"list mcp servers" → {"action": "list", "mcp_name": "", "agent_type": "", "confidence": 0.88}
"what servers are installed" → {"action": "status", "mcp_name": "", "agent_type": "", "confidence": 0.85}

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
                
                return MCPCommand(
                    action=parsed.get("action", "unknown"),
                    mcp_name=parsed.get("mcp_name", ""),
                    agent_type=parsed.get("agent_type", ""),
                    confidence=parsed.get("confidence", 0.5),
                    raw_input=user_input
                )
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Groq response as JSON: {response_text}")
                # Fallback to pattern matching
                return self._parse_with_patterns(user_input)
                
        except Exception as e:
            logger.error(f"Groq parsing failed: {e}")
            # Fallback to pattern matching
            return self._parse_with_patterns(user_input)
    
    def _parse_with_patterns(self, user_input: str) -> MCPCommand:
        """Parse command using pattern matching"""
        user_input_lower = user_input.lower().strip()
        
        # Extract MCP name
        mcp_name = ""
        mcp_keywords = ["github", "langsmith", "filesystem", "pagerduty", "blender", "redhat", "slack", "notion"]
        for keyword in mcp_keywords:
            if keyword in user_input_lower:
                mcp_name = keyword
                break
        
        # Determine action with better logic
        action = "unknown"
        confidence = 0.7
        
        # Check for status/list queries first (regardless of MCP name presence)
        if any(phrase in user_input_lower for phrase in ["what servers", "what mcp", "show me what", "list installed", "list my", "what's installed", "which servers", "currently installed"]):
            action = "status"
            confidence = 0.9
        elif any(word in user_input_lower for word in ["setup", "install", "download", "add"]) and mcp_name:
            action = "setup"
            confidence = 0.9
        elif any(word in user_input_lower for word in ["check", "available", "exists", "find"]) and mcp_name:
            action = "check"
            confidence = 0.85
        elif any(word in user_input_lower for word in ["list", "show", "display"]) and not any(word in user_input_lower for word in ["what", "which", "installed"]):
            action = "list"
            confidence = 0.8
        elif any(word in user_input_lower for word in ["create", "make", "build"]) and "agent" in user_input_lower:
            action = "create_agent"
            confidence = 0.9
        elif any(word in user_input_lower for word in ["what", "status", "installed", "which", "current", "show"]):
            action = "status"
            confidence = 0.75
        
        # Determine agent type
        agent_type = ""
        if action == "create_agent":
            if "monitoring" in user_input_lower or mcp_name == "langsmith":
                agent_type = "monitoring_agent"
            elif "devops" in user_input_lower or mcp_name == "github":
                agent_type = "devops_agent"
            elif "filesystem" in user_input_lower or "file" in user_input_lower:
                agent_type = "file_manager_agent"
            else:
                agent_type = "custom_agent"
        
        return MCPCommand(
            action=action,
            mcp_name=mcp_name,
            agent_type=agent_type,
            confidence=confidence,
            raw_input=user_input
        )
    
    async def _execute_command(self, command: MCPCommand) -> str:
        """Execute the parsed command"""
        try:
            if command.action == "setup":
                return await self._setup_mcp_server(command.mcp_name)
            elif command.action == "check":
                return await self._check_mcp_availability(command.mcp_name)
            elif command.action == "list":
                return await self._list_available_mcps(command.mcp_name)
            elif command.action == "create_agent":
                return await self._create_agent_with_mcp(command.mcp_name, command.agent_type)
            elif command.action == "status":
                return await self._get_mcp_status()
            else:
                # If no clear action detected, try to infer from context
                if any(word in command.raw_input.lower() for word in ["install", "insta", "instal"]):
                    return "❌ Please specify what to install\n💡 Example: 'setup github mcp server'"
                elif any(word in command.raw_input.lower() for word in ["what", "show", "list", "which", "display"]):
                    return await self._get_mcp_status()
                else:
                    return self._suggest_commands(command)
                
        except Exception as e:
            return f"❌ Error executing command: {e}"
    
    async def _setup_mcp_server(self, mcp_name: str) -> str:
        """Setup MCP server"""
        if not mcp_name:
            return "❌ Please specify an MCP server name\n💡 Example: 'setup github mcp server'"
        
        try:
            # Check if already installed
            check_result = await self._check_mcp_availability(mcp_name)
            if "already installed" in check_result.lower():
                return check_result
            
            # Find and install
            logger.info(f"🔍 Searching for {mcp_name} MCP servers...")
            servers = await self.protocol.list_available_mcp_servers(mcp_name)
            
            if not servers:
                return f"❌ No {mcp_name.title()} MCP servers found.\n💡 Try: 'list available mcp servers'"
            
            # Install the best match
            best_server = servers[0]
            logger.info(f"📥 Installing {best_server.name}...")
            
            success = await self.protocol.server_manager.download_and_install_server(best_server)
            
            if success:
                return f"""✅ Successfully installed {mcp_name.title()} MCP server!

📦 **Server Details:**
  • Name: {best_server.name}
  • Description: {best_server.description}
  • Language: {best_server.language}
  • Repository: {best_server.repository_url}

🎯 **Next Steps:**
  • Create agent: 'create monitoring agent with {mcp_name}'
  • Check status: 'what mcp servers are installed?'"""
            else:
                return f"❌ Failed to install {mcp_name.title()} MCP server.\n💡 Check the logs for details."
                
        except Exception as e:
            return f"❌ Error setting up {mcp_name} MCP server: {e}"
    
    async def _check_mcp_availability(self, mcp_name: str) -> str:
        """Check MCP server availability"""
        if not mcp_name:
            return "❌ Please specify an MCP server name\n💡 Example: 'check if github is available'"
        
        try:
            # Check if already installed
            python_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "python" / "servers" / f"{mcp_name.upper()}_MCP"
            js_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "js" / "servers" / f"{mcp_name.upper()}_MCP"
            
            if python_path.exists() or js_path.exists():
                location = python_path if python_path.exists() else js_path
                return f"""✅ {mcp_name.title()} MCP server is already installed!

📁 **Location:** {location.name}
🎯 **Ready to use:** You can now create agents with this MCP server
💡 **Try:** 'create monitoring agent with {mcp_name}'"""
            
            # Search for available servers
            servers = await self.protocol.list_available_mcp_servers(mcp_name)
            if servers:
                result = f"🔍 Found {len(servers)} {mcp_name.title()} MCP servers available:\n\n"
                for i, server in enumerate(servers[:3], 1):
                    result += f"  {i}. **{server.name}**\n"
                    result += f"     {server.description} ({server.language})\n\n"
                result += f"💡 **Install:** 'setup {mcp_name} mcp server'"
                return result
            else:
                return f"❌ No {mcp_name.title()} MCP servers found.\n💡 Try: 'list available mcp servers'"
                
        except Exception as e:
            return f"❌ Error checking {mcp_name}: {e}"
    
    async def _list_available_mcps(self, search_term: str = "") -> str:
        """List available MCP servers"""
        try:
            # If search_term is empty, just show status of installed servers first
            if not search_term:
                status_result = await self._get_mcp_status()
                if "No MCP servers currently installed" not in status_result:
                    return status_result + "\n\n💡 **Search for more:** 'list github servers'"
            
            servers = await self.protocol.list_available_mcp_servers(search_term)
            if not servers:
                return "❌ No MCP servers found.\n💡 Check your internet connection"
            
            result = f"📋 **Available MCP Servers** ({len(servers)} found):\n\n"
            
            for i, server in enumerate(servers[:8], 1):  # Limit to 8
                result += f"**{i}. {server.name}**\n"
                result += f"   📝 {server.description}\n"
                result += f"   🔧 Language: {server.language}\n"
                result += f"   🔗 {server.repository_url}\n\n"
            
            if len(servers) > 8:
                result += f"... and {len(servers) - 8} more servers available.\n\n"
            
            result += "💡 **Install any server:** 'setup [server_name] mcp server'"
            return result
            
        except Exception as e:
            return f"❌ Error listing servers: {e}"
    
    async def _create_agent_with_mcp(self, mcp_name: str, agent_type: str = "") -> str:
        """Create agent with MCP integration"""
        if not mcp_name:
            return "❌ Please specify which MCP to use\n💡 Example: 'create monitoring agent with langsmith'"
        
        try:
            # Auto-determine agent type if not specified
            if not agent_type:
                agent_type_map = {
                    "langsmith": "monitoring_agent",
                    "github": "devops_agent",
                    "filesystem": "file_manager_agent",
                    "pagerduty": "incident_management_agent"
                }
                agent_type = agent_type_map.get(mcp_name, "custom_agent")
            
            description = f"AI agent with {mcp_name.title()} MCP integration"
            
            request = AgentRequest(
                agent_type=agent_type,
                required_mcps=[mcp_name],
                description=description,
                metadata={"created_via": "natural_language", "mcp_focus": mcp_name}
            )
            
            logger.info(f"🤖 Creating {agent_type} with {mcp_name} MCP...")
            agent_config = await self.protocol.create_agent(request)
            
            result = f"""✅ Successfully created AI agent!

🤖 **Agent Details:**
  • ID: {agent_config['id']}
  • Type: {agent_config['type']}
  • Status: {agent_config['status']}
  • Description: {agent_config['description']}

📦 **MCP Integrations:**"""
            
            for i, mcp in enumerate(agent_config['mcp_servers'], 1):
                result += f"\n  {i}. {mcp['name']} - {mcp['description']}"
            
            result += f"\n\n🎯 Your {mcp_name.title()} agent is ready for operations!"
            return result
            
        except Exception as e:
            return f"❌ Error creating agent: {e}"
    
    async def _get_mcp_status(self) -> str:
        """Get status of installed MCP servers"""
        try:
            python_servers_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "python" / "servers"
            js_servers_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "js" / "servers"
            
            installed_servers = []
            
            # Check Python servers
            if python_servers_path.exists():
                for server_dir in python_servers_path.iterdir():
                    if server_dir.is_dir() and not server_dir.name.startswith('.') and server_dir.name != '__pycache__':
                        installed_servers.append(f"{server_dir.name} (Python)")
            
            # Check JS servers
            if js_servers_path.exists():
                for server_dir in js_servers_path.iterdir():
                    if server_dir.is_dir() and not server_dir.name.startswith('.'):
                        installed_servers.append(f"{server_dir.name} (JavaScript)")
            
            if installed_servers:
                result = f"📦 **Installed MCP Servers ({len(installed_servers)}):**\n\n"
                for i, server in enumerate(installed_servers, 1):
                    result += f"  {i}. {server}\n"
                result += f"\n💡 **Create agents:** 'create agent with [server_name]'"
                return result
            else:
                return """📦 No MCP servers currently installed.

💡 **Get started:**
  • Install servers: 'setup github mcp server'
  • List available: 'list available mcp servers'"""
                
        except Exception as e:
            return f"❌ Error getting status: {e}"
    
    def _suggest_commands(self, command: MCPCommand) -> str:
        """Suggest valid commands"""
        return f"""🤖 I understand you want to work with MCP servers.

**Available commands:**
  • 'setup [server] mcp server' - Install MCP server
  • 'check if [server] is available' - Check availability  
  • 'list available mcp servers' - List all servers
  • 'create agent with [server]' - Create AI agent
  • 'what mcp servers are installed?' - Show status

**Popular servers:** github, langsmith, filesystem, pagerduty

💡 **Try:** 'setup github mcp server'"""

class EnhancedMCPCLI:
    """Enhanced CLI with natural language processing"""
    
    def __init__(self, groq_api_key: str = None):
        self.base_path = Path(__file__).parent.parent
        self.processor = NaturalLanguageMCPProcessor(str(self.base_path), groq_api_key)
    
    async def interactive_mode(self):
        """Interactive mode"""
        print("🤖 Enhanced AI Agent Protocol - Natural Language Interface")
        print("=" * 60)
        print(f"Mode: {self.processor.mode.title()}" + (" (Groq LLM)" if self.processor.mode == "groq" else " (Pattern Matching)"))
        print()
        print("**Natural language commands:**")
        print("  • 'setup github mcp server'")
        print("  • 'check if langsmith is available'") 
        print("  • 'list available mcp servers'")
        print("  • 'create monitoring agent with langsmith'")
        print("  • 'what mcp servers are installed?'")
        print()
        print("Type 'quit' to exit")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n🎯 Your command: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print(f"\n🤖 Processing: {user_input}")
                print("-" * 40)
                
                response = await self.processor.process_command(user_input)
                
                print("✅ **Response:**")
                print(response)
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def process_command(self, command: str) -> str:
        """Process single command"""
        return await self.processor.process_command(command)

async def demo_enhanced_protocol():
    """Demo the enhanced protocol"""
    
    print("🚀 Enhanced AI Agent Protocol Demo")
    print("=" * 50)
    
    # Get Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        print("✅ Using Groq LLM for intelligent command processing")
    else:
        print("📝 Using pattern matching (no Groq API key)")
    
    cli = EnhancedMCPCLI(groq_api_key)
    
    # Demo commands
    demo_commands = [
        "what mcp servers are currently installed?",
        "setup github mcp server", 
        "check if langsmith is available",
        "list available mcp servers",
        "create a devops agent with github"
    ]
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n🎯 Command {i}/5: '{command}'")
        print("-" * 40)
        
        try:
            response = await cli.process_command(command)
            print("✅ **Response:**")
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
        await asyncio.sleep(1)
    
    print("\n🎉 Demo Complete!")
    print("\n🚀 **Try interactive mode:**")
    print("python src/enhanced_ai_protocol_working.py")

async def main():
    """Main function"""
    
    print("🤖 Enhanced AI Agent Protocol - Working Version")
    print("=" * 55)
    print("Natural language MCP server setup with Groq LLM")
    print()
    
    choice = input("Choose mode:\n1. Demo mode\n2. Interactive mode\n3. Exit\n\nYour choice: ").strip()
    
    if choice == "1":
        await demo_enhanced_protocol()
    elif choice == "2":
        groq_api_key = os.getenv("GROQ_API_KEY")
        cli = EnhancedMCPCLI(groq_api_key)
        await cli.interactive_mode()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
