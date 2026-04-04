"""
Thinguva Sentinel — Risk Timeline
===================================
Session-based tracking with escalation detection.
"""

import sqlite3
from datetime import datetime

class RiskTimeline:
    def __init__(self, db_path: str = "sentinel_audit.db"):
        self.db_path = db_path

    def get_session_timeline(self, session_id: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT timestamp, action, status
            FROM audit_log
            WHERE action LIKE ?
            ORDER BY id ASC
        """, (f'%{session_id}%',))
        rows = cursor.fetchall()
        conn.close()

        import json
        steps = []
        escalation = False
        prev_score = 0

        for i, row in enumerate(rows):
            try:
                action = json.loads(row[1])
                score = int(action.get("risk_score", 0))
            except:
                score = 0

            if score > prev_score + 20:
                escalation = True

            steps.append({
                "step": i + 1,
                "timestamp": row[0],
                "action": str(action.get("args", row[1]))[:60],
                "status": row[2],
                "risk_score": score,
                "risk_level": "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
            })
            prev_score = score

        return {
            "session_id": session_id,
            "total_steps": len(steps),
            "escalation_detected": escalation,
            "steps": steps
        }

    def get_recent_timeline(self, limit: int = 20) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT timestamp, action, status
            FROM audit_log
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        import json
        timeline = []
        for row in rows:
            try:
                action = json.loads(row[1])
                score = int(action.get("risk_score", 0))
                tool = action.get("tool", action.get("args", ""))
            except:
                score = 0
                tool = str(row[1])[:40]

            timeline.append({
                "timestamp": row[0],
                "action": str(tool)[:50],
                "status": row[2],
                "risk_score": score,
                "risk_level": "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
            })

        return timeline