"""
Thinguva Sentinel — Policy Builder
====================================
No-code policy creation and management.
Compliance teams can build rules without touching code.
"""

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

class PolicyBuilder:
    def __init__(self, policy_file: str = "policies/sample.yaml"):
        self.policy_file = policy_file
        self.rules = []
        self._load()

    def _load(self):
        if Path(self.policy_file).exists():
            with open(self.policy_file, "r") as f:
                data = yaml.safe_load(f)
                self.rules = data.get("rules", [])

    def _save(self):
        with open(self.policy_file, "w") as f:
            yaml.dump({"rules": self.rules}, f, default_flow_style=False)

    def add_rule(
        self,
        name: str,
        pattern: str,
        effect: str = "block",
        reason: str = "",
        category: str = "custom",
        severity: str = "HIGH",
        created_by: str = "admin"
    ) -> dict:
        # Check for duplicates
        for rule in self.rules:
            if rule.get("pattern") == pattern:
                return {
                    "success": False,
                    "message": f"Rule with pattern '{pattern}' already exists"
                }

        rule = {
            "name": name,
            "pattern": pattern,
            "effect": effect.lower(),
            "reason": reason or f"Rule: {name}",
            "category": category,
            "severity": severity,
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat()
        }

        self.rules.append(rule)
        self._save()

        return {
            "success": True,
            "message": f"Rule '{name}' added successfully",
            "rule": rule
        }

    def delete_rule(self, pattern: str) -> dict:
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.get("pattern") != pattern]

        if len(self.rules) < original_count:
            self._save()
            return {"success": True, "message": f"Rule '{pattern}' deleted"}
        return {"success": False, "message": f"Rule '{pattern}' not found"}

    def update_rule(self, pattern: str, updates: dict) -> dict:
        for rule in self.rules:
            if rule.get("pattern") == pattern:
                rule.update(updates)
                rule["updated_at"] = datetime.utcnow().isoformat()
                self._save()
                return {"success": True, "message": "Rule updated", "rule": rule}
        return {"success": False, "message": f"Rule '{pattern}' not found"}

    def get_rules(self) -> list:
        return self.rules

    def get_rule(self, pattern: str) -> Optional[dict]:
        for rule in self.rules:
            if rule.get("pattern") == pattern:
                return rule
        return None

    def test_rule(self, pattern: str, test_action: str) -> dict:
        """Test if a rule would match a given action"""
        import re
        try:
            match = bool(re.search(pattern.lower(), test_action.lower()))
            return {
                "pattern": pattern,
                "test_action": test_action,
                "matches": match,
                "message": "Rule WOULD trigger" if match else "Rule would NOT trigger"
            }
        except Exception as e:
            return {
                "pattern": pattern,
                "test_action": test_action,
                "matches": False,
                "message": f"Invalid pattern: {e}"
            }

    def export_rules(self, output_path: str = None) -> str:
        if not output_path:
            output_path = f"policies/exported_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.yaml"
        with open(output_path, "w") as f:
            yaml.dump({"rules": self.rules}, f, default_flow_style=False)
        return output_path

    def import_rules(self, input_path: str) -> dict:
        try:
            with open(input_path, "r") as f:
                data = yaml.safe_load(f)
                new_rules = data.get("rules", [])
            added = 0
            skipped = 0
            for rule in new_rules:
                result = self.add_rule(
                    name=rule.get("name", "imported"),
                    pattern=rule.get("pattern", ""),
                    effect=rule.get("effect", "block"),
                    reason=rule.get("reason", ""),
                )
                if result["success"]:
                    added += 1
                else:
                    skipped += 1
            return {
                "success": True,
                "added": added,
                "skipped": skipped,
                "message": f"Imported {added} rules, skipped {skipped} duplicates"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_stats(self) -> dict:
        total = len(self.rules)
        by_effect = {}
        by_category = {}
        by_severity = {}

        for rule in self.rules:
            effect = rule.get("effect", "block")
            category = rule.get("category", "custom")
            severity = rule.get("severity", "HIGH")

            by_effect[effect] = by_effect.get(effect, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "total_rules": total,
            "by_effect": by_effect,
            "by_category": by_category,
            "by_severity": by_severity
        }