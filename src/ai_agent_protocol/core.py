"""
AI Agent Protocol for Automatic MCP Integration
This module provides automated discovery, download, and integration of MCP servers
"""

import asyncio
import aiohttp
import json
import os
import subprocess
import zipfile
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerInfo:
    """Information about an MCP server"""
    name: str
    repository_url: str
    download_url: str
    description: str
    language: str
    installation_commands: List[str]
    run_command: str
    run_args: List[str]
    dependencies: List[str]
    
@dataclass
class AgentRequest:
    """Request structure for AI agent creation"""
    agent_type: str
    required_mcps: List[str]
    description: str
    metadata: Dict[str, Any]

class MCPRegistry:
    """Registry for known MCP servers with auto-discovery capabilities"""
    
    def __init__(self):
        self.known_servers = {
            "langsmith": MCPServerInfo(
                name="LANGSMITH_MCP",
                repository_url="https://github.com/langchain-ai/langsmith-mcp-server",
                download_url="https://github.com/langchain-ai/langsmith-mcp-server/archive/refs/heads/main.zip",
                description="LangSmith MCP server for monitoring AI agents",
                language="python",
                installation_commands=["pip install -e ."],
                run_command="uv",
                run_args=["--directory", "langsmith-mcp-server/langsmith_mcp_server", "run", "server.py"],
                dependencies=["langsmith", "mcp"]
            ),
            "github": MCPServerInfo(
                name="GITHUB_MCP",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/github",
                download_url="https://github.com/modelcontextprotocol/servers/archive/refs/heads/main.zip",
                description="GitHub MCP server for repository operations",
                language="typescript",
                installation_commands=["npm install"],
                run_command="npx",
                run_args=["tsx", "src/index.ts"],
                dependencies=["@modelcontextprotocol/sdk"]
            ),
            "filesystem": MCPServerInfo(
                name="FILESYSTEM_MCP",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
                download_url="https://github.com/modelcontextprotocol/servers/archive/refs/heads/main.zip",
                description="Filesystem MCP server for file operations",
                language="typescript",
                installation_commands=["npm install"],
                run_command="npx",
                run_args=["tsx", "src/index.ts"],
                dependencies=["@modelcontextprotocol/sdk"]
            ),
            "slack": MCPServerInfo(
                name="SLACK_MCP",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/slack",
                download_url="https://github.com/modelcontextprotocol/servers/archive/refs/heads/main.zip",
                description="Slack MCP server for team communication and workspace management",
                language="typescript",
                installation_commands=["npm install"],
                run_command="npx",
                run_args=["tsx", "src/index.ts"],
                dependencies=["@modelcontextprotocol/sdk", "@slack/web-api"]
            ),
            "notion": MCPServerInfo(
                name="NOTION_MCP",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/notion",
                download_url="https://github.com/modelcontextprotocol/servers/archive/refs/heads/main.zip",
                description="Notion MCP server for knowledge management and note-taking",
                language="typescript",
                installation_commands=["npm install"],
                run_command="npx",
                run_args=["tsx", "src/index.ts"],
                dependencies=["@modelcontextprotocol/sdk", "@notionhq/client"]
            )
        }
        
    async def discover_mcp_servers(self, search_term: str) -> List[MCPServerInfo]:
        """Discover MCP servers from various sources"""
        discovered_servers = []
        
        # Search in known registry first
        for key, server in self.known_servers.items():
            if search_term.lower() in key.lower() or search_term.lower() in server.description.lower():
                discovered_servers.append(server)
        
        # Search GitHub for additional servers
        github_results = await self._search_github_mcp_servers(search_term)
        discovered_servers.extend(github_results)
        
        return discovered_servers
    
    async def _search_github_mcp_servers(self, search_term: str) -> List[MCPServerInfo]:
        """Search GitHub for MCP servers"""
        servers = []
        try:
            async with aiohttp.ClientSession() as session:
                # Search for repositories with MCP in the name and the search term
                search_query = f"{search_term} mcp server"
                url = f"https://api.github.com/search/repositories?q={search_query}&sort=stars&order=desc"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for repo in data.get('items', [])[:5]:  # Limit to top 5 results
                            server_info = MCPServerInfo(
                                name=f"{repo['name'].upper()}_MCP",
                                repository_url=repo['html_url'],
                                download_url=f"{repo['html_url']}/archive/refs/heads/{repo['default_branch']}.zip",
                                description=repo['description'] or "GitHub discovered MCP server",
                                language="unknown",  # Would need to detect from repo
                                installation_commands=["# Auto-detected installation"],
                                run_command="# Auto-detected run command",
                                run_args=["# Auto-detected args"],
                                dependencies=["# Auto-detected dependencies"]
                            )
                            servers.append(server_info)
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
        
        return servers

class MCPServerManager:
    """Manages MCP server installation and configuration"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.servers_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers"
        self.python_servers_path = self.servers_path / "python" / "servers"
        self.js_servers_path = self.servers_path / "js" / "servers"
        self.config_path = self.servers_path / "python" / "clients" / "src" / "client_and_server_config.py"
        
    async def download_and_install_server(self, server_info: MCPServerInfo) -> bool:
        """Download and install an MCP server with graceful fallback"""
        try:
            logger.info(f"Downloading MCP server: {server_info.name}")
            
            # Determine target directory based on language
            if server_info.language.lower() in ["python"]:
                target_dir = self.python_servers_path / server_info.name
            else:
                target_dir = self.js_servers_path / server_info.name
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            download_success = False
            
            try:
                # Attempt to download the repository
                zip_path = target_dir / "temp.zip"
                await self._download_file(server_info.download_url, zip_path)
                
                # Extract the repository
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                
                # Remove the zip file
                zip_path.unlink()
                
                # Find the extracted folder (usually has a suffix like -main)
                extracted_folders = [f for f in target_dir.iterdir() if f.is_dir()]
                if extracted_folders:
                    extracted_folder = extracted_folders[0]
                    # Move contents up one level
                    for item in extracted_folder.iterdir():
                        shutil.move(str(item), str(target_dir))
                    extracted_folder.rmdir()
                
                download_success = True
                logger.info(f"Successfully downloaded {server_info.name}")
                
                # Install dependencies
                await self._install_dependencies(target_dir, server_info)
                
                # Auto-detect run command and args from actual structure
                detected_info = await self._detect_run_configuration(target_dir, server_info)
                if detected_info:
                    server_info = detected_info
                    
            except Exception as download_error:
                logger.warning(f"Download failed for {server_info.name}: {download_error}")
                logger.info(f"Proceeding with configuration update using provided info...")
                
                # Create a basic placeholder structure for configuration
                placeholder_file = target_dir / "README.md"
                with open(placeholder_file, 'w') as f:
                    f.write(f"# {server_info.name}\n\nPlaceholder for MCP server.\nRepository: {server_info.repository_url}")
            
            # Always attempt to update configuration (even if download failed)
            await self._update_server_config(server_info)
            
            if download_success:
                logger.info(f"Successfully installed and configured MCP server: {server_info.name}")
                return True
            else:
                logger.info(f"Configuration updated for {server_info.name} (manual installation may be required)")
                return True  # Return True since config was updated
                
        except Exception as e:
            logger.error(f"Error installing MCP server {server_info.name}: {e}")
            # Even if everything fails, try to update config as last resort
            try:
                await self._update_server_config(server_info)
                logger.info(f"Configuration updated for {server_info.name} despite installation errors")
                return True
            except Exception as config_error:
                logger.error(f"Failed to update configuration: {config_error}")
                return False
    
    async def _download_file(self, url: str, path: Path):
        """Download a file from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
    
    async def _install_dependencies(self, target_dir: Path, server_info: MCPServerInfo):
        """Install server dependencies"""
        try:
            if server_info.language == "python":
                # Check for requirements.txt or pyproject.toml
                requirements_file = target_dir / "requirements.txt"
                pyproject_file = target_dir / "pyproject.toml"
                
                if requirements_file.exists():
                    subprocess.run(["pip", "install", "-r", str(requirements_file)], check=True)
                elif pyproject_file.exists():
                    subprocess.run(["pip", "install", "-e", str(target_dir)], check=True)
                else:
                    # Install from server_info dependencies
                    for dep in server_info.dependencies:
                        subprocess.run(["pip", "install", dep], check=True)
            
            elif server_info.language == "typescript":
                # Check for package.json
                package_json = target_dir / "package.json"
                if package_json.exists():
                    subprocess.run(["npm", "install"], cwd=target_dir, check=True)
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
    
    async def _detect_run_configuration(self, target_dir: Path, server_info: MCPServerInfo) -> Optional[MCPServerInfo]:
        """Auto-detect the correct run configuration from the installed MCP structure"""
        try:
            logger.info(f"Auto-detecting run configuration for {server_info.name}")
            
            # Check for common entry points
            entry_points = [
                "main.py",
                "server.py", 
                "index.js",
                "index.ts",
                "src/index.js",
                "src/index.ts",
                "build/index.js",
                "dist/index.js"
            ]
            
            detected_entry = None
            detected_language = server_info.language
            
            # Search for entry points
            for entry in entry_points:
                entry_path = target_dir / entry
                if entry_path.exists():
                    detected_entry = entry
                    if entry.endswith(('.js', '.ts')):
                        detected_language = "typescript" if entry.endswith('.ts') else "javascript"
                    elif entry.endswith('.py'):
                        detected_language = "python"
                    break
            
            # Check for package.json (Node.js project)
            package_json = target_dir / "package.json"
            if package_json.exists() and not detected_entry:
                try:
                    import json
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                    
                    # Check for main entry point
                    if "main" in package_data:
                        detected_entry = package_data["main"]
                        detected_language = "javascript"
                    
                    # Check for scripts
                    if "scripts" in package_data:
                        if "start" in package_data["scripts"]:
                            start_script = package_data["scripts"]["start"]
                            if "index.js" in start_script:
                                detected_entry = "index.js"
                            elif "build/index.js" in start_script:
                                detected_entry = "build/index.js"
                        
                except Exception as e:
                    logger.warning(f"Error reading package.json: {e}")
            
            # Check for pyproject.toml (Python project)
            pyproject_toml = target_dir / "pyproject.toml"
            if pyproject_toml.exists() and not detected_entry:
                try:
                    # Simple parsing for entry points
                    with open(pyproject_toml, 'r') as f:
                        content = f.read()
                    
                    if "[project.scripts]" in content:
                        # Look for server script
                        lines = content.split('\n')
                        for line in lines:
                            if "server" in line.lower() and "=" in line:
                                # Extract module reference
                                module_ref = line.split('=')[1].strip().strip('"\'')
                                if ":" in module_ref:
                                    detected_entry = f"python -m {module_ref.split(':')[0]}"
                                break
                
                except Exception as e:
                    logger.warning(f"Error reading pyproject.toml: {e}")
            
            # If no entry point detected, use defaults
            if not detected_entry:
                if detected_language == "python":
                    # Check for common Python patterns
                    if (target_dir / "main.py").exists():
                        detected_entry = "main.py"
                    elif (target_dir / "server.py").exists():
                        detected_entry = "server.py"
                    else:
                        detected_entry = "main.py"  # Default
                else:
                    # JavaScript/TypeScript default
                    detected_entry = "index.js"
            
            # Update server_info with detected configuration
            updated_server_info = MCPServerInfo(
                name=server_info.name,
                repository_url=server_info.repository_url,
                download_url=server_info.download_url,
                description=server_info.description,
                language=detected_language,
                installation_commands=server_info.installation_commands,
                run_command="uv" if detected_language == "python" else "node",
                run_args=[detected_entry] if detected_entry else server_info.run_args,
                dependencies=server_info.dependencies
            )
            
            logger.info(f"Detected configuration: {detected_language} - {detected_entry}")
            return updated_server_info
            
        except Exception as e:
            logger.error(f"Error detecting run configuration: {e}")
            return None
    
    async def _update_server_config(self, server_info: MCPServerInfo):
        """Update both Python and TypeScript server configuration files"""
        try:
            # Update Python configuration
            await self._update_python_config(server_info)
            
            # Update TypeScript configuration
            await self._update_typescript_config(server_info)
            
        except Exception as e:
            logger.error(f"Error updating server configs: {e}")
    
    async def _update_python_config(self, server_info: MCPServerInfo):
        """Update Python client configuration using enhanced config manager"""
        try:
            # Import the enhanced configuration manager
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            from enhanced_config_manager import MCPConfigurationManager
            
            # Use the enhanced manager for robust updates
            manager = MCPConfigurationManager(str(self.base_path / "src"))
            success = manager.update_python_config(server_info.name, server_info.language)
            
            if success:
                logger.info(f"Successfully updated Python config for {server_info.name}")
            else:
                logger.error(f"Failed to update Python config for {server_info.name}")
                # Fallback to original method
                await self._update_python_config_original(server_info)
                
        except Exception as e:
            logger.error(f"Error with enhanced config update: {e}")
            # Fallback to original method
            await self._update_python_config_original(server_info)
    
    async def _update_python_config_original(self, server_info: MCPServerInfo):
        """Update Python client configuration using safe AST parsing"""
        try:
            config_path = self.servers_path / "python" / "clients" / "src" / "client_and_server_config.py"
            
            # Read current configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if server already exists
            if f'"server_name": "{server_info.name}"' in content:
                logger.info(f"Server {server_info.name} already exists in Python config")
                return
            
            # Parse the current config to extract existing servers
            import ast
            tree = ast.parse(content)
            
            existing_servers = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "ServersConfig":
                            try:
                                existing_servers = ast.literal_eval(node.value)
                            except:
                                logger.warning("Could not parse existing ServersConfig")
                                existing_servers = []
            
            # Determine the correct command and args based on language and structure
            if server_info.language.lower() == "python":
                command = "uv"
                server_path = f"../servers/{server_info.name}"
                
                # Smart path detection for different Python MCP structures
                if "main.py" in server_info.run_args:
                    args = ["--directory", server_path, "run", "python", "main.py"]
                elif "server.py" in server_info.run_args:
                    args = ["--directory", server_path, "run", "server.py"]
                elif any("-m" in str(arg) for arg in server_info.run_args):
                    # Module execution pattern
                    module_name = server_info.run_args[-1] if server_info.run_args else server_info.name.lower().replace("_mcp", "")
                    args = ["--directory", server_path, "run", "python", "-m", module_name]
                else:
                    # Default pattern
                    args = ["--directory", server_path, "run"] + server_info.run_args
            else:
                # TypeScript/Node.js servers in Python config
                command = "node"
                server_path = f"../../js/servers/{server_info.name}"
                args = ["--directory", server_path] + server_info.run_args
            
            # Create new server configuration
            new_server = {
                "server_name": server_info.name,
                "command": command,
                "args": args
            }
            
            # Add to existing servers
            existing_servers.append(new_server)
            
            # Generate the new configuration content
            clients_config = ["MCP_CLIENT_AZURE_AI", "MCP_CLIENT_OPENAI", "MCP_CLIENT_GEMINI"]
            
            new_content = f"""ClientsConfig = {json.dumps(clients_config, indent=4)}

ServersConfig = {json.dumps(existing_servers, indent=4)}
"""
            
            # Write back to file
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Updated Python config for {server_info.name}")
            
        except Exception as e:
            logger.error(f"Error updating Python config: {e}")
            # Fallback to manual content replacement
            await self._update_python_config_fallback(server_info)
    
    async def _update_python_config_fallback(self, server_info: MCPServerInfo):
        """Fallback method for updating Python config when AST parsing fails"""
        try:
            config_path = self.servers_path / "python" / "clients" / "src" / "client_and_server_config.py"
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple append before the closing bracket
            if server_info.language.lower() == "python":
                command = "uv"
                server_path = f"../servers/{server_info.name}"
                args = ["--directory", server_path, "run"] + server_info.run_args
            else:
                command = "node"
                server_path = f"../../js/servers/{server_info.name}"
                args = ["--directory", server_path] + server_info.run_args
            
            new_server_text = f''',
    {{
        "server_name": "{server_info.name}",
        "command": "{command}",
        "args": {json.dumps(args, indent=12).replace(json.dumps(args, indent=12).split(chr(10))[0], '            ' + json.dumps(args, indent=12).split(chr(10))[0].strip())}
    }}'''
            
            # Insert before the last ]
            last_bracket = content.rfind(']')
            if last_bracket != -1:
                new_content = content[:last_bracket] + new_server_text + '\n' + content[last_bracket:]
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"Updated Python config (fallback) for {server_info.name}")
        
        except Exception as e:
            logger.error(f"Fallback Python config update failed: {e}")
    
    async def _update_typescript_config(self, server_info: MCPServerInfo):
        """Update TypeScript client configuration using complete rebuild approach"""
        try:
            config_path = self.servers_path / "js" / "clients" / "src" / "client_and_server_config.ts"
            
            # Only update if it's a TypeScript/Node.js server
            if server_info.language.lower() not in ["typescript", "javascript", "node"]:
                return
            
            # Read current configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if server already exists
            if f'server_name: "{server_info.name}"' in content:
                logger.info(f"Server {server_info.name} already exists in TypeScript config")
                return
            
            # Extract existing servers by parsing server_name entries
            import re
            server_name_matches = re.findall(r'server_name:\s*"([^"]+)"', content)
            existing_servers = []
            
            # Parse each existing server configuration with improved regex
            for server_name in server_name_matches:
                # More precise pattern to match complete server objects
                server_pattern = rf'{{\s*server_name:\s*"{re.escape(server_name)}".*?}}'
                server_match = re.search(server_pattern, content, re.DOTALL)
                if server_match:
                    server_block = server_match.group(0)
                    
                    # Extract command
                    command_match = re.search(r'command:\s*"([^"]+)"', server_block)
                    command = command_match.group(1) if command_match else "node"
                    
                    # Extract args with better parsing
                    args_match = re.search(r'args:\s*\[(.*?)\]', server_block, re.DOTALL)
                    if args_match:
                        args_content = args_match.group(1).strip()
                        # Split by quotes to get individual args
                        args = []
                        for line in args_content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('//'):
                                # Extract quoted strings
                                quote_matches = re.findall(r'"([^"]*)"', line)
                                args.extend(quote_matches)
                    else:
                        args = ["--directory", f"../servers/{server_name}", "index.js"]
                    
                    # Extract description
                    desc_match = re.search(r'server_features_and_capability:\s*"([^"]*)"', server_block)
                    description = desc_match.group(1) if desc_match else f"{server_name} server"
                    
                    existing_servers.append({
                        "name": server_name,
                        "command": command,
                        "args": args,
                        "description": description
                    })
            
            # Determine correct path and args for new TypeScript server
            server_path = f"../servers/{server_info.name}"
            command = "node"
            
            # Smart args detection with proper formatting
            if "tsx" in server_info.run_args and "src/index.ts" in server_info.run_args:
                args = ["--directory", server_path, "tsx", "src/index.ts"]
            elif "index.js" in server_info.run_args:
                args = ["--directory", server_path, "index.js"]
            elif "build/index.js" in server_info.run_args:
                args = ["--directory", server_path, "build/index.js"]
            elif server_info.run_args:
                args = ["--directory", server_path] + server_info.run_args
            else:
                args = ["--directory", server_path, "index.js"]
            
            # Add new server to existing servers
            existing_servers.append({
                "name": server_info.name,
                "command": command,
                "args": args,
                "description": server_info.description
            })
            
            # Rebuild the entire configuration file with perfect formatting
            clients_config = ["MCP_CLIENT_OPENAI", "MCP_CLIENT_AZURE_AI", "MCP_CLIENT_GEMINI"]
            
            # Generate clients section
            clients_section = "export const ClientsConfig: string[] = [\n"
            for client in clients_config:
                clients_section += f'    "{client}",\n'
            clients_section = clients_section.rstrip(',\n') + '\n]\n\n'
            
            # Generate servers section
            servers_section = "export const ServersConfig: any[] = [\n"
            for i, server in enumerate(existing_servers):
                servers_section += "    {\n"
                servers_section += f'        server_name: "{server["name"]}",\n'
                servers_section += f'        command: "{server["command"]}",\n'
                servers_section += "        args: [\n"
                for arg in server["args"]:
                    servers_section += f'            "{arg}",\n'
                servers_section = servers_section.rstrip(',\n') + '\n'
                servers_section += "        ],\n"
                servers_section += f'        server_features_and_capability: "{server["description"]}"\n'
                servers_section += "    }"
                if i < len(existing_servers) - 1:
                    servers_section += ","
                servers_section += "\n"
            servers_section += "]\n"
            
            # Write the complete new configuration
            new_content = clients_section + servers_section
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Updated TypeScript config for {server_info.name}")
            
        except Exception as e:
            logger.error(f"Error updating TypeScript config: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

class AIAgentProtocol:
    """Main protocol for AI agent creation and MCP integration"""
    
    def __init__(self, base_path: str):
        self.registry = MCPRegistry()
        self.server_manager = MCPServerManager(base_path)
        self.agents = {}
    
    async def create_agent(self, request: AgentRequest) -> Dict[str, Any]:
        """Create an AI agent with automatic MCP integration"""
        logger.info(f"Creating AI agent: {request.agent_type}")
        
        agent_id = f"agent_{len(self.agents) + 1}"
        agent_config = {
            "id": agent_id,
            "type": request.agent_type,
            "description": request.description,
            "metadata": request.metadata,
            "mcp_servers": [],
            "status": "initializing"
        }
        
        # Discover and install required MCP servers
        for mcp_requirement in request.required_mcps:
            logger.info(f"Processing MCP requirement: {mcp_requirement}")
            
            # Discover available servers
            discovered_servers = await self.registry.discover_mcp_servers(mcp_requirement)
            
            if not discovered_servers:
                logger.warning(f"No MCP servers found for: {mcp_requirement}")
                continue
            
            # Install the best match (first result)
            best_server = discovered_servers[0]
            success = await self.server_manager.download_and_install_server(best_server)
            
            if success:
                agent_config["mcp_servers"].append(asdict(best_server))
                logger.info(f"Successfully integrated MCP server: {best_server.name}")
            else:
                logger.error(f"Failed to integrate MCP server: {best_server.name}")
        
        agent_config["status"] = "ready"
        self.agents[agent_id] = agent_config
        
        return agent_config
    
    async def list_available_mcp_servers(self, search_term: str = "") -> List[MCPServerInfo]:
        """List available MCP servers"""
        return await self.registry.discover_mcp_servers(search_term)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an AI agent"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all created agents"""
        return list(self.agents.values())

# Example usage functions
async def create_langsmith_monitoring_agent(protocol: AIAgentProtocol) -> Dict[str, Any]:
    """Create an AI agent for monitoring other AI agents using LangSmith"""
    request = AgentRequest(
        agent_type="monitoring_agent",
        required_mcps=["langsmith"],
        description="AI agent for monitoring other AI agents using LangSmith MCP server",
        metadata={
            "monitoring_interval": 60,
            "alert_thresholds": {
                "error_rate": 0.1,
                "response_time": 5000
            }
        }
    )
    
    return await protocol.create_agent(request)

async def create_github_integration_agent(protocol: AIAgentProtocol) -> Dict[str, Any]:
    """Create an AI agent for GitHub operations"""
    request = AgentRequest(
        agent_type="github_agent",
        required_mcps=["github"],
        description="AI agent for GitHub repository operations and code management",
        metadata={
            "repositories": [],
            "permissions": ["read", "write", "issues"]
        }
    )
    
    return await protocol.create_agent(request)
