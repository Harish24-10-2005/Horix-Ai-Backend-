"""
Predefined AI Agent Templates
"""

from typing import Dict, Any
from .core import AgentRequest, AIAgentProtocol

class AgentTemplates:
    """Collection of predefined agent templates"""
    
    @staticmethod
    def langsmith_monitoring_agent() -> AgentRequest:
        """Template for LangSmith monitoring agent"""
        return AgentRequest(
            agent_type="monitoring_agent",
            required_mcps=["langsmith"],
            description="AI agent for monitoring other AI agents using LangSmith MCP server",
            metadata={
                "monitoring_interval": 60,
                "alert_thresholds": {
                    "error_rate": 0.1,
                    "response_time": 5000,
                    "token_usage": 10000
                },
                "metrics_to_track": [
                    "response_time",
                    "error_rate",
                    "token_usage",
                    "request_count",
                    "success_rate"
                ],
                "notification_channels": ["email", "slack"],
                "dashboard_config": {
                    "refresh_interval": 30,
                    "charts": ["line", "bar", "gauge"]
                }
            }
        )
    
    @staticmethod
    def github_devops_agent() -> AgentRequest:
        """Template for GitHub DevOps agent"""
        return AgentRequest(
            agent_type="devops_agent",
            required_mcps=["github"],
            description="AI agent for GitHub repository operations and DevOps automation",
            metadata={
                "capabilities": [
                    "code_review",
                    "pr_management",
                    "issue_tracking",
                    "deployment_automation"
                ],
                "permissions": ["read", "write", "issues", "pull_requests"],
                "automation_rules": {
                    "auto_assign_reviewers": True,
                    "auto_label_issues": True,
                    "auto_merge_conditions": {
                        "required_reviews": 2,
                        "ci_status": "success"
                    }
                }
            }
        )
    
    @staticmethod
    def filesystem_manager_agent() -> AgentRequest:
        """Template for filesystem management agent"""
        return AgentRequest(
            agent_type="filesystem_agent",
            required_mcps=["filesystem"],
            description="AI agent for intelligent file and directory management",
            metadata={
                "capabilities": [
                    "file_organization",
                    "backup_management",
                    "cleanup_automation",
                    "content_analysis"
                ],
                "rules": {
                    "auto_organize": True,
                    "backup_schedule": "daily",
                    "cleanup_threshold": "30_days",
                    "duplicate_detection": True
                },
                "monitored_directories": [],
                "file_patterns": {
                    "documents": ["*.pdf", "*.doc", "*.docx"],
                    "images": ["*.jpg", "*.png", "*.gif"],
                    "code": ["*.py", "*.js", "*.ts", "*.java"]
                }
            }
        )
    
    @staticmethod
    def data_analysis_agent() -> AgentRequest:
        """Template for data analysis agent"""
        return AgentRequest(
            agent_type="data_analysis_agent",
            required_mcps=["filesystem", "github"],
            description="AI agent for automated data analysis and reporting",
            metadata={
                "capabilities": [
                    "data_processing",
                    "statistical_analysis",
                    "visualization",
                    "report_generation"
                ],
                "data_sources": [
                    "csv_files",
                    "databases",
                    "apis",
                    "github_metrics"
                ],
                "analysis_types": [
                    "descriptive",
                    "predictive",
                    "trend_analysis",
                    "anomaly_detection"
                ],
                "output_formats": ["pdf", "html", "json", "csv"]
            }
        )
    
    @staticmethod
    def security_audit_agent() -> AgentRequest:
        """Template for security audit agent"""
        return AgentRequest(
            agent_type="security_agent",
            required_mcps=["github", "filesystem"],
            description="AI agent for automated security auditing and compliance checking",
            metadata={
                "audit_types": [
                    "code_vulnerability_scan",
                    "dependency_check",
                    "configuration_audit",
                    "access_control_review"
                ],
                "compliance_standards": ["OWASP", "CIS", "SOC2"],
                "scan_schedule": "weekly",
                "severity_levels": ["critical", "high", "medium", "low"],
                "notification_thresholds": {
                    "critical": "immediate",
                    "high": "within_1_hour",
                    "medium": "daily_digest"
                }
            }
        )
    
    @staticmethod
    def custom_agent(agent_type: str, mcps: list, description: str, metadata: Dict[str, Any]) -> AgentRequest:
        """Template for custom agent creation"""
        return AgentRequest(
            agent_type=agent_type,
            required_mcps=mcps,
            description=description,
            metadata=metadata
        )

class QuickAgentFactory:
    """Factory for quickly creating common agent types"""
    
    def __init__(self, protocol: AIAgentProtocol):
        self.protocol = protocol
    
    async def create_langsmith_monitor(self, custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a LangSmith monitoring agent"""
        template = AgentTemplates.langsmith_monitoring_agent()
        if custom_config:
            template.metadata.update(custom_config)
        return await self.protocol.create_agent(template)
    
    async def create_github_devops(self, repositories: list = None, custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a GitHub DevOps agent"""
        template = AgentTemplates.github_devops_agent()
        if repositories:
            template.metadata["repositories"] = repositories
        if custom_config:
            template.metadata.update(custom_config)
        return await self.protocol.create_agent(template)
    
    async def create_filesystem_manager(self, directories: list = None, custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a filesystem management agent"""
        template = AgentTemplates.filesystem_manager_agent()
        if directories:
            template.metadata["monitored_directories"] = directories
        if custom_config:
            template.metadata.update(custom_config)
        return await self.protocol.create_agent(template)
    
    async def create_data_analyst(self, data_sources: list = None, custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a data analysis agent"""
        template = AgentTemplates.data_analysis_agent()
        if data_sources:
            template.metadata["data_sources"] = data_sources
        if custom_config:
            template.metadata.update(custom_config)
        return await self.protocol.create_agent(template)
    
    async def create_security_auditor(self, scan_targets: list = None, custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a security audit agent"""
        template = AgentTemplates.security_audit_agent()
        if scan_targets:
            template.metadata["scan_targets"] = scan_targets
        if custom_config:
            template.metadata.update(custom_config)
        return await self.protocol.create_agent(template)
