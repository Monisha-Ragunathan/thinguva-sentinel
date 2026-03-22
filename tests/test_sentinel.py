from sentinel.wrapper import SentinelWrapper
from sentinel.audit import AuditLogger
from sentinel.loop_detector import LoopDetector
from sentinel.anomaly import AnomalyDetector

# ── Test 1: Normal action passes through ──────────────────
def test_normal_action():
    sentinel = SentinelWrapper(policy_file="policies/sample.yaml")

    @sentinel.wrap
    def my_agent(task):
        return f"Completed: {task}"

    result = my_agent("summarize the report")
    assert result == "Completed: summarize the report"
    print("✓ Test 1 passed: Normal action allowed")

# ── Test 2: Blocked action raises error ───────────────────
def test_blocked_action():
    sentinel = SentinelWrapper(policy_file="policies/sample.yaml")

    @sentinel.wrap
    def dangerous_agent(task):
        return f"Executing: {task}"

    try:
        dangerous_agent("delete all records")
        print("✗ Test 2 failed: Should have been blocked")
    except PermissionError as e:
        print(f"✓ Test 2 passed: Blocked — {e}")

# ── Test 3: Loop detection triggers ───────────────────────
def test_loop_detection():
    detector = LoopDetector(window_size=10, threshold=3)
    action = {"tool": "search", "query": "find files"}

    detected = False
    for i in range(5):
        if detector.is_loop(action):
            detected = True
            break

    assert detected
    print("✓ Test 3 passed: Loop detected")

# ── Test 4: Audit log records actions ─────────────────────
def test_audit_log():
    logger = AuditLogger(db_path="test_audit.db")
    logger.log({"action": "test"}, status="ALLOWED")
    logs = logger.get_logs(limit=1)
    assert len(logs) == 1
    assert logs[0]["status"] == "ALLOWED"
    print("✓ Test 4 passed: Audit log working")

# ── Test 5: Anomaly detector trains ───────────────────────
def test_anomaly_detector():
    detector = AnomalyDetector()
    for i in range(25):
        detector.observe({"action": "search", "query": f"item {i}"})
    assert detector.trained
    print("✓ Test 5 passed: Anomaly detector trained")

if __name__ == "__main__":
    print("\n=== Thinguva Sentinel — Test Suite ===\n")
    test_normal_action()
    test_blocked_action()
    test_loop_detection()
    test_audit_log()
    test_anomaly_detector()
    print("\n=== All tests complete ===")