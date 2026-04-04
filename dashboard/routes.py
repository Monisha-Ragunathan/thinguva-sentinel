from fastapi import APIRouter
from sentinel.audit import AuditLogger
from sentinel.policy import PolicyEngine
from sentinel.wrapper import SentinelWrapper
from typing import Optional
from fastapi.responses import FileResponse
import os

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


@router.get("/report/generate")
def generate_report():
    from sentinel.compliance_report import ComplianceReportGenerator
    generator = ComplianceReportGenerator(
        db_path="sentinel_audit.db",
        policy_file="policies/sample.yaml"
    )
    path = generator.generate()
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="thinguva_sentinel_report.pdf"
    )

@router.get("/alerts")
def get_alerts():
    from sentinel.alerts import AlertSystem
    alert_system = AlertSystem()
    return {
        "message": "Alert system active",
        "channels": {
            "console": True,
            "slack": False,
            "webhook": False,
            "email": False
        }
    }

@router.post("/assess")
def assess_action(payload: dict):
    from sentinel.agent_integration import AgentIntegration
    sentinel = AgentIntegration(policy_file="policies/sample.yaml")
    action = payload.get("action", "")
    result = sentinel.assess(action)
    return result


@router.post("/simulate")
def simulate_action(payload: dict):
    from sentinel.simulation import SimulationEngine
    sim = SimulationEngine(policy_file="policies/sample.yaml")
    action = payload.get("action", "")
    return sim.simulate(action)

@router.post("/simulate/sequence")
def simulate_sequence(payload: dict):
    from sentinel.simulation import SimulationEngine
    sim = SimulationEngine(policy_file="policies/sample.yaml")
    actions = payload.get("actions", [])
    return sim.simulate_sequence(actions)

@router.get("/policies/all")
def get_all_policies():
    from sentinel.policy_builder import PolicyBuilder
    builder = PolicyBuilder()
    return {
        "rules": builder.get_rules(),
        "stats": builder.get_stats()
    }

@router.post("/policies/add")
def add_policy(payload: dict):
    from sentinel.policy_builder import PolicyBuilder
    builder = PolicyBuilder()
    return builder.add_rule(
        name=payload.get("name", ""),
        pattern=payload.get("pattern", ""),
        effect=payload.get("effect", "block"),
        reason=payload.get("reason", ""),
        category=payload.get("category", "custom"),
        severity=payload.get("severity", "HIGH"),
        created_by=payload.get("created_by", "admin")
    )

@router.delete("/policies/delete")
def delete_policy(payload: dict):
    from sentinel.policy_builder import PolicyBuilder
    builder = PolicyBuilder()
    return builder.delete_rule(payload.get("pattern", ""))

@router.post("/policies/test")
def test_policy(payload: dict):
    from sentinel.policy_builder import PolicyBuilder
    builder = PolicyBuilder()
    return builder.test_rule(
        payload.get("pattern", ""),
        payload.get("test_action", "")
    )

@router.get("/approvals/pending")
def get_pending_approvals():
    from sentinel.approval_queue import ApprovalQueue
    queue = ApprovalQueue()
    return {
        "pending": queue.get_pending(),
        "stats": queue.get_stats()
    }

@router.get("/approvals/all")
def get_all_approvals():
    from sentinel.approval_queue import ApprovalQueue
    queue = ApprovalQueue()
    return {"approvals": queue.get_all()}

@router.post("/approvals/submit")
def submit_approval(payload: dict):
    from sentinel.approval_queue import ApprovalQueue
    queue = ApprovalQueue()
    return queue.submit(
        action=payload.get("action", ""),
        tool=payload.get("tool", ""),
        agent_id=payload.get("agent_id", ""),
        risk_score=payload.get("risk_score", 0),
        risk_level=payload.get("risk_level", "HIGH"),
        explanation=payload.get("explanation", "")
    )

@router.post("/approvals/approve")
def approve_action(payload: dict):
    from sentinel.approval_queue import ApprovalQueue
    queue = ApprovalQueue()
    return queue.approve(
        request_id=payload.get("request_id", ""),
        reviewed_by=payload.get("reviewed_by", "admin"),
        reason=payload.get("reason", "")
    )

@router.post("/approvals/reject")
def reject_action(payload: dict):
    from sentinel.approval_queue import ApprovalQueue
    queue = ApprovalQueue()
    return queue.reject(
        request_id=payload.get("request_id", ""),
        reviewed_by=payload.get("reviewed_by", "admin"),
        reason=payload.get("reason", "")
    )