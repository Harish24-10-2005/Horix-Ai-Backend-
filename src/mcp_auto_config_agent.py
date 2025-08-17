"""
Intelligent MCP Configuration Agent using LangChain and Groq API

This agent automatically reads README files of downloaded MCP servers and 
configures them according to their documentation requirements.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import re
import tempfile
from datetime import datetime

# LangChain imports
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPConfiguration:
    """Represents MCP server configuration extracted from README"""
    server_name: str
    command: str
    args: List[str]
    env_vars: Dict[str, str]
    install_method: str
    dependencies: List[str]
    port: Optional[int] = None
    description: str = ""
    language: str = "unknown"
    build_required: bool = False
    build_command: Optional[str] = None

@dataclass
class ConfigurationError:
    """Represents an error in configuration parsing"""
    error_type: str
    message: str
    suggestion: str

class MCPAutoConfigAgent:
    """AI Agent for automatic MCP server configuration using LangChain and Groq"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Configuration paths
        self.js_config_path = self.base_path / "src/Base/MCP_structure/mcp_servers/js/clients/src/client_and_server_config.ts"
        self.py_config_path = self.base_path / "src/Base/MCP_structure/mcp_servers/python/clients/src/client_and_server_config.py"
        self.servers_path = self.base_path / "src/Base/MCP_structure/mcp_servers"
        
        # Create backup directory
        self.backup_dir = self.base_path / "config_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def _initialize_llm(self):
        """Initialize the language model (Groq preferred, OpenAI fallback)"""
        if not LANGCHAIN_AVAILABLE:
            logger.error("❌ LangChain not available. Please install: pip install langchain-groq langchain-core")
            return None
            
        if self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
            try:
                llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name="llama-3.1-8b-instant",
                    temperature=0.1,
                    max_tokens=2048
                )
                logger.info("✅ Groq LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")
                
        if self.openai_api_key and self.openai_api_key != "your_openai_api_key_here":
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    openai_api_key=self.openai_api_key,
                    model_name="gpt-3.5-turbo",
                    temperature=0.1,
                    max_tokens=2048
                )
                logger.info("✅ OpenAI LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
                
        logger.error("❌ No valid API key found. Please set GROQ_API_KEY or OPENAI_API_KEY in .env file")
        return None
        
    async def auto_configure_new_mcp(self, mcp_name: str, readme_path: str = None) -> bool:
        """Automatically configure a newly downloaded MCP server"""
        if not self.llm:
            logger.error("❌ No LLM available for configuration")
            return False
            
        try:
            logger.info(f"🤖 Starting auto-configuration for MCP: {mcp_name}")
            
            # Find and read README
            readme_content = await self._find_and_read_readme(mcp_name, readme_path)
            if not readme_content:
                logger.error(f"❌ No README found for {mcp_name}")
                return False
                
            # Analyze README with AI
            config = await self._analyze_readme_with_ai(mcp_name, readme_content)
            if not config:
                logger.error(f"❌ Failed to extract configuration from README for {mcp_name}")
                return False
                
            # Backup existing configurations
            await self._backup_configurations()
            
            # Apply configuration
            success = await self._apply_configuration(config)
            
            if success:
                logger.info(f"✅ Successfully configured {mcp_name}")
                await self._log_configuration_event(mcp_name, config, "SUCCESS")
            else:
                logger.error(f"❌ Failed to apply configuration for {mcp_name}")
                await self._log_configuration_event(mcp_name, config, "FAILED")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Error auto-configuring {mcp_name}: {e}")
            await self._log_configuration_event(mcp_name, None, "ERROR", str(e))
            return False
            
    async def _find_and_read_readme(self, mcp_name: str, readme_path: str = None) -> Optional[str]:
        """Find and read README file for MCP server"""
        try:
            if readme_path and Path(readme_path).exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            # Search in common locations
            search_paths = [
                self.servers_path / "python" / "servers" / mcp_name / "README.md",
                self.servers_path / "python" / "servers" / mcp_name / "readme.md",
                self.servers_path / "js" / "servers" / mcp_name / "README.md",
                self.servers_path / "js" / "servers" / mcp_name / "readme.md",
                self.base_path / "Doc" / f"{mcp_name}_README.md",
            ]
            
            for path in search_paths:
                if path.exists():
                    logger.info(f"📖 Found README at: {path}")
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                        
            logger.warning(f"⚠️  No README found for {mcp_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error reading README for {mcp_name}: {e}")
            return None
            
    async def _analyze_readme_with_ai(self, mcp_name: str, readme_content: str) -> Optional[MCPConfiguration]:
        """Use AI to analyze README and extract configuration"""
        try:
            system_prompt = """You are an expert at analyzing README files for MCP (Model Context Protocol) servers and extracting configuration information.

Your task is to analyze a README file and extract the configuration needed to properly set up the MCP server.

Extract and return ONLY a JSON object with these fields:
- server_name: The name of the MCP server
- command: The command to run the server (e.g., "python", "node", "uvx")
- args: Array of command line arguments
- env_vars: Object with required environment variables and their descriptions
- install_method: How to install dependencies ("pip", "npm", "uvx", "manual")
- dependencies: Array of required packages/dependencies
- language: Programming language ("python", "javascript", "typescript")
- build_required: Boolean if build step is needed
- build_command: Build command if required
- description: Brief description of what the server does
- port: Port number if the server runs on a specific port (null if not specified)

Guidelines:
1. Look for installation instructions, usage examples, and configuration requirements
2. Extract environment variables from code examples or documentation
3. Identify the main command to run the server
4. Note any build steps (npm run build, etc.)
5. Parse dependencies from package.json, requirements.txt, pyproject.toml, etc.

Example response:
{
  "server_name": "example-mcp",
  "command": "python",
  "args": ["main.py"],
  "env_vars": {"API_KEY": "Your API key here"},
  "install_method": "pip",
  "dependencies": ["package1", "package2"],
  "language": "python",
  "build_required": false,
  "build_command": null,
  "description": "Example MCP server",
  "port": null
}

Respond with ONLY the JSON object, no other text."""

            user_prompt = f"""Please analyze this README file for the MCP server "{mcp_name}" and extract configuration information:

README Content:
{readme_content}

Extract the configuration as JSON."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()
            
            # Clean up response and extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
                
            # Parse JSON response
            config_data = json.loads(response_text)
            
            # Create MCPConfiguration object
            config = MCPConfiguration(
                server_name=config_data.get('server_name', mcp_name),
                command=config_data.get('command', 'python'),
                args=config_data.get('args', []),
                env_vars=config_data.get('env_vars', {}),
                install_method=config_data.get('install_method', 'pip'),
                dependencies=config_data.get('dependencies', []),
                language=config_data.get('language', 'python'),
                build_required=config_data.get('build_required', False),
                build_command=config_data.get('build_command'),
                description=config_data.get('description', ''),
                port=config_data.get('port')
            )
            
            logger.info(f"✅ Successfully extracted configuration for {mcp_name}")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"AI Response: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing README with AI: {e}")
            return None
            
    async def _apply_configuration(self, config: MCPConfiguration) -> bool:
        """Apply the extracted configuration to the appropriate config files"""
        try:
            if config.language.lower() in ['python']:
                return await self._update_python_config(config)
            elif config.language.lower() in ['javascript', 'typescript']:
                return await self._update_javascript_config(config)
            else:
                logger.warning(f"Unknown language {config.language}, trying Python config")
                return await self._update_python_config(config)
                
        except Exception as e:
            logger.error(f"Error applying configuration: {e}")
            return False
            
    async def _update_python_config(self, config: MCPConfiguration) -> bool:
        """Update Python client configuration"""
        try:
            if not self.py_config_path.exists():
                logger.error(f"Python config file not found: {self.py_config_path}")
                return False
                
            with open(self.py_config_path, 'r') as f:
                content = f.read()
                
            # Parse existing configuration
            lines = content.split('\n')
            servers_config_start = -1
            servers_config_end = -1
            
            for i, line in enumerate(lines):
                if 'ServersConfig = [' in line:
                    servers_config_start = i
                elif servers_config_start != -1 and line.strip() == ']':
                    servers_config_end = i
                    break
                    
            if servers_config_start == -1:
                logger.error("Could not find ServersConfig in Python config")
                return False
                
            # Build new server configuration
            server_config = {
                "server_name": config.server_name,
                "command": config.command,
                "args": config.args,
                "env": config.env_vars
            }
            
            # Check if server already exists
            existing_servers = self._parse_existing_python_servers(content)
            server_exists = any(s.get('server_name') == config.server_name for s in existing_servers)
            
            if server_exists:
                logger.info(f"🔄 Updating existing server configuration for {config.server_name}")
                # Remove existing configuration
                existing_servers = [s for s in existing_servers if s.get('server_name') != config.server_name]
            else:
                logger.info(f"➕ Adding new server configuration for {config.server_name}")
                
            # Add new configuration
            existing_servers.append(server_config)
            
            # Rebuild ServersConfig section
            new_servers_section = "ServersConfig = [\n"
            for server in existing_servers:
                new_servers_section += "    {\n"
                new_servers_section += f'        "server_name": "{server["server_name"]}",\n'
                new_servers_section += f'        "command": "{server["command"]}",\n'
                new_servers_section += f'        "args": {json.dumps(server["args"])},\n'
                new_servers_section += f'        "env": {json.dumps(server["env"])}\n'
                new_servers_section += "    },\n"
            new_servers_section += "]\n"
            
            # Replace the ServersConfig section
            new_lines = lines[:servers_config_start] + new_servers_section.split('\n') + lines[servers_config_end+1:]
            new_content = '\n'.join(new_lines)
            
            # Write updated configuration
            with open(self.py_config_path, 'w') as f:
                f.write(new_content)
                
            logger.info(f"✅ Updated Python configuration for {config.server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Python config: {e}")
            return False
            
    async def _update_javascript_config(self, config: MCPConfiguration) -> bool:
        """Update JavaScript/TypeScript client configuration"""
        try:
            if not self.js_config_path.exists():
                logger.error(f"JavaScript config file not found: {self.js_config_path}")
                return False
                
            with open(self.js_config_path, 'r') as f:
                content = f.read()
                
            # Build new server configuration
            server_config = {
                "server_name": config.server_name,
                "command": config.command,
                "args": config.args,
                "server_features_and_capability": config.description or f"MCP Server for {config.server_name}"
            }
            
            # Parse existing servers
            existing_servers = self._parse_existing_js_servers(content)
            server_exists = any(s.get('server_name') == config.server_name for s in existing_servers)
            
            if server_exists:
                logger.info(f"🔄 Updating existing server configuration for {config.server_name}")
                existing_servers = [s for s in existing_servers if s.get('server_name') != config.server_name]
            else:
                logger.info(f"➕ Adding new server configuration for {config.server_name}")
                
            # Add new configuration
            existing_servers.append(server_config)
            
            # Rebuild ServersConfig section
            new_servers_section = "export const ServersConfig: any[] = [\n"
            for server in existing_servers:
                new_servers_section += "    {\n"
                new_servers_section += f'        server_name: "{server["server_name"]}",\n'
                new_servers_section += f'        command: "{server["command"]}",\n'
                new_servers_section += f'        args: {json.dumps(server["args"])},\n'
                new_servers_section += f'        server_features_and_capability: "{server["server_features_and_capability"]}"\n'
                new_servers_section += "    },\n"
            new_servers_section += "]\n"
            
            # Replace the ServersConfig section
            pattern = r'export const ServersConfig: any\[\] = \[.*?\];'
            new_content = re.sub(pattern, new_servers_section.strip(), content, flags=re.DOTALL)
            
            # Write updated configuration
            with open(self.js_config_path, 'w') as f:
                f.write(new_content)
                
            logger.info(f"✅ Updated JavaScript configuration for {config.server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating JavaScript config: {e}")
            return False
            
    def _parse_existing_python_servers(self, content: str) -> List[Dict]:
        """Parse existing Python server configurations"""
        try:
            # Extract ServersConfig array content
            start_pattern = r'ServersConfig\s*=\s*\['
            end_pattern = r'\]'
            
            start_match = re.search(start_pattern, content)
            if not start_match:
                return []
                
            start_pos = start_match.end() - 1  # Include the opening bracket
            
            # Find matching closing bracket
            bracket_count = 0
            end_pos = start_pos
            for i, char in enumerate(content[start_pos:], start_pos):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i + 1
                        break
                        
            # Extract the array content
            array_content = content[start_pos:end_pos]
            
            # Use regex to find server configurations
            server_pattern = r'\{[^}]*"server_name"[^}]*\}'
            servers = []
            
            for match in re.finditer(server_pattern, array_content, re.DOTALL):
                server_text = match.group(0)
                try:
                    # Extract individual fields
                    name_match = re.search(r'"server_name":\s*"([^"]*)"', server_text)
                    command_match = re.search(r'"command":\s*"([^"]*)"', server_text)
                    args_match = re.search(r'"args":\s*(\[[^\]]*\])', server_text)
                    env_match = re.search(r'"env":\s*(\{[^}]*\})', server_text)
                    
                    if name_match:
                        server = {
                            "server_name": name_match.group(1),
                            "command": command_match.group(1) if command_match else "python",
                            "args": json.loads(args_match.group(1)) if args_match else [],
                            "env": json.loads(env_match.group(1)) if env_match else {}
                        }
                        servers.append(server)
                except Exception as e:
                    logger.warning(f"Failed to parse server config: {e}")
                    continue
                    
            return servers
            
        except Exception as e:
            logger.error(f"Error parsing existing Python servers: {e}")
            return []
            
    def _parse_existing_js_servers(self, content: str) -> List[Dict]:
        """Parse existing JavaScript server configurations"""
        try:
            # Extract ServersConfig array content
            pattern = r'export const ServersConfig: any\[\] = \[(.*?)\];'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                return []
                
            array_content = match.group(1)
            
            # Parse server objects
            server_pattern = r'\{[^}]*server_name[^}]*\}'
            servers = []
            
            for match in re.finditer(server_pattern, array_content, re.DOTALL):
                server_text = match.group(0)
                try:
                    # Extract individual fields
                    name_match = re.search(r'server_name:\s*"([^"]*)"', server_text)
                    command_match = re.search(r'command:\s*"([^"]*)"', server_text)
                    args_match = re.search(r'args:\s*(\[[^\]]*\])', server_text)
                    desc_match = re.search(r'server_features_and_capability:\s*"([^"]*)"', server_text)
                    
                    if name_match:
                        server = {
                            "server_name": name_match.group(1),
                            "command": command_match.group(1) if command_match else "node",
                            "args": json.loads(args_match.group(1).replace("'", '"')) if args_match else [],
                            "server_features_and_capability": desc_match.group(1) if desc_match else ""
                        }
                        servers.append(server)
                except Exception as e:
                    logger.warning(f"Failed to parse JS server config: {e}")
                    continue
                    
            return servers
            
        except Exception as e:
            logger.error(f"Error parsing existing JavaScript servers: {e}")
            return []
            
    async def _backup_configurations(self):
        """Backup existing configurations before making changes"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup Python config
            if self.py_config_path.exists():
                backup_py = self.backup_dir / f"python_config_{timestamp}.py"
                backup_py.write_text(self.py_config_path.read_text())
                
            # Backup JavaScript config
            if self.js_config_path.exists():
                backup_js = self.backup_dir / f"js_config_{timestamp}.ts"
                backup_js.write_text(self.js_config_path.read_text())
                
            logger.info(f"✅ Configuration backups created with timestamp: {timestamp}")
            
        except Exception as e:
            logger.warning(f"Failed to create configuration backups: {e}")
            
    async def _log_configuration_event(self, mcp_name: str, config: Optional[MCPConfiguration], status: str, error: str = None):
        """Log configuration events for tracking and debugging"""
        try:
            log_file = self.base_path / "mcp_config_log.json"
            
            event = {
                "timestamp": datetime.now().isoformat(),
                "mcp_name": mcp_name,
                "status": status,
                "error": error,
                "config": {
                    "server_name": config.server_name if config else None,
                    "command": config.command if config else None,
                    "language": config.language if config else None,
                    "dependencies": config.dependencies if config else None
                } if config else None
            }
            
            # Read existing log
            log_data = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)
                except:
                    log_data = []
                    
            # Add new event
            log_data.append(event)
            
            # Keep only last 100 events
            log_data = log_data[-100:]
            
            # Write updated log
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to log configuration event: {e}")
            
    async def configure_all_mcps(self) -> Dict[str, bool]:
        """Auto-configure all MCP servers found in the servers directory"""
        results = {}
        
        # Find all MCP servers
        python_servers = []
        js_servers = []
        
        # Python servers
        py_servers_dir = self.servers_path / "python" / "servers"
        if py_servers_dir.exists():
            python_servers = [d.name for d in py_servers_dir.iterdir() if d.is_dir()]
            
        # JavaScript servers
        js_servers_dir = self.servers_path / "js" / "servers"
        if js_servers_dir.exists():
            js_servers = [d.name for d in js_servers_dir.iterdir() if d.is_dir()]
            
        all_servers = python_servers + js_servers
        
        logger.info(f"🔍 Found {len(all_servers)} MCP servers to configure")
        
        for server_name in all_servers:
            try:
                logger.info(f"🔧 Configuring {server_name}...")
                success = await self.auto_configure_new_mcp(server_name)
                results[server_name] = success
                
                if success:
                    logger.info(f"✅ {server_name} configured successfully")
                else:
                    logger.error(f"❌ Failed to configure {server_name}")
                    
            except Exception as e:
                logger.error(f"❌ Error configuring {server_name}: {e}")
                results[server_name] = False
                
        return results
        
    async def validate_configuration(self, mcp_name: str = None) -> Dict[str, Any]:
        """Validate MCP server configurations"""
        try:
            validation_results = {
                "valid_configs": [],
                "invalid_configs": [],
                "missing_dependencies": [],
                "errors": []
            }
            
            # Validate Python configurations
            if self.py_config_path.exists():
                with open(self.py_config_path, 'r') as f:
                    py_content = f.read()
                py_servers = self._parse_existing_python_servers(py_content)
                
                for server in py_servers:
                    if mcp_name and server.get('server_name') != mcp_name:
                        continue
                        
                    # Check if server directory exists
                    server_dir = self.servers_path / "python" / "servers" / server.get('server_name', '')
                    if server_dir.exists():
                        validation_results["valid_configs"].append(server.get('server_name'))
                    else:
                        validation_results["invalid_configs"].append({
                            "name": server.get('server_name'),
                            "reason": "Server directory not found"
                        })
                        
            # Validate JavaScript configurations
            if self.js_config_path.exists():
                with open(self.js_config_path, 'r') as f:
                    js_content = f.read()
                js_servers = self._parse_existing_js_servers(js_content)
                
                for server in js_servers:
                    if mcp_name and server.get('server_name') != mcp_name:
                        continue
                        
                    # Check if server directory exists
                    server_dir = self.servers_path / "js" / "servers" / server.get('server_name', '')
                    if server_dir.exists():
                        validation_results["valid_configs"].append(server.get('server_name'))
                    else:
                        validation_results["invalid_configs"].append({
                            "name": server.get('server_name'),
                            "reason": "Server directory not found"
                        })
                        
            return validation_results
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return {"errors": [str(e)]}

# CLI Interface
async def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Auto-Configuration Agent")
    parser.add_argument("--mcp-name", help="Name of specific MCP to configure")
    parser.add_argument("--readme-path", help="Path to README file")
    parser.add_argument("--configure-all", action="store_true", help="Configure all MCP servers")
    parser.add_argument("--validate", action="store_true", help="Validate configurations")
    parser.add_argument("--base-path", default=".", help="Base path for MCP structure")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = MCPAutoConfigAgent(args.base_path)
    
    if not agent.llm:
        print("❌ No LLM available. Please set GROQ_API_KEY or OPENAI_API_KEY in environment")
        return
        
    if args.configure_all:
        print("🚀 Configuring all MCP servers...")
        results = await agent.configure_all_mcps()
        
        print(f"\n📊 Configuration Results:")
        for name, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {name}")
            
    elif args.validate:
        print("🔍 Validating MCP configurations...")
        results = await agent.validate_configuration(args.mcp_name)
        
        print(f"\n📊 Validation Results:")
        print(f"✅ Valid: {len(results.get('valid_configs', []))}")
        print(f"❌ Invalid: {len(results.get('invalid_configs', []))}")
        
        if results.get('invalid_configs'):
            print("\n❌ Invalid Configurations:")
            for invalid in results['invalid_configs']:
                print(f"  - {invalid['name']}: {invalid['reason']}")
                
    elif args.mcp_name:
        print(f"🔧 Configuring MCP: {args.mcp_name}")
        success = await agent.auto_configure_new_mcp(args.mcp_name, args.readme_path)
        
        if success:
            print(f"✅ Successfully configured {args.mcp_name}")
        else:
            print(f"❌ Failed to configure {args.mcp_name}")
            
    else:
        print("Please specify --mcp-name, --configure-all, or --validate")

if __name__ == "__main__":
    asyncio.run(main())
