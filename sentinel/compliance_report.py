from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from sentinel.audit import AuditLogger
from sentinel.policy import PolicyEngine
import json

class ComplianceReportGenerator:
    def __init__(self, db_path: str = "sentinel_audit.db", policy_file: str = None):
        self.audit = AuditLogger(db_path=db_path)
        self.policy = PolicyEngine(policy_file) if policy_file else None

        # Colors
        self.purple = colors.HexColor("#6c63ff")
        self.dark = colors.HexColor("#1a1d2e")
        self.green = colors.HexColor("#48bb78")
        self.red = colors.HexColor("#fc8181")
        self.amber = colors.HexColor("#f6ad55")
        self.light_gray = colors.HexColor("#f7f8fc")
        self.mid_gray = colors.HexColor("#e2e8f0")

    def _styles(self):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="Title1",
            fontSize=24,
            fontName="Helvetica-Bold",
            textColor=colors.white,
            alignment=TA_LEFT,
            spaceAfter=4
        ))
        styles.add(ParagraphStyle(
            name="Subtitle1",
            fontSize=11,
            fontName="Helvetica",
            textColor=colors.HexColor("#a0aec0"),
            alignment=TA_LEFT,
            spaceAfter=2
        ))
        styles.add(ParagraphStyle(
            name="SectionHeader",
            fontSize=13,
            fontName="Helvetica-Bold",
            textColor=self.dark,
            spaceBefore=16,
            spaceAfter=8
        ))
        styles.add(ParagraphStyle(
            name="Body1",
            fontSize=10,
            fontName="Helvetica",
            textColor=colors.HexColor("#4a5568"),
            spaceAfter=4,
            leading=16
        ))
        styles.add(ParagraphStyle(
            name="Small1",
            fontSize=8,
            fontName="Helvetica",
            textColor=colors.HexColor("#718096"),
        ))
        return styles

    def generate(self, output_path: str = None, limit: int = 1000) -> str:
        if not output_path:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = f"thinguva_sentinel_report_{timestamp}.pdf"

        logs = self.audit.get_logs(limit=limit)
        total = len(logs)
        blocked = len([l for l in logs if l["status"] == "BLOCKED"])
        allowed = len([l for l in logs if l["status"] == "ALLOWED"])
        loops = len([l for l in logs if l["status"] == "LOOP_DETECTED"])
        anomalies = len([l for l in logs if l["status"] == "ANOMALY"])
        block_rate = f"{(blocked/total*100):.1f}%" if total > 0 else "0%"

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = self._styles()
        story = []

        # Header banner
        header_data = [[
            Paragraph("Thinguva Sentinel", styles["Title1"]),
            Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Subtitle1"])
        ]]
        header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), self.dark),
            ("PADDING", (0,0), (-1,-1), 16),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (1,0), (1,0), "RIGHT"),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 8))

        subtitle_data = [[
            Paragraph("Agent Governance &amp; Compliance Report", styles["Subtitle1"])
        ]]
        subtitle_table = Table(subtitle_data, colWidths=[6.5*inch])
        subtitle_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), self.purple),
            ("PADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(subtitle_table)
        story.append(Spacer(1, 20))

        # Executive summary
        story.append(Paragraph("Executive Summary", styles["SectionHeader"]))
        story.append(HRFlowable(width="100%", thickness=1, color=self.mid_gray))
        story.append(Spacer(1, 8))

        summary_data = [
            ["Metric", "Value", "Status"],
            ["Total Agent Actions", str(total), "—"],
            ["Actions Allowed", str(allowed), "✓ Normal"],
            ["Actions Blocked", str(blocked), "⚠ Review" if blocked > 0 else "✓ Clean"],
            ["Loops Detected", str(loops), "⚠ Review" if loops > 0 else "✓ Clean"],
            ["Anomalies Detected", str(anomalies), "⚠ Review" if anomalies > 0 else "✓ Clean"],
            ["Block Rate", block_rate, "⚠ High" if (total > 0 and blocked/total > 0.3) else "✓ Normal"],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), self.dark),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("PADDING", (0,0), (-1,-1), 10),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [self.light_gray, colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, self.mid_gray),
            ("TEXTCOLOR", (2,2), (2,2), self.green),
            ("TEXTCOLOR", (2,3), (2,3), self.red if blocked > 0 else self.green),
            ("TEXTCOLOR", (2,4), (2,4), self.amber if loops > 0 else self.green),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Policy rules
        if self.policy and self.policy.rules:
            story.append(Paragraph("Active Policy Rules", styles["SectionHeader"]))
            story.append(HRFlowable(width="100%", thickness=1, color=self.mid_gray))
            story.append(Spacer(1, 8))

            policy_data = [["Pattern", "Effect", "Reason"]]
            for rule in self.policy.rules:
                policy_data.append([
                    rule.get("pattern", ""),
                    rule.get("effect", "").upper(),
                    rule.get("reason", "")
                ])

            policy_table = Table(policy_data, colWidths=[1.5*inch, 1*inch, 4*inch])
            policy_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), self.dark),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 9),
                ("PADDING", (0,0), (-1,-1), 8),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [self.light_gray, colors.white]),
                ("GRID", (0,0), (-1,-1), 0.5, self.mid_gray),
                ("TEXTCOLOR", (1,1), (1,-1), self.red),
            ]))
            story.append(policy_table)
            story.append(Spacer(1, 20))

        # Audit log
        story.append(Paragraph("Full Audit Log", styles["SectionHeader"]))
        story.append(HRFlowable(width="100%", thickness=1, color=self.mid_gray))
        story.append(Spacer(1, 8))

        if logs:
            log_data = [["Timestamp", "Tool/Action", "Status", "Reason"]]
            for log in logs[:50]:
                try:
                    action = json.loads(log["action"])
                    tool = action.get("tool", action.get("args", "")[:30])
                except:
                    tool = str(log["action"])[:30]

                log_data.append([
                    log["timestamp"].replace("T", " ")[:19],
                    str(tool)[:35],
                    log["status"],
                    (log["reason"] or "—")[:40]
                ])

            log_table = Table(log_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 2.3*inch])
            log_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), self.dark),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("PADDING", (0,0), (-1,-1), 6),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [self.light_gray, colors.white]),
                ("GRID", (0,0), (-1,-1), 0.5, self.mid_gray),
            ]))
            story.append(log_table)
        else:
            story.append(Paragraph("No audit logs found.", styles["Body1"]))

        story.append(Spacer(1, 20))

        # Footer
        footer_data = [[
            Paragraph(
                "This report was generated by Thinguva Sentinel — Agent Governance Platform. "
                "All actions are cryptographically hashed and tamper-proof.",
                styles["Small1"]
            )
        ]]
        footer_table = Table(footer_data, colWidths=[6.5*inch])
        footer_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), self.light_gray),
            ("PADDING", (0,0), (-1,-1), 10),
            ("BOX", (0,0), (-1,-1), 0.5, self.mid_gray),
        ]))
        story.append(footer_table)

        doc.build(story)
        print(f"[Thinguva Sentinel] Compliance report generated: {output_path}")
        return output_path