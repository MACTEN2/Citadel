import json
from pathlib import Path

class PolicyValidator:
    """Evaluates extracted document records against enterprise policy rules."""

    def __init__(self, config_path: Path):
        with open(config_path, "r") as f:
            self.rules = json.load(f)

    def evaluate_compliance(self, record: dict) -> tuple[bool, list[str]]:
        """
        Validates invoice against spending limits, tax IDs, and mathematical consistency.
        Returns (is_compliant, list_of_violations).
        """
        violations = []

        # Rule 1: Spending Limit Audit
        max_limit = self.rules.get("max_auto_approve_amount", 2500.00)
        if record["total_amount"] > max_limit:
            violations.append(f"Exceeds max auto-approval threshold (${record['total_amount']:.2f} > ${max_limit:.2f})")

        # Rule 2: Tax ID Compliance Verification
        if self.rules.get("require_tax_id", True) and not record["tax_id"]:
            violations.append("Missing required Tax ID for compliance logging")

        # Rule 3: Approved Vendor Rules
        if self.rules.get("flag_unapproved_vendors", False):
            approved = self.rules.get("approved_vendors", [])
            if record["vendor"] not in approved:
                violations.append(f"Vendor '{record['vendor']}' is not in pre-approved enterprise vendor list")

        # Rule 4: Mathematical Validation ($\text{Subtotal} + \text{Tax} = \text{Total}$)
        calculated_total = round(record["subtotal"] + record["tax"], 2)
        if abs(calculated_total - record["total_amount"]) > 0.01 and record["total_amount"] > 0:
            violations.append(f"Math Discrepancy: Subtotal (${record['subtotal']:.2f}) + Tax (${record['tax']:.2f}) != Total (${record['total_amount']:.2f})")

        is_compliant = len(violations) == 0
        return is_compliant, violations