# CITADEL
enterprise-grade automated document audit, invoice processing, and policy compliance verification platform designed to eliminate manual cross-departmental administrative overhead.


## 🚀 Core Features
- **Automated Text Extraction (`extractor.py`)**: Parses incoming unstructured PDF invoices using robust pattern matching to pull key financial metadata (Vendor, Invoice ID, Date, Tax ID, Subtotal, Tax, Total Amount).
- **Compliance Policy Engine (`validator.py`)**: Evaluates extracted records against strict corporate rules defined in JSON config files (e.g., auto-approval limits, mandatory tax IDs, mathematical line-item integrity checking).
- **Smart Data Routing (`main.py`)**: Automatically sorts verified compliant invoices into structured Excel/CSV ledgers while securely quarantining non-compliant records for administrative review.
- **Traceable Audit Logging**: Records complete execution histories and warnings into a dedicated audit log file.


## 🛠️ Tech Stack & Requirements
- **Language**: Python 3.14 (or compatible 3.x)
- **Libraries**: `pypdf`, `pandas`, `openpyxl`, `pydantic`
- **Environment**: macOS (Zsh Terminal) / Virtual Environment (`venv`)


## ⚙️ Setup & Execution Guide

### 1. Initialize Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

## Project Directory Architecture
Plaintext
citadel-engine/
├── config/
│   └── policy_rules.json       # Spending limits, tax rules, and compliance thresholds
├── data/
│   ├── incoming_invoices/      # Raw unprocessed PDF documents
│   ├── processed_ledgers/      # Verified master Excel/CSV reports
│   └── quarantine_flagged/     # Flagged documents failing compliance checks
├── logs/
│   └── citadel_audit.log       # System audit and error traceability logs
├── src/
│   ├── __init__.py
│   ├── extractor.py            # PDF parsing & regex field extraction logic
│   ├── validator.py            # Compliance policy rule engine
│   └── main.py                 # Core CLI orchestrator & workflow runner
├── requirements.txt            # Project Python dependencies
└── README.md                   # Operational project documentation