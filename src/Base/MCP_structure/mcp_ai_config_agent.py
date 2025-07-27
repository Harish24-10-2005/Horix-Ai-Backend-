#!/usr/bin/env python3
"""
AI-Powered MCP Configuration Agent
==================================
Uses LangChain + Groq API to intelligently configure Python MCP servers
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import re

try:
    from langchain_groq import ChatGroq
    from langchain.schema import HumanMessage, SystemMessage
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatGroq = None
    HumanMessage = None
    SystemMessage = None

class MCPConfigurationAgent:
    """AI-powered agent for intelligent MCP server configuration"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        
        if not LANGCHAIN_AVAILABLE:
            print("⚠️  LangChain not available. Using intelligent fallback configuration.")
            self.llm = None
        elif not self.groq_api_key:
            print("⚠️  GROQ_API_KEY not found. Using intelligent fallback configuration.")
            self.llm = None
        else:
            try:
                self.llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name="mixtral-8x7b-32768",
                    temperature=0.1
                )
                print("✅ AI Agent initialized with Groq API")
            except Exception as e:
                print(f"⚠️  Failed to initialize Groq: {e}. Using fallback.")
                self.llm = None
        
        self.base_dir = Path(__file__).parent
        self.py_servers_dir = self.base_dir / "mcp_servers" / "python" / "servers"
        self.config_file = self.base_dir / "mcp_servers" / "python" / "clients" / "src" / "client_and_server_config.py"
    
    def scan_python_servers(self) -> Dict[str, Any]:
        """Scan for Python MCP servers and gather intelligence"""
        servers = {}
        
        if not self.py_servers_dir.exists():
            return servers
        
        for server_dir in self.py_servers_dir.glob("*"):
            if server_dir.is_dir():
                server_info = self._analyze_server_directory(server_dir)
                if server_info:
                    servers[server_dir.name] = server_info
        
        return servers
    
    def _analyze_server_directory(self, server_dir: Path) -> Optional[Dict[str, Any]]:
        """Analyze a server directory to determine configuration"""
        info = {
            "name": server_dir.name,
            "path": str(server_dir),
            "type": "python",
            "files": {},
            "config_hints": []
        }
        
        # Check for key files
        key_files = ["pyproject.toml", "setup.py", "requirements.txt", "README.md", "main.py", "__init__.py"]
        for file_name in key_files:
            file_path = server_dir / file_name
            if file_path.exists():
                info["files"][file_name] = str(file_path)
                if file_path.stat().st_size < 10000:  # Only read small files
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            info["files"][f"{file_name}_content"] = f.read()[:2000]  # First 2000 chars
                    except:
                        pass
        
        # Check for package structure
        src_dirs = list(server_dir.glob("src/*")) + list(server_dir.glob("*/"))
        info["has_src_structure"] = any(d.is_dir() and d.name not in ["__pycache__", ".git", "tests"] for d in src_dirs)
        
        # Check for uv.lock or other dependency files
        info["has_uv"] = (server_dir / "uv.lock").exists()
        info["has_poetry"] = (server_dir / "poetry.lock").exists()
        info["has_pipenv"] = (server_dir / "Pipfile").exists()
        
        return info
    
    async def generate_smart_config(self, servers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use AI to generate optimal configurations for detected servers"""
        if not self.llm or not servers:
            return self._fallback_configuration(servers)
        
        try:
            # Prepare context for AI
            server_context = json.dumps(servers, indent=2)
            
            system_prompt = """You are an expert MCP (Model Context Protocol) server configuration specialist. 
            Your task is to analyze Python MCP server directories and generate optimal configuration entries.
            
            For each server, you need to determine:
            1. The correct command to run the server (uvx, python, uv, etc.)
            2. The proper arguments array
            3. Any required environment variables
            4. The server capabilities description
            
            Common patterns:
            - If server has uv.lock: use "uv run" with proper module path
            - If server is a published package: use "uvx package-name" 
            - If server has pyproject.toml with scripts: use those entry points
            - If server has main.py: use "python main.py"
            - If server has __main__.py: use "python -m module_name"
            
            Return ONLY a valid JSON array of server configurations. No explanation text."""
            
            human_prompt = f"""Analyze these Python MCP servers and generate configurations:

{server_context}

For each server, generate a configuration object with:
- server_name: The directory name
- command: The command to run (uvx, python, uv, etc.)
- args: Array of arguments
- env: Object with any required environment variables (use demo/test values)
- server_features_and_capability: Brief description of what the server does

Return only the JSON array of configurations."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse AI response
            config_text = response.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', config_text, re.DOTALL)
            if json_match:
                config_json = json_match.group()
                configurations = json.loads(config_json)
                return configurations
            else:
                print("⚠️  AI response not in expected JSON format. Using fallback.")
                return self._fallback_configuration(servers)
                
        except Exception as e:
            print(f"⚠️  AI configuration failed: {e}. Using fallback.")
            return self._fallback_configuration(servers)
    
    def _fallback_configuration(self, servers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback configuration when AI is not available"""
        configurations = []
        
        for server_name, info in servers.items():
            config = {
                "server_name": server_name,
                "server_features_and_capability": f"Python MCP server: {server_name}"
            }
            
            # Determine configuration based on analysis
            if server_name == "LANGSMITH_MCP":
                config.update({
                    "command": "uvx",
                    "args": ["langsmith-mcp-server"],
                    "env": {"LANGSMITH_API_KEY": "lsv2_demo_key_for_testing"}
                })
            elif "pyproject.toml_content" in info["files"]:
                pyproject_content = info["files"]["pyproject.toml_content"]
                if "uvx" in pyproject_content or "langsmith" in pyproject_content:
                    # Looks like a uvx package
                    package_name = server_name.lower().replace("_", "-")
                    config.update({
                        "command": "uvx",
                        "args": [package_name],
                        "env": {}
                    })
                elif info["has_uv"]:
                    config.update({
                        "command": "uv",
                        "args": ["--directory", f"../servers/{server_name}", "run", "python", "-m", server_name.lower()],
                        "env": {}
                    })
                else:
                    config.update({
                        "command": "python",
                        "args": ["-m", server_name.lower()],
                        "env": {}
                    })
            elif "main.py" in info["files"]:
                config.update({
                    "command": "python",
                    "args": [f"../servers/{server_name}/main.py"],
                    "env": {}
                })
            else:
                config.update({
                    "command": "python",
                    "args": ["-m", server_name.lower()],
                    "env": {}
                })
            
            configurations.append(config)
        
        return configurations
    
    def update_config_file(self, configurations: List[Dict[str, Any]]) -> bool:
        """Update the Python client configuration file"""
        if not configurations:
            print("⚠️  No configurations to update")
            return False
        
        try:
            # Read current config file
            if not self.config_file.exists():
                print(f"❌ Config file not found: {self.config_file}")
                return False
            
            with open(self.config_file, 'r') as f:
                content = f.read()
            
            # Generate new ServersConfig section
            config_lines = ["ServersConfig = [\n"]
            for config in configurations:
                config_lines.append("    {\n")
                config_lines.append(f'        "server_name": "{config["server_name"]}",\n')
                config_lines.append(f'        "command": "{config["command"]}",\n')
                config_lines.append(f'        "args": {json.dumps(config["args"])}')
                
                if config.get("env"):
                    config_lines.append(',\n')
                    config_lines.append(f'        "env": {json.dumps(config["env"])}')
                
                config_lines.append('\n    },\n')
            config_lines.append("]\n")
            
            # Replace ServersConfig section
            lines = content.split('\n')
            start_idx = -1
            end_idx = -1
            
            for i, line in enumerate(lines):
                if "ServersConfig = [" in line:
                    start_idx = i
                elif start_idx != -1 and line.strip() == "]":
                    end_idx = i
                    break
            
            if start_idx != -1 and end_idx != -1:
                new_content = '\n'.join(lines[:start_idx]) + '\n' + ''.join(config_lines) + '\n'.join(lines[end_idx + 1:])
                
                with open(self.config_file, 'w') as f:
                    f.write(new_content)
                
                print(f"✅ Updated Python config with {len(configurations)} servers")
                return True
            else:
                print("❌ Could not find ServersConfig section to replace")
                return False
                
        except Exception as e:
            print(f"❌ Failed to update config file: {e}")
            return False
    
    async def run_intelligent_configuration(self) -> bool:
        """Main method to run intelligent configuration"""
        print("🤖 AI Agent: Scanning Python MCP servers...")
        
        # Scan for servers
        servers = self.scan_python_servers()
        if not servers:
            print("⚠️  No Python MCP servers found")
            return False
        
        print(f"🔍 AI Agent: Found {len(servers)} Python servers: {list(servers.keys())}")
        
        # Generate configurations using AI
        print("🧠 AI Agent: Generating intelligent configurations...")
        configurations = await self.generate_smart_config(servers)
        
        if not configurations:
            print("❌ AI Agent: No valid configurations generated")
            return False
        
        # Update configuration file
        print("📝 AI Agent: Updating configuration file...")
        success = self.update_config_file(configurations)
        
        if success:
            print("✅ AI Agent: Python MCP configuration completed successfully!")
            for config in configurations:
                print(f"   🐍 {config['server_name']}: {config['command']} {' '.join(config['args'])}")
        
        return success

def run_sync_configuration():
    """Synchronous wrapper for the async configuration"""
    agent = MCPConfigurationAgent()
    return asyncio.run(agent.run_intelligent_configuration())

async def main():
    """CLI interface for the AI configuration agent"""
    agent = MCPConfigurationAgent()
    await agent.run_intelligent_configuration()

if __name__ == "__main__":
    asyncio.run(main())
