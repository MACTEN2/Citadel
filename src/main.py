import os
import sys
import json
import logging
import shutil
import pandas as pd
from pathlib import Path
from pypdf import PdfWriter
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("=" * 65)
    print("      🛡️  CITADEL ENGINE: ENTERPRISE COMPLIANCE & AUDIT SUITE      ")
    print("=" * 65)

def run_citadel_audit():
    print("\n[+] Executing Automated Document Compliance Audit...")
    validator = PolicyValidator(CONFIG_FILE)
    pdf_files = list(INCOMING_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"\n[!] No pending PDF invoices found in '{INCOMING_DIR.relative_to(BASE_DIR)}'.")
        print("    Use option [2] from the menu to generate a sample invoice first.")
        input("\nPress Enter to return to main menu...")
        return

    print(f"\n[+] Found {len(pdf_files)} document(s) for processing...\n")

    approved_records = []
    quarantined_records = []

    for pdf_path in pdf_files:
        record = InvoiceExtractor.parse_invoice_data(pdf_path)
        is_compliant, violations = validator.evaluate_compliance(record)

        if is_compliant:
            print(f"  [APPROVED] {pdf_path.name:<22} | Vendor: {record['vendor']:<18} | Amount: ${record['total_amount']:.2f}")
            logging.info(f"APPROVED: {pdf_path.name} | Vendor: {record['vendor']} | Amount: ${record['total_amount']}")
            approved_records.append(record)
        else:
            reason_str = "; ".join(violations)
            print(f"  [FLAGGED]  {pdf_path.name:<22} | Reason: {reason_str}")
            logging.warning(f"FLAGGED: {pdf_path.name} | Violations: {reason_str}")
            record["violations"] = reason_str
            quarantined_records.append(record)
            shutil.move(str(pdf_path), str(QUARANTINE_DIR / pdf_path.name))

    if approved_records:
        df_approved = pd.DataFrame(approved_records)
        df_approved.drop(columns=["raw_text", "filepath"], inplace=True, errors="ignore")
        output_excel = PROCESSED_DIR / "master_approved_ledger.xlsx"
        output_csv = PROCESSED_DIR / "master_approved_ledger.csv"
        df_approved.to_excel(output_excel, index=False)
        df_approved.to_csv(output_csv, index=False)
        print(f"\n[✓] Master Approved Ledger exported to '{output_excel.relative_to(BASE_DIR)}'")

    if quarantined_records:
        df_flagged = pd.DataFrame(quarantined_records)
        df_flagged.drop(columns=["raw_text", "filepath"], inplace=True, errors="ignore")
        flagged_csv = QUARANTINE_DIR / "quarantine_audit_report.csv"
        df_flagged.to_csv(flagged_csv, index=False)
        print(f"[!] Quarantine Audit Summary saved to '{flagged_csv.relative_to(BASE_DIR)}'")

    print(f"\n[✓] Audit Complete. Logs updated at '{LOG_FILE.relative_to(BASE_DIR)}'.")
    input("\nPress Enter to return to main menu...")

def generate_mock_invoice():
    print("\n[+] Generating Mock Test Invoice...")
    filename = f"invoice_test_{len(list(INCOMING_DIR.glob('*.pdf'))) + 1}.pdf"
    filepath = INCOMING_DIR / filename

    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(filepath, 'wb') as f:
        writer.write(f)

    print(f"[✓] Sample invoice generated at: '{filepath.relative_to(BASE_DIR)}'")
    print("    (Note: Drop real text-based PDFs or use this blank template to test workflow routing).")
    input("\nPress Enter to return to main menu...")

def view_audit_logs():
    print("\n" + "=" * 50)
    print("         RECENT SYSTEM AUDIT LOGS         ")
    print("=" * 50)
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            recent = lines[-15:] if len(lines) >= 15 else lines
            for line in recent:
                print(line.strip())
    else:
        print("[*] No audit logs recorded yet.")
    print("=" * 50)
    input("\nPress Enter to return to main menu...")

def inspect_policy_rules():
    print("\n" + "=" * 50)
    print("         CURRENT ENTERPRISE POLICY RULES         ")
    print("=" * 50)
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            rules = json.load(f)
            print(json.dumps(rules, indent=4))
    else:
        print("[!] Policy configuration file not found.")
    print("=" * 50)
    input("\nPress Enter to return to main menu...")

def main_menu():
    while True:
        clear_screen()
        print_banner()
        print("\n[1] Run Document & Compliance Audit")
        print("[2] Generate Sample Test Invoice PDF")
        print("[3] View Recent Audit Logs")
        print("[4] Inspect Active Enterprise Policy Rules")
        print("[5] Exit Citadel Engine")
        
        choice = input("\nSelect an option [1-5]: ").strip()

        if choice == "1":
            run_citadel_audit()
        elif choice == "2":
            generate_mock_invoice()
        elif choice == "3":
            view_audit_logs()
        elif choice == "4":
            inspect_policy_rules()
        elif choice == "5":
            print("\nShutting down Citadel Engine. Stay secure!")
            sys.exit(0)
        else:
            input("\n[!] Invalid selection. Press Enter to try again...")

if __name__ == "__main__":
    main_menu()