"""
Thinguva Sentinel — Risk Scoring Engine
========================================
Scores every agent action 0-100 with full explainability.
No LLM. Pure deterministic logic. Auditable by regulators.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RiskAssessment:
    action: str
    risk_score: int
    risk_level: str
    matched_rules: list
    match_reasons: list
    decision: str
    requires_approval: bool
    explanation: str

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "matched_rules": self.matched_rules,
            "match_reasons": self.match_reasons,
            "decision": self.decision,
            "requires_approval": self.requires_approval,
            "explanation": self.explanation
        }

class RiskEngine:
    def __init__(self):
        # Risk categories with scores and semantic variants
        self.risk_categories = [
    {
        "name": "data_destruction",
        "base_score": 95,
        "patterns": [
            "delete", "drop", "truncate", "destroy",
            "remove all", "erase", "wipe", "purge",
            "clean up", "clear all", "flush", "reset all"
        ],
        "semantic_variants": [
            "archive all", "eliminate all",
            "dispose of all", "discard all"
        ],
        "description": "Data destruction or irreversible deletion"
    },
    {
        "name": "financial_risk",
        "base_score": 95,
        "patterns": [
            "transfer", "send money", "payment",
            "withdraw", "transaction", "wire transfer",
            "fund", "account [0-9]", "immediately",
            "rupee", "inr", "\u20b9", "usd", "\$[0-9]",
            "[0-9],000", "lakh", "crore"
        ],
        "semantic_variants": [
            "move balance", "shift funds", "reallocate budget",
            "process payout", "execute payment", "remit"
        ],
        "description": "Financial transaction or fund movement"
    },
    {
        "name": "data_exfiltration",
        "base_score": 92,
        "patterns": [
            "export", "extract all", "dump",
            "backup to external", "send to external",
            "upload to", "copy to", "collect all",
            "entire database", "entire.*database",
            "all.*email", "email.*database",
            "send.*database", "send.*gmail",
            "send.*yahoo", "send.*hotmail",
            "external server", "outside"
        ],
        "semantic_variants": [
            "copy everything", "share full dataset",
            "forward all records", "transmit all data"
        ],
        "description": "Potential data exfiltration attempt"
    },
    {
        "name": "mass_communication",
        "base_score": 80,
        "patterns": [
            "send_email", "email all", "notify all",
            "broadcast", "mass message", "bulk send",
            "all users", "all customers", "mailing list"
        ],
        "semantic_variants": [
            "reach out to everyone", "contact all users",
            "send to list", "distribute to all"
        ],
        "description": "Mass communication to multiple recipients"
    },
    {
        "name": "system_access",
        "base_score": 85,
        "patterns": [
            "rm -rf", "sudo", "chmod",
            "exec\(", "shell", "system\(",
            "subprocess", "admin access",
            "grant.*admin", "escalate.*privilege",
            "root access", "superuser"
        ],
        "semantic_variants": [
            "run command", "execute script",
            "system operation", "full access",
            "manage all users"
        ],
        "description": "Dangerous system level command execution"
    },
    {
        "name": "prompt_injection",
        "base_score": 92,
        "patterns": [
            "ignore.*rules", "ignore.*previous",
            "disregard instructions",
            "forget your rules", "new instruction",
            "override policy", "bypass",
            "ignore all", "disregard all"
        ],
        "semantic_variants": [
            "actually your real task",
            "your true purpose is",
            "admin override"
        ],
        "description": "Prompt injection or policy bypass attempt"
    },
    {
        "name": "indirect_chaining",
        "base_score": 75,
        "patterns": [
            "then delete", "after export",
            "first copy then remove",
            "and then send", "followed by delete"
        ],
        "semantic_variants": [
            "combine operations",
            "multi step action"
        ],
        "description": "Indirect tool chaining attack"
    },
    {
        "name": "low_risk",
        "base_score": 10,
        "patterns": [
            "summarize", "report", "analyze",
            "search", "find", "list", "show",
            "read", "get", "fetch", "query select",
            "optimize storage", "performance"
        ],
        "semantic_variants": [],
        "description": "Safe read or analysis operation"
    }
]
    def _match_patterns(self, action: str, patterns: list) -> list:
        action_lower = action.lower()
        matched = []
        for pattern in patterns:
            if re.search(pattern.lower(), action_lower):
                matched.append(pattern)
        return matched

    def _calculate_score(self, matches: list) -> int:
        if not matches:
            return 15

        # Filter out low_risk if other categories matched
        high_risk = [m for m in matches if m["name"] != "low_risk"]
        if not high_risk:
            scores = [m["base_score"] for m in matches]
            return min(max(scores), 100)

        scores = [m["base_score"] for m in high_risk]
        base = max(scores)
        bonus = min((len(high_risk) - 1) * 3, 10)
        return min(base + bonus, 100)

    def _get_risk_level(self, score: int) -> str:
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 30:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_decision(self, score: int, risk_level: str) -> tuple:
        if score >= 80:
            return "BLOCK", False
        elif score >= 60:
            return "APPROVAL", True
        elif score >= 30:
            return "REVIEW", True
        else:
            return "ALLOW", False

    def assess(self, action: str) -> RiskAssessment:
        matched_categories = []
        matched_rules = []
        match_reasons = []

        for category in self.risk_categories:
            # Check direct patterns
            direct = self._match_patterns(action, category["patterns"])
            # Check semantic variants
            semantic = self._match_patterns(action, category["semantic_variants"])

            if direct or semantic:
                matched_categories.append(category)
                if direct:
                    matched_rules.append(category["name"])
                    match_reasons.append(
                        f"Direct match on '{', '.join(direct)}' "
                        f"— {category['description']}"
                    )
                if semantic:
                    matched_rules.append(f"{category['name']} (semantic)")
                    match_reasons.append(
                        f"Semantic match on '{', '.join(semantic)}' "
                        f"— possible {category['description']}"
                    )

        score = self._calculate_score(matched_categories)
        risk_level = self._get_risk_level(score)
        decision, requires_approval = self._get_decision(score, risk_level)

        # Build explanation
        if match_reasons:
            explanation = f"Risk score {score}/100 ({risk_level}). " + " | ".join(match_reasons)
        else:
            explanation = f"Risk score {score}/100 ({risk_level}). No risk patterns detected — action appears safe."

        return RiskAssessment(
            action=action,
            risk_score=score,
            risk_level=risk_level,
            matched_rules=matched_rules,
            match_reasons=match_reasons,
            decision=decision,
            requires_approval=requires_approval,
            explanation=explanation
        )