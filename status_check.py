#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Status Check for Enhanced AI Agent Protocol
Verifies all components are working and provides system overview
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def safe_print(text):
    """Print text safely handling Unicode encoding issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII representation
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

def check_system_status():
    """Quick system status check"""
    safe_print("🔍 Enhanced AI Agent Protocol - System Status Check")
    print("=" * 55)
    
    # Check core imports
    try:
        from ai_agent_protocol.core import AIAgentProtocol
        safe_print("✅ Core AI Agent Protocol: READY")
    except Exception as e:
        safe_print(f"❌ Core Protocol: ERROR - {e}")
        return False
    
    try:
        from enhanced_ai_protocol_working import EnhancedMCPCLI
        safe_print("✅ Enhanced Natural Language Processing: READY")
    except Exception as e:
        safe_print(f"❌ Enhanced Protocol: ERROR - {e}")
        return False
    
    try:
        from prompt_based_mcp_addition import EnhancedMCPCLIWithPromptAddition
        safe_print("✅ Prompt-Based MCP Addition: READY")
    except Exception as e:
        safe_print(f"❌ Prompt Addition: ERROR - {e}")
        return False
    
    # Check file structure
    required_files = [
        "final_demo.py",
        "test_all_modes.py", 
        "README.md",
        "src/ai_agent_protocol/core.py",
        "src/enhanced_ai_protocol_working.py",
        "src/prompt_based_mcp_addition.py"
    ]
    
    print("\n📁 File Structure Check:")
    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            safe_print(f"✅ {file_path}")
        else:
            safe_print(f"❌ {file_path} - MISSING")
            all_files_exist = False
    
    if not all_files_exist:
        return False
    
    safe_print("\n🎯 System Overview:")
    safe_print("📦 Available Modes:")
    print("  1. Comprehensive Demo (final_demo.py → Option 1)")
    print("  2. Interactive Mode (final_demo.py → Option 2)")
    print("  3. Prompt-Based MCP Addition Demo (final_demo.py → Option 3)")
    print("  4. Direct Component Access")
    print("  5. Comprehensive Testing (test_all_modes.py)")
    
    safe_print("\n🧠 AI Capabilities:")
    print("  • Natural language command understanding")
    print("  • Automatic MCP server discovery")
    print("  • GitHub search and installation") 
    print("  • AI agent creation")
    print("  • Pattern matching + optional Groq LLM")
    
    safe_print(f"\n🚀 Quick Start:")
    print(f"  python final_demo.py")
    print(f"  python test_all_modes.py")
    
    safe_print("\n✅ SYSTEM STATUS: ALL COMPONENTS READY")
    safe_print("🎉 Ready to use Enhanced AI Agent Protocol!")
    
    return True

if __name__ == "__main__":
    check_system_status()
