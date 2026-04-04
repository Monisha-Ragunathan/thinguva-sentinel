"""
Thinguva Sentinel — Policy Modes
==================================
Three operating modes for different enterprise needs:
🟢 STRICT   — block aggressively
🟡 BALANCED — allow + review
🔵 LEARNING — only log, no blocking
"""

import json
from pathlib import Path
from datetime import datetime

MODES = {
    "strict": {
        "name": "Strict",
        "description": "Block aggressively. Any risk triggers a block.",
        "color": "green",
        "block_threshold": 30,
        "review_threshold": 15,
        "block_on_unknown": True,
        "log_all": True
    },
    "balanced": {
        "name": "Balanced",
        "description": "Block critical, review high, allow low risk.",
        "color": "amber",
        "block_threshold": 80,
        "review_threshold": 40,
        "block_on_unknown": False,
        "log_all": True
    },
    "learning": {
        "name": "Learning",
        "description": "Log everything but never block. Safe for onboarding.",
        "color": "blue",
        "block_threshold": 101,
        "review_threshold": 101,
        "block_on_unknown": False,
        "log_all": True
    }
}

class PolicyModeManager:
    def __init__(self, config_path: str = "policies/mode.json"):
        self.config_path = config_path
        self.current_mode = "balanced"
        self._load()

    def _load(self):
        if Path(self.config_path).exists():
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.current_mode = data.get("mode", "balanced")

    def _save(self):
        Path(self.config_path).parent.mkdir(exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump({
                "mode": self.current_mode,
                "updated_at": datetime.utcnow().isoformat()
            }, f, indent=2)

    def get_mode(self) -> dict:
        mode_config = MODES.get(self.current_mode, MODES["balanced"])
        return {
            "current_mode": self.current_mode,
            **mode_config
        }

    def set_mode(self, mode: str) -> dict:
        if mode not in MODES:
            return {
                "success": False,
                "message": f"Invalid mode. Choose: {list(MODES.keys())}"
            }
        old_mode = self.current_mode
        self.current_mode = mode
        self._save()
        print(f"[Thinguva Sentinel] Mode changed: {old_mode} → {mode}")
        return {
            "success": True,
            "message": f"Mode changed to {mode}",
            "mode": self.get_mode()
        }

    def get_all_modes(self) -> dict:
        return {
            "current": self.current_mode,
            "modes": MODES
        }

    def apply_mode_to_decision(
        self,
        risk_score: int,
        original_decision: str
    ) -> dict:
        """Apply current mode to override decisions"""
        mode = MODES.get(self.current_mode, MODES["balanced"])

        if self.current_mode == "learning":
            return {
                "decision": "ALLOW",
                "mode_override": True,
                "reason": "Learning mode — logging only, no blocking"
            }

        if risk_score >= mode["block_threshold"]:
            decision = "BLOCK"
        elif risk_score >= mode["review_threshold"]:
            decision = "REVIEW"
        else:
            decision = "ALLOW"

        mode_override = decision != original_decision
        return {
            "decision": decision,
            "mode_override": mode_override,
            "reason": f"{mode['name']} mode applied" if mode_override else ""
        }