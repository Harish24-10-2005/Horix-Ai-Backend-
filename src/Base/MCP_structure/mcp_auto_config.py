#!/usr/bin/env python3
"""
MCP Server Automatic Configuration Manager
==========================================
Automatically downloads, configures, and manages MCP servers
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil
import importlib.util

class MCPServerManager:
    """Manages automatic download and configuration of MCP servers"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.servers_dir = self.base_dir / "mcp_servers"
        self.js_servers_dir = self.servers_dir / "js" / "servers"
        self.python_servers_dir = self.servers_dir / "python" / "servers"
        self.config_templates = self._load_config_templates()
        
    def _load_config_templates(self) -> Dict[str, Any]:
        """Load predefined server configurations"""
        return {
            "LANGSMITH_MCP": {
                "type": "python",
                "install_method": "uvx",
                "package_name": "langsmith-mcp-server",
                "command": "uvx",
                "args": ["langsmith-mcp-server"],
                "env_required": {
                    "LANGSMITH_API_KEY": "lsv2_demo_key_for_testing"
                },
                "repository": "https://github.com/langchain-ai/langsmith-mcp-server.git",
                "description": "MCP server for Langsmith SDK integration"
            },
            "LEETCODE_MCP": {
                "type": "javascript",
                "install_method": "npm",
                "package_name": "@jinzcdev/leetcode-mcp-server",
                "command": "node",
                "args": ["build/index.js"],
                "env_required": {},
                "repository": "https://github.com/jinzcdev/leetcode-mcp-server.git",
                "description": "An MCP server enabling automated access to LeetCode's problems, solutions, and public data"
            },
            "BUGSNAG_MCP": {
                "type": "javascript",
                "install_method": "npm",
                "package_name": "bugsnag-mcp-server",
                "command": "node",
                "args": ["build/index.js"],
                "env_required": {
                    "BUGSNAG_API_KEY": "your_bugsnag_api_key"
                },
                "repository": "https://github.com/modelcontextprotocol/servers.git",
                "subfolder": "src/bugsnag",
                "description": "A Model Context Protocol (MCP) server for interacting with Bugsnag"
            },
            "FILESYSTEM_MCP": {
                "type": "python",
                "install_method": "pip",
                "package_name": "mcp-server-filesystem",
                "command": "python",
                "args": ["-m", "mcp_server_filesystem"],
                "env_required": {},
                "repository": "https://github.com/modelcontextprotocol/servers.git",
                "subfolder": "src/filesystem",
                "description": "MCP server for filesystem operations"
            },
            "GITHUB_MCP": {
                "type": "python",
                "install_method": "pip",
                "package_name": "mcp-server-github",
                "command": "python",
                "args": ["-m", "mcp_server_github"],
                "env_required": {
                    "GITHUB_TOKEN": "your_github_token"
                },
                "repository": "https://github.com/modelcontextprotocol/servers.git",
                "subfolder": "src/github",
                "description": "MCP server for GitHub integration"
            }
        }
    
    def install_server(self, server_name: str, force_reinstall: bool = False) -> bool:
        """Install a specific MCP server"""
        if server_name not in self.config_templates:
            print(f"❌ Unknown server: {server_name}")
            print(f"Available servers: {list(self.config_templates.keys())}")
            return False
        
        config = self.config_templates[server_name]
        print(f"🚀 Installing {server_name}...")
        print(f"📝 Description: {config['description']}")
        
        try:
            if config["type"] == "python":
                return self._install_python_server(server_name, config, force_reinstall)
            elif config["type"] == "javascript":
                return self._install_javascript_server(server_name, config, force_reinstall)
            else:
                print(f"❌ Unsupported server type: {config['type']}")
                return False
        except Exception as e:
            print(f"❌ Failed to install {server_name}: {e}")
            return False
    
    def _install_python_server(self, server_name: str, config: Dict[str, Any], force_reinstall: bool) -> bool:
        """Install Python-based MCP server"""
        target_dir = self.python_servers_dir / server_name
        
        if target_dir.exists() and not force_reinstall:
            print(f"✅ {server_name} already exists. Use force_reinstall=True to reinstall.")
            return True
        
        if force_reinstall and target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if config["install_method"] == "uvx":
            # For uvx packages, just test installation
            print(f"📦 Testing uvx installation: {config['package_name']}")
            result = subprocess.run([
                "uvx", config["package_name"], "--help"
            ], capture_output=True, text=True, cwd=target_dir)
            
            if result.returncode == 0:
                print(f"✅ {server_name} uvx package verified")
                return True
            else:
                print(f"❌ Failed to verify uvx package: {result.stderr}")
                return False
                
        elif config["install_method"] == "pip":
            # Clone repository if needed
            if "repository" in config:
                print(f"📥 Cloning repository: {config['repository']}")
                subprocess.run([
                    "git", "clone", config["repository"], str(target_dir)
                ], check=True)
                
                if "subfolder" in config:
                    subfolder_path = target_dir / config["subfolder"]
                    if subfolder_path.exists():
                        # Move subfolder contents to target_dir
                        for item in subfolder_path.iterdir():
                            shutil.move(str(item), str(target_dir))
                        shutil.rmtree(subfolder_path.parent)
            
            # Install dependencies
            requirements_file = target_dir / "requirements.txt"
            if requirements_file.exists():
                print(f"📦 Installing requirements...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
            
            # Install package if specified
            if config["package_name"]:
                print(f"📦 Installing package: {config['package_name']}")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", config["package_name"]
                ], check=True)
        
        print(f"✅ {server_name} installed successfully")
        return True
    
    def _install_javascript_server(self, server_name: str, config: Dict[str, Any], force_reinstall: bool) -> bool:
        """Install JavaScript-based MCP server"""
        target_dir = self.js_servers_dir / server_name
        
        if target_dir.exists() and not force_reinstall:
            print(f"✅ {server_name} already exists. Use force_reinstall=True to reinstall.")
            return True
        
        if force_reinstall and target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if "repository" in config:
            print(f"📥 Cloning repository: {config['repository']}")
            subprocess.run([
                "git", "clone", config["repository"], str(target_dir)
            ], check=True)
            
            if "subfolder" in config:
                subfolder_path = target_dir / config["subfolder"]
                if subfolder_path.exists():
                    # Move subfolder contents to target_dir
                    for item in subfolder_path.iterdir():
                        shutil.move(str(item), str(target_dir))
                    shutil.rmtree(subfolder_path.parent)
        
        # Install npm dependencies
        package_json = target_dir / "package.json"
        if package_json.exists():
            print(f"📦 Installing npm dependencies...")
            subprocess.run(["npm", "install"], cwd=target_dir, check=True)
            
            # Build if build script exists
            with open(package_json) as f:
                pkg_data = json.load(f)
                if "scripts" in pkg_data and "build" in pkg_data["scripts"]:
                    print(f"🔨 Building project...")
                    subprocess.run(["npm", "run", "build"], cwd=target_dir, check=True)
        
        print(f"✅ {server_name} installed successfully")
        return True
    
    def generate_config(self, server_names: List[str], output_type: str = "both") -> Dict[str, Any]:
        """Generate configuration for specified servers"""
        configs = {
            "javascript": [],
            "python": []
        }
        
        for server_name in server_names:
            if server_name not in self.config_templates:
                print(f"⚠️  Unknown server: {server_name}")
                continue
            
            config = self.config_templates[server_name].copy()
            server_config = {
                "server_name": server_name,
                "command": config["command"],
                "args": config["args"],
                "server_features_and_capability": config["description"]
            }
            
            # Add environment variables if required
            if config["env_required"]:
                server_config["env"] = config["env_required"]
            
            configs[config["type"]].append(server_config)
        
        return configs
    
    def update_client_configs(self, server_names: List[str]) -> bool:
        """Update client configuration files with new servers"""
        configs = self.generate_config(server_names)
        
        # Update JavaScript client config
        js_config_file = self.servers_dir / "js" / "clients" / "src" / "client_and_server_config.ts"
        if js_config_file.exists() and configs["javascript"]:
            self._update_js_config(js_config_file, configs["javascript"])
        
        # Update Python client config
        py_config_file = self.servers_dir / "python" / "clients" / "src" / "client_and_server_config.py"
        if py_config_file.exists() and configs["python"]:
            self._update_py_config(py_config_file, configs["python"])
        
        return True
    
    def _update_js_config(self, config_file: Path, server_configs: List[Dict[str, Any]]):
        """Update JavaScript client configuration"""
        print(f"📝 Updating JavaScript config: {config_file}")
        
        # Read current config
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Generate new servers config
        servers_config = "export const ServersConfig: any[] = [\n"
        for config in server_configs:
            servers_config += "    {\n"
            servers_config += f'        server_name: "{config["server_name"]}",\n'
            servers_config += f'        command: "{config["command"]}",\n'
            if "args" in config:
                args_str = json.dumps(config["args"])
                servers_config += f'        args: {args_str},\n'
            servers_config += f'        server_features_and_capability: "{config["server_features_and_capability"]}"\n'
            servers_config += "    },\n"
        servers_config += "]"
        
        # Replace ServersConfig section
        import re
        pattern = r'export const ServersConfig: any\[\] = \[.*?\];'
        new_content = re.sub(pattern, servers_config, content, flags=re.DOTALL)
        
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ JavaScript config updated with {len(server_configs)} servers")
    
    def _update_py_config(self, config_file: Path, server_configs: List[Dict[str, Any]]):
        """Update Python client configuration"""
        print(f"📝 Updating Python config: {config_file}")
        
        # Read current config
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        # Find ServersConfig section
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(lines):
            if "ServersConfig = [" in line:
                start_idx = i
            elif start_idx != -1 and line.strip() == "]":
                end_idx = i
                break
        
        if start_idx == -1:
            print("❌ Could not find ServersConfig in Python config")
            return
        
        # Generate new config
        new_config_lines = ["ServersConfig = [\n"]
        for config in server_configs:
            new_config_lines.append("    {\n")
            new_config_lines.append(f'        "server_name": "{config["server_name"]}",\n')
            new_config_lines.append(f'        "command": "{config["command"]}",\n')
            if "args" in config:
                new_config_lines.append(f'        "args": {json.dumps(config["args"])},\n')
            if "env" in config:
                new_config_lines.append(f'        "env": {json.dumps(config["env"])},\n')
            new_config_lines.append(f'        "server_features_and_capability": "{config["server_features_and_capability"]}"\n')
            new_config_lines.append("    },\n")
        new_config_lines.append("]\n")
        
        # Replace config section
        new_lines = lines[:start_idx] + new_config_lines + lines[end_idx + 1:]
        
        with open(config_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ Python config updated with {len(server_configs)} servers")
    
    def install_and_configure(self, server_names: List[str], force_reinstall: bool = False) -> bool:
        """Install servers and update configurations"""
        print(f"🚀 Installing and configuring {len(server_names)} MCP servers...")
        
        # Install each server
        success_count = 0
        for server_name in server_names:
            if self.install_server(server_name, force_reinstall):
                success_count += 1
        
        if success_count == 0:
            print("❌ No servers were installed successfully")
            return False
        
        # Update client configurations
        self.update_client_configs(server_names)
        
        print(f"✅ Successfully installed and configured {success_count}/{len(server_names)} servers")
        return True
    
    def list_available_servers(self):
        """List all available servers"""
        print("📋 Available MCP Servers:")
        print("=" * 50)
        for name, config in self.config_templates.items():
            print(f"🔧 {name}")
            print(f"   Type: {config['type']}")
            print(f"   Install: {config['install_method']}")
            print(f"   Description: {config['description']}")
            if config['env_required']:
                print(f"   Required ENV: {list(config['env_required'].keys())}")
            print()

def main():
    """CLI interface for MCP Server Manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server Automatic Configuration Manager")
    parser.add_argument("--list", action="store_true", help="List available servers")
    parser.add_argument("--install", nargs="+", help="Install specific servers")
    parser.add_argument("--configure", nargs="+", help="Configure clients for specific servers")
    parser.add_argument("--install-and-configure", nargs="+", help="Install servers and configure clients")
    parser.add_argument("--force", action="store_true", help="Force reinstall if server exists")
    parser.add_argument("--all", action="store_true", help="Process all available servers")
    
    args = parser.parse_args()
    
    manager = MCPServerManager()
    
    if args.list:
        manager.list_available_servers()
        return
    
    if args.all:
        server_names = list(manager.config_templates.keys())
    else:
        server_names = []
        if args.install:
            server_names.extend(args.install)
        if args.configure:
            server_names.extend(args.configure)
        if args.install_and_configure:
            server_names.extend(args.install_and_configure)
    
    if not server_names:
        print("❌ No servers specified. Use --help for usage information.")
        return
    
    if args.install or args.install_and_configure:
        for server_name in server_names:
            manager.install_server(server_name, args.force)
    
    if args.configure or args.install_and_configure:
        manager.update_client_configs(server_names)

if __name__ == "__main__":
    main()
