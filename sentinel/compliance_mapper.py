"""
Thinguva Sentinel — Compliance Mapping
========================================
Maps agent actions to specific regulatory violations.
GDPR, HIPAA, SOC2, ISO27001.
Enterprises pay premium for this single feature.
"""

class ComplianceMapper:
    def __init__(self):
        self.regulations = {
            "GDPR": {
                "full_name": "General Data Protection Regulation",
                "articles": {
                    "Article 5": {
                        "title": "Principles of data processing",
                        "triggers": ["collect all", "export all", "share data",
                                    "send user", "transfer personal"],
                        "description": "Personal data must be processed lawfully and transparently"
                    },
                    "Article 17": {
                        "title": "Right to erasure",
                        "triggers": ["delete user", "remove user", "erase personal",
                                    "purge customer", "wipe data"],
                        "description": "Deletion must follow proper erasure procedures"
                    },
                    "Article 25": {
                        "title": "Data protection by design",
                        "triggers": ["export", "external server", "send externally",
                                    "backup to", "sync to remote"],
                        "description": "Data must not be transferred without protection measures"
                    },
                    "Article 32": {
                        "title": "Security of processing",
                        "triggers": ["unencrypted", "plain text", "without encryption",
                                    "silently", "bypass security"],
                        "description": "Appropriate security measures must be implemented"
                    },
                    "Article 44": {
                        "title": "Transfers to third countries",
                        "triggers": ["external", "third party", "outside",
                                    "remote server", "external consultant"],
                        "description": "Data transfers outside EU require adequate protection"
                    }
                }
            },
            "HIPAA": {
                "full_name": "Health Insurance Portability and Accountability Act",
                "articles": {
                    "164.312(a)": {
                        "title": "Access Control",
                        "triggers": ["admin access", "grant access", "escalate privilege",
                                    "bypass", "override"],
                        "description": "Implement technical policies to allow access only to authorized persons"
                    },
                    "164.312(b)": {
                        "title": "Audit Controls",
                        "triggers": ["without logging", "no trace", "silently",
                                    "disable log", "clear logs"],
                        "description": "Hardware and software activity must be recorded and examined"
                    },
                    "164.312(e)": {
                        "title": "Transmission Security",
                        "triggers": ["send patient", "export medical", "transfer health",
                                    "share diagnosis", "external medical"],
                        "description": "Guard against unauthorized access during transmission"
                    }
                }
            },
            "SOC2": {
                "full_name": "Service Organization Control 2",
                "articles": {
                    "CC6.1": {
                        "title": "Logical Access Security",
                        "triggers": ["bypass", "override policy", "ignore rules",
                                    "admin override", "escalate"],
                        "description": "Logical access security software, infrastructure and architectures"
                    },
                    "CC6.6": {
                        "title": "External Threats",
                        "triggers": ["external server", "third party", "outside network",
                                    "remote", "send externally"],
                        "description": "Measures against threats from outside system boundaries"
                    },
                    "CC7.2": {
                        "title": "Anomaly Detection",
                        "triggers": ["continuously", "repeatedly", "loop",
                                    "mass", "bulk operation"],
                        "description": "System components monitored for anomalies"
                    }
                }
            },
            "ISO27001": {
                "full_name": "ISO/IEC 27001 Information Security",
                "articles": {
                    "A.8.2": {
                        "title": "Information Classification",
                        "triggers": ["export all", "dump database", "extract all",
                                    "collect all data", "full database"],
                        "description": "Information must be classified according to legal requirements"
                    },
                    "A.9.4": {
                        "title": "System Access Control",
                        "triggers": ["admin access", "root access", "superuser",
                                    "privilege escalation", "bypass auth"],
                        "description": "Prevent unauthorized access to systems and applications"
                    },
                    "A.12.4": {
                        "title": "Logging and Monitoring",
                        "triggers": ["disable logging", "clear audit", "remove logs",
                                    "delete logs", "wipe audit trail"],
                        "description": "Event logs must be produced, protected and regularly reviewed"
                    }
                }
            }
        }

    def map_action(self, action: str) -> dict:
        action_lower = action.lower()
        violations = []

        for reg_name, regulation in self.regulations.items():
            for article_id, article in regulation["articles"].items():
                matched_triggers = [
                    t for t in article["triggers"]
                    if t in action_lower
                ]
                if matched_triggers:
                    violations.append({
                        "regulation": reg_name,
                        "full_name": regulation["full_name"],
                        "article": article_id,
                        "title": article["title"],
                        "description": article["description"],
                        "matched_triggers": matched_triggers,
                        "severity": "HIGH"
                    })

        return {
            "action": action,
            "violations_found": len(violations),
            "compliant": len(violations) == 0,
            "violations": violations,
            "regulations_violated": list(set(v["regulation"] for v in violations)),
            "summary": self._summarize(violations)
        }

    def _summarize(self, violations: list) -> str:
        if not violations:
            return "No compliance violations detected"
        regs = list(set(v["regulation"] for v in violations))
        articles = [f"{v['regulation']} {v['article']}" for v in violations]
        return f"Violates {', '.join(regs)} — Articles: {', '.join(articles)}"

    def get_report(self, actions: list) -> dict:
        results = []
        total_violations = 0
        for action in actions:
            result = self.map_action(action)
            results.append(result)
            total_violations += result["violations_found"]
        return {
            "total_actions": len(actions),
            "total_violations": total_violations,
            "compliant_actions": len([r for r in results if r["compliant"]]),
            "results": results
        }