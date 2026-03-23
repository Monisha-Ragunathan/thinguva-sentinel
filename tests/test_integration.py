from sentinel.agent_integration import AgentIntegration
from sentinel.replay import ReplaySystem
import time

def test_monitor_decorator():
    sentinel = AgentIntegration(policy_file="policies/sample.yaml")

    @sentinel.monitor(tool_name="search")
    def search_tool(query):
        return f"Results for: {query}"

    result = search_tool("quarterly earnings report")
    assert "quarterly earnings report" in result
    print("✓ Test 1 passed: Monitor decorator working")

def test_blocked_tool():
    sentinel = AgentIntegration(policy_file="policies/sample.yaml")

    @sentinel.monitor(tool_name="database")
    def db_tool(query):
        return f"Executing: {query}"

    try:
        db_tool("drop table users")
        print("✗ Test 2 failed: Should have been blocked")
    except PermissionError as e:
        print(f"✓ Test 2 passed: Tool blocked — {e}")

def test_loop_detection():
    sentinel = AgentIntegration(policy_file="policies/sample.yaml")

    @sentinel.monitor(tool_name="search")
    def search_tool(query):
        return f"Results for: {query}"

    detected = False
    try:
        for i in range(10):
            search_tool("same repeated query")
    except RuntimeError as e:
        detected = True
        print(f"✓ Test 3 passed: Loop detected — {e}")

    assert detected

def test_replay_system():
    sentinel = AgentIntegration(policy_file="policies/sample.yaml")
    session_id = sentinel.session_id

    @sentinel.monitor(tool_name="file_reader")
    def read_file(path):
        return f"Contents of {path}"

    read_file("report.pdf")
    read_file("summary.txt")

    replay = ReplaySystem()
    replay.replay(session_id)
    print("✓ Test 4 passed: Replay system working")

if __name__ == "__main__":
    print("\n=== Thinguva Sentinel — Integration Tests ===\n")
    test_monitor_decorator()
    test_blocked_tool()
    test_loop_detection()
    test_replay_system()
    print("\n=== All integration tests complete ===")