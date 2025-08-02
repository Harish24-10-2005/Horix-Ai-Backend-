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
    """Interactive session with AI-powered natural language understanding"""
    from enhanced_ai_protocol_working import EnhancedMCPCLI
    
    # Get Groq API key for AI capabilities
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    print("🤖 Enhanced AI Agent Protocol - Interactive Mode")
    print("=" * 50)
    
    if groq_api_key and groq_api_key != "dummy_key":
        print("🧠 AI Mode: Groq LLM (Full AI capabilities)")
        print("✨ Advanced natural language understanding enabled")
    else:
        print("� AI Mode: Enhanced Pattern Matching")
        print("💡 Add GROQ_API_KEY environment variable for full AI capabilities")
    
    print("\n�💬 Natural Language MCP Management + Dynamic Addition")
    print()
    print("🆕 **AI-Powered Features:**")
    print("  🎯 Understands ANY MCP server request (not just predefined)")
    print("  🔍 Searches GitHub automatically for matching servers")
    print("  🤖 AI selects the best match for your needs")
    print("  📝 Natural language understanding of user intent")
    print()
    print("**Try these example commands:**")
    print("  • 'I need to manage my Docker containers'")
    print("  • 'Help me set up email automation for my business'")
    print("  • 'I want to monitor my application performance'")
    print("  • 'Set up payment processing for my app'")
    print("  • 'Search for machine learning MCP servers'")
    print("  • 'what mcp servers are installed?'")
    print("  🆕 'add leetcode mcp server for coding practice'")
    print("  🆕 'I need a database mcp for PostgreSQL'")
    print()
    print("Type 'quit' to exit, 'demo' for full demo")
    print("=" * 50)
    
    # Initialize the AI-enhanced CLI
    cli = EnhancedMCPCLI(groq_api_key)
    
    while True:
        try:
            user_input = input("\n🎯 Your request: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for using Enhanced AI Agent Protocol!")
                break
            elif user_input.lower() == 'demo':
                print("\n🚀 Running comprehensive demo...")
                await comprehensive_demo()
                continue
            elif not user_input:
                continue
            
            print(f"\n🤖 AI Processing: {user_input}")
            print("-" * 50)
            
            response = await cli.process_command(user_input)
            
            print("🎯 **AI Response:**")
            print(response)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using Enhanced AI Agent Protocol!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

async def pure_ai_mode():
    """Pure AI mode with real Groq API - Full AI capabilities"""
    from enhanced_ai_protocol_working import EnhancedMCPCLI
    
    print("🤖 Pure AI Mode - Enhanced AI Agent Protocol")
    print("=" * 60)
    
    # Initialize with real API key from environment
    cli = EnhancedMCPCLI()  # This will auto-detect your Groq API key
    
    if cli.processor.mode == "groq":
        print("🧠 AI Mode: Groq LLM (Real AI Intelligence)")
        print("✨ Full AI capabilities with your Groq API key!")
        print("🚀 Advanced natural language understanding powered by Groq")
    else:
        print("🧠 AI Mode: Enhanced Simulation")
        print("⚠️ Groq API not available, using advanced pattern matching")
    
    print()
    print("🚀 **Real AI Capabilities:**")
    print("  🎯 True natural language understanding via Groq LLM")
    print("  🔍 Intelligent technology detection and intent extraction")
    print("  🤖 AI-powered MCP server discovery and selection")
    print("  📝 Context-aware responses and suggestions")
    print("  ⚡ Real-time AI analysis of your requests")
    print()
    print("💡 **What makes this 'Real AI':**")
    print("  • Groq LLM processes your natural language")
    print("  • AI understands context and intent beyond keywords")
    print("  • Intelligent MCP server matching and ranking")
    print("  • Dynamic response generation based on your needs")
    print("  • Advanced error handling and suggestions")
    print()
    print("🌟 **Try these natural language requests:**")
    print("  • 'I need to manage my Docker containers efficiently'")
    print("  • 'Help me set up monitoring for my web applications'")
    print("  • 'I want to automate email notifications for my users'")
    print("  • 'Set up integration with my PostgreSQL database'")
    print("  • 'I need payment processing for my e-commerce site'")
    print("  • 'Help me with Kubernetes cluster management'")
    print("  • 'I want to track issues and bugs in my project'")
    print("  • 'Set up social media integration for my app'")
    print()
    print("Type 'quit' to exit, 'help' for more examples")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n🎯 Describe what you need: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🎉 Thanks for using Real AI Mode!")
                print("💡 Your Groq AI integration is working perfectly!")
                break
            elif user_input.lower() == 'help':
                print("""
🆕 **More Real AI Examples to Try:**

🐳 **Container Management:**
  • 'I need better Docker container monitoring'
  • 'Help me orchestrate my microservices with Kubernetes'

📧 **Communication & Automation:**
  • 'Set up automated email campaigns for my business'
  • 'I want Slack integration for team notifications'

💾 **Data & Storage:**
  • 'Help me manage my MongoDB database connections'
  • 'I need backup automation for my critical files'

🔐 **Security & Authentication:**
  • 'Set up OAuth authentication for my application'
  • 'I need security monitoring for my infrastructure'

📊 **Analytics & Monitoring:**
  • 'Help me create dashboards for my application metrics'
  • 'I want to track user behavior in my web app'

💳 **Business Operations:**
  • 'Set up Stripe payment processing for subscriptions'
  • 'I need calendar integration for appointment booking'

🤖 **The AI will understand your intent and find the right solution!**""")
                continue
            elif not user_input:
                continue
            
            print(f"\n🧠 Real AI Analyzing: {user_input}")
            print("-" * 50)
            
            response = await cli.process_command(user_input)
            
            print("🤖 **AI Response:**")
            print(response)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n🎉 Thanks for using Real AI Mode!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

async def demo_ai_mode():
    """Demo AI mode with simulated intelligent responses - No API key required"""
    from enhanced_ai_protocol_working import EnhancedMCPCLI
    
    print("🧪 Demo AI Mode - Enhanced AI Agent Protocol")
    print("=" * 60)
    print("🧠 AI Mode: Advanced Simulated Intelligence")
    print("✨ Full AI-like behavior without requiring any API keys!")
    print()
    print("🚀 **Demo AI Capabilities:**")
    print("  🎯 Advanced intent recognition from natural language")
    print("  🔍 Intelligent technology detection in your requests")
    print("  🤖 AI-like understanding of ANY service or technology")
    print("  📝 Context-aware responses and suggestions")
    print("  ⚡ Works completely offline - no API keys needed!")
    print()
    print("💡 **What makes this 'Demo AI':**")
    print("  • Advanced pattern recognition algorithms")
    print("  • Intent extraction from conversational language")
    print("  • Technology inference from user descriptions")
    print("  • Intelligent response generation")
    print("  • Context-aware command understanding")
    print()
    print("🌟 **Try these natural language requests:**")
    print("  • 'I need to manage my Docker containers efficiently'")
    print("  • 'Help me set up monitoring for my web applications'")
    print("  • 'I want to automate email notifications for my users'")
    print("  • 'Set up integration with my PostgreSQL database'")
    print("  • 'I need payment processing for my e-commerce site'")
    print("  • 'Help me with Kubernetes cluster management'")
    print("  • 'I want to track issues and bugs in my project'")
    print("  • 'Set up social media integration for my app'")
    print()
    print("Type 'quit' to exit, 'help' for more examples")
    print("=" * 60)
    
    # Initialize with demo_mode for simulated AI
    cli = EnhancedMCPCLI("demo_mode")
    
    while True:
        try:
            user_input = input("\n🎯 Describe what you need: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🎉 Thanks for trying Demo AI Mode!")
                print("💡 For real AI, try option 4 with your Groq API key!")
                break
            elif user_input.lower() == 'help':
                print("""
🆕 **More Demo AI Examples to Try:**

🐳 **Container Management:**
  • 'I need better Docker container monitoring'
  • 'Help me orchestrate my microservices with Kubernetes'

📧 **Communication & Automation:**
  • 'Set up automated email campaigns for my business'
  • 'I want Slack integration for team notifications'

💾 **Data & Storage:**
  • 'Help me manage my MongoDB database connections'
  • 'I need backup automation for my critical files'

🔐 **Security & Authentication:**
  • 'Set up OAuth authentication for my application'
  • 'I need security monitoring for my infrastructure'

📊 **Analytics & Monitoring:**
  • 'Help me create dashboards for my application metrics'
  • 'I want to track user behavior in my web app'

💳 **Business Operations:**
  • 'Set up Stripe payment processing for subscriptions'
  • 'I need calendar integration for appointment booking'

🔍 **Just describe what you want to accomplish!**""")
                continue
            elif not user_input:
                continue
            
            print(f"\n🧠 Demo AI Analyzing: {user_input}")
            print("-" * 50)
            
            response = await cli.process_command(user_input)
            
            print("🤖 **Demo AI Response:**")
            print(response)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n🎉 Thanks for trying Demo AI Mode!")
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
    print("4. 🤖 Real AI Mode (Uses Your Groq API)")
    print("5. 🧪 Demo AI Mode (No API Required)")
    print("6. 🚪 Exit")
    print()
    
    choice = input("Your choice (1-6): ").strip()
    
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
    elif choice == "4":
        print("\n🤖 Starting Real AI Mode...")
        asyncio.run(pure_ai_mode())
    elif choice == "5":
        print("\n🧪 Starting Demo AI Mode...")
        asyncio.run(demo_ai_mode())
    else:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
