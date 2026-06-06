"""
Thinguva Sentinel — Plugin/Hook System
========================================
Add Thinguva Sentinel to ANY existing system
with pre and post action hooks.
One line of code. Maximum adoption.

Usage:
    from sentinel.hooks import SentinelHooks

    hooks = SentinelHooks(policy_file="policies/sample.yaml")

    @hooks.before_action
    def my_agent_tool(input):
        return do_something(input)
"""

from typing import Callable, Any, Optional
from datetime import datetime
from sentinel.agent_integration import AgentIntegration
from sentinel.compliance_mapper import ComplianceMapper
from sentinel.destination_intel import DestinationIntel

class SentinelHooks:
    def __init__(
        self,
        policy_file: str = None,
        on_block: Optional[Callable] = None,
        on_allow: Optional[Callable] = None,
        on_anomaly: Optional[Callable] = None,
        strict_mode: bool = False
    ):
        self.sentinel = AgentIntegration(policy_file=policy_file)
        self.compliance = ComplianceMapper()
        self.destination = DestinationIntel()
        self.on_block = on_block
        self.on_allow = on_allow
        self.on_anomaly = on_anomaly
        self.strict_mode = strict_mode
        self.hook_log = []

    def before_action(self, func: Callable) -> Callable:
        """
        Decorator — runs Sentinel check BEFORE function executes.
        Blocks execution if action is dangerous.

        Usage:
            @hooks.before_action
            def my_tool(input):
                return process(input)
        """
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            action_str = f"{func.__name__}: {str(args)} {str(kwargs)}"

            # Run assessment
            assessment = self.sentinel.assess(action_str)
            decision = assessment["decision"]
            risk_score = assessment["risk_score"]

            # Log the hook
            self.hook_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "hook": "before_action",
                "function": func.__name__,
                "action": action_str,
                "decision": decision,
                "risk_score": risk_score
            })

            if decision == "BLOCK":
                if self.on_block:
                    self.on_block(action_str, assessment)
                raise PermissionError(
                    f"[Thinguva Sentinel] Blocked '{func.__name__}': "
                    f"{assessment['explanation']}"
                )

            if self.on_allow:
                self.on_allow(action_str, assessment)

            return func(*args, **kwargs)
        return wrapper

    def after_action(self, func: Callable) -> Callable:
        """
        Decorator — runs Sentinel audit AFTER function executes.
        Logs result without blocking.

        Usage:
            @hooks.after_action
            def my_tool(input):
                return process(input)
        """
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            action_str = f"{func.__name__}: result={str(result)[:100]}"

            assessment = self.sentinel.assess(action_str)
            self.hook_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "hook": "after_action",
                "function": func.__name__,
                "result_preview": str(result)[:100],
                "risk_score": assessment["risk_score"]
            })

            if assessment["risk_score"] > 70 and self.on_anomaly:
                self.on_anomaly(action_str, assessment)

            return result
        return wrapper

    def protect(self, func: Callable) -> Callable:
        """
        Full protection — before AND after hooks combined.
        Most comprehensive option.

        Usage:
            @hooks.protect
            def my_tool(input):
                return process(input)
        """
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            action_str = f"{func.__name__}: {str(args)}"
            assessment = self.sentinel.assess(action_str)

            # Pre-execution check
            if assessment["decision"] == "BLOCK":
                if self.on_block:
                    self.on_block(action_str, assessment)
                raise PermissionError(
                    f"[Thinguva Sentinel] Blocked '{func.__name__}'"
                )

            # Execute
            result = func(*args, **kwargs)

            # Post-execution audit
            self.hook_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "hook": "protect",
                "function": func.__name__,
                "decision": assessment["decision"],
                "risk_score": assessment["risk_score"],
                "result_preview": str(result)[:100]
            })

            return result
        return wrapper

    def check(self, action: str) -> dict:
        """
        Direct check without decorator.
        Use when you need programmatic access.

        Usage:
            result = hooks.check("delete all records")
            if result["safe"]:
                execute()
        """
        assessment = self.sentinel.assess(action)
        compliance = self.compliance.map_action(action)
        destination = self.destination.analyze(action)

        return {
            "safe": assessment["decision"] == "ALLOW",
            "decision": assessment["decision"],
            "risk_score": assessment["risk_score"],
            "risk_level": assessment["risk_level"],
            "explanation": assessment["explanation"],
            "compliance_violations": compliance["violations_found"],
            "compliance_summary": compliance["summary"],
            "destination_risk": destination["highest_risk"],
            "destination_summary": destination["summary"],
            "blocked": assessment["decision"] == "BLOCK"
        }

    def get_hook_log(self) -> list:
        return self.hook_log

    def clear_log(self):
        self.hook_log = []