from typing import Callable, Any, Optional
from sentinel.audit import AuditLogger
from sentinel.loop_detector import LoopDetector
from sentinel.policy import PolicyEngine
from sentinel.anomaly import AnomalyDetector
from sentinel.human_approval import HumanApprovalSystem
from sentinel.alerts import AlertSystem
from sentinel.risk_engine import RiskEngine
from sentinel.semantic_matcher import SemanticMatcher
from sentinel.identity import IdentityManager
import functools
import time

class AgentIntegration:
    def __init__(
        self,
        policy_file: str = None,
        require_approval: bool = False,
        anomaly_detection: bool = True,
        slack_webhook: str = None,
        webhook_url: str = None,
        email_config: dict = None
    ):
        self.audit = AuditLogger()
        self.loop_detector = LoopDetector()
        self.policy_engine = PolicyEngine(policy_file)
        self.anomaly_detector = AnomalyDetector()
        self.approval_system = HumanApprovalSystem()
        self.alert_system = AlertSystem(
            slack_webhook=slack_webhook,
            webhook_url=webhook_url,
            email_config=email_config
        )
        self.risk_engine = RiskEngine()
        self.semantic_matcher = SemanticMatcher()
        self.identity_manager = IdentityManager()
        self.require_approval = require_approval
        self.anomaly_detection = anomaly_detection
        self.session_id = str(int(time.time()))

    def register_agent(self, agent_id: str, agent_name: str, role: str = "readonly", owner: str = "unknown"):
        return self.identity_manager.register_agent(
            agent_id=agent_id,
            agent_name=agent_name,
            role=role,
            owner=owner
        )

    def monitor(self, tool_name: str, agent_id: str = None):
        """Decorator to monitor any agent tool or function"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                action_str = f"{tool_name}: {str(args)} {str(kwargs)}"
                action = {
                    "tool": tool_name,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "session": self.session_id,
                    "agent_id": agent_id or "unregistered"
                }

                # Step 1: Risk assessment
                assessment = self.risk_engine.assess(action_str)
                action["risk_score"] = assessment.risk_score
                action["risk_level"] = assessment.risk_level
                action["matched_rules"] = str(assessment.matched_rules)
                action["explanation"] = assessment.explanation

                # Step 2: Semantic threat detection
                is_threat, threat_reasons = self.semantic_matcher.is_semantic_threat(action_str)
                if is_threat:
                    reason = f"Semantic threat detected: {'; '.join(threat_reasons)}"
                    self.audit.log(action, status="BLOCKED", reason=reason)
                    self.alert_system.alert({
                        "status": "BLOCKED",
                        "tool": tool_name,
                        "reason": reason,
                        "risk_score": assessment.risk_score
                    })
                    raise PermissionError(f"[Thinguva Sentinel] {reason}")

                # Step 3: Identity & RBAC check
                if agent_id:
                    access_ok, access_reason = self.identity_manager.check_access(
                        agent_id, tool_name, assessment.risk_score
                    )
                    if not access_ok:
                        self.audit.log(action, status="BLOCKED", reason=access_reason)
                        raise PermissionError(f"[Thinguva Sentinel] {access_reason}")

                # Step 4: Policy check
                allowed, reason = self.policy_engine.check(action)
                if not allowed:
                    self.audit.log(action, status="BLOCKED", reason=reason)
                    self.alert_system.alert({
                        "status": "BLOCKED",
                        "tool": tool_name,
                        "reason": reason,
                        "risk_score": assessment.risk_score
                    })
                    raise PermissionError(f"[Thinguva Sentinel] Blocked — {reason}")

                # Step 5: Loop detection
                if self.loop_detector.is_loop(action):
                    self.audit.log(action, status="LOOP_DETECTED")
                    self.alert_system.alert({
                        "status": "LOOP_DETECTED",
                        "tool": tool_name,
                        "reason": "Agent repeated same action too many times"
                    })
                    raise RuntimeError("[Thinguva Sentinel] Loop detected — agent stopped")

                # Step 6: Anomaly detection
                if self.anomaly_detection:
                    self.anomaly_detector.observe(action)
                    if self.anomaly_detector.is_anomaly(action):
                        self.audit.log(action, status="ANOMALY", reason="Unusual behavior detected")
                        self.alert_system.alert({
                            "status": "ANOMALY",
                            "tool": tool_name,
                            "reason": "Unusual behavior detected"
                        })
                        raise RuntimeError("[Thinguva Sentinel] Anomaly detected")

                # Step 7: High risk needs approval
                if assessment.risk_level in ["HIGH", "CRITICAL"] and self.require_approval:
                    approved = self.approval_system.request(action)
                    if not approved:
                        self.audit.log(action, status="REJECTED", reason="Human rejected high risk action")
                        raise PermissionError("[Thinguva Sentinel] High risk action rejected by human")

                # Step 8: Execute and log
                self.audit.log(action, status="ALLOWED")
                return func(*args, **kwargs)

            return wrapper
        return decorator

    def wrap_langchain_tool(self, tool):
        original_run = tool._run

        @self.monitor(tool_name=tool.name)
        def monitored_run(*args, **kwargs):
            return original_run(*args, **kwargs)

        tool._run = monitored_run
        return tool

    def assess(self, action: str) -> dict:
        """Assess any action and return full risk report"""
        assessment = self.risk_engine.assess(action)
        is_threat, threat_reasons = self.semantic_matcher.is_semantic_threat(action)
        return {
            **assessment.to_dict(),
            "semantic_threats": threat_reasons
        }