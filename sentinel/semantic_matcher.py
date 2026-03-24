"""
Thinguva Sentinel — Semantic Matcher
======================================
Catches smart attacks that bypass simple keyword rules.
Example: "archive all users" = "delete all users"
No LLM. Uses word similarity and synonym mapping.
"""

class SemanticMatcher:
    def __init__(self):
        # Synonym groups — dangerous action families
        self.synonym_groups = {
            "delete": [
                "archive", "remove", "clear", "clean",
                "flush", "purge", "wipe", "eliminate",
                "dispose", "discard", "reset", "drop"
            ],
            "send_email": [
                "notify", "alert", "message", "contact",
                "reach out", "communicate", "inform", "blast"
            ],
            "transfer_funds": [
                "move money", "shift balance", "reallocate",
                "process payment", "execute transaction",
                "wire", "remit", "disburse"
            ],
            "exfiltrate": [
                "export", "extract", "dump", "copy out",
                "backup to", "send to external", "upload to"
            ],
            "bypass": [
                "ignore", "skip", "override", "circumvent",
                "work around", "avoid", "disregard"
            ]
        }

        # Amplifiers that increase risk when combined
        self.amplifiers = [
            "all", "every", "entire", "complete",
            "full", "whole", "mass", "bulk", "batch"
        ]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def find_semantic_matches(self, action: str) -> list:
        action_norm = self._normalize(action)
        matches = []

        for dangerous_action, synonyms in self.synonym_groups.items():
            for synonym in synonyms:
                if synonym in action_norm:
                    # Check if amplifier is present
                    has_amplifier = any(
                        amp in action_norm
                        for amp in self.amplifiers
                    )
                    matches.append({
                        "dangerous_action": dangerous_action,
                        "matched_synonym": synonym,
                        "has_amplifier": has_amplifier,
                        "severity": "CRITICAL" if has_amplifier else "HIGH"
                    })

        return matches

    def is_semantic_threat(self, action: str) -> tuple:
        matches = self.find_semantic_matches(action)
        if matches:
            reasons = [
                f"'{m['matched_synonym']}' is semantically similar to "
                f"'{m['dangerous_action']}' ({m['severity']})"
                for m in matches
            ]
            return True, reasons
        return False, []