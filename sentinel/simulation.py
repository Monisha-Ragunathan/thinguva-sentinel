"""
Thinguva Sentinel — Simulation Mode
=====================================
"What would happen if agent runs this?"
No execution. Pure risk analysis.
Perfect for demos, testing, and pre-deployment checks.
"""

from datetime import datetime
from sentinel.agent_integration import AgentIntegration
from typing import Optional

class SimulationEngine:
    def __init__(self, policy_file: str = None):
        self.sentinel = AgentIntegration(policy_file=policy_file)
        self.simulation_history = []

    def simulate(self, action: str, agent_id: str = None) -> dict:
        """
        Simulate what would happen if agent runs this action.
        No execution — pure risk analysis.
        """
        assessment = self.sentinel.assess(action)

        result = {
            "mode": "SIMULATION",
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "agent_id": agent_id or "anonymous",
            "risk_score": assessment["risk_score"],
            "risk_level": assessment["risk_level"],
            "decision": assessment["decision"],
            "would_execute": assessment["decision"] == "ALLOW",
            "safe_to_run": assessment["risk_score"] < 30,
            "requires_approval": assessment["requires_approval"],
            "explanation": assessment["explanation"],
            "matched_rules": assessment["matched_rules"],
            "semantic_threats": assessment["semantic_threats"],
            "intent_analysis": assessment["intent_analysis"],
            "recommendation": self._get_recommendation(assessment),
            "alternatives": self._get_alternatives(action, assessment)
        }

        self.simulation_history.append(result)
        return result

    def _get_recommendation(self, assessment: dict) -> str:
        score = assessment["risk_score"]
        decision = assessment["decision"]

        if decision == "ALLOW":
            return "Safe to execute — no policy violations detected"
        elif decision == "REVIEW":
            return "Review recommended before execution — medium risk detected"
        elif decision == "APPROVAL":
            return "Human approval required before execution — high risk action"
        else:
            return "Do NOT execute — critical risk detected. Redesign the action."

    def _get_alternatives(self, action: str, assessment: dict) -> list:
        """Suggest safer alternatives based on detected risks"""
        alternatives = []
        action_lower = action.lower()

        if "delete" in action_lower or "remove" in action_lower:
            alternatives.append("Consider soft-delete: mark as inactive instead")
            alternatives.append("Archive with retention policy instead of deletion")

        if "export" in action_lower or "send" in action_lower:
            alternatives.append("Use internal secure transfer instead of external")
            alternatives.append("Apply data masking before export")

        if "all" in action_lower:
            alternatives.append("Process in smaller batches with approval per batch")
            alternatives.append("Add specific filters to limit scope")

        if not alternatives:
            alternatives.append("Action appears safe — no alternatives needed")

        return alternatives

    def simulate_sequence(self, actions: list, agent_id: str = None) -> dict:
        """
        Simulate a sequence of actions — detects escalation patterns.
        Example: read → compress → send externally = escalation
        """
        results = []
        max_score = 0
        escalation_detected = False
        previous_score = 0

        for i, action in enumerate(actions):
            result = self.simulate(action, agent_id)
            results.append({
                "step": i + 1,
                "action": action,
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "decision": result["decision"]
            })

            # Detect escalation — each step getting riskier
            if result["risk_score"] > previous_score + 20:
                escalation_detected = True

            max_score = max(max_score, result["risk_score"])
            previous_score = result["risk_score"]

        return {
            "mode": "SEQUENCE_SIMULATION",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id or "anonymous",
            "total_steps": len(actions),
            "steps": results,
            "max_risk_score": max_score,
            "escalation_detected": escalation_detected,
            "overall_decision": "BLOCK" if max_score >= 80 else "APPROVAL" if max_score >= 60 else "ALLOW",
            "summary": self._summarize_sequence(results, escalation_detected)
        }

    def _summarize_sequence(self, results: list, escalation: bool) -> str:
        if escalation:
            return "ESCALATION DETECTED — sequence of actions shows increasing risk pattern"
        blocked = [r for r in results if r["decision"] == "BLOCK"]
        if blocked:
            return f"{len(blocked)} critical actions detected in sequence"
        return "Sequence appears safe overall"

    def get_history(self) -> list:
        return self.simulation_history

    def export_simulation_report(self, output_path: str = None) -> str:
        if not output_path:
            output_path = f"simulation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(output_path, "w") as f:
            json.dump({
                "generated_at": datetime.utcnow().isoformat(),
                "total_simulations": len(self.simulation_history),
                "simulations": self.simulation_history
            }, f, indent=2)
        return output_path