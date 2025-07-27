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
        """Download and install an MCP server"""
        try:
            logger.info(f"Downloading MCP server: {server_info.name}")
            
            # Determine target directory based on language
            if server_info.language == "python":
                target_dir = self.python_servers_path / server_info.name
            else:
                target_dir = self.js_servers_path / server_info.name
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the repository
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
            
            # Install dependencies
            await self._install_dependencies(target_dir, server_info)
            
            # Update configuration
            await self._update_server_config(server_info)
            
            logger.info(f"Successfully installed MCP server: {server_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error installing MCP server {server_info.name}: {e}")
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
    
    async def _update_server_config(self, server_info: MCPServerInfo):
        """Update the server configuration file"""
        try:
            # Read current configuration
            with open(self.config_path, 'r') as f:
                content = f.read()
            
            # Parse the current ServersConfig
            import re
            
            # Find the ServersConfig list
            servers_config_match = re.search(r'ServersConfig = \[(.*?)\]', content, re.DOTALL)
            if servers_config_match:
                # Create new server configuration
                server_path = f"../servers/{server_info.name}"
                if server_info.language == "python":
                    server_path = f"../servers/{server_info.name}"
                else:
                    server_path = f"../../js/servers/{server_info.name}"
                
                new_server_config = f'''    {{
        "server_name": "{server_info.name}",
        "command": "{server_info.run_command}",
        "args": {json.dumps(["--directory", server_path] + server_info.run_args)}
    }}'''
                
                # Insert the new configuration
                current_configs = servers_config_match.group(1).strip()
                if current_configs:
                    updated_configs = current_configs + ",\n" + new_server_config
                else:
                    updated_configs = new_server_config
                
                # Replace in content
                new_content = content.replace(
                    servers_config_match.group(0),
                    f"ServersConfig = [\n{updated_configs}\n]"
                )
                
                # Write back to file
                with open(self.config_path, 'w') as f:
                    f.write(new_content)
                    
        except Exception as e:
            logger.error(f"Error updating server config: {e}")

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
