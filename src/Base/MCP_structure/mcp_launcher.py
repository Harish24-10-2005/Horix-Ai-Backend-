#!/usr/bin/env python3
"""
MCP Clients Launcher (Python)
==============================

A simple Python script that launches both JavaScript and Python MCP clients
in separate terminals, following the exact setup steps from README.md.

Usage:
    python mcp_launcher.py [options]

Options:
    --help              Show this help message
    --js-only           Run only JavaScript client
    --python-only       Run only Python client
    --dev               Run JavaScript client in development mode
    --clean             Clean build directories before starting

Examples:
    python mcp_launcher.py                    # Run both clients
    python mcp_launcher.py --js-only          # JavaScript only
    python mcp_launcher.py --python-only      # Python only
    python mcp_launcher.py --dev              # Both (JS in dev mode)

Client Endpoints:
    JavaScript MCP Client: http://localhost:3001
    Python MCP Client: http://localhost:3000
"""

import os
import sys
import subprocess
import platform
import time
import argparse
import shutil
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class MCPLauncher:
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_windows = self.platform == 'windows'
        self.is_macos = self.platform == 'darwin'
        self.is_linux = self.platform == 'linux'
        
        # Paths
        self.base_dir = Path(__file__).parent.absolute()
        self.js_dir = self.base_dir / "mcp_servers" / "js"
        self.js_client_dir = self.js_dir / "clients"
        self.python_dir = self.base_dir / "mcp_servers" / "python" / "clients"
        
    def log(self, message, color=Colors.WHITE):
        """Print colored log message"""
        print(f"{color}{message}{Colors.RESET}")
        
    def log_success(self, message):
        self.log(f"✅ {message}", Colors.GREEN)
        
    def log_error(self, message):
        self.log(f"❌ {message}", Colors.RED)
        
    def log_warning(self, message):
        self.log(f"⚠️  {message}", Colors.YELLOW)
        
    def log_info(self, message):
        self.log(f"ℹ️  {message}", Colors.CYAN)

    def run_command(self, command, cwd=None, check=True):
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            if check:
                raise e
            return e

    def check_prerequisites(self):
        """Check if required tools are installed (per README)"""
        self.log("🔍 Checking prerequisites...", Colors.CYAN)
        
        # Check Node.js (20.8+ per README)
        try:
            result = self.run_command("node --version")
            node_version = result.stdout.strip()
            self.log_success(f"Node.js found: {node_version}")
        except subprocess.CalledProcessError:
            self.log_error("Node.js 20.8+ required (per README)")
            return False
            
        # Check Python (3.8+ per README)
        try:
            result = self.run_command("python --version")
            python_version = result.stdout.strip()
            self.log_success(f"Python found: {python_version}")
        except subprocess.CalledProcessError:
            self.log_error("Python 3.8+ required (per README)")
            return False
            
        # Check npm
        try:
            result = self.run_command("npm --version")
            npm_version = result.stdout.strip()
            self.log_success(f"npm found: v{npm_version}")
        except subprocess.CalledProcessError:
            self.log_error("npm required for JavaScript dependencies")
            return False
            
        return True

    def run_auto_configuration(self):
        """Run automatic MCP server configuration using AI for Python"""
        try:
            # Smart configuration for Python using AI agent
            self.log("🤖 Running AI-powered Python MCP configuration...", Colors.CYAN)
            
            try:
                from mcp_ai_config_agent import run_sync_configuration
                python_success = run_sync_configuration()
            except ImportError:
                self.log_warning("AI configuration agent not available, using smart fallback")
                python_success = self._run_smart_config()
            except Exception as e:
                self.log_warning(f"AI configuration failed: {e}, using smart fallback")
                python_success = self._run_smart_config()
            
            # Standard configuration for JavaScript (current technique is fine)
            self.log("🔧 Running JavaScript MCP auto-configuration...", Colors.CYAN)
            js_success = self._configure_javascript_servers()
            
            if python_success or js_success:
                self.log_success("MCP server configurations updated successfully")
            else:
                self.log_warning("No MCP servers detected. Install servers to enable MCP functionality.")
                
        except Exception as e:
            self.log_error(f"Auto-configuration failed: {e}")
    
    def _run_smart_config(self):
        """Fallback smart configuration for Python"""
        try:
            from mcp_smart_config import update_configs
            update_configs()
            return True
        except:
            return False
    
    def _configure_javascript_servers(self):
        """Configure JavaScript MCP servers using current technique"""
        try:
            js_servers_dir = self.base_dir / "mcp_servers" / "js" / "servers"
            js_config_file = self.base_dir / "mcp_servers" / "js" / "clients" / "src" / "client_and_server_config.ts"
            
            if not js_servers_dir.exists() or not js_config_file.exists():
                return False
            
            servers = []
            for server_dir in js_servers_dir.glob("*"):
                if server_dir.is_dir():
                    build_index = server_dir / "build" / "index.js"
                    if build_index.exists():
                        servers.append({
                            "server_name": server_dir.name,
                            "command": "node",
                            "args": [f"../servers/{server_dir.name}/build/index.js"],
                            "server_features_and_capability": f"Auto-configured {server_dir.name} server"
                        })
            
            if servers:
                self._update_js_config_file(js_config_file, servers)
                return True
            return False
            
        except Exception as e:
            self.log_warning(f"JavaScript auto-configuration failed: {e}")
            return False
    
    def _update_js_config_file(self, config_file, servers):
        """Update JavaScript configuration file"""
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Generate new config
            config_lines = ["export const ServersConfig: any[] = [\n"]
            for server in servers:
                config_lines.append("    {\n")
                config_lines.append(f'        server_name: "{server["server_name"]}",\n')
                config_lines.append(f'        command: "{server["command"]}",\n')
                args_str = str(server["args"]).replace("'", '"')
                config_lines.append(f'        args: {args_str},\n')
                config_lines.append(f'        server_features_and_capability: "{server["server_features_and_capability"]}"\n')
                config_lines.append("    },\n")
            config_lines.append("];\n")
            
            # Replace in content
            import re
            pattern = r'export const ServersConfig: any\[\] = \[.*?\];'
            new_content = re.sub(pattern, ''.join(config_lines).rstrip() + ';', content, flags=re.DOTALL)
            
            with open(config_file, 'w') as f:
                f.write(new_content)
            
            return True
        except Exception as e:
            print(f"Failed to update JS config: {e}")
            return False
                
        except ImportError:
            # Auto-manager not available, skip auto-configuration
            pass
        except Exception as e:
            self.log_warning(f"Auto-configuration failed: {e}")

    def setup_javascript_client(self, clean=False):
        """Setup JavaScript client following README steps"""
        self.log("🟨 Setting up JavaScript MCP Client (per README)...", Colors.YELLOW)
        
        # Step 1: Navigate to JavaScript Directory (per README)
        if not self.js_dir.exists():
            self.log_error(f"JavaScript directory not found: {self.js_dir}")
            return False
            
        try:
            # Step 2: Install Dependencies (per README)
            self.log("📦 Running: npm install", Colors.YELLOW)
            self.run_command("npm install", cwd=self.js_dir)
            
            # Step 3: Build All Components (per README)
            if clean and (self.js_client_dir / "build").exists():
                self.log("🧹 Cleaning JavaScript build directory...", Colors.YELLOW)
                shutil.rmtree(self.js_client_dir / "build")
                
            self.log("🔨 Running: npm run build:all", Colors.YELLOW)
            try:
                self.run_command("npm run build:all", cwd=self.js_dir)
            except subprocess.CalledProcessError:
                # Fallback: build clients individually
                self.log("🔄 build:all not found, building clients individually...", Colors.YELLOW)
                self.run_command("npm run build", cwd=self.js_client_dir)
                
            self.log_success("JavaScript client setup complete")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"JavaScript setup failed: {e}")
            return False

    def setup_python_client(self):
        """Setup Python client following README steps"""
        self.log("🐍 Setting up Python MCP Client (per README)...", Colors.YELLOW)
        
        # Step 1: Navigate to Python Directory (per README)
        if not self.python_dir.exists():
            self.log_error(f"Python client directory not found: {self.python_dir}")
            return False
            
        try:
            # Step 2: Create Virtual Environment (per README)
            venv_dir = self.python_dir / "venv"
            if not venv_dir.exists():
                self.log("🔧 Running: python -m venv venv", Colors.YELLOW)
                self.run_command("python -m venv venv", cwd=self.python_dir)
                
            # Step 4: Install Dependencies (per README)
            self.log("📦 Running: pip install -r requirements.txt", Colors.YELLOW)
            if self.is_windows:
                pip_path = venv_dir / "Scripts" / "pip.exe"
            else:
                pip_path = venv_dir / "bin" / "pip"
                
            self.run_command(f'"{pip_path}" install -r requirements.txt', cwd=self.python_dir)
            
            self.log_success("Python client setup complete")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"Python setup failed: {e}")
            return False

    def start_javascript_client(self, dev_mode=False):
        """Start JavaScript client in new terminal (Step 4 per README)"""
        self.log("🚀 Starting JavaScript MCP Client...", Colors.GREEN)
        
        # Step 4: Start Development Server (per README)
        command = "npm run dev:client" if dev_mode else "npm start"
        mode = "Development (per README)" if dev_mode else "Production"
        
        if self.is_windows:
            # Windows - use cmd to start new window
            terminal_cmd = f'''start "JavaScript MCP Client" cmd /k "echo JavaScript MCP Client Terminal && echo ===================================== && echo Location: {self.js_client_dir} && echo Server: http://localhost:3001 && echo Mode: {mode} && echo. && cd /d "{self.js_client_dir}" && {command}"'''
            subprocess.Popen(terminal_cmd, shell=True)
            
        elif self.is_macos:
            # macOS - use AppleScript to open new Terminal window
            script = f'''
            tell application "Terminal"
                do script "echo 'JavaScript MCP Client Terminal' && echo '=====================================' && echo 'Location: {self.js_client_dir}' && echo 'Server: http://localhost:3001' && echo 'Mode: {mode}' && echo '' && cd '{self.js_client_dir}' && {command}"
                activate
            end tell
            '''
            subprocess.Popen(['osascript', '-e', script])
            
        else:
            # Linux - use gnome-terminal or xterm
            script = f"echo 'JavaScript MCP Client Terminal' && echo '=====================================' && echo 'Location: {self.js_client_dir}' && echo 'Server: http://localhost:3001' && echo 'Mode: {mode}' && echo '' && cd '{self.js_client_dir}' && {command}; exec bash"
            try:
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', script])
            except FileNotFoundError:
                try:
                    subprocess.Popen(['xterm', '-e', f'bash -c "{script}"'])
                except FileNotFoundError:
                    self.log_error("No suitable terminal found (gnome-terminal or xterm required)")
                    return False
                    
        return True

    def start_python_client(self):
        """Start Python client in new terminal (Step 5 per README)"""
        self.log("🚀 Starting Python MCP Client...", Colors.GREEN)
        
        # Step 5: Run the Client (per README) - using run.py instead of src/main.py
        if self.is_windows:
            # Step 3: Activate Virtual Environment (Windows per README)
            activate_cmd = f'"{self.python_dir}\\venv\\Scripts\\activate"'
            python_cmd = "python run.py"
            
            terminal_cmd = f'''start "Python MCP Client" cmd /k "echo Python MCP Client Terminal && echo ================================ && echo Location: {self.python_dir} && echo Server: http://localhost:3000 && echo Mode: Production && echo. && cd /d "{self.python_dir}" && {activate_cmd} && {python_cmd}"'''
            subprocess.Popen(terminal_cmd, shell=True)
            
        elif self.is_macos:
            # Unix activation (per README)
            script = f'''
            tell application "Terminal"
                do script "echo 'Python MCP Client Terminal' && echo '================================' && echo 'Location: {self.python_dir}' && echo 'Server: http://localhost:3000' && echo 'Mode: Production' && echo '' && cd '{self.python_dir}' && source venv/bin/activate && python run.py"
                activate
            end tell
            '''
            subprocess.Popen(['osascript', '-e', script])
            
        else:
            # Linux
            script = f"echo 'Python MCP Client Terminal' && echo '================================' && echo 'Location: {self.python_dir}' && echo 'Server: http://localhost:3000' && echo 'Mode: Production' && echo '' && cd '{self.python_dir}' && source venv/bin/activate && python run.py; exec bash"
            try:
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', script])
            except FileNotFoundError:
                try:
                    subprocess.Popen(['xterm', '-e', f'bash -c "{script}"'])
                except FileNotFoundError:
                    self.log_error("No suitable terminal found (gnome-terminal or xterm required)")
                    return False
                    
        return True

    def show_help(self):
        """Show help information"""
        print(__doc__)

    def run(self, args):
        """Main execution function"""
        if args.show_help:
            self.show_help()
            return
            
        self.log("🚀 MCP Clients Launcher (Python)", Colors.CYAN)
        self.log("=================================", Colors.CYAN)
        self.log("Following README.md setup specifications", Colors.CYAN)
        print()
        
        # Prerequisites check
        if not self.check_prerequisites():
            self.log_error("Prerequisites check failed. Install missing requirements per README.")
            sys.exit(1)
            
        # Auto-configuration check
        self.run_auto_configuration()
        
        print()
        self.log("📋 Execution Plan:", Colors.CYAN)
        if not args.python_only:
            mode = "Development Mode" if args.dev else "Production Mode"
            self.log(f"   🟨 JavaScript MCP Client ({mode})", Colors.CYAN)
        if not args.js_only:
            self.log("   🐍 Python MCP Client (Production Mode)", Colors.CYAN)
        print()
        
        # Setup phase
        self.log("🔧 Setup Phase (following README steps)...", Colors.CYAN)
        
        if not args.python_only:
            if not self.setup_javascript_client(args.clean):
                self.log_error("JavaScript client setup failed")
                sys.exit(1)
                
        if not args.js_only:
            if not self.setup_python_client():
                self.log_error("Python client setup failed")
                sys.exit(1)
                
        self.log_success("All clients setup complete!")
        print()
        
        # Launch phase
        self.log("🚀 Launch Phase...", Colors.CYAN)
        
        if not args.python_only:
            if not self.start_javascript_client(args.dev):
                self.log_error("Failed to start JavaScript client")
                sys.exit(1)
            time.sleep(3)  # Allow JS client to start
            
        if not args.js_only:
            if not self.start_python_client():
                self.log_error("Failed to start Python client")
                sys.exit(1)
                
        print()
        self.log("🎉 MCP Clients Launched Successfully!", Colors.GREEN)
        self.log("====================================", Colors.GREEN)
        print()
        
        if not args.python_only:
            self.log("🟨 JavaScript Client: http://localhost:3001", Colors.YELLOW)
        if not args.js_only:
            self.log("🐍 Python Client: http://localhost:3000", Colors.YELLOW)
            
        print()
        self.log("📝 Instructions:", Colors.CYAN)
        print("• Each client runs in a separate terminal window")
        print("• Clients are configured per README specifications")
        print("• Close terminal windows to stop clients")
        print("• Use Ctrl+C in terminals for graceful shutdown")
        print()
        self.log("🔧 Configuration Files:", Colors.CYAN)
        print("• JavaScript: mcp_servers/js/clients/src/client_and_server_config.ts")
        print("• Python: mcp_servers/python/clients/src/client_and_server_config.py")
        print()
        self.log("📚 Documentation: mcp_servers_documentation/", Colors.CYAN)
        self.log("🧪 API Testing: postman_api_collections/", Colors.CYAN)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MCP Clients Launcher - Launch JavaScript and Python MCP clients",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcp_launcher.py                    # Run both clients
  python mcp_launcher.py --js-only          # JavaScript only
  python mcp_launcher.py --python-only      # Python only
  python mcp_launcher.py --dev              # Both (JS in dev mode)
  python mcp_launcher.py --clean            # Clean build + run both

Client Endpoints:
  JavaScript MCP Client: http://localhost:3001
  Python MCP Client: http://localhost:3000
        """
    )
    
    parser.add_argument('--show-help', action='store_true', help='Show detailed help information')
    parser.add_argument('--js-only', action='store_true', help='Run only JavaScript client')
    parser.add_argument('--python-only', action='store_true', help='Run only Python client')
    parser.add_argument('--dev', action='store_true', help='Run JavaScript client in development mode')
    parser.add_argument('--clean', action='store_true', help='Clean build directories before starting')
    
    args = parser.parse_args()
    
    launcher = MCPLauncher()
    try:
        launcher.run(args)
    except KeyboardInterrupt:
        launcher.log("\n🛑 Launcher interrupted by user", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        launcher.log_error(f"Launcher failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
