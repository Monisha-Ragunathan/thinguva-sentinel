import json
import sqlite3
from datetime import datetime

class ReplaySystem:
    def __init__(self, db_path: str = "sentinel_audit.db"):
        self.db_path = db_path

    def get_session(self, session_id: str) -> list:
        """Get all actions from a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT timestamp, action, status, reason, hash
            FROM audit_log
            WHERE action LIKE ?
            ORDER BY id ASC
        """, (f'%{session_id}%',))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": r[0],
                "action": json.loads(r[1]),
                "status": r[2],
                "reason": r[3],
                "hash": r[4]
            }
            for r in rows
        ]

    def replay(self, session_id: str):
        """Replay and print a full agent session step by step"""
        actions = self.get_session(session_id)
        if not actions:
            print(f"No session found for ID: {session_id}")
            return

        print("\n" + "="*60)
        print(f"[Thinguva Sentinel] Replaying session: {session_id}")
        print(f"Total actions: {len(actions)}")
        print("="*60)

        for i, entry in enumerate(actions, 1):
            action = entry["action"]
            status = entry["status"]
            reason = entry["reason"] or ""
            timestamp = entry["timestamp"]

            status_symbol = {
                "ALLOWED": "✓",
                "BLOCKED": "✗",
                "LOOP_DETECTED": "↻",
                "ANOMALY": "⚠",
                "REJECTED": "✗"
            }.get(status, "?")

            print(f"\nStep {i} — {timestamp}")
            print(f"  Tool    : {action.get('tool', 'unknown')}")
            print(f"  Args    : {action.get('args', '')}")
            print(f"  Status  : {status_symbol} {status}")
            if reason:
                print(f"  Reason  : {reason}")
            print(f"  Hash    : {entry['hash'][:16]}...")

        print("\n" + "="*60)
        print("[Thinguva Sentinel] Replay complete")
        print("="*60 + "\n")

    def export_session(self, session_id: str, output_path: str = None):
        """Export session as JSON for compliance reports"""
        actions = self.get_session(session_id)
        if not output_path:
            output_path = f"session_{session_id}.json"
        with open(output_path, "w") as f:
            json.dump({
                "session_id": session_id,
                "exported_at": datetime.utcnow().isoformat(),
                "total_actions": len(actions),
                "actions": actions
            }, f, indent=2)
        print(f"[Thinguva Sentinel] Session exported to {output_path}")
        return output_path