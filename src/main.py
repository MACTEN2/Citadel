import os
import sys
import logging
import shutil
import pandas as pd
from pathlib import Path
from extractor import InvoiceExtractor
from validator import PolicyValidator

# Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "policy_rules.json"
INCOMING_DIR = BASE_DIR / "data" / "incoming_invoices"
PROCESSED_DIR = BASE_DIR / "data" / "processed_ledgers"
QUARANTINE_DIR = BASE_DIR / "data" / "quarantine_flagged"
LOG_FILE = BASE_DIR / "logs" / "citadel_audit.log"

# Logging Configuration
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_citadel_audit():
    print("=" * 60)
    print("   CITADEL ENGINE: AUTOMATED DOCUMENT & COMPLIANCE AUDITOR   ")
    print("=" * 60)
    
    validator = PolicyValidator(CONFIG_FILE)
    pdf_files = list(INCOMING_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"\n[*] No pending PDF invoices found in '{INCOMING_DIR.relative_to(BASE_DIR)}'.")
        print("    Place sample PDF invoices into the incoming directory and re-run.")
        return

    print(f"\n[+] Found {len(pdf_files)} document(s) for audit processing...\n")

    approved_records = []
    quarantined_records = []

    for pdf_path in pdf_files:
        record = InvoiceExtractor.parse_invoice_data(pdf_path)
        is_compliant, violations = validator.evaluate_compliance(record)

        if is_compliant:
            print(f"[APPROVED] {pdf_path.name:<25} | Vendor: {record['vendor']:<20} | Amount: ${record['total_amount']:.2f}")
            logging.info(f"APPROVED: {pdf_path.name} | Vendor: {record['vendor']} | Amount: ${record['total_amount']}")
            approved_records.append(record)
        else:
            reason_str = "; ".join(violations)
            print(f"[FLAGGED]  {pdf_path.name:<25} | Reason: {reason_str}")
            logging.warning(f"FLAGGED: {pdf_path.name} | Violations: {reason_str}")
            record["violations"] = reason_str
            quarantined_records.append(record)
            
            # Quarantine the file
            shutil.move(str(pdf_path), str(QUARANTINE_DIR / pdf_path.name))

    # Export Approved Ledger
    if approved_records:
        df_approved = pd.DataFrame(approved_records)
        df_approved.drop(columns=["raw_text", "filepath"], inplace=True, errors="ignore")
        output_excel = PROCESSED_DIR / "master_approved_ledger.xlsx"
        output_csv = PROCESSED_DIR / "master_approved_ledger.csv"
        
        df_approved.to_excel(output_excel, index=False)
        df_approved.to_csv(output_csv, index=False)
        print(f"\n[✓] Master Approved Ledger exported to '{output_excel.relative_to(BASE_DIR)}'")

    # Export Flagged Audit Summary
    if quarantined_records:
        df_flagged = pd.DataFrame(quarantined_records)
        df_flagged.drop(columns=["raw_text", "filepath"], inplace=True, errors="ignore")
        flagged_csv = QUARANTINE_DIR / "quarantine_audit_report.csv"
        df_flagged.to_csv(flagged_csv, index=False)
        print(f"[!] Quarantine Audit Summary saved to '{flagged_csv.relative_to(BASE_DIR)}'")

    print(f"\n[✓] Citadel Audit Execution Complete. Logs updated at '{LOG_FILE.relative_to(BASE_DIR)}'.")

if __name__ == "__main__":
    run_citadel_audit()