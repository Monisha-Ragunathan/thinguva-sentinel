import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path

class AuditLogger:
    def __init__(self, db_path: str = "sentinel_audit.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                reason TEXT,
                hash TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def log(self, action: dict, status: str, reason: str = None):
        timestamp = datetime.utcnow().isoformat()
        action_str = json.dumps(action)
        record = f"{timestamp}{action_str}{status}"
        hash_value = self._hash(record)

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO audit_log (timestamp, action, status, reason, hash)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, action_str, status, reason, hash_value))
        conn.commit()
        conn.close()

        print(f"[Thinguva Sentinel] {status} | {timestamp} | {reason or ''}")

    def get_logs(self, limit: int = 100) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT timestamp, action, status, reason, hash
            FROM audit_log
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": r[0],
                "action": r[1],
                "status": r[2],
                "reason": r[3],
                "hash": r[4]
            }
            for r in rows
        ]

    def export_json(self, output_path: str = "audit_export.json"):
        logs = self.get_logs(limit=10000)
        with open(output_path, "w") as f:
            json.dump(logs, f, indent=2)
        print(f"[Thinguva Sentinel] Audit log exported to {output_path}")