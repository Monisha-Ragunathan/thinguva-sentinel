import httpx
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

class AlertSystem:
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        email_config: Optional[dict] = None,
        webhook_url: Optional[str] = None
    ):
        self.slack_webhook = slack_webhook
        self.email_config = email_config
        self.webhook_url = webhook_url
        self.alert_history = []

    def _format_message(self, event: dict) -> str:
        status = event.get("status", "UNKNOWN")
        tool = event.get("tool", "unknown")
        reason = event.get("reason", "")
        timestamp = datetime.utcnow().isoformat()

        icons = {
            "BLOCKED": "🚫",
            "LOOP_DETECTED": "🔄",
            "ANOMALY": "⚠️",
            "REJECTED": "❌"
        }
        icon = icons.get(status, "ℹ️")

        return (
            f"{icon} *Thinguva Sentinel Alert*\n"
            f"Status   : {status}\n"
            f"Tool     : {tool}\n"
            f"Reason   : {reason}\n"
            f"Time     : {timestamp}"
        )

    def send_slack(self, event: dict) -> bool:
        if not self.slack_webhook:
            print("[Thinguva Sentinel] No Slack webhook configured")
            return False
        try:
            message = self._format_message(event)
            payload = {"text": message}
            response = httpx.post(
                self.slack_webhook,
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print("[Thinguva Sentinel] Slack alert sent")
                return True
            else:
                print(f"[Thinguva Sentinel] Slack alert failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[Thinguva Sentinel] Slack error: {e}")
            return False

    def send_webhook(self, event: dict) -> bool:
        if not self.webhook_url:
            print("[Thinguva Sentinel] No webhook URL configured")
            return False
        try:
            payload = {
                "source": "thinguva_sentinel",
                "timestamp": datetime.utcnow().isoformat(),
                "event": event
            }
            response = httpx.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            if response.status_code in [200, 201, 204]:
                print("[Thinguva Sentinel] Webhook alert sent")
                return True
            else:
                print(f"[Thinguva Sentinel] Webhook failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[Thinguva Sentinel] Webhook error: {e}")
            return False

    def send_email(self, event: dict) -> bool:
        if not self.email_config:
            print("[Thinguva Sentinel] No email config provided")
            return False
        try:
            cfg = self.email_config
            msg = MIMEMultipart()
            msg["From"] = cfg["from"]
            msg["To"] = cfg["to"]
            msg["Subject"] = f"[Thinguva Sentinel] Alert — {event.get('status', 'EVENT')}"

            body = self._format_message(event).replace("*", "")
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(cfg["smtp_host"], cfg.get("smtp_port", 587)) as server:
                server.starttls()
                server.login(cfg["username"], cfg["password"])
                server.send_message(msg)

            print("[Thinguva Sentinel] Email alert sent")
            return True
        except Exception as e:
            print(f"[Thinguva Sentinel] Email error: {e}")
            return False

    def alert(self, event: dict):
        """Send alert through all configured channels"""
        self.alert_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event
        })

        # Always print to console
        message = self._format_message(event)
        print("\n" + "="*50)
        print(message)
        print("="*50 + "\n")

        # Send to configured channels
        if self.slack_webhook:
            self.send_slack(event)
        if self.webhook_url:
            self.send_webhook(event)
        if self.email_config:
            self.send_email(event)

    def get_history(self) -> list:
        return self.alert_history