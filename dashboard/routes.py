from fastapi import APIRouter
from sentinel.audit import AuditLogger
from sentinel.policy import PolicyEngine
from sentinel.wrapper import SentinelWrapper
from typing import Optional

router = APIRouter()
audit = AuditLogger()
policy = PolicyEngine(policy_file="policies/sample.yaml")

@router.get("/logs")
def get_logs(limit: int = 50):
    logs = audit.get_logs(limit=limit)
    return {"logs": logs, "total": len(logs)}

@router.get("/logs/violations")
def get_violations(limit: int = 50):
    logs = audit.get_logs(limit=limit)
    violations = [l for l in logs if l["status"] == "BLOCKED"]
    return {"violations": violations, "total": len(violations)}

@router.get("/policies")
def get_policies():
    return {"rules": policy.rules, "total": len(policy.rules)}

@router.post("/test/action")
def test_action(payload: dict):
    sentinel = SentinelWrapper(policy_file="policies/sample.yaml")

    @sentinel.wrap
    def mock_agent(task):
        return f"Executed: {task}"

    try:
        task = payload.get("action", "default task")
        result = mock_agent(task)
        return {"status": "ALLOWED", "result": result}
    except PermissionError as e:
        return {"status": "BLOCKED", "reason": str(e)}
    except RuntimeError as e:
        return {"status": "LOOP_DETECTED", "reason": str(e)}

@router.get("/stats")
def get_stats():
    logs = audit.get_logs(limit=1000)
    total = len(logs)
    blocked = len([l for l in logs if l["status"] == "BLOCKED"])
    allowed = len([l for l in logs if l["status"] == "ALLOWED"])
    loops = len([l for l in logs if l["status"] == "LOOP_DETECTED"])
    return {
        "total_actions": total,
        "allowed": allowed,
        "blocked": blocked,
        "loops_detected": loops,
        "block_rate": f"{(blocked/total*100):.1f}%" if total > 0 else "0%"
    }