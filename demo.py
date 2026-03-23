"""
Thinguva Sentinel — Live Demo Script
=====================================
Run this to see Thinguva Sentinel in action.
Perfect for investor and customer demos.
"""

import time
import sys

def print_slow(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def section(title):
    print("\n" + "="*60)
    print_slow(f"  {title}")
    print("="*60)

def demo():
    print("\n")
    print_slow("  ████████╗██╗  ██╗██╗███╗   ██╗ ██████╗ ██╗   ██╗██╗   ██╗ █████╗ ")
    print_slow("     ██╔══╝██║  ██║██║████╗  ██║██╔════╝ ██║   ██║██║   ██║██╔══██╗")
    print_slow("     ██║   ███████║██║██╔██╗ ██║██║  ███╗██║   ██║██║   ██║███████║")
    print_slow("     ██║   ██╔══██║██║██║╚██╗██║██║   ██║██║   ██║╚██╗ ██╔╝██╔══██║")
    print_slow("     ██║   ██║  ██║██║██║ ╚████║╚██████╔╝╚██████╔╝ ╚████╔╝ ██║  ██║")
    print_slow("     ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝   ╚═══╝  ╚═╝  ╚═╝")
    print()
    print_slow("                    S E N T I N E L")
    print_slow("          Agent Governance & Reliability Platform")
    print_slow("              From Coimbatore to the World 🌍")
    print()
    time.sleep(1)

    # ── Demo 1: Basic governance ──────────────────────────
    section("DEMO 1 — Policy Enforcement")
    print_slow("\n  Scenario: A financial services company deploys an AI agent")
    print_slow("  to manage customer accounts. Without governance, the agent")
    print_slow("  could delete records, send emails, or transfer funds.")
    print()
    time.sleep(0.5)

    from sentinel.agent_integration import AgentIntegration

    sentinel = AgentIntegration(policy_file="policies/sample.yaml")

    @sentinel.monitor(tool_name="account_manager")
    def account_agent(action):
        return f"Executed: {action}"

    test_actions = [
        ("summarize customer portfolio", True),
        ("generate monthly report", True),
        ("delete customer record #4521", False),
        ("send_email to all customers", False),
        ("transfer funds to account #9988", False),
        ("analyze transaction history", True),
    ]

    print_slow("\n  Running agent actions through Thinguva Sentinel...\n")
    time.sleep(0.3)

    for action, should_pass in test_actions:
        time.sleep(0.4)
        try:
            result = account_agent(action)
            print(f"  ✓ ALLOWED  → {action}")
        except PermissionError as e:
            print(f"  ✗ BLOCKED  → {action}")
        except RuntimeError as e:
            print(f"  ↻ LOOP     → {action}")

    time.sleep(0.5)

    # ── Demo 2: Loop detection ────────────────────────────
    section("DEMO 2 — Infinite Loop Detection")
    print_slow("\n  Scenario: An agent gets stuck in a loop, repeatedly")
    print_slow("  calling the same search tool. Without Sentinel, this")
    print_slow("  burns compute indefinitely. Sentinel catches it.")
    print()
    time.sleep(0.5)

    sentinel2 = AgentIntegration(policy_file="policies/sample.yaml")

    @sentinel2.monitor(tool_name="search")
    def search_agent(query):
        return f"Results: {query}"

    print_slow("\n  Agent starting search loop...\n")
    loop_count = 0
    try:
        for i in range(20):
            search_agent("find customer data")
            loop_count += 1
            print(f"  Call #{i+1} — search tool invoked")
            time.sleep(0.1)
    except RuntimeError:
        print(f"\n  ↻ LOOP DETECTED after {loop_count+1} calls — agent stopped automatically")
        print(f"  💰 Estimated compute saved: ${(20 - loop_count) * 0.002:.4f}")

    time.sleep(0.5)

    # ── Demo 3: Audit trail ───────────────────────────────
    section("DEMO 3 — Tamper-Proof Audit Trail")
    print_slow("\n  Every action is SHA256 hashed and stored locally.")
    print_slow("  Regulators can verify nothing was altered.")
    print()
    time.sleep(0.5)

    from sentinel.audit import AuditLogger
    logger = AuditLogger()
    logs = logger.get_logs(limit=5)

    print_slow("\n  Last 5 actions in audit log:\n")
    for log in logs:
        status_icon = {"ALLOWED": "✓", "BLOCKED": "✗", "LOOP_DETECTED": "↻"}.get(log["status"], "?")
        print(f"  {status_icon} {log['timestamp'].split('T')[1][:8]} | {log['status']:<14} | hash: {log['hash'][:20]}...")
        time.sleep(0.2)

    time.sleep(0.5)

    # ── Demo 4: Compliance report ─────────────────────────
    section("DEMO 4 — Compliance Report Generation")
    print_slow("\n  One click generates a complete PDF compliance report")
    print_slow("  for regulators, auditors, and enterprise security teams.")
    print()
    time.sleep(0.5)

    print_slow("\n  Generating compliance report...")
    time.sleep(0.5)

    from sentinel.compliance_report import ComplianceReportGenerator
    generator = ComplianceReportGenerator(
        db_path="sentinel_audit.db",
        policy_file="policies/sample.yaml"
    )
    path = generator.generate(output_path="demo_compliance_report.pdf")
    print(f"\n  ✓ Report saved to: {path}")
    print_slow("  Ready for regulators. Cryptographically verified.")

    time.sleep(0.5)

    # ── Demo 5: Session replay ────────────────────────────
    section("DEMO 5 — Session Replay")
    print_slow("\n  Any agent session can be replayed step by step.")
    print_slow("  Perfect for incident investigation and debugging.")
    print()
    time.sleep(0.5)

    from sentinel.replay import ReplaySystem
    replay = ReplaySystem()
    session_id = sentinel.session_id
    replay.replay(session_id)

    # ── Summary ───────────────────────────────────────────
    section("THINGUVA SENTINEL — SUMMARY")
    print()
    print_slow("  ✓ Policy enforcement     — dangerous actions blocked")
    print_slow("  ✓ Loop detection         — infinite cycles stopped")
    print_slow("  ✓ Anomaly detection      — unusual behavior flagged")
    print_slow("  ✓ Tamper-proof audit log — every action hashed")
    print_slow("  ✓ Session replay         — full incident reconstruction")
    print_slow("  ✓ Compliance reports     — regulator-ready PDF")
    print_slow("  ✓ Zero LLM dependency    — no data leaves your walls")
    print_slow("  ✓ One command install    — docker-compose up")
    print()
    print_slow("  Built by Thinguva — From Coimbatore to the World 🌍")
    print_slow("  github.com/Monisha-Ragunathan/thinguva-sentinel")
    print()
    print("="*60 + "\n")

if __name__ == "__main__":
    demo()