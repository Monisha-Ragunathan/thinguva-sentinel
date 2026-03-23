from sentinel.compliance_report import ComplianceReportGenerator

def test_generate_report():
    generator = ComplianceReportGenerator(
        db_path="sentinel_audit.db",
        policy_file="policies/sample.yaml"
    )
    path = generator.generate(output_path="thinguva_sentinel_report.pdf")
    print(f"✓ Report generated: {path}")

if __name__ == "__main__":
    print("\n=== Thinguva Sentinel — Compliance Report Test ===\n")
    test_generate_report()
    print("\n=== Done ===")