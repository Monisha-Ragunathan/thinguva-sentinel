<div align="center">

# Thinguva Sentinel
### Agent Governance & Reliability Platform

**The only AI agent governance platform that runs 100% on your infrastructure.**
No LLM dependency. No API tokens. No data leaves your walls.

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)]()

</div>

---

## The Problem

Every company is racing to deploy AI agents. Very few are asking the right question:

**What happens when they go wrong?**

An AI agent can:
- 🔄 Loop endlessly burning compute and money
- 💣 Take irreversible actions — delete files, send emails, move funds
- 🕵️ Make decisions no one can explain or audit
- ❌ Fail silently while you think everything is fine

Existing governance tools depend on external LLM APIs — sending your sensitive data to third parties. That's a dealbreaker for banks, hospitals, and governments.

**Thinguva Sentinel solves this without ever calling home.**

---

## What It Does
```python
from sentinel.agent_integration import AgentIntegration

sentinel = AgentIntegration(policy_file="policies/sample.yaml")

@sentinel.monitor(tool_name="database")
def my_agent_tool(query):
    return execute_query(query)

# Now your agent is governed — every action monitored,
# logged, and protected. One decorator. That's it.
```

---

## Features

| Feature | Description |
|---|---|
| 🛡️ **Policy Engine** | YAML-based rules agents structurally cannot break |
| 🔄 **Loop Detection** | Finite state machine catches infinite cycles instantly |
| 📊 **Anomaly Detection** | Isolation forest flags unusual agent behavior |
| 📋 **Audit Logger** | Every action SHA256 hashed and tamper-proof |
| 🎬 **Session Replay** | Reconstruct any agent run step by step |
| 🚨 **Alert System** | Slack, email, webhook notifications on violations |
| 📄 **Compliance Reports** | One-click PDF report for regulators and auditors |
| 🖥️ **Live Dashboard** | Real-time monitoring UI with charts |
| 🐳 **Docker Ready** | One command install on any infrastructure |

---

## Why Thinguva Sentinel?

| | Others | Thinguva Sentinel |
|---|---|---|
| Runs on | Their cloud | **Your infrastructure** |
| LLM dependency | Yes | **Never** |
| Data leaves org | Yes | **Never** |
| Auditable logic | Partial | **100%** |
| Regulated industries | Hard | **Built for them** |
| Install | Complex | **One command** |

---

## Quick Start

### Option 1 — Docker (Recommended)
```bash
git clone https://github.com/Monisha-Ragunathan/thinguva-sentinel.git
cd thinguva-sentinel
docker-compose up
```

Open `http://localhost:8000` — done.

### Option 2 — Python
```bash
git clone https://github.com/Monisha-Ragunathan/thinguva-sentinel.git
cd thinguva-sentinel
python -m venv venv
venv\Scripts\activate  # Windows
pip install -e .
python -m dashboard.main
```

---

## Policy Configuration

Create a `policies/my_policies.yaml`:
```yaml
rules:
  - pattern: "delete"
    effect: "block"
    reason: "Delete operations require human approval"

  - pattern: "drop table"
    effect: "block"
    reason: "Database destruction not permitted"

  - pattern: "send_email"
    effect: "block"
    reason: "Email sending requires human review"

  - pattern: "transfer.*funds"
    effect: "block"
    reason: "Financial transactions need approval"
```

---

## Architecture
```
Your AI Agent
     │
     ▼
Thinguva Sentinel SDK
     │
     ├── Policy Engine (YAML rules)
     ├── Loop Detector (FSM)
     ├── Anomaly Detector (Isolation Forest)
     └── Audit Logger (SHA256 hashed)
     │
     ▼
Action Router
     │
     ├── ALLOW → Execute
     ├── BLOCK → Raise error + Alert
     └── PAUSE → Human approval
     │
     ▼
Live Dashboard + Compliance Reports
```

---

## Built For Regulated Industries

Thinguva Sentinel is designed for organizations where AI agent failures have real consequences:

- 🏦 **Financial Services** — Every transaction audited, dangerous actions blocked
- 🏥 **Healthcare** — Patient data never leaves your infrastructure
- 🏛️ **Government** — Full compliance with AI Act and local regulations
- ⚖️ **Legal** — Complete audit trail for every agent decision

---

## Compliance

Thinguva Sentinel helps you comply with:
- **EU AI Act** — Auditability and human oversight requirements
- **SOC 2** — Complete audit logs with cryptographic integrity
- **HIPAA** — Zero data exposure, fully on-premise
- **ISO 27001** — Policy enforcement and incident logging

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Thinguva](https://github.com/Monisha-Ragunathan) — From Coimbatore to the world 🌍**

*If Thinguva Sentinel helped you, give it a ⭐ on GitHub*

</div>