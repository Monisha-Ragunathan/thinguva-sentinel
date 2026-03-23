import time
from datetime import datetime

class HumanApprovalSystem:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.pending = {}

    def request(self, action: dict) -> bool:
        """
        Request human approval for an action.
        In terminal mode — asks human to type yes/no.
        In API mode — can be extended to send webhook/slack alert.
        """
        print("\n" + "="*60)
        print("[Thinguva Sentinel] HUMAN APPROVAL REQUIRED")
        print("="*60)
        print(f"Time     : {datetime.utcnow().isoformat()}")
        print(f"Tool     : {action.get('tool', 'unknown')}")
        print(f"Action   : {action.get('args', '')}")
        print(f"Session  : {action.get('session', '')}")
        print("="*60)

        start = time.time()
        while time.time() - start < self.timeout:
            try:
                response = input("Approve this action? (yes/no): ").strip().lower()
                if response in ["yes", "y"]:
                    print("[Thinguva Sentinel] Action APPROVED by human\n")
                    return True
                elif response in ["no", "n"]:
                    print("[Thinguva Sentinel] Action REJECTED by human\n")
                    return False
                else:
                    print("Please type yes or no")
            except KeyboardInterrupt:
                return False

        print("[Thinguva Sentinel] Approval timeout — action blocked\n")
        return False

    def auto_approve(self, action: dict) -> bool:
        """For testing — auto approves without human input"""
        return True

    def auto_reject(self, action: dict) -> bool:
        """For testing — auto rejects without human input"""
        return False