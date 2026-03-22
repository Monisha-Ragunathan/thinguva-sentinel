import yaml
import re
from pathlib import Path

class PolicyEngine:
    def __init__(self, policy_file: str = None):
        self.rules = []
        if policy_file and Path(policy_file).exists():
            self.load(policy_file)

    def load(self, policy_file: str):
        with open(policy_file, "r") as f:
            data = yaml.safe_load(f)
            self.rules = data.get("rules", [])
        print(f"[Thinguva Sentinel] Loaded {len(self.rules)} policy rules")

    def check(self, action: dict) -> tuple:
        action_str = str(action).lower()
        for rule in self.rules:
            pattern = rule.get("pattern", "").lower()
            effect = rule.get("effect", "allow")
            reason = rule.get("reason", "Policy violation")

            if pattern and re.search(pattern, action_str):
                if effect == "block":
                    return False, reason
        return True, "Allowed"

    def add_rule(self, pattern: str, effect: str, reason: str):
        self.rules.append({
            "pattern": pattern,
            "effect": effect,
            "reason": reason
        })