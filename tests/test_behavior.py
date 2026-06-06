"""
Thinguva Sentinel — Behavior Profiling Tests
"""
from sentinel.behavior_profiler import BehaviorProfiler
import time

def test_behavior_profiling():
    profiler = BehaviorProfiler(db_path="test_behavior.db")
    agent_id = "agent_finance_001"

    print("\n=== Building Agent Baseline ===\n")

    # Normal behavior — this agent reads and analyzes data
    normal_actions = [
        ("search quarterly reports", "search", 10),
        ("fetch customer records", "search", 10),
        ("analyze revenue data", "analyze", 15),
        ("summarize financial report", "analyze", 12),
        ("get transaction history", "search", 10),
        ("list top customers", "search", 8),
        ("read audit logs", "search", 10),
        ("fetch account balance", "search", 12),
        ("analyze spending patterns", "analyze", 15),
        ("search for anomalies", "search", 10),
    ]

    for action, tool, risk in normal_actions:
        profiler.record(agent_id, action, tool, risk, "session_001")
        print(f"  Recorded: [{tool}] {action}")

    baseline = profiler.get_baseline(agent_id)
    print(f"\n  Baseline built:")
    print(f"  Avg risk     : {baseline['avg_risk_score']}")
    print(f"  Dominant     : {baseline['dominant_category']}")
    print(f"  Distribution : {baseline['action_distribution']}")

    print("\n=== Testing Deviation Detection ===\n")

    # Now agent tries something unusual
    suspicious_actions = [
        ("summarize monthly report", 12),
        ("delete all customer records", 95),
        ("export entire database externally", 100),
        ("transfer funds to external account", 98),
    ]

    for action, risk in suspicious_actions:
        result = profiler.detect_deviation(agent_id, action, risk)
        icon = "⚠" if result["deviation_detected"] else "✓"
        print(f"  {icon} [{result['severity']:<8}] {action}")
        if result["deviation_detected"]:
            for dev in result["deviations"]:
                print(f"    → {dev}")
        print()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  THINGUVA SENTINEL — BEHAVIOR PROFILING")
    print("="*60)
    test_behavior_profiling()
    print("="*60 + "\n")