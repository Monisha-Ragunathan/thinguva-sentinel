from typing import Callable, Any, Optional
from sentinel.audit import AuditLogger
from sentinel.loop_detector import LoopDetector
from sentinel.policy import PolicyEngine
from sentinel.anomaly import AnomalyDetector
from sentinel.human_approval import HumanApprovalSystem
import functools
import time
from sentinel.alerts import AlertSystem

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
        self.require_approval = require_approval
        self.anomaly_detection = anomaly_detection
        self.session_id = str(int(time.time()))

    def monitor(self, tool_name: str):
        """Decorator to monitor any agent tool or function"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                action = {
                    "tool": tool_name,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "session": self.session_id
                }

                # Step 1: Policy check
                allowed, reason = self.policy_engine.check(action)
                if not allowed:
                    self.audit.log(action, status="BLOCKED", reason=reason)
                    raise PermissionError(
                        f"[Thinguva Sentinel] Blocked — {reason}"
                    )

                # Step 2: Loop detection
                if self.loop_detector.is_loop(action):
                    self.audit.log(action, status="LOOP_DETECTED")
                    raise RuntimeError(
                        "[Thinguva Sentinel] Loop detected — agent stopped"
                    )

                # Step 3: Anomaly detection
                if self.anomaly_detection:
                    self.anomaly_detector.observe(action)
                    if self.anomaly_detector.is_anomaly(action):
                        self.audit.log(action, status="ANOMALY", reason="Unusual behavior detected")
                        raise RuntimeError(
                            "[Thinguva Sentinel] Anomaly detected — action flagged"
                        )

                # Step 4: Human approval if required
                if self.require_approval:
                    approved = self.approval_system.request(action)
                    if not approved:
                        self.audit.log(action, status="REJECTED", reason="Human rejected")
                        raise PermissionError(
                            "[Thinguva Sentinel] Action rejected by human"
                        )

                # Step 5: Execute and log
                self.audit.log(action, status="ALLOWED")
                result = func(*args, **kwargs)
                return result

            return wrapper
        return decorator

    def wrap_langchain_tool(self, tool):
        """Wrap a LangChain tool with Sentinel monitoring"""
        original_run = tool._run

        @self.monitor(tool_name=tool.name)
        def monitored_run(*args, **kwargs):
            return original_run(*args, **kwargs)

        tool._run = monitored_run
        return tool