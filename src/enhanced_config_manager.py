"""
Enhanced Configuration Manager for MCP Servers
Provides robust configuration updates with proper validation and error handling
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MCPConfigurationManager:
    """Enhanced configuration manager with robust error handling"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.python_config_path = self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "python" / "clients" / "src" / "client_and_server_config.py"
        self.ts_config_path = self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "js" / "clients" / "src" / "client_and_server_config.ts"
    
    def detect_server_configuration(self, server_name: str, language: str) -> Dict[str, Any]:
        """Intelligently detect the correct configuration for a server"""
        config = {
            "server_name": server_name,
            "command": "",
            "args": [],
            "env": {}
        }
        
        if language.lower() == "python":
            server_path = self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "python" / "servers" / server_name
            config["command"] = "uv"
            
            # Smart detection based on server structure
            if server_name == "LANGSMITH_MCP":
                # Special case for LangSmith - check actual structure
                config["args"] = [
                    "--directory",
                    f"../servers/{server_name}",
                    "run",
                    "python",
                    "-m",
                    "langsmith_mcp_server.server"
                ]
                config["env"] = {"LANGSMITH_API_KEY": "lsv2_demo_key_for_testing"}
            else:
                # Generic Python server detection
                if (server_path / "main.py").exists():
                    config["args"] = ["--directory", f"../servers/{server_name}", "run", "main.py"]
                elif (server_path / "server.py").exists():
                    config["args"] = ["--directory", f"../servers/{server_name}", "run", "server.py"]
                elif (server_path / "src" / "main.py").exists():
                    config["args"] = ["--directory", f"../servers/{server_name}", "run", "src/main.py"]
                elif (server_path / "src" / "server.py").exists():
                    config["args"] = ["--directory", f"../servers/{server_name}", "run", "src/server.py"]
                else:
                    # Check for package structure
                    package_dir = None
                    if server_path.exists():
                        for item in server_path.iterdir():
                            if item.is_dir() and not item.name.startswith('.'):
                                if (item / "server.py").exists():
                                    package_dir = item.name
                                    break
                    
                    if package_dir:
                        config["args"] = ["--directory", f"../servers/{server_name}/{package_dir}", "run", "server.py"]
                    else:
                        # Default fallback
                        config["args"] = ["--directory", f"../servers/{server_name}", "run", "main.py"]
                        
        else:  # JavaScript/TypeScript
            config["command"] = "node"
            if (self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "js" / "servers" / server_name / "build" / "index.js").exists():
                config["args"] = [f"../servers/{server_name}/build/index.js"]
            elif (self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "js" / "servers" / server_name / "dist" / "index.js").exists():
                config["args"] = [f"../servers/{server_name}/dist/index.js"]
            elif (self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "js" / "servers" / server_name / "index.js").exists():
                config["args"] = [f"../servers/{server_name}/index.js"]
            else:
                config["args"] = [f"../servers/{server_name}/build/index.js"]  # Default
        
        return config
    
    def update_python_config(self, server_name: str, language: str = "python") -> bool:
        """Update Python configuration with proper error handling"""
        try:
            # Detect the correct configuration
            server_config = self.detect_server_configuration(server_name, language)
            
            # Read current configuration
            with open(self.python_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if server already exists
            if f'"server_name": "{server_name}"' in content:
                logger.info(f"Server {server_name} already exists in Python config")
                return True
            
            # Parse the current config safely
            try:
                tree = ast.parse(content)
                existing_servers = []
                clients_config = ["MCP_CLIENT_AZURE_AI", "MCP_CLIENT_OPENAI", "MCP_CLIENT_GEMINI"]
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id == "ServersConfig":
                                    existing_servers = ast.literal_eval(node.value)
                                elif target.id == "ClientsConfig":
                                    clients_config = ast.literal_eval(node.value)
                
                # Add new server
                existing_servers.append(server_config)
                
                # Generate new content
                new_content = f"""ClientsConfig = {json.dumps(clients_config, indent=4)}

ServersConfig = {json.dumps(existing_servers, indent=4)}
"""
                
                # Write back to file
                with open(self.python_config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"Successfully updated Python config for {server_name}")
                return True
                
            except Exception as parse_error:
                logger.error(f"Error parsing Python config: {parse_error}")
                return self._fallback_python_update(server_config)
                
        except Exception as e:
            logger.error(f"Error updating Python config: {e}")
            return False
    
    def _fallback_python_update(self, server_config: Dict[str, Any]) -> bool:
        """Fallback method for updating Python config"""
        try:
            # Generate a clean, complete configuration file
            clients_config = ["MCP_CLIENT_AZURE_AI", "MCP_CLIENT_OPENAI", "MCP_CLIENT_GEMINI"]
            servers_config = [server_config]
            
            new_content = f"""ClientsConfig = {json.dumps(clients_config, indent=4)}

ServersConfig = {json.dumps(servers_config, indent=4)}
"""
            
            with open(self.python_config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Fallback update successful for {server_config['server_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Fallback update failed: {e}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate both Python and TypeScript configurations"""
        results = {
            "python": {"valid": False, "errors": [], "servers": []},
            "typescript": {"valid": False, "errors": [], "servers": []}
        }
        
        # Validate Python config
        try:
            with open(self.python_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "ServersConfig":
                            servers = ast.literal_eval(node.value)
                            results["python"]["servers"] = servers
                            results["python"]["valid"] = True
                            
        except Exception as e:
            results["python"]["errors"].append(str(e))
        
        # Validate TypeScript config
        try:
            with open(self.ts_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex parsing for TypeScript
            servers_match = re.search(r'export const ServersConfig.*?=\s*(\[.*?\]);', content, re.DOTALL)
            if servers_match:
                results["typescript"]["valid"] = True
                
        except Exception as e:
            results["typescript"]["errors"].append(str(e))
        
        return results

if __name__ == "__main__":
    # Test the configuration manager
    manager = MCPConfigurationManager("d:/Horix AI/Backend/src")
    
    # Test detection
    config = manager.detect_server_configuration("LANGSMITH_MCP", "python")
    print("Detected config:", json.dumps(config, indent=2))
    
    # Test validation
    validation = manager.validate_configuration()
    print("Validation results:", json.dumps(validation, indent=2))
