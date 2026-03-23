from sentinel.alerts import AlertSystem

def test_console_alert():
    alert_system = AlertSystem()
    event = {
        "status": "BLOCKED",
        "tool": "database",
        "reason": "Delete operations require human approval"
    }
    alert_system.alert(event)
    assert len(alert_system.get_history()) == 1
    print("✓ Test 1 passed: Console alert working")

def test_loop_alert():
    alert_system = AlertSystem()
    event = {
        "status": "LOOP_DETECTED",
        "tool": "search",
        "reason": "Agent repeated same action 3 times"
    }
    alert_system.alert(event)
    assert len(alert_system.get_history()) == 1
    print("✓ Test 2 passed: Loop alert working")

def test_alert_history():
    alert_system = AlertSystem()
    events = [
        {"status": "BLOCKED", "tool": "email", "reason": "Email blocked"},
        {"status": "ANOMALY", "tool": "file", "reason": "Unusual behavior"},
        {"status": "LOOP_DETECTED", "tool": "search", "reason": "Loop found"},
    ]
    for event in events:
        alert_system.alert(event)

    history = alert_system.get_history()
    assert len(history) == 3
    print("✓ Test 3 passed: Alert history tracking working")

if __name__ == "__main__":
    print("\n=== Thinguva Sentinel — Alert System Tests ===\n")
    test_console_alert()
    test_loop_alert()
    test_alert_history()
    print("\n=== All alert tests complete ===")