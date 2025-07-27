"""
Example usage of the AI Agent Protocol
This script demonstrates how to use the protocol to create various types of AI agents
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from ai_agent_protocol.core import AIAgentProtocol, AgentRequest
from ai_agent_protocol.templates import QuickAgentFactory

async def example_langsmith_monitoring_agent():
    """Example: Create a LangSmith monitoring agent"""
    print("🚀 Creating LangSmith Monitoring Agent...")
    print("=" * 50)
    
    # Initialize the protocol
    base_path = Path(__file__).parent.parent.parent
    protocol = AIAgentProtocol(str(base_path))
    
    # Create a LangSmith monitoring agent request
    request = AgentRequest(
        agent_type="monitoring_agent",
        required_mcps=["langsmith"],
        description="AI agent for monitoring other AI agents using LangSmith MCP server",
        metadata={
            "monitoring_interval": 60,
            "alert_thresholds": {
                "error_rate": 0.1,
                "response_time": 5000
            },
            "metrics_to_track": [
                "response_time",
                "error_rate", 
                "token_usage",
                "request_count"
            ]
        }
    )
    
    # Create the agent
    try:
        agent_config = await protocol.create_agent(request)
        
        print(f"✅ Agent created successfully!")
        print(f"Agent ID: {agent_config['id']}")
        print(f"Type: {agent_config['type']}")
        print(f"Status: {agent_config['status']}")
        print(f"Description: {agent_config['description']}")
        print(f"MCP Servers integrated: {len(agent_config['mcp_servers'])}")
        
        for mcp in agent_config['mcp_servers']:
            print(f"  - {mcp['name']}: {mcp['description']}")
        
        return agent_config
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

async def example_github_devops_agent():
    """Example: Create a GitHub DevOps agent"""
    print("\n🔧 Creating GitHub DevOps Agent...")
    print("=" * 50)
    
    base_path = Path(__file__).parent.parent.parent
    protocol = AIAgentProtocol(str(base_path))
    
    request = AgentRequest(
        agent_type="devops_agent",
        required_mcps=["github"],
        description="AI agent for GitHub repository operations and DevOps automation",
        metadata={
            "repositories": ["my-org/my-repo"],
            "capabilities": [
                "code_review",
                "pr_management", 
                "issue_tracking",
                "deployment_automation"
            ],
            "automation_rules": {
                "auto_assign_reviewers": True,
                "auto_label_issues": True
            }
        }
    )
    
    try:
        agent_config = await protocol.create_agent(request)
        
        print(f"✅ Agent created successfully!")
        print(f"Agent ID: {agent_config['id']}")
        print(f"Type: {agent_config['type']}")
        print(f"Status: {agent_config['status']}")
        print(f"MCP Servers integrated: {len(agent_config['mcp_servers'])}")
        
        return agent_config
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

async def example_using_quick_factory():
    """Example: Using the QuickAgentFactory for easier agent creation"""
    print("\n⚡ Using Quick Agent Factory...")
    print("=" * 50)
    
    base_path = Path(__file__).parent.parent.parent
    protocol = AIAgentProtocol(str(base_path))
    factory = QuickAgentFactory(protocol)
    
    # Create a LangSmith monitoring agent with custom config
    custom_config = {
        "monitoring_interval": 30,  # Override default
        "additional_metrics": ["memory_usage", "cpu_usage"]
    }
    
    try:
        agent_config = await factory.create_langsmith_monitor(custom_config)
        
        print(f"✅ Quick agent created successfully!")
        print(f"Agent ID: {agent_config['id']}")
        print(f"Type: {agent_config['type']}")
        print(f"Status: {agent_config['status']}")
        
        return agent_config
        
    except Exception as e:
        print(f"❌ Error creating quick agent: {e}")
        return None

async def example_list_available_mcps():
    """Example: List available MCP servers"""
    print("\n📋 Listing Available MCP Servers...")
    print("=" * 50)
    
    base_path = Path(__file__).parent.parent.parent
    protocol = AIAgentProtocol(str(base_path))
    
    try:
        # List all available MCPs
        servers = await protocol.list_available_mcp_servers("")
        
        print(f"Found {len(servers)} MCP servers:")
        for i, server in enumerate(servers, 1):
            print(f"{i}. {server.name}")
            print(f"   Description: {server.description}")
            print(f"   Language: {server.language}")
            print(f"   Repository: {server.repository_url}")
            print()
            
        # Search for specific MCP servers
        print("🔍 Searching for 'langsmith' MCP servers...")
        langsmith_servers = await protocol.list_available_mcp_servers("langsmith")
        
        print(f"Found {len(langsmith_servers)} LangSmith-related servers:")
        for server in langsmith_servers:
            print(f"  - {server.name}: {server.description}")
            
    except Exception as e:
        print(f"❌ Error listing MCP servers: {e}")

async def example_multi_mcp_agent():
    """Example: Create an agent that uses multiple MCP servers"""
    print("\n🔗 Creating Multi-MCP Agent...")
    print("=" * 50)
    
    base_path = Path(__file__).parent.parent.parent
    protocol = AIAgentProtocol(str(base_path))
    
    request = AgentRequest(
        agent_type="comprehensive_agent",
        required_mcps=["langsmith", "github", "filesystem"],
        description="Comprehensive AI agent with multiple MCP integrations for full-stack monitoring and automation",
        metadata={
            "capabilities": [
                "ai_monitoring",
                "code_management", 
                "file_operations",
                "automated_reporting"
            ],
            "integration_strategy": "unified_dashboard",
            "data_flow": {
                "langsmith": "metrics_collection",
                "github": "code_analysis",
                "filesystem": "artifact_storage"
            }
        }
    )
    
    try:
        agent_config = await protocol.create_agent(request)
        
        print(f"✅ Multi-MCP agent created successfully!")
        print(f"Agent ID: {agent_config['id']}")
        print(f"Type: {agent_config['type']}")
        print(f"Status: {agent_config['status']}")
        print(f"MCP Servers integrated: {len(agent_config['mcp_servers'])}")
        
        for mcp in agent_config['mcp_servers']:
            print(f"  - {mcp['name']}: {mcp['description']}")
        
        return agent_config
        
    except Exception as e:
        print(f"❌ Error creating multi-MCP agent: {e}")
        return None

async def main():
    """Run all examples"""
    print("🤖 AI Agent Protocol Examples")
    print("=" * 60)
    
    # Example 1: List available MCP servers
    await example_list_available_mcps()
    
    # Example 2: Create LangSmith monitoring agent
    langsmith_agent = await example_langsmith_monitoring_agent()
    
    # Example 3: Create GitHub DevOps agent
    github_agent = await example_github_devops_agent()
    
    # Example 4: Use quick factory
    quick_agent = await example_using_quick_factory()
    
    # Example 5: Create multi-MCP agent
    multi_agent = await example_multi_mcp_agent()
    
    print("\n📊 Summary")
    print("=" * 50)
    print(f"Created agents:")
    agents = [langsmith_agent, github_agent, quick_agent, multi_agent]
    successful_agents = [agent for agent in agents if agent is not None]
    
    for agent in successful_agents:
        print(f"  - {agent['id']}: {agent['type']} ({agent['status']})")
    
    print(f"\nTotal agents created: {len(successful_agents)}")

if __name__ == "__main__":
    asyncio.run(main())
