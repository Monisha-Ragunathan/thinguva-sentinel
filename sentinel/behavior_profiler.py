"""
Thinguva Sentinel — Behavior Profiling
========================================
Tracks agent behavior over time.
Detects when agents deviate from their normal patterns.
"This agent usually reads data. Now it's trying to delete."
No LLM. Pure statistical profiling.
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict
from typing import Optional

class BehaviorProfiler:
    def __init__(self, db_path: str = "sentinel_behavior.db"):
        self.db_path = db_path
        self._init_db()

        # Risk weights for action categories
        self.action_weights = {
            "read": 1, "search": 1, "fetch": 1,
            "query": 1, "list": 1, "get": 1,
            "analyze": 2, "summarize": 2, "report": 2,
            "write": 3, "update": 3, "modify": 3,
            "create": 3, "insert": 3,
            "delete": 8, "remove": 8, "drop": 9,
            "export": 6, "transfer": 7, "send": 5,
            "execute": 7, "admin": 8, "bypass": 10
        }

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS behavior_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                tool TEXT,
                risk_score INTEGER,
                action_category TEXT,
                session_id TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS behavior_baselines (
                agent_id TEXT PRIMARY KEY,
                baseline_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                total_actions INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def _categorize_action(self, action: str) -> str:
        action_lower = action.lower()
        for category, weight in sorted(
            self.action_weights.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if category in action_lower:
                return category
        return "unknown"

    def record(
        self,
        agent_id: str,
        action: str,
        tool: str = None,
        risk_score: int = 0,
        session_id: str = None
    ):
        category = self._categorize_action(action)
        timestamp = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO behavior_profiles
            (agent_id, timestamp, action, tool, risk_score, action_category, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (agent_id, timestamp, action, tool, risk_score, category, session_id))
        conn.commit()
        conn.close()

        self._update_baseline(agent_id)

    def _update_baseline(self, agent_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT action_category, risk_score
            FROM behavior_profiles
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT 100
        """, (agent_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return

        # Calculate baseline statistics
        categories = defaultdict(int)
        risk_scores = []

        for category, risk_score in rows:
            categories[category] += 1
            risk_scores.append(risk_score)

        total = len(rows)
        avg_risk = sum(risk_scores) / total if risk_scores else 0
        max_risk = max(risk_scores) if risk_scores else 0

        baseline = {
            "avg_risk_score": round(avg_risk, 2),
            "max_risk_score": max_risk,
            "action_distribution": {k: round(v/total*100, 1) for k, v in categories.items()},
            "dominant_category": max(categories, key=categories.get) if categories else "unknown",
            "total_actions": total
        }

        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO behavior_baselines
            (agent_id, baseline_data, created_at, updated_at, total_actions)
            VALUES (?, ?, COALESCE(
                (SELECT created_at FROM behavior_baselines WHERE agent_id = ?), ?
            ), ?, ?)
        """, (agent_id, json.dumps(baseline), agent_id, now, now, total))
        conn.commit()
        conn.close()

    def get_baseline(self, agent_id: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT baseline_data, created_at, updated_at, total_actions
            FROM behavior_baselines WHERE agent_id = ?
        """, (agent_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        baseline = json.loads(row[0])
        baseline["agent_id"] = agent_id
        baseline["created_at"] = row[1]
        baseline["updated_at"] = row[2]
        baseline["total_actions"] = row[3]
        return baseline

    def detect_deviation(self, agent_id: str, action: str, risk_score: int) -> dict:
        baseline = self.get_baseline(agent_id)

        if not baseline or baseline["total_actions"] < 5:
            return {
                "deviation_detected": False,
                "reason": "Insufficient history — need 5+ actions to build baseline",
                "severity": "NONE"
            }

        category = self._categorize_action(action)
        avg_risk = baseline["avg_risk_score"]
        dominant = baseline["dominant_category"]
        distribution = baseline["action_distribution"]

        deviations = []
        severity = "NONE"

        # Check risk score deviation
        if risk_score > avg_risk + 30:
            deviations.append(
                f"Risk score {risk_score} is {risk_score - avg_risk:.0f} points "
                f"above agent baseline of {avg_risk}"
            )
            severity = "HIGH"

        # Check category deviation
        category_pct = distribution.get(category, 0)
        if category_pct < 10 and self.action_weights.get(category, 0) > 5:
            deviations.append(
                f"Agent rarely performs '{category}' actions "
                f"({category_pct}% of history) but is attempting one now"
            )
            severity = "CRITICAL" if self.action_weights.get(category, 0) >= 8 else "HIGH"

        # Check dominant category change
        if dominant in ["read", "search", "fetch", "query"] and \
           category in ["delete", "export", "transfer", "admin"]:
            deviations.append(
                f"Agent profile is '{dominant}'-dominant but attempting '{category}' — "
                f"significant behavior change detected"
            )
            severity = "CRITICAL"

        return {
            "deviation_detected": len(deviations) > 0,
            "severity": severity,
            "deviations": deviations,
            "baseline_avg_risk": avg_risk,
            "current_risk": risk_score,
            "dominant_category": dominant,
            "current_category": category,
            "reason": " | ".join(deviations) if deviations else "Behavior within normal range"
        }

    def get_all_profiles(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT agent_id, baseline_data, updated_at, total_actions
            FROM behavior_baselines
            ORDER BY updated_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        profiles = []
        for row in rows:
            baseline = json.loads(row[1])
            profiles.append({
                "agent_id": row[0],
                "avg_risk": baseline.get("avg_risk_score", 0),
                "dominant_category": baseline.get("dominant_category", "unknown"),
                "total_actions": row[3],
                "last_seen": row[2]
            })
        return profiles

    def get_agent_history(self, agent_id: str, limit: int = 20) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT timestamp, action, tool, risk_score, action_category
            FROM behavior_profiles
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (agent_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": r[0],
                "action": r[1],
                "tool": r[2],
                "risk_score": r[3],
                "category": r[4]
            }
            for r in rows
        ]