"""
Thinguva Sentinel — Agent Identity & RBAC
==========================================
Tracks who is running what agent and enforces
role-based access control on agent actions.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class AgentIdentity:
    agent_id: str
    agent_name: str
    role: str
    owner: str
    allowed_tools: List[str] = field(default_factory=list)
    max_risk_score: int = 100
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    def can_use_tool(self, tool_name: str) -> bool:
        if not self.allowed_tools:
            return True
        return tool_name in self.allowed_tools

    def can_take_risk(self, risk_score: int) -> bool:
        return risk_score <= self.max_risk_score

class IdentityManager:
    def __init__(self):
        self.agents = {}
        self._setup_default_roles()

    def _setup_default_roles(self):
        """Default role templates"""
        self.role_templates = {
            "readonly": {
                "max_risk_score": 20,
                "allowed_tools": ["search", "read", "fetch", "query", "list"]
            },
            "analyst": {
                "max_risk_score": 40,
                "allowed_tools": ["search", "read", "fetch", "query",
                                  "list", "report", "summarize", "analyze"]
            },
            "operator": {
                "max_risk_score": 70,
                "allowed_tools": []  # All tools but risk limited
            },
            "admin": {
                "max_risk_score": 100,
                "allowed_tools": []  # Full access
            }
        }

    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        role: str = "readonly",
        owner: str = "unknown",
        allowed_tools: list = None,
        max_risk_score: int = None
    ) -> AgentIdentity:
        template = self.role_templates.get(role, self.role_templates["readonly"])
        identity = AgentIdentity(
            agent_id=agent_id,
            agent_name=agent_name,
            role=role,
            owner=owner,
            allowed_tools=allowed_tools or template["allowed_tools"],
            max_risk_score=max_risk_score or template["max_risk_score"]
        )
        self.agents[agent_id] = identity
        print(f"[Thinguva Sentinel] Agent registered: {agent_name} ({role})")
        return identity

    def get_agent(self, agent_id: str) -> Optional[AgentIdentity]:
        return self.agents.get(agent_id)

    def check_access(
        self,
        agent_id: str,
        tool_name: str,
        risk_score: int
    ) -> tuple:
        identity = self.get_agent(agent_id)
        if not identity:
            return False, "Unknown agent — not registered with Sentinel"

        if not identity.can_use_tool(tool_name):
            return False, (
                f"Agent '{identity.agent_name}' ({identity.role}) "
                f"is not permitted to use tool '{tool_name}'"
            )

        if not identity.can_take_risk(risk_score):
            return False, (
                f"Action risk score {risk_score} exceeds "
                f"agent '{identity.agent_name}' limit of {identity.max_risk_score}"
            )

        return True, "Access granted"