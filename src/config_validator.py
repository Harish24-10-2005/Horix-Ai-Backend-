"""
Configuration Validator for MCP Client Configurations
Validates and tests the Python and TypeScript configuration files
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MCPConfigValidator:
    """Validates MCP client configuration files"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.python_config_path = self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "python" / "clients" / "src" / "client_and_server_config.py"
        self.ts_config_path = self.base_path / "Base" / "MCP_structure" / "mcp_servers" / "js" / "clients" / "src" / "client_and_server_config.ts"
    
    def validate_python_config(self) -> Dict[str, Any]:
        """Validate Python configuration file"""
        try:
            with open(self.python_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the Python file safely
            tree = ast.parse(content)
            
            clients_config = None
            servers_config = None
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "ClientsConfig":
                                clients_config = ast.literal_eval(node.value)
                            elif target.id == "ServersConfig":
                                servers_config = ast.literal_eval(node.value)
            
            # Validate structure
            errors = []
            warnings = []
            
            if not clients_config:
                errors.append("ClientsConfig not found or invalid")
            elif not isinstance(clients_config, list):
                errors.append("ClientsConfig must be a list")
            
            if not servers_config:
                errors.append("ServersConfig not found or invalid")
            elif not isinstance(servers_config, list):
                errors.append("ServersConfig must be a list")
            else:
                # Validate each server config
                for i, server in enumerate(servers_config):
                    if not isinstance(server, dict):
                        errors.append(f"Server config {i} must be a dictionary")
                        continue
                    
                    required_fields = ["server_name", "command", "args"]
                    for field in required_fields:
                        if field not in server:
                            errors.append(f"Server config {i} missing required field: {field}")
                    
                    if "args" in server and not isinstance(server["args"], list):
                        errors.append(f"Server config {i}: args must be a list")
                    
                    # Check for duplicates
                    server_names = [s.get("server_name") for s in servers_config if isinstance(s, dict)]
                    duplicates = [name for name in set(server_names) if server_names.count(name) > 1]
                    if duplicates:
                        warnings.append(f"Duplicate server names found: {duplicates}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "clients": clients_config,
                "servers": servers_config,
                "server_count": len(servers_config) if servers_config else 0
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse Python config: {e}"],
                "warnings": [],
                "clients": None,
                "servers": None,
                "server_count": 0
            }
    
    def validate_typescript_config(self) -> Dict[str, Any]:
        """Validate TypeScript configuration file"""
        try:
            with open(self.ts_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            errors = []
            warnings = []
            
            # Extract ClientsConfig
            clients_match = re.search(r'export const ClientsConfig:\s*.*?\[\s*(.*?)\s*\]', content, re.DOTALL)
            clients_config = None
            if clients_match:
                try:
                    # Clean up the match and parse as JSON array
                    clients_str = clients_match.group(1).strip()
                    if clients_str:
                        # Convert TypeScript array to JSON by removing quotes and re-adding them properly
                        clients_items = [item.strip().strip('"\'') for item in clients_str.split(',') if item.strip()]
                        clients_config = clients_items
                except Exception as e:
                    errors.append(f"Failed to parse ClientsConfig: {e}")
            
            # Extract ServersConfig - use simple counting approach
            servers_config = []
            server_count = 0
            
            # Count server_name occurrences in the entire file (more reliable)
            server_name_matches = re.findall(r'server_name:\s*"([^"]+)"', content)
            server_count = len(server_name_matches)
            
            if server_count > 0:
                # Create placeholder server objects for validation
                servers_config = [{"name": name} for name in server_name_matches]
                
                # Basic structure validation - check if ServersConfig export exists
                if 'export const ServersConfig' not in content:
                    errors.append("ServersConfig export statement not found")
                
                # Check for required fields by counting occurrences
                command_count = content.count('command:')
                args_count = content.count('args:')
                
                if command_count != server_count:
                    warnings.append(f"Expected {server_count} command fields, found {command_count}")
                if args_count != server_count:
                    warnings.append(f"Expected {server_count} args fields, found {args_count}")
            
            # Basic validation
            if not clients_match:
                errors.append("ClientsConfig export not found")
            
            # Syntax validation
            if 'export const ClientsConfig' not in content:
                errors.append("ClientsConfig export statement malformed")
            if 'export const ServersConfig' not in content and server_count == 0:
                errors.append("ServersConfig export statement malformed")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "clients": clients_config,
                "servers": servers_config,
                "server_count": server_count
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to read TypeScript config: {e}"],
                "warnings": [],
                "clients": None,
                "servers": None,
                "server_count": 0
            }
    
    def validate_all_configs(self) -> Dict[str, Any]:
        """Validate both configuration files"""
        python_result = self.validate_python_config()
        typescript_result = self.validate_typescript_config()
        
        return {
            "python": python_result,
            "typescript": typescript_result,
            "overall_valid": python_result["valid"] and typescript_result["valid"],
            "total_errors": len(python_result["errors"]) + len(typescript_result["errors"]),
            "total_warnings": len(python_result["warnings"]) + len(typescript_result["warnings"])
        }
    
    def print_validation_report(self):
        """Print a comprehensive validation report"""
        result = self.validate_all_configs()
        
        print("🔍 MCP Configuration Validation Report")
        print("=" * 50)
        
        # Python Config
        python = result["python"]
        print(f"\n📄 Python Configuration ({self.python_config_path.name}):")
        if python["valid"]:
            print(f"  ✅ Valid - {python['server_count']} servers configured")
        else:
            print(f"  ❌ Invalid - {len(python['errors'])} errors")
            for error in python["errors"]:
                print(f"    • {error}")
        
        if python["warnings"]:
            print(f"  ⚠️  {len(python['warnings'])} warnings:")
            for warning in python["warnings"]:
                print(f"    • {warning}")
        
        # TypeScript Config
        typescript = result["typescript"]
        print(f"\n📄 TypeScript Configuration ({self.ts_config_path.name}):")
        if typescript["valid"]:
            print(f"  ✅ Valid - {typescript['server_count']} servers configured")
        else:
            print(f"  ❌ Invalid - {len(typescript['errors'])} errors")
            for error in typescript["errors"]:
                print(f"    • {error}")
        
        if typescript["warnings"]:
            print(f"  ⚠️  {len(typescript['warnings'])} warnings:")
            for warning in typescript["warnings"]:
                print(f"    • {warning}")
        
        # Overall Status
        print(f"\n🎯 Overall Status:")
        if result["overall_valid"]:
            print("  ✅ All configurations are valid!")
        else:
            print(f"  ❌ Issues found - {result['total_errors']} errors, {result['total_warnings']} warnings")
        
        print("=" * 50)
        
        return result

def main():
    """Test the configuration validator"""
    import sys
    from pathlib import Path
    
    # Get the project base path (go up from src to project root, then into src)
    base_path = Path(__file__).parent.parent / "src"
    
    validator = MCPConfigValidator(str(base_path))
    validator.print_validation_report()

if __name__ == "__main__":
    main()
