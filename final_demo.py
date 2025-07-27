"""
Comprehensive demo showcasing Enhanced AI Agent Protocol
Natural Language MCP Server    print("✨ **Key Capabilities Demonstrated:**")
    print("  ✅ Natural language command understanding")
    print("  ✅ Automatic MCP server discovery and status")
    print("  ✅ Intelligent agent type selection")
    print("  ✅ Conversational interaction style")
    print("  ✅ Error handling and helpful suggestions")
    print("  🆕 Prompt-based MCP server addition")
    print("  🆕 Automatic GitHub search for MCPs")
    print()
    print("🚀 **Next Steps:**")
    print("  • Try interactive mode: python src/enhanced_ai_protocol_working.py")
    print("  • Add Groq API key for LLM-powered processing")
    print("  • Extend with custom MCP server definitions")
    print()
    print("💡 **Sample Commands to Try:**")
    print("  • 'setup github mcp server'")
    print("  • 'create monitoring agent with langsmith'")
    print("  • 'add leetcode mcp server for coding practice'")
    print("  • 'I need a docker mcp to manage containers'")
    print("  • 'what mcp servers can I install?'")
    print("  • 'I need help with filesystem integration'")mpt-Based MCP Addition
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from enhanced_ai_protocol_working import EnhancedMCPCLI
from prompt_based_mcp_addition import EnhancedMCPCLIWithPromptAddition

async def comprehensive_demo():
    """Comprehensive demo of natural language MCP management"""
    
    print("🚀 Enhanced AI Agent Protocol - Comprehensive Demo")
    print("=" * 60)
    print("🧠 Intelligent Natural Language Processing for MCP Management")
    print("🆕 NEW: Add MCP servers via natural language prompts!")
    print("🔧 Mode: Pattern Matching (works without API keys)")
    print("✨ Demonstrates automatic MCP server setup and AI agent creation")
    print()
    
    cli = EnhancedMCPCLIWithPromptAddition()
    
    # Realistic user scenarios
    scenarios = [
        {
            "title": "📋 Check Current Installation Status",
            "commands": [
                "what mcp servers are currently installed?",
                "show me what's available"
            ]
        },
        {
            "title": "🔍 Explore Available MCP Servers", 
            "commands": [
                "check if github is available",
                "check if langsmith is available"
            ]
        },
        {
            "title": "🤖 Create AI Agents with Natural Language",
            "commands": [
                "create a monitoring agent with langsmith",
                "make a devops agent using github",
                "build a file manager agent with filesystem"
            ]
        },
        {
            "title": "💬 Conversational Commands",
            "commands": [
                "I want to setup a new mcp server for blender",
                "help me create an agent for monitoring my projects",
                "show me everything that's installed"
            ]
        },
        {
            "title": "🆕 Add New MCP Servers via Prompts",
            "commands": [
                "add leetcode mcp server for coding practice",
                "I need a docker mcp to manage containers",
                "create an email mcp server for gmail integration"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print("=" * 50)
        
        for command in scenario['commands']:
            print(f"\n🎯 **User says:** '{command}'")
            print("-" * 40)
            
            try:
                response = await cli.process_command(command)
                print("🤖 **AI Response:**")
                print(response)
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 40)
            await asyncio.sleep(0.5)
    
    print("\n🎉 **Demo Complete!**")
    print("\n✨ **Key Capabilities Demonstrated:**")
    print("  ✅ Natural language command understanding")
    print("  ✅ Automatic MCP server discovery and status")
    print("  ✅ Intelligent agent type selection")
    print("  ✅ Conversational interaction style")
    print("  ✅ Error handling and helpful suggestions")
    print()
    print("🚀 **Next Steps:**")
    print("  • Try interactive mode: python src/enhanced_ai_protocol_working.py")
    print("  • Add Groq API key for LLM-powered processing")
    print("  • Extend with custom MCP server definitions")
    print()
    print("💡 **Sample Commands to Try:**")
    print("  • 'setup github mcp server'")
    print("  • 'create monitoring agent with langsmith'")
    print("  • 'what mcp servers can I install?'")
    print("  • 'I need help with filesystem integration'")

async def interactive_session():
    """Start an interactive session"""
    
    print("🤖 Enhanced AI Agent Protocol - Interactive Mode")
    print("=" * 50)
    print("💬 Natural Language MCP Management + Dynamic Addition")
    print()
    print("**Try these example commands:**")
    print("  • 'what mcp servers are installed?'")
    print("  • 'setup github mcp server'")
    print("  • 'create monitoring agent with langsmith'")
    print("  • 'check if filesystem is available'")
    print("  🆕 'add leetcode mcp server for coding practice'")
    print("  🆕 'I need a docker mcp to manage containers'")
    print()
    print("Type 'quit' to exit, 'demo' for full demo")
    print("=" * 50)
    
    cli = EnhancedMCPCLIWithPromptAddition()
    
    while True:
        try:
            user_input = input("\n🎯 Your command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for using Enhanced AI Agent Protocol!")
                break
            elif user_input.lower() == 'demo':
                print("\n🚀 Running comprehensive demo...")
                await comprehensive_demo()
                continue
            elif not user_input:
                continue
            
            print(f"\n🤖 Processing: {user_input}")
            print("-" * 40)
            
            response = await cli.process_command(user_input)
            
            print("**AI Response:**")
            print(response)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using Enhanced AI Agent Protocol!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main function with mode selection"""
    
    print("🚀 Enhanced AI Agent Protocol")
    print("=" * 40)
    print("Natural Language MCP Server Management")
    print("🆕 NEW: Add MCPs via prompts!")
    print()
    print("Select mode:")
    print("1. 📋 Comprehensive Demo")
    print("2. 💬 Interactive Mode")  
    print("3. 🧪 Prompt-Based MCP Addition Demo")
    print("4. 🚪 Exit")
    print()
    
    choice = input("Your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🎬 Starting comprehensive demo...")
        asyncio.run(comprehensive_demo())
    elif choice == "2":
        print("\n💬 Starting interactive mode...")
        asyncio.run(interactive_session())
    elif choice == "3":
        print("\n🧪 Running prompt-based MCP addition demo...")
        from prompt_based_mcp_addition import demo_prompt_based_mcp_addition
        asyncio.run(demo_prompt_based_mcp_addition())
    else:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
