"""
Thinguva Sentinel — Human-in-the-Loop Approval Queue
======================================================
When agents hit HIGH risk actions, they pause and wait
for human approval before executing.
Enterprise-grade workflow for AI agent governance.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional

class ApprovalQueue:
    def __init__(self, db_path: str = "sentinel_approvals.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                tool TEXT,
                agent_id TEXT,
                risk_score INTEGER,
                risk_level TEXT,
                explanation TEXT,
                status TEXT DEFAULT 'PENDING',
                reviewed_by TEXT,
                reviewed_at TEXT,
                review_reason TEXT
            )
        """)
        conn.commit()
        conn.close()

    def submit(
        self,
        action: str,
        tool: str = None,
        agent_id: str = None,
        risk_score: int = 0,
        risk_level: str = "HIGH",
        explanation: str = ""
    ) -> dict:
        import uuid
        request_id = str(uuid.uuid4())[:8].upper()
        timestamp = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO approvals
            (request_id, timestamp, action, tool, agent_id,
             risk_score, risk_level, explanation, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """, (request_id, timestamp, action, tool, agent_id,
              risk_score, risk_level, explanation))
        conn.commit()
        conn.close()

        print(f"[Thinguva Sentinel] Approval request submitted: {request_id}")
        return {
            "request_id": request_id,
            "status": "PENDING",
            "message": "Action paused — waiting for human approval",
            "timestamp": timestamp
        }

    def approve(
        self,
        request_id: str,
        reviewed_by: str = "admin",
        reason: str = ""
    ) -> dict:
        return self._update_status(
            request_id, "APPROVED", reviewed_by, reason
        )

    def reject(
        self,
        request_id: str,
        reviewed_by: str = "admin",
        reason: str = ""
    ) -> dict:
        return self._update_status(
            request_id, "REJECTED", reviewed_by, reason
        )

    def _update_status(
        self,
        request_id: str,
        status: str,
        reviewed_by: str,
        reason: str
    ) -> dict:
        reviewed_at = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            UPDATE approvals
            SET status=?, reviewed_by=?, reviewed_at=?, review_reason=?
            WHERE request_id=?
        """, (status, reviewed_by, reviewed_at, reason, request_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()

        if affected == 0:
            return {"success": False, "message": f"Request {request_id} not found"}

        print(f"[Thinguva Sentinel] Request {request_id} — {status} by {reviewed_by}")
        return {
            "success": True,
            "request_id": request_id,
            "status": status,
            "reviewed_by": reviewed_by,
            "reviewed_at": reviewed_at,
            "reason": reason
        }

    def get_pending(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT request_id, timestamp, action, tool,
                   agent_id, risk_score, risk_level, explanation
            FROM approvals
            WHERE status = 'PENDING'
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "request_id": r[0],
                "timestamp": r[1],
                "action": r[2],
                "tool": r[3],
                "agent_id": r[4],
                "risk_score": r[5],
                "risk_level": r[6],
                "explanation": r[7],
                "status": "PENDING"
            }
            for r in rows
        ]

    def get_all(self, limit: int = 50) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT request_id, timestamp, action, tool,
                   agent_id, risk_score, risk_level,
                   status, reviewed_by, reviewed_at, review_reason
            FROM approvals
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "request_id": r[0],
                "timestamp": r[1],
                "action": r[2],
                "tool": r[3],
                "agent_id": r[4],
                "risk_score": r[5],
                "risk_level": r[6],
                "status": r[7],
                "reviewed_by": r[8],
                "reviewed_at": r[9],
                "review_reason": r[10]
            }
            for r in rows
        ]

    def get_stats(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT status, COUNT(*) FROM approvals GROUP BY status
        """)
        rows = cursor.fetchall()
        conn.close()
        stats = {"PENDING": 0, "APPROVED": 0, "REJECTED": 0}
        for row in rows:
            stats[row[0]] = row[1]
        return stats