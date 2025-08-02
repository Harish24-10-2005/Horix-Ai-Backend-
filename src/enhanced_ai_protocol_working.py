"""
Working Enhanced AI Agent Protocol with Natural Language Processing
Simplified version that works with Groq LLM for MCP setup commands
"""

import asyncio
import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Continue without dotenv if not available

# Import existing protocol
import sys
sys.path.append(str(Path(__file__).parent))
from ai_agent_protocol.core import AIAgentProtocol, AgentRequest

# Try to import Groq
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, SystemMessage
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ Groq not available, using pattern matching")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPCommand:
    """Parsed MCP command structure"""
    action: str  # setup, check, list, create_agent, status
    mcp_name: str
    agent_type: str = ""
    confidence: float = 0.0
    raw_input: str = ""

class NaturalLanguageMCPProcessor:
    """Natural language processor for MCP commands"""
    
    def __init__(self, base_path: str, groq_api_key: str = None):
        self.base_path = Path(base_path)
        self.protocol = AIAgentProtocol(str(base_path))
        
        # Load API key from multiple sources
        if groq_api_key == "demo_mode":
            self.groq_api_key = "demo_mode"
        elif groq_api_key:
            self.groq_api_key = groq_api_key
        else:
            # Try to load from environment or .env file
            self.groq_api_key = os.getenv("GROQ_API_KEY")
            if not self.groq_api_key:
                try:
                    # Try to load from .env file
                    env_path = Path(__file__).parent.parent / ".env"
                    if env_path.exists():
                        with open(env_path, 'r') as f:
                            for line in f:
                                if line.startswith('GROQ_API_KEY'):
                                    self.groq_api_key = line.split('=')[1].strip().strip('"').strip("'")
                                    break
                except Exception as e:
                    logger.warning(f"Could not load .env file: {e}")
        
        # Force demo mode if explicitly requested
        if self.groq_api_key == "demo_mode":
            self.mode = "demo_ai"
            logger.info("🧪 Demo AI mode activated (simulated AI responses)")
        # Initialize Groq if available and valid key provided
        elif GROQ_AVAILABLE and self.groq_api_key and self.groq_api_key != "dummy_key":
            try:
                # Create the Groq client
                self.llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name="llama3-8b-8192",  # Updated to current supported model
                    temperature=0.1,
                    max_tokens=1024
                )
                self.mode = "groq"
                logger.info("✅ Groq LLM initialized (will validate on first use)")
                    
            except Exception as e:
                logger.warning(f"Groq setup failed: {e}")
                logger.info("🔧 Falling back to demo AI mode")
                self.mode = "demo_ai"
        else:
            self.mode = "demo_ai"
            logger.info("🧪 Using enhanced AI simulation mode (no valid API key)")
    
    async def process_command(self, user_input: str) -> str:
        """Process natural language command"""
        try:
            logger.info(f"🤖 Processing: {user_input}")
            
            # Parse the command
            if self.mode == "groq":
                command = await self._parse_with_groq(user_input)
            elif self.mode == "demo_ai":
                command = await self._parse_with_demo_ai(user_input)
            else:
                command = self._parse_with_patterns(user_input)
            
            # Execute the command
            return await self._execute_command(command)
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"❌ Error: {e}\n💡 Try commands like 'setup github mcp server'"
    
    async def _parse_with_groq(self, user_input: str) -> MCPCommand:
        """Parse command using Groq LLM with enhanced MCP detection"""
        try:
            system_prompt = """You are an expert at parsing natural language commands for MCP (Model Context Protocol) server management.

Parse the user's command and respond with ONLY a JSON object with these fields:
- action: one of "setup", "check", "list", "create_agent", "status", "search"
- mcp_name: the MCP server/service type needed (extract from user intent, not just exact matches)
- agent_type: type of agent to create or empty string
- confidence: confidence score 0.0-1.0
- purpose: brief description of what the user wants to accomplish

You should understand user intent even if they don't mention exact MCP server names.

Examples:
"setup github mcp server" → {"action": "setup", "mcp_name": "github", "agent_type": "", "confidence": 0.95, "purpose": "setup github integration"}

"I need to manage my Docker containers" → {"action": "setup", "mcp_name": "docker", "agent_type": "", "confidence": 0.90, "purpose": "container management"}

"Help me monitor my application performance" → {"action": "setup", "mcp_name": "monitoring", "agent_type": "monitoring_agent", "confidence": 0.88, "purpose": "application monitoring"}

"I want to work with my PostgreSQL database" → {"action": "setup", "mcp_name": "postgres", "agent_type": "", "confidence": 0.92, "purpose": "database integration"}

"Set up email automation for my business" → {"action": "setup", "mcp_name": "email", "agent_type": "", "confidence": 0.89, "purpose": "email automation"}

"What servers are installed" → {"action": "status", "mcp_name": "", "agent_type": "", "confidence": 0.95, "purpose": "check installed servers"}

"Find MCP servers for payment processing" → {"action": "search", "mcp_name": "payment", "agent_type": "", "confidence": 0.87, "purpose": "payment integration"}

"Create a monitoring agent" → {"action": "create_agent", "mcp_name": "monitoring", "agent_type": "monitoring_agent", "confidence": 0.93, "purpose": "create monitoring agent"}

Extract the core service/technology the user needs, even if not explicitly mentioned as "MCP server".

Respond with ONLY the JSON object, no other text."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()
            
            # Try to extract JSON from response
            try:
                # Remove any markdown formatting
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]
                
                parsed = json.loads(response_text)
                
                # If no MCP name detected by AI, try our enhanced extraction
                if not parsed.get("mcp_name"):
                    extracted_intent = self._extract_mcp_intent_from_prompt(user_input)
                    if extracted_intent:
                        parsed["mcp_name"] = extracted_intent
                        parsed["confidence"] = max(0.7, parsed.get("confidence", 0.5))
                
                logger.info(f"🤖 Groq parsed command: {parsed}")
                
                return MCPCommand(
                    action=parsed.get("action", "unknown"),
                    mcp_name=parsed.get("mcp_name", ""),
                    agent_type=parsed.get("agent_type", ""),
                    confidence=parsed.get("confidence", 0.5),
                    raw_input=user_input
                )
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Groq response as JSON: {response_text}")
                # Fallback to pattern matching
                return self._parse_with_patterns(user_input)
                
        except Exception as e:
            logger.error(f"Groq parsing failed: {e}")
            # Fallback to pattern matching
            return self._parse_with_patterns(user_input)
    
    async def _parse_with_demo_ai(self, user_input: str) -> MCPCommand:
        """Parse command using simulated AI understanding (no API key needed)"""
        user_input_lower = user_input.lower().strip()
        
        # Advanced AI-like intent recognition patterns
        ai_intent_map = {
            # Technology-specific intents
            r'\b(container|docker|podman|containerization)\b': ('docker', 'setup', 0.95),
            r'\b(kubernetes|k8s|cluster|orchestration)\b': ('kubernetes', 'setup', 0.94),
            r'\b(database|db|postgres|mysql|mongodb|sql|nosql)\b': ('database', 'setup', 0.92),
            r'\b(email|mail|smtp|gmail|outlook|messaging|notification)\b': ('email', 'setup', 0.91),
            r'\b(git|github|gitlab|version control|repository|repo)\b': ('github', 'setup', 0.93),
            r'\b(monitor|monitoring|observability|metrics|logging|alerting)\b': ('monitoring', 'setup', 0.90),
            r'\b(chat|slack|teams|discord|communication)\b': ('slack', 'setup', 0.89),
            r'\b(payment|stripe|paypal|billing|checkout|transaction)\b': ('payment', 'setup', 0.88),
            r'\b(calendar|schedule|meeting|appointment|time)\b': ('calendar', 'setup', 0.87),
            r'\b(weather|forecast|climate|temperature)\b': ('weather', 'setup', 0.86),
            r'\b(file|filesystem|storage|document|backup)\b': ('filesystem', 'setup', 0.85),
            r'\b(api|rest|graphql|webhook|endpoint)\b': ('api', 'setup', 0.84),
            r'\b(cloud|aws|azure|gcp|serverless)\b': ('cloud', 'setup', 0.83),
            r'\b(security|auth|authentication|oauth|login)\b': ('security', 'setup', 0.82),
            r'\b(analytics|data|dashboard|visualization|metrics)\b': ('analytics', 'setup', 0.81),
            r'\b(machine learning|ml|ai|neural|model)\b': ('ml', 'setup', 0.80),
            r'\b(social|twitter|facebook|linkedin|social media)\b': ('social', 'setup', 0.79),
            r'\b(video|streaming|media|youtube|content)\b': ('media', 'setup', 0.78),
            r'\b(crypto|bitcoin|blockchain|ethereum|defi)\b': ('crypto', 'setup', 0.77),
            r'\b(ci|cd|pipeline|deployment|automation|devops)\b': ('cicd', 'setup', 0.76),
            r'\b(bug|issue|tracking|ticket|jira|linear)\b': ('issue-tracking', 'setup', 0.75),
            r'\b(search|elasticsearch|solr|indexing)\b': ('search', 'setup', 0.74),
        }
        
        # Intent-based action detection
        action_patterns = {
            r'\b(what|which|show|list|display|tell me)\s+(.*?)\s+(installed|available|current)\b': 'status',
            r'\b(install|setup|add|download|get|configure)\b': 'setup',
            r'\b(check|verify|test|validate)\s+if\b': 'check',
            r'\b(create|make|build|generate)\s+(.*?)\s+agent\b': 'create_agent',
            r'\b(search|find|look for|discover)\b': 'search',
            r'\b(list|show|display)\s+(available|all)\b': 'list'
        }
        
        # AI-like understanding: extract technology and action
        detected_tech = ""
        detected_action = "setup"  # Default to setup for most requests
        confidence = 0.7
        
        # First, detect technology/service intent
        for pattern, (tech, default_action, conf) in ai_intent_map.items():
            if re.search(pattern, user_input_lower):
                detected_tech = tech
                detected_action = default_action
                confidence = conf
                break
        
        # Then, refine the action based on explicit action words
        for pattern, action in action_patterns.items():
            if re.search(pattern, user_input_lower):
                detected_action = action
                confidence = min(0.95, confidence + 0.1)
                break
        
        # Special handling for status queries (improved detection)
        if any(phrase in user_input_lower for phrase in [
            "what servers", "what mcp", "show me what", "list installed", 
            "what's installed", "currently installed", "available servers",
            "wht are", "what are", "show mcps", "mcps avail", "mcp avail",
            "available mcp", "installed mcp", "current mcp"
        ]):
            detected_action = "status"
            confidence = 0.95
        
        # Agent type determination for create_agent actions
        agent_type = ""
        if detected_action == "create_agent":
            agent_type_map = {
                "monitoring": "monitoring_agent",
                "github": "devops_agent", 
                "filesystem": "file_manager_agent",
                "docker": "container_agent",
                "kubernetes": "orchestration_agent",
                "database": "data_agent",
                "email": "communication_agent",
                "security": "security_agent"
            }
            agent_type = agent_type_map.get(detected_tech, "custom_agent")
        
        logger.info(f"🧪 Demo AI parsed: tech='{detected_tech}', action='{detected_action}', confidence={confidence}")
        
        return MCPCommand(
            action=detected_action,
            mcp_name=detected_tech,
            agent_type=agent_type,
            confidence=confidence,
            raw_input=user_input
        )
    
    def _parse_with_patterns(self, user_input: str) -> MCPCommand:
        """Parse command using AI-enhanced pattern matching"""
        user_input_lower = user_input.lower().strip()
        
        # Use AI to extract MCP information from any user prompt
        mcp_name = self._extract_mcp_intent_from_prompt(user_input)
        
        # If no specific MCP detected, try to infer from context
        if not mcp_name:
            # Look for technology/service mentions that could be MCP servers
            tech_patterns = {
                r'\b(container|docker|podman)\b': 'docker',
                r'\b(kubernetes|k8s|kubectl)\b': 'kubernetes', 
                r'\b(database|db|postgres|mysql|mongodb|redis)\b': 'database',
                r'\b(git|github|gitlab|version control)\b': 'github',
                r'\b(email|mail|gmail|outlook|smtp)\b': 'email',
                r'\b(chat|slack|teams|discord|communication)\b': 'chat',
                r'\b(cloud|aws|azure|gcp|google cloud)\b': 'cloud',
                r'\b(api|rest|graphql|webhook)\b': 'api',
                r'\b(file|filesystem|storage|drive)\b': 'filesystem',
                r'\b(monitor|monitoring|observability|logs)\b': 'monitoring',
                r'\b(ci|cd|pipeline|jenkins|github actions)\b': 'cicd',
                r'\b(bug|error|tracking|jira|linear)\b': 'issue-tracking',
                r'\b(calendar|schedule|time|meeting)\b': 'calendar',
                r'\b(weather|forecast|climate)\b': 'weather',
                r'\b(search|google|bing|elasticsearch)\b': 'search',
                r'\b(backup|sync|synchronization)\b': 'backup',
                r'\b(security|auth|authentication|oauth)\b': 'security',
                r'\b(payment|stripe|paypal|billing)\b': 'payment',
                r'\b(social|twitter|facebook|linkedin)\b': 'social',
                r'\b(video|youtube|streaming|media)\b': 'media',
                r'\b(crypto|bitcoin|blockchain|ethereum)\b': 'crypto',
                r'\b(machine learning|ml|ai|tensorflow|pytorch)\b': 'ml',
                r'\b(data|analytics|visualization|dashboard)\b': 'analytics'
            }
            
            for pattern, service in tech_patterns.items():
                if re.search(pattern, user_input_lower):
                    mcp_name = service
                    break
        
        # Determine action with better logic
        action = "unknown"
        confidence = 0.7
        
        # Check for status/list queries first (regardless of MCP name presence)
        if any(phrase in user_input_lower for phrase in ["what servers", "what mcp", "show me what", "list installed", "list my", "what's installed", "which servers", "currently installed"]):
            action = "status"
            confidence = 0.9
        elif any(word in user_input_lower for word in ["setup", "install", "download", "add"]) and mcp_name:
            action = "setup"
            confidence = 0.9
        elif any(word in user_input_lower for word in ["check", "available", "exists", "find"]) and mcp_name:
            action = "check"
            confidence = 0.85
        elif any(word in user_input_lower for word in ["list", "show", "display"]) and not any(word in user_input_lower for word in ["what", "which", "installed"]):
            action = "list"
            confidence = 0.8
        elif any(word in user_input_lower for word in ["create", "make", "build"]) and "agent" in user_input_lower:
            action = "create_agent"
            confidence = 0.9
        elif any(word in user_input_lower for word in ["what", "status", "installed", "which", "current", "show"]):
            action = "status"
            confidence = 0.75
        
        # Determine agent type
        agent_type = ""
        if action == "create_agent":
            if "monitoring" in user_input_lower or mcp_name == "langsmith":
                agent_type = "monitoring_agent"
            elif "devops" in user_input_lower or mcp_name == "github":
                agent_type = "devops_agent"
            elif "filesystem" in user_input_lower or "file" in user_input_lower:
                agent_type = "file_manager_agent"
            else:
                agent_type = "custom_agent"
        
        return MCPCommand(
            action=action,
            mcp_name=mcp_name,
            agent_type=agent_type,
            confidence=confidence,
            raw_input=user_input
        )
    
    def _extract_mcp_intent_from_prompt(self, user_input: str) -> str:
        """Use AI to extract MCP server intent from any user prompt"""
        try:
            if self.mode == "groq" and hasattr(self, 'llm'):
                # Use Groq LLM to understand the intent
                return self._ai_extract_mcp_intent(user_input)
            else:
                # Fallback to enhanced pattern matching
                return self._pattern_extract_mcp_intent(user_input)
        except Exception as e:
            logger.warning(f"Error extracting MCP intent: {e}")
            return ""
    
    def _ai_extract_mcp_intent(self, user_input: str) -> str:
        """Use Groq AI to extract MCP server intent from user prompt"""
        try:
            system_prompt = """You are an expert at understanding user intentions for MCP (Model Context Protocol) server needs.

Analyze the user's request and determine what type of MCP server or service they need based on their description. 

Examples:
- "I need to manage my Docker containers" → "docker"
- "Help me track my GitHub repositories" → "github" 
- "I want to monitor my application performance" → "monitoring"
- "Set up email automation for my business" → "email"
- "I need to work with my PostgreSQL database" → "postgres"
- "Help me manage my Kubernetes cluster" → "kubernetes"
- "I want to integrate with Slack for notifications" → "slack"
- "Need to backup my files to cloud storage" → "backup"
- "I want to track bugs and issues in my project" → "issue-tracking"
- "Help me schedule meetings and manage calendar" → "calendar"
- "I need to process payments for my application" → "payment"
- "Want to analyze data and create dashboards" → "analytics"
- "I need machine learning capabilities" → "ml"
- "Help me with CI/CD pipeline automation" → "cicd"

Respond with ONLY the service/technology name (lowercase, single word or hyphenated), or "unknown" if unclear.

Examples of good responses: docker, github, email, postgres, kubernetes, slack, monitoring, analytics, ml, cicd, backup, calendar, payment, issue-tracking, filesystem, weather, social, media, crypto, security, api, cloud, search"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"User request: {user_input}")
            ]
            
            response = self.llm.invoke(messages)
            intent = response.content.strip().lower()
            
            # Validate the response
            if intent and intent != "unknown" and len(intent) < 30:
                logger.info(f"🤖 AI extracted MCP intent: '{intent}' from '{user_input}'")
                return intent
            
        except Exception as e:
            logger.error(f"AI intent extraction failed: {e}")
        
        return ""
    
    def _pattern_extract_mcp_intent(self, user_input: str) -> str:
        """Enhanced pattern-based MCP intent extraction"""
        user_input_lower = user_input.lower()
        
        # Direct service mentions
        direct_services = {
            'docker', 'kubernetes', 'k8s', 'github', 'gitlab', 'slack', 'discord',
            'email', 'gmail', 'postgres', 'mysql', 'mongodb', 'redis', 'aws', 'azure',
            'gcp', 'jira', 'linear', 'notion', 'obsidian', 'stripe', 'paypal',
            'twitter', 'facebook', 'linkedin', 'youtube', 'spotify', 'netflix',
            'zoom', 'teams', 'calendar', 'weather', 'filesystem', 'monitoring'
        }
        
        for service in direct_services:
            if service in user_input_lower:
                return service
        
        # Intent-based patterns (what the user wants to do)
        intent_patterns = {
            r'\b(manage|control|work with|use|integrate|connect to|setup|configure)\s+(containers?|docker|podman)\b': 'docker',
            r'\b(kubernetes|k8s|cluster|pods?|deployments?)\b': 'kubernetes',
            r'\b(git|repository|repo|version control|source control)\b': 'github',
            r'\b(database|db|sql|nosql|data storage)\b': 'database',
            r'\b(email|mail|smtp|notifications|messaging)\b': 'email',
            r'\b(chat|communication|team|collaboration)\b': 'slack',
            r'\b(monitor|monitoring|observability|metrics|logging|alerting)\b': 'monitoring',
            r'\b(files?|filesystem|storage|documents?|backup)\b': 'filesystem',
            r'\b(payment|billing|checkout|transactions?|money)\b': 'payment',
            r'\b(calendar|schedule|meetings?|appointments?|time)\b': 'calendar',
            r'\b(weather|forecast|climate|temperature)\b': 'weather',
            r'\b(search|find|lookup|query|index)\b': 'search',
            r'\b(social|social media|posts?|tweets?)\b': 'social',
            r'\b(video|streaming|media|youtube|content)\b': 'media',
            r'\b(security|auth|authentication|login|oauth)\b': 'security',
            r'\b(api|rest|graphql|webhooks?|endpoints?)\b': 'api',
            r'\b(cloud|aws|azure|gcp|serverless)\b': 'cloud',
            r'\b(ci|cd|pipeline|deployment|automation|devops)\b': 'cicd',
            r'\b(bug|bugs|issue|issues|tracking|tickets?)\b': 'issue-tracking',
            r'\b(analytics|data|dashboard|visualization|metrics)\b': 'analytics',
            r'\b(machine learning|ml|ai|neural|model)\b': 'ml',
            r'\b(crypto|bitcoin|blockchain|ethereum|defi)\b': 'crypto'
        }
        
        for pattern, service in intent_patterns.items():
            if re.search(pattern, user_input_lower):
                return service
        
        return ""
    
    async def _execute_command(self, command: MCPCommand) -> str:
        """Execute the parsed command with AI-enhanced routing"""
        try:
            if command.action == "setup":
                return await self._setup_mcp_server(command.mcp_name)
            elif command.action == "check":
                return await self._check_mcp_availability(command.mcp_name)
            elif command.action == "list":
                return await self._list_available_mcps(command.mcp_name)
            elif command.action == "search":
                return await self._ai_search_mcp_servers(command.mcp_name)
            elif command.action == "create_agent":
                return await self._create_agent_with_mcp(command.mcp_name, command.agent_type)
            elif command.action == "status":
                return await self._get_mcp_status()
            else:
                # AI-enhanced fallback - try to understand intent better
                return await self._ai_fallback_handler(command)
                
        except Exception as e:
            return f"❌ Error executing command: {e}"
    
    async def _ai_search_mcp_servers(self, search_term: str) -> str:
        """AI-powered search for MCP servers"""
        if not search_term:
            return "❌ Please specify what to search for\n💡 Example: 'search for payment MCP servers'"
        
        try:
            # Generate search terms using AI
            search_terms = await self._generate_search_terms_for_mcp(search_term)
            
            # Search GitHub
            github_results = await self._search_github_for_mcp(search_terms)
            
            if not github_results:
                return f"""🔍 No MCP servers found for '{search_term}'

🤖 **AI Suggestions:**
  • Try broader terms: 'search for integration servers'
  • Check built-in servers: 'list available mcp servers'
  • Create custom MCP: Consider building one for {search_term}"""
            
            # Use AI to categorize and present results
            categorized = await self._ai_categorize_search_results(search_term, github_results)
            
            result = f"🔍 **AI-Discovered MCP Servers for '{search_term}'** ({len(github_results)} found):\n\n"
            
            for i, repo in enumerate(github_results[:5], 1):
                result += f"**{i}. {repo['name']}** ⭐ {repo.get('stargazers_count', 0)}\n"
                result += f"   📝 {repo.get('description', 'No description')}\n"
                result += f"   💻 Language: {repo.get('language', 'Unknown')}\n"
                result += f"   🔗 {repo['html_url']}\n"
                
                # Only add AI relevance for the top result to save API calls
                if hasattr(self, 'llm') and self.mode == "groq" and i == 1:
                    try:
                        relevance = await self._ai_calculate_relevance(search_term, repo)
                        result += f"   🤖 AI Relevance: {relevance}/10\n"
                    except:
                        pass
                
                result += "\n"
            
            result += f"💡 **Install any server:** 'setup [server_name] for {search_term}'"
            return result
            
        except Exception as e:
            return f"❌ Error searching for MCP servers: {e}"
    
    async def _ai_categorize_search_results(self, search_term: str, results: List[Dict]) -> Dict:
        """Use AI to categorize search results by relevance and quality"""
        try:
            if self.mode != "groq" or not hasattr(self, 'llm'):
                return {"high": results[:2], "medium": results[2:4], "low": results[4:]}
            
            # AI categorization logic here
            return {"high": results[:3], "medium": results[3:], "low": []}
            
        except Exception as e:
            logger.warning(f"AI categorization failed: {e}")
            return {"high": results[:2], "medium": results[2:4], "low": results[4:]}
    
    async def _ai_calculate_relevance(self, search_term: str, repo: Dict) -> int:
        """Calculate AI relevance score for a repository"""
        try:
            system_prompt = f"""Rate the relevance of this repository for "{search_term}" integration on a scale of 1-10.

Consider:
- Name relevance to "{search_term}"
- Description mentioning MCP or Model Context Protocol
- Stars and activity as quality indicators
- Language and technology stack

Respond with ONLY a number 1-10."""

            repo_info = {
                "name": repo['name'],
                "description": repo.get('description', ''),
                "stars": repo.get('stargazers_count', 0),
                "language": repo.get('language', '')
            }

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=json.dumps(repo_info))
            ]
            
            response = await self.llm.ainvoke(messages)
            return int(response.content.strip())
            
        except Exception as e:
            return 5  # Default relevance score
    
    async def _ai_fallback_handler(self, command: MCPCommand) -> str:
        """AI-enhanced fallback for unclear commands"""
        try:
            if self.mode == "groq" and hasattr(self, 'llm'):
                system_prompt = """The user's command wasn't clearly understood. Based on their input, provide a helpful response that:

1. Acknowledges what they might be trying to do
2. Suggests 2-3 specific commands they could try
3. Offers to help them find what they need

Be helpful and specific. Use the user's original input to understand their intent."""

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"User input: {command.raw_input}")
                ]
                
                response = await self.llm.ainvoke(messages)
                return f"🤖 **AI Assistant:** {response.content}\n\n💡 **Try these commands:**\n  • 'what mcp servers are installed?'\n  • 'search for [technology] MCP servers'\n  • 'I need help with [specific task]'"
            elif self.mode == "demo_ai":
                return await self._demo_ai_fallback_handler(command)
            
        except Exception as e:
            logger.warning(f"AI fallback failed: {e}")
        
        # Basic fallback
        return self._suggest_commands(command)
    
    async def _demo_ai_fallback_handler(self, command: MCPCommand) -> str:
        """Demo AI fallback with intelligent suggestions"""
        user_input = command.raw_input.lower()
        
        # Intelligent suggestions based on user input analysis
        suggestions = []
        
        # Technology-specific suggestions
        if any(word in user_input for word in ['app', 'application', 'web', 'site', 'software']):
            suggestions.extend([
                "'I need monitoring for my web application'",
                "'Set up GitHub integration for my app development'",
                "'Help me with database connections for my app'"
            ])
        
        if any(word in user_input for word in ['business', 'company', 'enterprise', 'team']):
            suggestions.extend([
                "'Set up email automation for my business'",
                "'I need Slack integration for team communication'",
                "'Help me with payment processing for my business'"
            ])
        
        if any(word in user_input for word in ['data', 'information', 'analytics', 'metrics']):
            suggestions.extend([
                "'I need database integration for data management'",
                "'Set up analytics dashboard for my metrics'",
                "'Help me with data backup and storage'"
            ])
        
        # Default suggestions if no specific context
        if not suggestions:
            suggestions = [
                "'I need to manage my Docker containers'",
                "'Help me set up email automation'",
                "'I want to monitor my applications'",
                "'Set up payment processing for my project'"
            ]
        
        return f"""🤖 **AI Analysis:** I understand you're looking for help, but I need a bit more context.

**Based on your request, you might want to try:**
{chr(10).join(f"  • {suggestion}" for suggestion in suggestions[:3])}

**Or describe what you want to accomplish:**
  • "I need help with [specific technology]"
  • "I want to integrate [service] with my project"
  • "Help me automate [specific task]"

**Current system status:**
  • Type 'what mcp servers are installed?' to see what's available
  • Type 'list available mcp servers' to browse options

💡 **The AI understands natural language - just describe what you need!**"""
    
    async def _setup_mcp_server(self, mcp_name: str) -> str:
        """Setup MCP server with AI-powered discovery and installation"""
        if not mcp_name:
            return "❌ Please describe what you want to do\n💡 Example: 'I need to manage my Docker containers'"
        
        try:
            # Check if already installed
            check_result = await self._check_mcp_availability(mcp_name)
            if "already installed" in check_result.lower():
                return check_result
            
            # Use AI to enhance understanding of user intent
            if self.mode == "groq" and hasattr(self, 'llm'):
                enhanced_intent = await self._ai_enhance_user_intent(mcp_name)
                logger.info(f"🤖 AI Enhanced Intent: {enhanced_intent}")
            else:
                enhanced_intent = mcp_name
            
            # Use AI to generate search terms for GitHub
            search_terms = await self._generate_search_terms_for_mcp(enhanced_intent)
            logger.info(f"🔍 AI-generated search terms for '{enhanced_intent}': {search_terms}")
            
            # Search GitHub using the AI-generated terms
            github_results = await self._search_github_for_mcp(search_terms)
            
            if github_results:
                # Use AI to rank and select the best match
                best_match = await self._ai_select_best_mcp_match(enhanced_intent, github_results)
                
                if best_match:
                    # Use AI to understand why this match was selected
                    ai_reasoning = ""
                    if self.mode == "groq" and hasattr(self, 'llm'):
                        ai_reasoning = await self._ai_explain_selection(enhanced_intent, best_match)
                    
                    # Attempt to install the best match
                    logger.info(f"🚀 Installing AI-selected MCP: {best_match['name']}")
                    
                    # Create MCPServerInfo from GitHub result
                    from ai_agent_protocol.core import MCPServerInfo
                    
                    # Construct proper zip download URL
                    # GitHub's default branch is usually 'main' but could be 'master' or other
                    default_branch = best_match.get('default_branch', 'main')
                    if not default_branch:  # Fallback if default_branch is None
                        default_branch = 'main'
                    zip_download_url = f"{best_match['html_url']}/archive/refs/heads/{default_branch}.zip"
                    
                    server_info = MCPServerInfo(
                        name=best_match['name'],
                        repository_url=best_match['html_url'],
                        download_url=zip_download_url,
                        description=best_match.get('description', f"AI-discovered MCP for {enhanced_intent}"),
                        language=best_match.get('language', 'Python'),
                        installation_commands=[],
                        run_command="",
                        run_args=[],
                        dependencies=[]
                    )
                    
                    # Try to install
                    success = await self.protocol.server_manager.download_and_install_server(server_info)
                    
                    if success:
                        ai_response = f"""✅ AI Successfully Analyzed and Installed MCP Server!

🤖 **AI Analysis:**
{ai_reasoning if ai_reasoning else f"Selected {best_match['name']} as the best match for your '{enhanced_intent}' needs."}

🎯 **AI-Selected Server:**
  • Name: {best_match['name']}
  • Description: {best_match.get('description', 'AI-discovered MCP server')}
  • Language: {best_match.get('language', 'Unknown')}
  • Stars: ⭐ {best_match.get('stargazers_count', 0)}
  • Repository: {best_match['html_url']}

💡 **AI Suggestions:**
  • Try: 'create agent with {enhanced_intent}'
  • Ask: 'what can I do with {best_match['name']}?'
  • Explore: 'what mcp servers are installed?'"""
                        
                        return ai_response
                    else:
                        return f"❌ Failed to install {best_match['name']}. Check logs for details."
                else:
                    # AI found no relevant match
                    return f"""🤖 AI Analysis: No specific MCP servers found for '{mcp_name}'

❌ **Search Results:** Found {len(github_results)} MCP repositories, but none are specifically designed for {mcp_name} integration.

🔍 **AI Recommendations:**
  • Try more specific search: 'search for {mcp_name} integration tools'
  • Explore popular alternatives: 'setup monitoring mcp server'
  • Check what's available: 'list available mcp servers'
  • Consider similar services: 'setup filesystem mcp server'

💡 **Note:** The AI avoided installing generic MCP tools that aren't {mcp_name}-specific."""
            
            # If no GitHub results, use AI to provide intelligent suggestions
            if self.mode == "groq" and hasattr(self, 'llm'):
                ai_suggestions = await self._ai_suggest_alternatives(enhanced_intent)
                return f"""🤖 AI Analysis: No direct MCP servers found for '{enhanced_intent}'

{ai_suggestions}

🔍 **AI Recommendations:**
  • Try broader search: 'search for {enhanced_intent} integration servers'
  • Explore similar: 'setup monitoring mcp server'
  • Check available: 'list available mcp servers'"""
            
            # Fallback to basic response
            return f"""🤖 AI Analysis: Looking for {mcp_name.title()} MCP servers...

❌ No suitable MCP servers found automatically.

🔍 **AI Suggestions:**
  • Search manually: 'search github for {mcp_name} mcp'
  • Try similar services: 'setup monitoring mcp server'
  • Check available: 'list available mcp servers'

💡 **Custom Integration:** You might need to create a custom MCP for {mcp_name}"""
                
        except Exception as e:
            logger.error(f"Error in AI-powered MCP setup: {e}")
            return f"❌ Error setting up {mcp_name} MCP server: {e}"
    
    async def _generate_search_terms_for_mcp(self, mcp_name: str) -> List[str]:
        """Use AI to generate search terms for finding MCP servers"""
        try:
            if self.mode == "groq" and hasattr(self, 'llm'):
                system_prompt = """Generate 3 search terms for finding MCP (Model Context Protocol) servers on GitHub.

Given a service/technology name, provide exactly 3 search terms that would find relevant MCP servers.

Examples:
docker → ["docker mcp", "mcp docker", "docker-mcp-server"]
email → ["email mcp", "mcp email", "email-mcp-server"]
monitoring → ["monitoring mcp", "mcp monitoring", "monitoring-mcp"]

Respond with a JSON array of exactly 3 search terms, no other text."""

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Service: {mcp_name}")
                ]
                
                response = await self.llm.ainvoke(messages)
                search_terms = json.loads(response.content.strip())
                
                return search_terms if isinstance(search_terms, list) else [f"{mcp_name} mcp"]
                
        except Exception as e:
            logger.warning(f"AI search term generation failed: {e}")
        
        # Fallback search terms - only 3 terms
        return [
            f"{mcp_name} mcp",
            f"mcp {mcp_name}",
            f"{mcp_name}-mcp-server"
        ]
    
    async def _search_github_for_mcp(self, search_terms: List[str]) -> List[Dict]:
        """Search GitHub for MCP servers using AI-generated terms"""
        import aiohttp
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for term in search_terms[:3]:  # Limit to 3 terms to avoid rate limits
                    url = f"https://api.github.com/search/repositories?q={term}&sort=stars&order=desc&per_page=5"
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            for item in data.get('items', []):
                                # Use simple filtering first, then AI for final selection
                                name = item['name'].lower()
                                desc = (item.get('description') or '').lower()
                                
                                # Enhanced MCP filtering - must be MCP AND service-specific
                                service_keyword = term.split()[0].lower()
                                if ('mcp' in name or 'mcp' in desc or 'model context protocol' in desc):
                                    # If it's an MCP server, check if it's relevant to the service
                                    if (service_keyword in name or service_keyword in desc or
                                        # Additional service-specific keywords
                                        (service_keyword == 'docker' and any(kw in desc for kw in ['container', 'docker', 'containerization'])) or
                                        (service_keyword == 'email' and any(kw in desc for kw in ['email', 'mail', 'smtp'])) or
                                        (service_keyword == 'github' and any(kw in desc for kw in ['git', 'github', 'repository'])) or
                                        (service_keyword == 'monitoring' and any(kw in desc for kw in ['monitor', 'observability', 'metrics'])) or
                                        # Generic fallback for other services
                                        service_keyword in name):
                                        results.append(item)
                        
                        await asyncio.sleep(0.5)  # Rate limiting
            
            # Remove duplicates 
            seen = set()
            unique_results = []
            for repo in results:
                if repo['id'] not in seen:
                    seen.add(repo['id'])
                    unique_results.append(repo)
            
            # Sort by relevance first, then by stars
            # Prioritize repositories with service name in the title
            def relevance_score(repo):
                name = repo['name'].lower()
                desc = (repo.get('description') or '').lower()
                stars = repo.get('stargazers_count', 0)
                
                # Extract service name from first search term
                service_name = search_terms[0].split()[0].lower() if search_terms else ""
                
                # Relevance scoring
                score = 0
                if service_name in name:
                    score += 1000  # High priority for service name in repo name
                if f"{service_name}-mcp" in name or f"mcp-{service_name}" in name:
                    score += 500   # High priority for specific MCP server naming
                if service_name in desc and "mcp" in desc:
                    score += 100   # Medium priority for service mentioned in MCP description
                
                # Add normalized star count (max 100 points)
                score += min(stars / 100, 100)
                
                return score
            
            unique_results.sort(key=relevance_score, reverse=True)
            
            logger.info(f"🔍 Found {len(unique_results)} relevant repositories")
            return unique_results[:10]  # Return top 10
                        
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
        
        return results
    
    async def _ai_check_repo_relevance(self, search_term: str, repo: Dict) -> bool:
        """Use AI to check if a repository is relevant to the search term"""
        try:
            system_prompt = f"""Determine if this GitHub repository is relevant for '{search_term}' MCP server needs.

Consider:
- Repository name and description
- Whether it's related to MCP (Model Context Protocol)
- If it could help with '{search_term}' integration
- Quality indicators (stars, recent activity)

Respond with only "yes" or "no"."""

            repo_info = {
                "name": repo['name'],
                "description": repo.get('description', ''),
                "stars": repo.get('stargazers_count', 0)
            }

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Search term: {search_term}\nRepository: {json.dumps(repo_info)}")
            ]
            
            response = await self.llm.ainvoke(messages)
            result = response.content.strip().lower()
            
            return result == "yes"
            
        except Exception as e:
            logger.warning(f"AI relevance check failed: {e}")
            return True  # Default to include if AI fails
    
    async def _ai_select_best_mcp_match(self, mcp_name: str, github_results: List[Dict]) -> Optional[Dict]:
        """Use AI to select the best MCP server from GitHub results"""
        try:
            if not github_results or self.mode != "groq" or not hasattr(self, 'llm'):
                return github_results[0] if github_results else None
            
            # Prepare repository information for AI analysis
            repo_info = []
            for i, repo in enumerate(github_results[:5]):  # Limit to top 5
                info = {
                    "index": i,
                    "name": repo['name'],
                    "description": repo.get('description', ''),
                    "stars": repo.get('stargazers_count', 0),
                    "language": repo.get('language', 'Unknown'),
                    "updated": repo.get('updated_at', '')
                }
                repo_info.append(info)
            
            system_prompt = f"""You are selecting the best MCP server repository for "{mcp_name}" integration.

CRITICAL INSTRUCTIONS:
1. You MUST respond with ONLY a single number (0-4) or -1
2. Do NOT include any explanatory text, descriptions, or reasoning
3. ONLY select repositories that are specifically designed for "{mcp_name}"
4. If NO repository is specifically for "{mcp_name}", respond with -1

Selection criteria (in order of importance):
1. Repository name contains "{mcp_name}" 
2. Repository description mentions "{mcp_name}" integration or "{mcp_name}" MCP
3. Repository is clearly an MCP server FOR "{mcp_name}" (not a general tool)
4. Reject generic MCP tools, web panels, or management interfaces

For "{mcp_name}", ONLY accept repositories that are:
- Specifically designed as MCP servers for "{mcp_name}"
- Have "{mcp_name}" in the name or are clearly "{mcp_name}"-focused
- Are NOT general management tools or web interfaces

RESPOND WITH ONLY ONE NUMBER: 0, 1, 2, 3, 4, or -1"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Repositories to analyze:\n{json.dumps(repo_info, indent=2)}")
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()
            
            # Extract number from response (in case AI adds extra text)
            import re
            number_match = re.search(r'^(-?\d+)', response_text)
            if number_match:
                selected_index = int(number_match.group(1))
            else:
                logger.warning(f"AI returned invalid response: {response_text}")
                selected_index = -1
            
            if selected_index == -1:
                # AI found no relevant matches
                return None
            elif 0 <= selected_index < len(github_results):
                return github_results[selected_index]
                
        except Exception as e:
            logger.warning(f"AI selection failed: {e}")
        
        # Fallback: return the first result with most stars
        return max(github_results, key=lambda x: x.get('stargazers_count', 0)) if github_results else None
    
    async def _ai_enhance_user_intent(self, mcp_name: str) -> str:
        """Use AI to enhance understanding of user intent"""
        try:
            system_prompt = f"""You are analyzing a user's request for MCP server setup. The user mentioned '{mcp_name}'.

Based on this, provide a more specific and enhanced understanding of what they likely need.

Examples:
- "docker" → "docker container management and orchestration"
- "email" → "email automation and SMTP integration"  
- "monitoring" → "application performance monitoring and observability"
- "github" → "git repository management and version control"
- "payment" → "payment processing and financial transactions"

Respond with a more descriptive phrase that captures the user's likely intent, keep it concise (under 8 words)."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"User wants: {mcp_name}")
            ]
            
            response = await self.llm.ainvoke(messages)
            enhanced = response.content.strip()
            
            return enhanced if enhanced else mcp_name
            
        except Exception as e:
            logger.warning(f"AI intent enhancement failed: {e}")
            return mcp_name
    
    async def _ai_explain_selection(self, intent: str, selected_repo: Dict) -> str:
        """Use AI to explain why a particular repository was selected"""
        try:
            system_prompt = f"""Explain in 2-3 sentences why this repository is a good match for the user's '{intent}' needs.

Focus on:
- How the repository relates to their intent
- Key features that make it suitable
- Why it's better than alternatives

Be concise and helpful."""

            repo_info = {
                "name": selected_repo['name'],
                "description": selected_repo.get('description', ''),
                "stars": selected_repo.get('stargazers_count', 0),
                "language": selected_repo.get('language', '')
            }

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"User intent: {intent}\nSelected repository: {json.dumps(repo_info)}")
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"AI explanation failed: {e}")
            return f"This repository appears to be the best match for {intent} based on its popularity and description."
    
    async def _ai_suggest_alternatives(self, intent: str) -> str:
        """Use AI to suggest alternatives when no direct matches are found"""
        try:
            system_prompt = f"""The user is looking for MCP servers related to '{intent}' but none were found on GitHub.

Provide helpful suggestions for:
1. Alternative search terms they could try
2. Related technologies that might have MCP servers
3. General advice for their use case

Be encouraging and provide 3-4 concrete suggestions."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"No MCP servers found for: {intent}")
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"AI alternatives failed: {e}")
            return f"Consider searching for related technologies or creating a custom MCP server for {intent}."
    
    async def _check_mcp_availability(self, mcp_name: str) -> str:
        """Check MCP server availability"""
        if not mcp_name:
            return "❌ Please specify an MCP server name\n💡 Example: 'check if github is available'"
        
        try:
            # Check if already installed
            python_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "python" / "servers" / f"{mcp_name.upper()}_MCP"
            js_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "js" / "servers" / f"{mcp_name.upper()}_MCP"
            
            if python_path.exists() or js_path.exists():
                location = python_path if python_path.exists() else js_path
                return f"""✅ {mcp_name.title()} MCP server is already installed!

📁 **Location:** {location.name}
🎯 **Ready to use:** You can now create agents with this MCP server
💡 **Try:** 'create monitoring agent with {mcp_name}'"""
            
            # Search for available servers
            servers = await self.protocol.list_available_mcp_servers(mcp_name)
            if servers:
                result = f"🔍 Found {len(servers)} {mcp_name.title()} MCP servers available:\n\n"
                for i, server in enumerate(servers[:3], 1):
                    result += f"  {i}. **{server.name}**\n"
                    result += f"     {server.description} ({server.language})\n\n"
                result += f"💡 **Install:** 'setup {mcp_name} mcp server'"
                return result
            else:
                return f"❌ No {mcp_name.title()} MCP servers found.\n💡 Try: 'list available mcp servers'"
                
        except Exception as e:
            return f"❌ Error checking {mcp_name}: {e}"
    
    async def _list_available_mcps(self, search_term: str = "") -> str:
        """List available MCP servers"""
        try:
            # If search_term is empty, just show status of installed servers first
            if not search_term:
                status_result = await self._get_mcp_status()
                if "No MCP servers currently installed" not in status_result:
                    return status_result + "\n\n💡 **Search for more:** 'list github servers'"
            
            servers = await self.protocol.list_available_mcp_servers(search_term)
            if not servers:
                return "❌ No MCP servers found.\n💡 Check your internet connection"
            
            result = f"📋 **Available MCP Servers** ({len(servers)} found):\n\n"
            
            for i, server in enumerate(servers[:8], 1):  # Limit to 8
                result += f"**{i}. {server.name}**\n"
                result += f"   📝 {server.description}\n"
                result += f"   🔧 Language: {server.language}\n"
                result += f"   🔗 {server.repository_url}\n\n"
            
            if len(servers) > 8:
                result += f"... and {len(servers) - 8} more servers available.\n\n"
            
            result += "💡 **Install any server:** 'setup [server_name] mcp server'"
            return result
            
        except Exception as e:
            return f"❌ Error listing servers: {e}"
    
    async def _create_agent_with_mcp(self, mcp_name: str, agent_type: str = "") -> str:
        """Create agent with MCP integration"""
        if not mcp_name:
            return "❌ Please specify which MCP to use\n💡 Example: 'create monitoring agent with langsmith'"
        
        try:
            # Auto-determine agent type if not specified
            if not agent_type:
                agent_type_map = {
                    "langsmith": "monitoring_agent",
                    "github": "devops_agent",
                    "filesystem": "file_manager_agent",
                    "pagerduty": "incident_management_agent"
                }
                agent_type = agent_type_map.get(mcp_name, "custom_agent")
            
            description = f"AI agent with {mcp_name.title()} MCP integration"
            
            request = AgentRequest(
                agent_type=agent_type,
                required_mcps=[mcp_name],
                description=description,
                metadata={"created_via": "natural_language", "mcp_focus": mcp_name}
            )
            
            logger.info(f"🤖 Creating {agent_type} with {mcp_name} MCP...")
            agent_config = await self.protocol.create_agent(request)
            
            result = f"""✅ Successfully created AI agent!

🤖 **Agent Details:**
  • ID: {agent_config['id']}
  • Type: {agent_config['type']}
  • Status: {agent_config['status']}
  • Description: {agent_config['description']}

📦 **MCP Integrations:**"""
            
            for i, mcp in enumerate(agent_config['mcp_servers'], 1):
                result += f"\n  {i}. {mcp['name']} - {mcp['description']}"
            
            result += f"\n\n🎯 Your {mcp_name.title()} agent is ready for operations!"
            return result
            
        except Exception as e:
            return f"❌ Error creating agent: {e}"
    
    async def _get_mcp_status(self) -> str:
        """Get status of installed MCP servers with AI-enhanced explanations"""
        try:
            python_servers_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "python" / "servers"
            js_servers_path = self.base_path / "src" / "Base" / "MCP_structure" / "mcp_servers" / "js" / "servers"
            
            installed_servers = []
            
            # Check Python servers
            if python_servers_path.exists():
                for server_dir in python_servers_path.iterdir():
                    if server_dir.is_dir() and not server_dir.name.startswith('.') and server_dir.name != '__pycache__':
                        installed_servers.append(f"{server_dir.name} (Python)")
            
            # Check JS servers
            if js_servers_path.exists():
                for server_dir in js_servers_path.iterdir():
                    if server_dir.is_dir() and not server_dir.name.startswith('.'):
                        installed_servers.append(f"{server_dir.name} (JavaScript)")
            
            if installed_servers:
                result = f"📦 **Installed MCP Servers ({len(installed_servers)}):**\n\n"
                for i, server in enumerate(installed_servers, 1):
                    result += f"  {i}. {server}\n"
                
                # Use AI to provide intelligent suggestions based on installed servers
                if self.mode == "groq" and hasattr(self, 'llm'):
                    ai_suggestions = await self._ai_analyze_installed_servers(installed_servers)
                    result += f"\n🤖 **AI Analysis:**\n{ai_suggestions}\n"
                
                result += f"\n💡 **Actions you can take:**\n"
                result += f"  • Create agents: 'create agent with [server_name]'\n"
                result += f"  • Get help: 'what can I do with [server_name]?'\n"
                result += f"  • Add more: 'I need help with [technology]'"
                
                return result
            else:
                # Use AI to provide intelligent getting started advice
                if self.mode == "groq" and hasattr(self, 'llm'):
                    ai_advice = await self._ai_getting_started_advice()
                    return f"""📦 No MCP servers currently installed.

🤖 **AI Recommendations:**
{ai_advice}

💡 **Quick starts:**
  • 'I need to manage my Docker containers'
  • 'Help me set up email automation'
  • 'I want to monitor my applications'"""
                else:
                    return """📦 No MCP servers currently installed.

💡 **Get started:**
  • Install servers: 'setup github mcp server'
  • List available: 'list available mcp servers'"""
                
        except Exception as e:
            return f"❌ Error getting status: {e}"
    
    async def _ai_analyze_installed_servers(self, servers: List[str]) -> str:
        """Use AI to analyze installed servers and provide intelligent suggestions"""
        try:
            system_prompt = """Analyze the installed MCP servers and provide helpful insights.

Suggest:
1. What the user can accomplish with these servers
2. Potential workflows or combinations
3. Missing servers that would complement these

Be concise and actionable (3-4 sentences max)."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Installed servers: {', '.join(servers)}")
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"AI server analysis failed: {e}")
            return "You have several MCP servers installed and ready to use!"
    
    async def _ai_getting_started_advice(self) -> str:
        """Use AI to provide getting started advice when no servers are installed"""
        try:
            system_prompt = """The user has no MCP servers installed yet. Provide encouraging and helpful advice for getting started.

Include:
1. Popular use cases for MCP servers
2. Easy first servers to install
3. How to explore what's available

Be encouraging and specific (3-4 sentences)."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content="User has no MCP servers installed, what should they do?")
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"AI getting started advice failed: {e}")
            return "Start by telling me what you want to accomplish! For example: 'I need to manage my Docker containers' or 'Help me set up monitoring for my apps'."
    
    def _suggest_commands(self, command: MCPCommand) -> str:
        """Suggest valid commands"""
        return f"""🤖 I understand you want to work with MCP servers.

**Available commands:**
  • 'setup [server] mcp server' - Install MCP server
  • 'check if [server] is available' - Check availability  
  • 'list available mcp servers' - List all servers
  • 'create agent with [server]' - Create AI agent
  • 'what mcp servers are installed?' - Show status

**Popular servers:** github, langsmith, filesystem, pagerduty

💡 **Try:** 'setup github mcp server'"""

class EnhancedMCPCLI:
    """Enhanced CLI with natural language processing"""
    
    def __init__(self, groq_api_key: str = None):
        self.base_path = Path(__file__).parent.parent
        self.processor = NaturalLanguageMCPProcessor(str(self.base_path), groq_api_key)
    
    async def interactive_mode(self):
        """Interactive mode with AI-powered MCP understanding"""
        print("🤖 Enhanced AI Agent Protocol - AI-Powered Natural Language Interface")
        print("=" * 70)
        print(f"🧠 AI Mode: {self.processor.mode.title()}" + (" (Groq LLM)" if self.processor.mode == "groq" else " (Enhanced Pattern Matching)"))
        print()
        print("🆕 **AI-Powered Features:**")
        print("  🎯 Understands ANY MCP server request (not just predefined)")
        print("  🔍 Searches GitHub automatically for matching servers")
        print("  🤖 AI selects the best match for your needs")
        print("  📝 Natural language understanding of user intent")
        print()
        print("**Examples of what you can say:**")
        print("  • 'I need to manage my Docker containers'")
        print("  • 'Help me set up email automation'")
        print("  • 'I want to monitor my application performance'")
        print("  • 'Set up payment processing for my app'")
        print("  • 'I need to work with my PostgreSQL database'")
        print("  • 'Help me integrate with Kubernetes'")
        print("  • 'Search for machine learning MCP servers'")
        print("  • 'Find MCP servers for social media integration'")
        print()
        print("**Traditional commands still work:**")
        print("  • 'setup github mcp server'")
        print("  • 'what mcp servers are installed?'")
        print("  • 'create monitoring agent with langsmith'")
        print()
        print("Type 'quit' to exit")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("\n🎯 Your request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print(f"\n🤖 AI Processing: {user_input}")
                print("-" * 50)
                
                response = await self.processor.process_command(user_input)
                
                print("🎯 **AI Response:**")
                print(response)
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def process_command(self, command: str) -> str:
        """Process single command"""
        return await self.processor.process_command(command)

async def demo_enhanced_protocol():
    """Demo the AI-enhanced protocol with natural language understanding"""
    
    print("🚀 AI-Enhanced Agent Protocol Demo")
    print("=" * 50)
    print("🧠 Showcasing AI-powered MCP server discovery")
    
    # Get Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        print("✅ Using Groq LLM for intelligent command processing")
    else:
        print("📝 Using enhanced pattern matching (no Groq API key)")
        print("💡 Add GROQ_API_KEY for full AI capabilities")
    
    cli = EnhancedMCPCLI(groq_api_key)
    
    # Demo commands showcasing AI understanding
    demo_commands = [
        "what mcp servers are currently installed?",
        "I need to manage my Docker containers",
        "Help me set up email automation for my business", 
        "I want to monitor my application performance",
        "Search for payment processing MCP servers",
        "Set up integration with my PostgreSQL database"
    ]
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n🎯 AI Demo {i}/6: '{command}'")
        print("-" * 50)
        
        try:
            response = await cli.process_command(command)
            print("🤖 **AI Response:**")
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
        
        if i < len(demo_commands):
            input("Press Enter to continue...")
    
    print("\n🎉 AI Demo Complete!")
    print("\n🚀 **Key AI Features Demonstrated:**")
    print("  ✅ Natural language understanding (not just keywords)")
    print("  ✅ Intent recognition from user descriptions")
    print("  ✅ Automatic GitHub search for MCP servers")
    print("  ✅ AI-powered server selection and ranking")
    print("  ✅ Context-aware responses and suggestions")
    print("\n💡 **Try interactive mode:**")
    print("python src/enhanced_ai_protocol_working.py")

async def main():
    """Main function"""
    
    print("🤖 Enhanced AI Agent Protocol - Working Version")
    print("=" * 55)
    print("Natural language MCP server setup with Groq LLM")
    print()
    
    choice = input("Choose mode:\n1. Demo mode\n2. Interactive mode\n3. Exit\n\nYour choice: ").strip()
    
    if choice == "1":
        await demo_enhanced_protocol()
    elif choice == "2":
        groq_api_key = os.getenv("GROQ_API_KEY")
        cli = EnhancedMCPCLI(groq_api_key)
        await cli.interactive_mode()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
