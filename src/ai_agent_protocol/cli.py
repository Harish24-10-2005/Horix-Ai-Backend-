"""
Command Line Interface for AI Agent Protocol
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from ai_agent_protocol.core import AIAgentProtocol, AgentRequest

class AgentCLI:
    """Command line interface for the AI Agent Protocol"""
    
    def __init__(self):
        self.protocol = None
        self.base_path = Path(__file__).parent.parent.parent
    
    async def initialize(self):
        """Initialize the protocol"""
        self.protocol = AIAgentProtocol(str(self.base_path))
    
    async def create_agent(self, agent_type: str, mcps: list, description: str, metadata: dict = None):
        """Create a new AI agent"""
        if not self.protocol:
            await self.initialize()
        
        request = AgentRequest(
            agent_type=agent_type,
            required_mcps=mcps,
            description=description,
            metadata=metadata or {}
        )
        
        print(f"Creating AI agent of type: {agent_type}")
        print(f"Required MCPs: {', '.join(mcps)}")
        print(f"Description: {description}")
        print()
        
        try:
            agent_config = await self.protocol.create_agent(request)
            print("✅ Agent created successfully!")
            print(f"Agent ID: {agent_config['id']}")
            print(f"Status: {agent_config['status']}")
            print(f"Integrated MCP Servers: {len(agent_config['mcp_servers'])}")
            
            for i, mcp in enumerate(agent_config['mcp_servers'], 1):
                print(f"  {i}. {mcp['name']} - {mcp['description']}")
            
            return agent_config
            
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            return None
    
    async def list_mcp_servers(self, search_term: str = ""):
        """List available MCP servers"""
        if not self.protocol:
            await self.initialize()
        
        print(f"Searching for MCP servers: '{search_term}'" if search_term else "Listing all available MCP servers:")
        print()
        
        try:
            servers = await self.protocol.list_available_mcp_servers(search_term)
            
            if not servers:
                print("No MCP servers found.")
                return
            
            for i, server in enumerate(servers, 1):
                print(f"{i}. {server.name}")
                print(f"   Description: {server.description}")
                print(f"   Language: {server.language}")
                print(f"   Repository: {server.repository_url}")
                print()
                
        except Exception as e:
            print(f"❌ Error listing MCP servers: {e}")
    
    async def list_agents(self):
        """List all created agents"""
        if not self.protocol:
            await self.initialize()
        
        agents = self.protocol.list_agents()
        
        if not agents:
            print("No agents created yet.")
            return
        
        print("Created AI Agents:")
        print()
        
        for agent in agents:
            print(f"ID: {agent['id']}")
            print(f"Type: {agent['type']}")
            print(f"Description: {agent['description']}")
            print(f"Status: {agent['status']}")
            print(f"MCP Servers: {len(agent['mcp_servers'])}")
            print()
    
    async def get_agent_status(self, agent_id: str):
        """Get status of a specific agent"""
        if not self.protocol:
            await self.initialize()
        
        agent = self.protocol.get_agent_status(agent_id)
        
        if not agent:
            print(f"Agent with ID '{agent_id}' not found.")
            return
        
        print(f"Agent Status: {agent['id']}")
        print(f"Type: {agent['type']}")
        print(f"Description: {agent['description']}")
        print(f"Status: {agent['status']}")
        print(f"Metadata: {json.dumps(agent['metadata'], indent=2)}")
        print(f"MCP Servers: {len(agent['mcp_servers'])}")
        
        for i, mcp in enumerate(agent['mcp_servers'], 1):
            print(f"  {i}. {mcp['name']} - {mcp['description']}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="AI Agent Protocol CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create agent command
    create_parser = subparsers.add_parser('create', help='Create a new AI agent')
    create_parser.add_argument('agent_type', help='Type of agent to create')
    create_parser.add_argument('--mcps', nargs='+', required=True, help='Required MCP servers')
    create_parser.add_argument('--description', required=True, help='Agent description')
    create_parser.add_argument('--metadata', help='Agent metadata as JSON string')
    
    # List MCP servers command
    list_mcp_parser = subparsers.add_parser('list-mcps', help='List available MCP servers')
    list_mcp_parser.add_argument('--search', help='Search term for MCP servers')
    
    # List agents command
    list_agents_parser = subparsers.add_parser('list-agents', help='List all created agents')
    
    # Get agent status command
    status_parser = subparsers.add_parser('status', help='Get agent status')
    status_parser.add_argument('agent_id', help='Agent ID to check')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create CLI instance
    cli = AgentCLI()
    
    # Execute command
    if args.command == 'create':
        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("❌ Invalid metadata JSON format")
                return
        
        asyncio.run(cli.create_agent(
            args.agent_type,
            args.mcps,
            args.description,
            metadata
        ))
    
    elif args.command == 'list-mcps':
        asyncio.run(cli.list_mcp_servers(args.search or ""))
    
    elif args.command == 'list-agents':
        asyncio.run(cli.list_agents())
    
    elif args.command == 'status':
        asyncio.run(cli.get_agent_status(args.agent_id))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
