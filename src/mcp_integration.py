"""
Integration script for automatic MCP configuration after download
This script integrates the AI configuration agent with the existing MCP download system
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.mcp_auto_config_agent import MCPAutoConfigAgent

logger = logging.getLogger(__name__)

class MCPDownloadIntegration:
    """Integration layer for automatic MCP configuration after download"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.config_agent = MCPAutoConfigAgent(str(self.base_path))
        
    async def on_mcp_downloaded(self, mcp_name: str, download_path: str = None, language: str = None):
        """
        Hook function to be called after MCP server is downloaded
        This should be integrated into the existing download workflow
        """
        try:
            logger.info(f"🔗 MCP download completed: {mcp_name}")
            logger.info(f"🤖 Starting automatic configuration...")
            
            # Auto-configure the newly downloaded MCP
            success = await self.config_agent.auto_configure_new_mcp(mcp_name)
            
            if success:
                logger.info(f"✅ Auto-configuration completed successfully for {mcp_name}")
                return True
            else:
                logger.error(f"❌ Auto-configuration failed for {mcp_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in MCP download integration: {e}")
            return False
    
    async def configure_existing_mcp(self, mcp_name: str):
        """Configure an existing MCP server"""
        return await self.config_agent.auto_configure_new_mcp(mcp_name)
    
    async def validate_all_configurations(self):
        """Validate all MCP configurations"""
        return await self.config_agent.validate_configuration()

# Integration function for existing codebase
async def integrate_with_existing_system():
    """
    Integration points for the existing MCP download system
    This function shows how to integrate the auto-config agent
    """
    
    # Example integration with ai_agent_protocol/core.py
    print("🔌 Setting up MCP Auto-Configuration Integration...")
    
    integration = MCPDownloadIntegration()
    
    # Example: Configure all existing MCPs
    print("🔧 Configuring all existing MCP servers...")
    results = await integration.config_agent.configure_all_mcps()
    
    print(f"\n📊 Configuration Results:")
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    return integration

# Patch for existing core.py - add this to MCPServerManager class
CORE_PY_INTEGRATION_CODE = '''
# Add this import at the top of core.py
from ..mcp_auto_config_agent import MCPAutoConfigAgent

# Add this method to MCPServerManager class
async def _auto_configure_downloaded_mcp(self, server_info: MCPServerInfo):
    """Auto-configure MCP server after download using AI agent"""
    try:
        from ..mcp_integration import MCPDownloadIntegration
        
        integration = MCPDownloadIntegration(str(self.base_path))
        success = await integration.on_mcp_downloaded(
            mcp_name=server_info.name,
            language=server_info.language
        )
        
        if success:
            logger.info(f"✅ Auto-configuration completed for {server_info.name}")
        else:
            logger.warning(f"⚠️ Auto-configuration failed for {server_info.name}")
            
        return success
        
    except Exception as e:
        logger.error(f"Auto-configuration error for {server_info.name}: {e}")
        return False

# Add this call in download_and_install_server method after successful download:
# await self._auto_configure_downloaded_mcp(server_info)
'''

async def main():
    """Main function for testing integration"""
    print("🚀 MCP Auto-Configuration Integration Test")
    print("=" * 50)
    
    integration = await integrate_with_existing_system()
    
    print("\n🔍 Validating all configurations...")
    validation = await integration.validate_all_configurations()
    
    print(f"\n📊 Validation Summary:")
    print(f"✅ Valid configs: {len(validation.get('valid_configs', []))}")
    print(f"❌ Invalid configs: {len(validation.get('invalid_configs', []))}")
    
    if validation.get('errors'):
        print(f"⚠️ Errors: {len(validation['errors'])}")
        for error in validation['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    asyncio.run(main())
