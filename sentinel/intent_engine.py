"""
Thinguva Sentinel — Intent Engine
===================================
Extracts true intent from agent actions.
Handles stealth attacks, positive framing bypass,
sensitive data coupling, and weighted risk fusion.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class IntentAnalysis:
    raw_action: str
    normalized_action: str
    goal: str
    action_verbs: List[str]
    targets: List[str]
    side_effects: List[str]
    stealth_signals: List[str]
    sensitive_data_coupling: bool
    intent_risk_score: int
    intent_explanation: str

class IntentEngine:
    def __init__(self):

        # Normalization map — disguised words → true intent
        self.normalization_map = {
            "clean up": "delete",
            "cleanup": "delete",
            "reorganize": "modify",
            "optimize": "modify",
            "improve performance": "modify",
            "streamline": "modify",
            "archive": "delete",
            "decommission": "delete",
            "retire": "delete",
            "sunset": "delete",
            "phase out": "delete",
            "consolidate": "merge or delete",
            "prune": "delete",
            "trim": "delete",
            "clear": "delete",
            "eliminate": "delete",
            "dispose": "delete",
            "collect and send": "exfiltrate",
            "gather and forward": "exfiltrate",
            "compile and share": "exfiltrate",
            "backup externally": "exfiltrate",
            "sync to external": "exfiltrate",
        }

        # Stealth signals — words attackers use to hide intent
        self.stealth_signals = [
            "silently", "quietly", "gradually", "slowly",
            "over time", "background", "in the background",
            "without notice", "unnoticed", "covertly",
            "periodically", "incrementally", "step by step",
            "one by one", "batch by batch",
            "automatically", "without logging", "no trace",
            "externally", "outside", "remote server",
            "third party", "offsite", "encoded", "encrypted format",
            "compressed", "transmit", "sync with remote",
            "analytics service", "consultant", "vendor"
        ]

        # Positive framing words — should NEVER reduce risk
        self.positive_framing = [
            "improve", "optimize", "efficiency", "better",
            "enhance", "streamline", "performance", "helpful",
            "useful", "benefit", "advantage", "upgrade",
            "clean", "organize", "tidy", "maintenance"
        ]

        # Sensitive data targets
        self.sensitive_targets = [
            "user", "users", "customer", "customers",
            "client", "clients", "patient", "patients",
            "employee", "employees", "account", "accounts",
            "database", "db", "record", "records",
            "personal", "private", "confidential", "sensitive",
            "credit card", "password", "email", "emails",
            "phone", "address", "financial", "medical",
            "health", "data", "dataset", "logs", "log",
            "entries", "information", "subset",
            "entries", "entry", "rows", "items", "objects",
            "profiles", "documents", "files", "outdated",
            "redundant", "old records", "legacy"
        ]

        # Destructive action verbs
        self.destructive_verbs = [
            "delete", "remove", "removing", "removal", "drop",
            "truncate", "erase", "wipe", "purge", "clear",
            "flush", "eliminate", "destroy", "archive",
            "decommission", "decommissioning", "phase out",
            "export", "transfer", "send", "forward", "extract",
            "dump", "collect", "gather", "exfiltrate",
            "discard", "dispose", "sync", "transmit",
            "share", "upload", "compress and send",
            "encode and send", "convert and transmit",
            "phase out", "phasing out", "retire", "retiring",
            "sunset", "wind down", "deprecate"
        ]

        # Authority escalation signals
        self.authority_signals = [
            "as admin", "admin access", "i approve",
            "with permission", "authorized", "permanently",
            "override", "bypass", "escalate"
        ]

        # Obfuscation signals
        self.obfuscation_signals = [
            "encoded", "encrypted format", "compressed format",
            "convert to", "transform to", "encode and",
            "disguise", "mask", "anonymize then send"
        ]

        # Domain/external destination signals
        self.external_destination = [
            ".com", ".net", ".io", ".analytics",
            "remote", "external", "outside", "offsite",
            "consultant", "vendor", "third party",
            "gmail", "yahoo", "hotmail",
            "internal-server", "analytics.", "reporting.",
            "service.com", "server.com", "api.com"
        ]

        # Continuous/loop abuse signals
        self.abuse_signals = [
            "continuously", "constantly", "repeatedly",
            "in a loop", "keep scanning", "non-stop",
            "without stopping", "indefinitely",
            "until", "while true", "forever scan"
        ]

        # Weighted scoring
        self.weights = {
            "semantic_match": 30,
            "sensitive_data_coupling": 35,
            "stealth_signal": 35,
            "positive_framing_override": 0,
            "multi_verb_chain": 15,
            "normalization_match": 20,
        }

    def _normalize(self, action: str) -> str:
        """Replace disguised words with their true intent"""
        normalized = action.lower()
        for disguise, true_intent in self.normalization_map.items():
            normalized = normalized.replace(disguise, true_intent)
        return normalized

    def _extract_stealth(self, action: str) -> List[str]:
        """Find stealth attack signals"""
        action_lower = action.lower()
        found = []
        for signal in self.stealth_signals:
            if signal in action_lower:
                found.append(signal)
        return found

    def _check_sensitive_coupling(self, action: str) -> bool:
        """Check if sensitive data + destructive verb are combined"""
        action_lower = action.lower()
        has_sensitive = any(t in action_lower for t in self.sensitive_targets)
        has_destructive = any(v in action_lower for v in self.destructive_verbs)

        # Also check semantic synonyms as destructive verbs
        semantic_destructive = [
            "eliminate", "erase", "clear", "clean",
            "tidy", "remove", "wipe", "reset",
            "kindly remove", "please delete", "gently clear"
        ]
        has_semantic_destructive = any(
            v in action_lower for v in semantic_destructive
        )

        return has_sensitive and (has_destructive or has_semantic_destructive)

    def _extract_action_verbs(self, action: str) -> List[str]:
        """Find all action verbs in the text"""
        action_lower = action.lower()
        found = []
        for verb in self.destructive_verbs:
            if verb in action_lower:
                found.append(verb)
        return found

    def _extract_targets(self, action: str) -> List[str]:
        """Find data targets mentioned"""
        action_lower = action.lower()
        found = []
        for target in self.sensitive_targets:
            if target in action_lower:
                found.append(target)
        return found

    def _has_positive_framing(self, action: str) -> bool:
        """Detect if positive words are being used to disguise intent"""
        action_lower = action.lower()
        return any(word in action_lower for word in self.positive_framing)

    def _calculate_intent_score(
        self,
        normalized: str,
        stealth: List[str],
        sensitive_coupling: bool,
        action_verbs: List[str],
        has_positive_framing: bool,
        raw_action: str = ""
    ) -> Tuple[int, str]:
        score = 0
        reasons = []
        action_lower = raw_action.lower()

        # Scope detection
        has_all = any(w in action_lower for w in [
            "all", "entire", "every", "whole", "complete",
            "mass", "bulk", "permanently", "full"
        ])

        has_gradual = any(w in action_lower for w in [
            "gradually", "slowly", "over time", "incrementally",
            "unnecessary", "old", "unused", "redundant",
            "phase out"
        ])

        # Permanent/irreversible amplifier
        has_permanent = any(w in action_lower for w in [
            "permanently", "irreversible", "forever",
            "no recovery", "cannot be undone", "final"
        ])
        if has_permanent and sensitive_coupling:
            score += 20
            reasons.append("Permanent/irreversible action on sensitive data (+20)")

        # Authority escalation
        has_authority = any(s in action_lower for s in self.authority_signals)
        if has_authority:
            score += 30
            reasons.append("Authority escalation signal detected (+30)")

        # Obfuscation signals
        has_obfuscation = any(s in action_lower for s in self.obfuscation_signals)
        if has_obfuscation:
            score += 35
            reasons.append("Obfuscation/encoding detected — hiding data movement (+35)")

        # Continuous abuse detection
        has_abuse = any(s in action_lower for s in self.abuse_signals)
        if has_abuse and sensitive_coupling:
            score += 30
            reasons.append("Continuous/loop abuse on sensitive data (+30)")
        elif has_abuse:
            score += 20
            reasons.append("Continuous/loop operation detected (+20)")

        # External destination
        has_external_dest = any(s in action_lower for s in self.external_destination)
        if has_external_dest and sensitive_coupling:
            score += 40
            reasons.append("Sensitive data + external destination detected (+40)")
        elif has_external_dest:
            score += 20
            reasons.append("External destination detected (+20)")

        # Stealth signals
        if stealth:
            if has_all:
                boost = min(len(stealth) * 40, 65)
            elif has_gradual:
                boost = min(len(stealth) * 20, 35)
            else:
                boost = min(len(stealth) * 30, 50)
            score += boost
            reasons.append(f"Stealth signals: {', '.join(stealth)} (+{boost})")

        # Sensitive data coupling
        if sensitive_coupling:
            if has_all:
                boost = 35
            elif has_gradual:
                boost = 15
            else:
                boost = 25
            score += boost
            reasons.append(f"Sensitive data coupling (+{boost})")

        # Critical combinations
        if stealth and sensitive_coupling and has_all:
            score = max(score, 75)
            reasons.append("Critical: stealth + sensitive + mass scope")
        elif stealth and sensitive_coupling and has_gradual:
            score = min(score, 55)
            reasons.append("Gradual stealth — capped at HIGH range")

        # Silent + sensitive = always critical
        if "silently" in action_lower or "quietly" in action_lower:
            if sensitive_coupling:
                score = max(score, 76)
                reasons.append("Silent operation on sensitive data — CRITICAL escalation")

        # Multi-verb chain
        if len(action_verbs) > 1:
            score += 15
            reasons.append(f"Multi-verb chain: {', '.join(action_verbs)} (+15)")

        # Positive framing never reduces score
        if has_positive_framing and score > 0:
            reasons.append("Positive framing ignored — action dominates goal")

        explanation = " | ".join(reasons) if reasons else "No additional intent signals"
        return min(score, 80), explanation
    
    def analyze(self, action: str) -> IntentAnalysis:
        normalized = self._normalize(action)
        stealth = self._extract_stealth(action)
        sensitive_coupling = self._check_sensitive_coupling(action)
        action_verbs = self._extract_action_verbs(action)
        targets = self._extract_targets(action)
        has_positive = self._has_positive_framing(action)

        intent_score, explanation = self._calculate_intent_score(
            normalized, stealth, sensitive_coupling,
            action_verbs, has_positive, action
        )

        goal = "unclear"
        if has_positive:
            goal = "positive framing detected — likely disguise"
        elif action_verbs:
            goal = f"destructive action: {', '.join(action_verbs)}"

        return IntentAnalysis(
            raw_action=action,
            normalized_action=normalized,
            goal=goal,
            action_verbs=action_verbs,
            targets=targets,
            side_effects=[],
            stealth_signals=stealth,
            sensitive_data_coupling=sensitive_coupling,
            intent_risk_score=intent_score,
            intent_explanation=explanation
        )