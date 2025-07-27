# MCP Launcher Usage Examples

## Quick Start

The simplest way to run both MCP clients:

```bash
python mcp_launcher.py
```

This will:
1. Check prerequisites (Node.js 20.8+, Python 3.8+, npm)
2. Set up JavaScript client (npm install, build)
3. Set up Python client (create venv, install dependencies)  
4. Launch both clients in separate terminal windows

## Common Usage Patterns

### 1. Run Both Clients (Default)
```bash
python mcp_launcher.py
```
- JavaScript client: http://localhost:3001 (Production mode)
- Python client: http://localhost:3000

### 2. JavaScript Client Only
```bash
python mcp_launcher.py --js-only
```
- Only starts JavaScript MCP client
- Useful for frontend development

### 3. Python Client Only  
```bash
python mcp_launcher.py --python-only
```
- Only starts Python MCP client
- Useful for backend development

### 4. Development Mode (JavaScript with Hot Reload)
```bash
python mcp_launcher.py --dev
```
- JavaScript client runs with `npm run dev:client` (hot reload)
- Python client runs normally
- Perfect for development workflow

### 5. JavaScript Development Only
```bash
python mcp_launcher.py --js-only --dev
```
- Only JavaScript client in development mode
- Maximum development efficiency

### 6. Clean Build
```bash
python mcp_launcher.py --clean
```
- Cleans JavaScript build directory before starting
- Useful after code changes or switching branches

### 7. Get Help
```bash
# Quick help
python mcp_launcher.py --help

# Detailed help with examples
python mcp_launcher.py --show-help
```

## What Happens When You Run It

### Prerequisites Check
✅ Node.js version check (20.8+ required)  
✅ Python version check (3.8+ required)  
✅ npm availability check  

### JavaScript Setup (per README)
1. Navigate to `mcp_servers/js`
2. Run `npm install` 
3. Run `npm run build:all` (with fallback)
4. Ready to start client

### Python Setup (per README)  
1. Navigate to `mcp_servers/python/clients`
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Ready to start client

### Launch Phase
- JavaScript client opens in new terminal window
- Python client opens in new terminal window  
- Each terminal shows client status and server URL
- Launcher provides summary of running services

## Terminal Windows

Each client gets its own terminal window with:

**JavaScript Terminal:**
```
JavaScript MCP Client Terminal
=====================================
Location: /path/to/mcp_servers/js/clients
Server: http://localhost:3001
Mode: Production (or Development per README)

[Client startup logs...]
```

**Python Terminal:**
```
Python MCP Client Terminal
================================
Location: /path/to/mcp_servers/python/clients  
Server: http://localhost:3000
Mode: Production

[Client startup logs...]
```

## Cross-Platform Support

The launcher automatically detects your platform and uses appropriate terminal commands:

- **Windows**: Uses `cmd` with `start` command
- **macOS**: Uses AppleScript to open Terminal windows
- **Linux**: Uses `gnome-terminal` or `xterm` as fallback

## Configuration

The launcher preserves all README-specified configurations:

- **JavaScript config**: `mcp_servers/js/clients/src/client_and_server_config.ts`
- **Python config**: `mcp_servers/python/clients/src/client_and_server_config.py`

## Troubleshooting

### Prerequisites Issues
```bash
❌ Node.js 20.8+ required (per README)
```
**Solution**: Install Node.js from https://nodejs.org

```bash
❌ Python 3.8+ required (per README)  
```
**Solution**: Install Python from https://python.org

### Build Issues
```bash
❌ JavaScript setup failed
```
**Solution**: Check Node.js/npm installation, network connectivity

```bash
❌ Python setup failed
```
**Solution**: Check Python installation, virtual environment permissions

### Port Conflicts
If ports 3000 or 3001 are already in use:

**Windows:**
```cmd
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Unix/macOS:**
```bash
lsof -ti:3000 | xargs kill
```

### Manual Recovery
If launcher fails, you can manually follow README steps:

**JavaScript:**
```bash
cd mcp_servers/js
npm install
npm run build:all
cd clients  
npm start
```

**Python:**
```bash
cd mcp_servers/python/clients
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/macOS
pip install -r requirements.txt
python run.py
```

## Integration with Development Workflow

### Daily Development
```bash
# Start development session
python mcp_launcher.py --dev

# Work on code changes...

# Restart with clean build when needed
python mcp_launcher.py --clean --dev
```

### Backend-Only Development  
```bash
python mcp_launcher.py --python-only
```

### Frontend-Only Development
```bash
python mcp_launcher.py --js-only --dev
```

### Testing Both Clients
```bash
python mcp_launcher.py
# Test integration between clients
```

## Why Use the Python Launcher?

✅ **Single File**: One simple Python file, no .bat or .exe dependencies  
✅ **Cross-Platform**: Works on Windows, macOS, Linux  
✅ **README Compliant**: Follows exact setup steps from README.md  
✅ **Error Handling**: Comprehensive validation and helpful error messages  
✅ **Flexible**: Multiple options for different development scenarios  
✅ **Colored Output**: Easy-to-read status messages and progress indicators  
✅ **Terminal Management**: Automatically opens separate terminals per platform  

The launcher makes it trivial to get both MCP clients running exactly as specified in the README, saving time and ensuring consistent setup across different environments.
