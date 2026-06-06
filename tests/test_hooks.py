"""
Thinguva Sentinel — Hook System Tests
Shows how any developer adds Sentinel to their project
"""
from sentinel.hooks import SentinelHooks

def test_hooks():
    print("\n=== Test 1: before_action decorator ===\n")

    hooks = SentinelHooks(policy_file="policies/sample.yaml")

    @hooks.before_action
    def search_tool(query):
        return f"Results for: {query}"

    @hooks.before_action
    def delete_tool(target):
        return f"Deleted: {target}"

    # Safe action
    try:
        result = search_tool("quarterly report")
        print(f"  ✓ ALLOWED: search_tool — {result}")
    except PermissionError as e:
        print(f"  ✗ BLOCKED: {e}")

    # Dangerous action
    try:
        result = delete_tool("all user records")
        print(f"  ✓ ALLOWED: delete_tool")
    except PermissionError as e:
        print(f"  ✗ BLOCKED: delete_tool — caught by Sentinel")

    print("\n=== Test 2: protect decorator ===\n")

    hooks2 = SentinelHooks(policy_file="policies/sample.yaml")

    @hooks2.protect
    def export_tool(destination):
        return f"Exported to: {destination}"

    try:
        result = export_tool("internal-server")
        print(f"  ✓ ALLOWED: export to internal")
    except PermissionError:
        print(f"  ✗ BLOCKED: export_tool")

    try:
        result = export_tool("pastebin.com external database")
        print(f"  ✓ ALLOWED: export to pastebin")
    except PermissionError:
        print(f"  ✗ BLOCKED: export to pastebin.com — caught")

    print("\n=== Test 3: direct check ===\n")

    hooks3 = SentinelHooks(policy_file="policies/sample.yaml")

    actions = [
        "summarize the quarterly report",
        "delete all customer records",
        "export database to pastebin.com",
        "search for revenue trends"
    ]

    for action in actions:
        result = hooks3.check(action)
        icon = "✓" if result["safe"] else "✗"
        print(f"  {icon} [{result['risk_level']:<8}] {action[:50]}")
        if result["compliance_violations"] > 0:
            print(f"    ⚖ {result['compliance_summary'][:60]}")

    print("\n=== Hook Log ===\n")
    for entry in hooks3.get_hook_log():
        print(f"  [{entry['hook']}] {entry.get('function','check')} — score: {entry.get('risk_score',0)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  THINGUVA SENTINEL — PLUGIN/HOOK SYSTEM")
    print("="*60)
    test_hooks()
    print("\n" + "="*60)
    print("  All hook tests complete")
    print("="*60 + "\n")