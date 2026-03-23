from typing import Callable, Any
from sentinel.audit import AuditLogger
from sentinel.loop_detector import LoopDetector
from sentinel.policy import PolicyEngine

class SentinelWrapper:
    def __init__(self, policy_file: str = None):
        self.audit = AuditLogger()
        self.loop_detector = LoopDetector()
        self.policy_engine = PolicyEngine(policy_file)

    def wrap(self, agent_func: Callable) -> Callable:
        def protected(*args, **kwargs):
            action = {
                "args": str(args),
                "kwargs": str(kwargs)
            }
            # Step 1: Policy check
            allowed, reason = self.policy_engine.check(action)
            if not allowed:
                self.audit.log(action, status="BLOCKED", reason=reason)
                self.alert_system.alert({
                    "status": "BLOCKED",
                    "tool": tool_name,
                    "reason": reason
                })
                raise PermissionError(
                    f"[Thinguva Sentinel] Blocked — {reason}"
                )

            # Step 2: Loop detection
            if self.loop_detector.is_loop(action):
                self.audit.log(action, status="LOOP_DETECTED")
                self.alert_system.alert({
                    "status": "LOOP_DETECTED",
                    "tool": tool_name,
                    "reason": "Agent repeated same action too many times"
                })
                raise RuntimeError(
                    "[Thinguva Sentinel] Loop detected — agent stopped"
                )

            # Step 3: Anomaly detection
            if self.anomaly_detection:
                self.anomaly_detector.observe(action)
                if self.anomaly_detector.is_anomaly(action):
                    self.audit.log(action, status="ANOMALY", reason="Unusual behavior detected")
                    self.alert_system.alert({
                        "status": "ANOMALY",
                        "tool": tool_name,
                        "reason": "Unusual behavior detected"
                    })
                    raise RuntimeError(
                        "[Thinguva Sentinel] Anomaly detected — action flagged"
                    )

            # Log and execute
            self.audit.log(action, status="ALLOWED")
            return agent_func(*args, **kwargs)
        return protected