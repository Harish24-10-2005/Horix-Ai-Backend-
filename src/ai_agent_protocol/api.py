"""
FastAPI Web Interface for AI Agent Protocol
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
from pathlib import Path
import sys

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from ai_agent_protocol.core import AIAgentProtocol, AgentRequest, MCPServerInfo
from ai_agent_protocol.templates import QuickAgentFactory

app = FastAPI(
    title="AI Agent Protocol API",
    description="API for automatic MCP integration and AI agent creation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global protocol instance
protocol: Optional[AIAgentProtocol] = None
factory: Optional[QuickAgentFactory] = None

# Pydantic models for API
class CreateAgentRequest(BaseModel):
    agent_type: str
    required_mcps: List[str]
    description: str
    metadata: Dict[str, Any] = {}

class AgentResponse(BaseModel):
    id: str
    type: str
    description: str
    status: str
    mcp_servers: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class MCPServerResponse(BaseModel):
    name: str
    repository_url: str
    download_url: str
    description: str
    language: str
    dependencies: List[str]

class QuickAgentRequest(BaseModel):
    agent_type: str
    custom_config: Dict[str, Any] = {}
    additional_params: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the protocol on startup"""
    global protocol, factory
    base_path = Path(__file__).parent.parent.parent
    protocol = AIAgentProtocol(str(base_path))
    factory = QuickAgentFactory(protocol)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Agent Protocol API",
        "version": "1.0.0",
        "endpoints": {
            "create_agent": "/agents",
            "list_agents": "/agents",
            "get_agent": "/agents/{agent_id}",
            "list_mcps": "/mcps",
            "search_mcps": "/mcps/search/{search_term}",
            "quick_agent": "/agents/quick/{agent_type}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "protocol_initialized": protocol is not None}

@app.post("/agents", response_model=AgentResponse)
async def create_agent(request: CreateAgentRequest, background_tasks: BackgroundTasks):
    """Create a new AI agent with MCP integration"""
    if not protocol:
        raise HTTPException(status_code=500, detail="Protocol not initialized")
    
    try:
        agent_request = AgentRequest(
            agent_type=request.agent_type,
            required_mcps=request.required_mcps,
            description=request.description,
            metadata=request.metadata
        )
        
        # Create agent in background
        agent_config = await protocol.create_agent(agent_request)
        
        return AgentResponse(
            id=agent_config["id"],
            type=agent_config["type"],
            description=agent_config["description"],
            status=agent_config["status"],
            mcp_servers=agent_config["mcp_servers"],
            metadata=agent_config["metadata"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@app.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all created agents"""
    if not protocol:
        raise HTTPException(status_code=500, detail="Protocol not initialized")
    
    try:
        agents = protocol.list_agents()
        return [
            AgentResponse(
                id=agent["id"],
                type=agent["type"],
                description=agent["description"],
                status=agent["status"],
                mcp_servers=agent["mcp_servers"],
                metadata=agent["metadata"]
            )
            for agent in agents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    if not protocol:
        raise HTTPException(status_code=500, detail="Protocol not initialized")
    
    try:
        agent = protocol.get_agent_status(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentResponse(
            id=agent["id"],
            type=agent["type"],
            description=agent["description"],
            status=agent["status"],
            mcp_servers=agent["mcp_servers"],
            metadata=agent["metadata"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent: {str(e)}")

@app.get("/mcps", response_model=List[MCPServerResponse])
async def list_mcp_servers():
    """List all available MCP servers"""
    if not protocol:
        raise HTTPException(status_code=500, detail="Protocol not initialized")
    
    try:
        servers = await protocol.list_available_mcp_servers("")
        return [
            MCPServerResponse(
                name=server.name,
                repository_url=server.repository_url,
                download_url=server.download_url,
                description=server.description,
                language=server.language,
                dependencies=server.dependencies
            )
            for server in servers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing MCP servers: {str(e)}")

@app.get("/mcps/search/{search_term}", response_model=List[MCPServerResponse])
async def search_mcp_servers(search_term: str):
    """Search for MCP servers"""
    if not protocol:
        raise HTTPException(status_code=500, detail="Protocol not initialized")
    
    try:
        servers = await protocol.list_available_mcp_servers(search_term)
        return [
            MCPServerResponse(
                name=server.name,
                repository_url=server.repository_url,
                download_url=server.download_url,
                description=server.description,
                language=server.language,
                dependencies=server.dependencies
            )
            for server in servers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching MCP servers: {str(e)}")

@app.post("/agents/quick/{agent_type}", response_model=AgentResponse)
async def create_quick_agent(agent_type: str, request: QuickAgentRequest):
    """Create a quick agent using predefined templates"""
    if not factory:
        raise HTTPException(status_code=500, detail="Factory not initialized")
    
    try:
        if agent_type == "langsmith_monitor":
            agent_config = await factory.create_langsmith_monitor(request.custom_config)
        elif agent_type == "github_devops":
            repositories = request.additional_params.get("repositories", [])
            agent_config = await factory.create_github_devops(repositories, request.custom_config)
        elif agent_type == "filesystem_manager":
            directories = request.additional_params.get("directories", [])
            agent_config = await factory.create_filesystem_manager(directories, request.custom_config)
        elif agent_type == "data_analyst":
            data_sources = request.additional_params.get("data_sources", [])
            agent_config = await factory.create_data_analyst(data_sources, request.custom_config)
        elif agent_type == "security_auditor":
            scan_targets = request.additional_params.get("scan_targets", [])
            agent_config = await factory.create_security_auditor(scan_targets, request.custom_config)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown quick agent type: {agent_type}")
        
        return AgentResponse(
            id=agent_config["id"],
            type=agent_config["type"],
            description=agent_config["description"],
            status=agent_config["status"],
            mcp_servers=agent_config["mcp_servers"],
            metadata=agent_config["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating quick agent: {str(e)}")

@app.get("/agents/templates/available")
async def get_available_templates():
    """Get list of available agent templates"""
    return {
        "templates": [
            {
                "type": "langsmith_monitor",
                "name": "LangSmith Monitoring Agent",
                "description": "Monitors AI agents using LangSmith MCP server",
                "required_mcps": ["langsmith"]
            },
            {
                "type": "github_devops",
                "name": "GitHub DevOps Agent",
                "description": "Automates GitHub operations and DevOps tasks",
                "required_mcps": ["github"]
            },
            {
                "type": "filesystem_manager",
                "name": "Filesystem Manager Agent",
                "description": "Manages files and directories intelligently",
                "required_mcps": ["filesystem"]
            },
            {
                "type": "data_analyst",
                "name": "Data Analysis Agent",
                "description": "Performs automated data analysis and reporting",
                "required_mcps": ["filesystem", "github"]
            },
            {
                "type": "security_auditor",
                "name": "Security Audit Agent",
                "description": "Performs security audits and compliance checks",
                "required_mcps": ["github", "filesystem"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
