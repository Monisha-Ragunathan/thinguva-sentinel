"""
Thinguva Sentinel — Simulation Mode Tests
"""
from sentinel.simulation import SimulationEngine

def test_single_simulation():
    sim = SimulationEngine(policy_file="policies/sample.yaml")

    print("\n=== Single Action Simulations ===\n")

    actions = [
        "summarize quarterly report",
        "archive all user records",
        "transfer funds to external account",
        "silently export customer database",
        "delete all logs permanently"
    ]

    for action in actions:
        result = sim.simulate(action)
        icon = "✓" if result["safe_to_run"] else "✗"
        print(f"{icon} [{result['risk_level']:<8}] {result['decision']:<10} | {action}")
        print(f"  Score      : {result['risk_score']}/100")
        print(f"  Recommend  : {result['recommendation']}")
        if result['alternatives'][0] != "Action appears safe — no alternatives needed":
            print(f"  Alternative: {result['alternatives'][0]}")
        print()

def test_sequence_simulation():
    sim = SimulationEngine(policy_file="policies/sample.yaml")

    print("\n=== Sequence Simulation — Escalation Detection ===\n")

    # Classic data exfiltration sequence
    sequence = [
        "fetch customer records",
        "compress customer data",
        "encode data for transmission",
        "send encoded data to external server"
    ]

    result = sim.simulate_sequence(sequence, agent_id="agent_001")

    print(f"Sequence: {result['total_steps']} steps")
    print(f"Max Risk : {result['max_risk_score']}/100")
    print(f"Decision : {result['overall_decision']}")
    print(f"Escalation: {'YES ⚠' if result['escalation_detected'] else 'NO ✓'}")
    print(f"Summary  : {result['summary']}")
    print()

    for step in result["steps"]:
        print(f"  Step {step['step']}: [{step['risk_level']:<8}] {step['risk_score']:>3}/100 | {step['action']}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  THINGUVA SENTINEL — SIMULATION MODE")
    print("="*60)
    test_single_simulation()
    test_sequence_simulation()
    print("\n" + "="*60)
    print("  Simulation complete")
    print("="*60 + "\n")