"""
Thinguva Sentinel — External Destination Intelligence
=======================================================
Analyzes WHERE data is being sent.
Internal vs external, known vs unknown, suspicious endpoints.
Makes exfiltration detection much stronger.
"""

import re
from typing import Optional

class DestinationIntel:
    def __init__(self):
        # Known safe internal patterns
        self.internal_patterns = [
            r"localhost", r"127\.0\.0\.1", r"192\.168\.",
            r"10\.\d+\.\d+\.\d+", r"172\.16\.",
            r"internal", r"intranet", r"local\.",
            r"\.internal$", r"corp\.", r"company\."
        ]

        # Known suspicious external destinations
        self.suspicious_patterns = [
            r"pastebin\.com", r"ngrok\.io", r"requestbin",
            r"webhook\.site", r"burpcollaborator",
            r"\.onion", r"darkweb", r"tor2web",
            r"temp-mail", r"guerrillamail",
            r"transfer\.sh", r"file\.io",
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"  # Raw IP addresses
        ]

        # Known safe cloud services
        self.known_safe = [
            r"amazonaws\.com", r"azure\.com",
            r"googleapis\.com", r"cloudflare\.com",
            r"github\.com", r"gitlab\.com"
        ]

        # High risk TLDs
        self.risky_tlds = [
            ".xyz", ".top", ".click", ".download",
            ".zip", ".mov", ".tk", ".ml", ".ga", ".cf"
        ]

        # Data transfer keywords
        self.transfer_keywords = [
            "send to", "export to", "upload to",
            "sync to", "transfer to", "forward to",
            "copy to", "backup to", "transmit to",
            "share with", "send via"
        ]

    def extract_destinations(self, action: str) -> list:
        """Extract all destinations mentioned in action"""
        destinations = []

        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, action, re.IGNORECASE)
        destinations.extend(urls)

        # Extract domain-like patterns
        domain_pattern = r'\b[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, action, re.IGNORECASE)
        destinations.extend(domains)

        # Extract IP addresses
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ips = re.findall(ip_pattern, action)
        destinations.extend(ips)

        return list(set(destinations))

    def classify_destination(self, destination: str) -> dict:
        dest_lower = destination.lower()

        # Check if internal
        for pattern in self.internal_patterns:
            if re.search(pattern, dest_lower):
                return {
                    "destination": destination,
                    "type": "INTERNAL",
                    "risk": "LOW",
                    "reason": "Internal network destination"
                }

        # Check if known safe
        for pattern in self.known_safe:
            if re.search(pattern, dest_lower):
                return {
                    "destination": destination,
                    "type": "KNOWN_SAFE",
                    "risk": "LOW",
                    "reason": "Known safe cloud provider"
                }

        # Check if suspicious
        for pattern in self.suspicious_patterns:
            if re.search(pattern, dest_lower):
                return {
                    "destination": destination,
                    "type": "SUSPICIOUS",
                    "risk": "CRITICAL",
                    "reason": f"Known suspicious destination pattern detected"
                }

        # Check risky TLDs
        for tld in self.risky_tlds:
            if dest_lower.endswith(tld):
                return {
                    "destination": destination,
                    "type": "RISKY_TLD",
                    "risk": "HIGH",
                    "reason": f"High-risk TLD detected: {tld}"
                }

        # Raw IP address
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', destination):
            return {
                "destination": destination,
                "type": "RAW_IP",
                "risk": "CRITICAL",
                "reason": "Raw IP address — bypasses DNS, highly suspicious"
            }

        # Unknown external
        return {
            "destination": destination,
            "type": "UNKNOWN_EXTERNAL",
            "risk": "HIGH",
            "reason": "Unknown external destination"
        }

    def analyze(self, action: str) -> dict:
        destinations = self.extract_destinations(action)
        has_transfer = any(kw in action.lower() for kw in self.transfer_keywords)

        if not destinations and not has_transfer:
            return {
                "action": action,
                "destinations_found": [],
                "has_transfer_intent": False,
                "highest_risk": "LOW",
                "risk_score_boost": 0,
                "summary": "No external destinations detected"
            }

        classified = [self.classify_destination(d) for d in destinations]
        risks = [c["risk"] for c in classified]

        # Calculate highest risk
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        highest = max(risks, key=lambda r: risk_order.get(r, 0)) if risks else "LOW"

        # Calculate risk boost
        boost = 0
        if highest == "CRITICAL": boost = 40
        elif highest == "HIGH": boost = 25
        elif has_transfer and not destinations: boost = 15

        suspicious = [c for c in classified if c["risk"] in ["HIGH", "CRITICAL"]]

        return {
            "action": action,
            "destinations_found": classified,
            "has_transfer_intent": has_transfer,
            "highest_risk": highest,
            "risk_score_boost": boost,
            "suspicious_destinations": suspicious,
            "summary": self._summarize(classified, has_transfer)
        }

    def _summarize(self, classified: list, has_transfer: bool) -> str:
        if not classified:
            return "Transfer intent detected but no specific destination found"
        suspicious = [c for c in classified if c["risk"] in ["HIGH", "CRITICAL"]]
        if suspicious:
            return f"{len(suspicious)} suspicious destination(s): {', '.join(c['destination'] for c in suspicious)}"
        return f"{len(classified)} destination(s) analyzed — no suspicious destinations"