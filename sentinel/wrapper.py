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
            # Check policy
            allowed, reason = self.policy_engine.check(action)
            if not allowed:
                self.audit.log(action, status="BLOCKED", reason=reason)
                raise PermissionError(f"Thinguva Sentinel blocked action: {reason}")

            # Check for loops
            if self.loop_detector.is_loop(action):
                self.audit.log(action, status="LOOP_DETECTED")
                raise RuntimeError("Thinguva Sentinel detected an infinite loop")

            # Log and execute
            self.audit.log(action, status="ALLOWED")
            return agent_func(*args, **kwargs)
        return protected