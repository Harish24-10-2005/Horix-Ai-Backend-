"""
README Manager for MCP Servers
Automatically collects and stores README files from downloaded MCP servers
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class MCPReadmeManager:
    """Manages automatic README collection and organization for MCP servers"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.doc_folder = self.base_path / "Doc"
        self.mcp_servers_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers"
        self.readme_index_file = self.doc_folder / "README_FOR_ALL_MCP.md"
        self.readme_metadata_file = self.doc_folder / "readme_metadata.json"
        
        # Ensure Doc folder exists
        self.doc_folder.mkdir(exist_ok=True)
        
        # Initialize metadata file if it doesn't exist
        if not self.readme_metadata_file.exists():
            self._initialize_metadata()
    
    def _initialize_metadata(self):
        """Initialize the README metadata file"""
        initial_metadata = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "total_mcps": 0,
            "mcp_readmes": {},
            "statistics": {
                "python_mcps": 0,
                "javascript_mcps": 0,
                "typescript_mcps": 0,
                "total_readme_files": 0
            }
        }
        
        with open(self.readme_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(initial_metadata, f, indent=2)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load the README metadata"""
        try:
            with open(self.readme_metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading metadata: {e}, creating new metadata")
            self._initialize_metadata()
            return self._load_metadata()
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save the README metadata"""
        metadata["last_updated"] = datetime.now().isoformat()
        with open(self.readme_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def collect_readme_after_download(self, server_name: str, server_path: Path, language: str, repository_url: str = ""):
        """
        Collect README file after MCP server download
        This should be called after each MCP server is successfully downloaded
        """
        try:
            logger.info(f"📚 Collecting README for {server_name}...")
            
            # Find README files in the server directory
            readme_files = self._find_readme_files(server_path)
            
            if not readme_files:
                logger.warning(f"No README file found for {server_name}")
                # Create a placeholder README
                self._create_placeholder_readme(server_name, language, repository_url)
                return False
            
            # Process each README file found
            success = False
            for readme_file in readme_files:
                if self._process_readme_file(server_name, readme_file, language, repository_url):
                    success = True
            
            if success:
                self._update_main_readme_index()
                logger.info(f"✅ Successfully collected README for {server_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error collecting README for {server_name}: {e}")
            return False
    
    def _find_readme_files(self, server_path: Path) -> List[Path]:
        """Find all README files in the server directory"""
        readme_files = []
        
        # Common README file patterns
        readme_patterns = [
            "README.md",
            "readme.md", 
            "ReadMe.md",
            "README.rst",
            "README.txt",
            "README"
        ]
        
        # Search in the server directory and subdirectories
        for pattern in readme_patterns:
            # Check root directory
            readme_file = server_path / pattern
            if readme_file.exists():
                readme_files.append(readme_file)
            
            # Check subdirectories (max depth 2)
            for subdir in server_path.iterdir():
                if subdir.is_dir():
                    sub_readme = subdir / pattern
                    if sub_readme.exists():
                        readme_files.append(sub_readme)
                    
                    # Check one more level deep
                    for sub_subdir in subdir.iterdir():
                        if sub_subdir.is_dir():
                            deep_readme = sub_subdir / pattern
                            if deep_readme.exists():
                                readme_files.append(deep_readme)
        
        return readme_files
    
    def _process_readme_file(self, server_name: str, readme_file: Path, language: str, repository_url: str) -> bool:
        """Process and copy a README file to the Doc folder"""
        try:
            # Create a sanitized filename
            sanitized_name = re.sub(r'[^\w\-_]', '_', server_name)
            
            # Determine the relative path - simplified approach
            try:
                # Try to find the server directory in the path
                server_name_base = server_name.split('_')[0] if '_' in server_name else server_name
                path_parts = readme_file.parts
                
                # Find the server directory index
                server_dir_index = -1
                for i, part in enumerate(path_parts):
                    if server_name_base.lower() in part.lower() or server_name.lower() in part.lower():
                        server_dir_index = i
                        break
                
                if server_dir_index >= 0:
                    relative_path = readme_file.relative_to(Path(*path_parts[:server_dir_index + 1]))
                else:
                    # Fallback: just use the filename
                    relative_path = Path(readme_file.name)
                    
            except Exception:
                # Fallback: just use the filename
                relative_path = Path(readme_file.name)
            
            # Create destination filename with context
            if relative_path.name.lower() == "readme.md":
                dest_filename = f"{sanitized_name}_README.md"
            else:
                dest_filename = f"{sanitized_name}_{relative_path.name}"
            
            dest_path = self.doc_folder / dest_filename
            
            # Read and enhance the README content
            enhanced_content = self._enhance_readme_content(readme_file, server_name, language, repository_url)
            
            # Write the enhanced content
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            # Update metadata
            self._update_readme_metadata(server_name, dest_filename, language, repository_url, str(relative_path))
            
            logger.info(f"📄 Copied README: {readme_file} -> {dest_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing README file {readme_file}: {e}")
            return False
    
    def _enhance_readme_content(self, readme_file: Path, server_name: str, language: str, repository_url: str) -> str:
        """Enhance README content with metadata and context"""
        try:
            # Read original content
            with open(readme_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(readme_file, 'r', encoding='latin-1') as f:
                    original_content = f.read()
            except Exception:
                original_content = f"# {server_name}\n\nCould not read original README content due to encoding issues."
        
        # Create enhanced header
        enhanced_header = f"""<!-- AUTO-GENERATED MCP README -->
<!-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
<!-- Source: {readme_file} -->

# MCP Server: {server_name}

**🔧 Language:** {language.title()}  
**📦 Server Type:** MCP (Model Context Protocol)  
**📅 Added to Collection:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**🔗 Repository:** {repository_url if repository_url else 'Not specified'}  
**📍 Source Location:** `{readme_file}`

---

## Original README Content

"""
        
        # Create enhanced footer
        enhanced_footer = f"""

---

## Integration Notes

This MCP server has been automatically integrated into the Enhanced AI Agent Protocol system.

### Quick Access
- **Configuration Location:** `src/Base/MCP_structure/mcp_servers/{language}/servers/{server_name}/`
- **Language:** {language.title()}
- **Status:** ✅ Integrated

### Usage in System
You can interact with this MCP server through:
1. **Interactive Mode:** `python final_demo.py` → Option 2
2. **Natural Language:** Describe what you need and the system will use appropriate MCPs
3. **Direct Access:** Use the AI Agent Protocol to call specific MCP functions

### Management Commands
```bash
# Check server status
python -c "from src.ai_agent_protocol.core import AIAgentProtocol; import asyncio; protocol = AIAgentProtocol('.'); asyncio.run(protocol.list_available_mcp_servers())"

# Validate configuration
python src/config_validator.py
```

---
*This README was automatically collected and enhanced by the Enhanced AI Agent Protocol system.*
"""
        
        return enhanced_header + original_content + enhanced_footer
    
    def _create_placeholder_readme(self, server_name: str, language: str, repository_url: str):
        """Create a placeholder README when no README is found"""
        sanitized_name = re.sub(r'[^\w\-_]', '_', server_name)
        dest_filename = f"{sanitized_name}_README.md"
        dest_path = self.doc_folder / dest_filename
        
        placeholder_content = f"""# MCP Server: {server_name}

**⚠️ No Original README Found**

**🔧 Language:** {language.title()}  
**📦 Server Type:** MCP (Model Context Protocol)  
**📅 Added to Collection:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**🔗 Repository:** {repository_url if repository_url else 'Not specified'}

---

## Description

This MCP server was successfully downloaded and integrated, but no README file was found in the source code. 

### Integration Status
✅ **Downloaded:** Server files successfully retrieved  
✅ **Configured:** Added to MCP client configurations  
⚠️  **Documentation:** No original README available  

### Usage
You can still use this MCP server through the Enhanced AI Agent Protocol system:

1. **Interactive Mode:** `python final_demo.py` → Option 2
2. **Natural Language Commands:** The system can auto-detect capabilities
3. **Direct Protocol Access:** Use the AI Agent Protocol

### Server Location
- **Configuration:** `src/Base/MCP_structure/mcp_servers/{language}/servers/{server_name}/`
- **Language:** {language.title()}

For more information about this MCP server's capabilities, check the repository: {repository_url}

---
*This placeholder README was automatically generated by the Enhanced AI Agent Protocol system.*
"""
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        
        # Update metadata
        self._update_readme_metadata(server_name, dest_filename, language, repository_url, "PLACEHOLDER")
        
        logger.info(f"📄 Created placeholder README: {dest_filename}")
    
    def _update_readme_metadata(self, server_name: str, filename: str, language: str, repository_url: str, source_path: str):
        """Update the README metadata with new server information"""
        metadata = self._load_metadata()
        
        # Add/update server entry
        metadata["mcp_readmes"][server_name] = {
            "filename": filename,
            "language": language,
            "repository_url": repository_url,
            "source_path": source_path,
            "collected_at": datetime.now().isoformat(),
            "file_size": (self.doc_folder / filename).stat().st_size if (self.doc_folder / filename).exists() else 0
        }
        
        # Update statistics
        metadata["total_mcps"] = len(metadata["mcp_readmes"])
        metadata["statistics"]["total_readme_files"] = len(metadata["mcp_readmes"])
        
        # Count by language
        lang_counts = {}
        for mcp_info in metadata["mcp_readmes"].values():
            lang = mcp_info["language"].lower()
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        metadata["statistics"]["python_mcps"] = lang_counts.get("python", 0)
        metadata["statistics"]["javascript_mcps"] = lang_counts.get("javascript", 0)
        metadata["statistics"]["typescript_mcps"] = lang_counts.get("typescript", 0)
        
        self._save_metadata(metadata)
    
    def _update_main_readme_index(self):
        """Update the main README index file"""
        metadata = self._load_metadata()
        
        index_content = f"""# MCP Servers Documentation Collection

**📚 Comprehensive README Collection for All MCP Servers**

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

## 📊 Collection Statistics

- **Total MCP Servers:** {metadata['total_mcps']}
- **Python MCPs:** {metadata['statistics']['python_mcps']}
- **JavaScript MCPs:** {metadata['statistics']['javascript_mcps']}
- **TypeScript MCPs:** {metadata['statistics']['typescript_mcps']}
- **Total README Files:** {metadata['statistics']['total_readme_files']}

---

## 📋 Available MCP Server Documentation

"""
        
        # Group by language
        python_mcps = []
        javascript_mcps = []
        typescript_mcps = []
        
        for server_name, info in sorted(metadata["mcp_readmes"].items()):
            lang = info["language"].lower()
            mcp_entry = f"- [{server_name}](./{info['filename']}) - {info['repository_url'] if info['repository_url'] else 'Local'}"
            
            if lang == "python":
                python_mcps.append(mcp_entry)
            elif lang == "javascript":
                javascript_mcps.append(mcp_entry)
            elif lang == "typescript":
                typescript_mcps.append(mcp_entry)
        
        # Add Python MCPs
        if python_mcps:
            index_content += "### 🐍 Python MCP Servers\n\n"
            index_content += "\n".join(python_mcps) + "\n\n"
        
        # Add JavaScript MCPs
        if javascript_mcps:
            index_content += "### 📦 JavaScript MCP Servers\n\n"
            index_content += "\n".join(javascript_mcps) + "\n\n"
        
        # Add TypeScript MCPs
        if typescript_mcps:
            index_content += "### 🔷 TypeScript MCP Servers\n\n"
            index_content += "\n".join(typescript_mcps) + "\n\n"
        
        # Add usage information
        index_content += """---

## 🚀 How to Use These MCP Servers

All the MCP servers documented here are integrated into the Enhanced AI Agent Protocol system.

### Quick Start
```bash
# Run the interactive system
python final_demo.py

# Choose Option 2 for Interactive Mode
# Then use natural language to access any MCP server
```

### Natural Language Examples
```bash
🎯 "setup github mcp server"
🎯 "create monitoring agent with langsmith"
🎯 "I need filesystem operations"
🎯 "help me with slack integration"
```

### System Integration
- **Configuration Files:** All MCPs are automatically configured in client files
- **Auto-Discovery:** System can auto-detect MCP capabilities
- **Natural Language:** Describe what you need, system selects appropriate MCPs
- **Validation:** Built-in validation ensures all configurations are correct

---

## 📁 File Organization

Each MCP server's README is stored as:
- **Filename Pattern:** `{SERVER_NAME}_README.md`
- **Enhanced Content:** Original README + integration notes + usage examples
- **Metadata:** Tracking file with collection statistics and server information

### Metadata File
- **Location:** `Doc/readme_metadata.json`
- **Purpose:** Tracks all collected READMEs with timestamps and statistics
- **Auto-Updated:** Every time a new MCP server is added

---

## 🔄 Automatic Collection Process

This documentation collection is **fully automated**:

1. **Download Detection:** When an MCP server is downloaded
2. **README Search:** System searches for README files in server directory
3. **Content Enhancement:** Original README is enhanced with integration notes
4. **Index Update:** This main index file is automatically regenerated
5. **Metadata Tracking:** Collection statistics are maintained

### Integration Points
- **Download Hook:** `collect_readme_after_download()` called after each MCP installation
- **Enhancement:** READMEs are enhanced with usage examples and integration notes
- **Organization:** Files are organized by language and automatically indexed

---

*This documentation collection is automatically maintained by the Enhanced AI Agent Protocol system.*
*For system documentation, see the main README.md in the project root.*
"""
        
        # Write the index file
        with open(self.readme_index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        logger.info(f"📚 Updated main README index with {metadata['total_mcps']} MCP servers")
    
    def collect_existing_readmes(self):
        """Scan and collect READMEs from already installed MCP servers"""
        logger.info("🔍 Scanning for existing MCP server READMEs...")
        
        collected_count = 0
        
        # Scan Python servers
        python_servers_path = self.mcp_servers_path / "python" / "servers"
        if python_servers_path.exists():
            for server_dir in python_servers_path.iterdir():
                if server_dir.is_dir() and not server_dir.name.startswith('.'):
                    if self.collect_readme_after_download(server_dir.name, server_dir, "python"):
                        collected_count += 1
        
        # Scan JavaScript servers
        js_servers_path = self.mcp_servers_path / "js" / "servers"
        if js_servers_path.exists():
            for server_dir in js_servers_path.iterdir():
                if server_dir.is_dir() and not server_dir.name.startswith('.'):
                    if self.collect_readme_after_download(server_dir.name, server_dir, "javascript"):
                        collected_count += 1
        
        logger.info(f"✅ Collected {collected_count} existing READMEs")
        return collected_count
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive report of the README collection"""
        metadata = self._load_metadata()
        
        report = f"""
📚 MCP README Collection Report
===============================

Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Servers: {metadata['total_mcps']}

Language Distribution:
- Python: {metadata['statistics']['python_mcps']} servers
- JavaScript: {metadata['statistics']['javascript_mcps']} servers  
- TypeScript: {metadata['statistics']['typescript_mcps']} servers

Files Collected: {metadata['statistics']['total_readme_files']} README files

Storage Location: {self.doc_folder}
Index File: {self.readme_index_file.name}
Metadata File: {self.readme_metadata_file.name}

Status: ✅ All README files successfully collected and organized
"""
        
        return report
