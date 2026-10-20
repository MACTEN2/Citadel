import re
from pathlib import Path
from pypdf import PdfReader

class InvoiceExtractor:
    """Extracts structured financial metadata from raw PDF text stream."""

    @staticmethod
    def extract_text_from_pdf(pdf_path: Path) -> str:
        """Parses raw text out of a target PDF file."""
        text = ""
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            print(f"[!] Error reading PDF {pdf_path.name}: {e}")
        return text

    @classmethod
    def parse_invoice_data(cls, pdf_path: Path) -> dict:
        """Extracts key invoice elements using robust regular expressions."""
        raw_text = cls.extract_text_from_pdf(pdf_path)

        # Extraction logic matching key financial metadata formats
        vendor_match = re.search(r"Vendor:\s*(.+)", raw_text, re.IGNORECASE)
        inv_id_match = re.search(r"Invoice\s*(?:ID|#)?:\s*([A-Z0-9-]+)", raw_text, re.IGNORECASE)
        date_match = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", raw_text, re.IGNORECASE)
        tax_id_match = re.search(r"Tax\s*ID:\s*([A-Z0-9-]+)", raw_text, re.IGNORECASE)
        
        subtotal_match = re.search(r"Subtotal:\s*\$?([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
        tax_match = re.search(r"Tax:\s*\$?([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
        total_match = re.search(r"Total:\s*\$?([\d,]+\.\d{2})", raw_text, re.IGNORECASE)

        def to_float(match):
            return float(match.group(1).replace(",", "")) if match else 0.0

        return {
            "filename": pdf_path.name,
            "filepath": str(pdf_path),
            "vendor": vendor_match.group(1).strip() if vendor_match else "Unknown Vendor",
            "invoice_id": inv_id_match.group(1).strip() if inv_id_match else "N/A",
            "date": date_match.group(1).strip() if date_match else "N/A",
            "tax_id": tax_id_match.group(1).strip() if tax_id_match else None,
            "subtotal": to_float(subtotal_match),
            "tax": to_float(tax_match),
            "total_amount": to_float(total_match),
            "raw_text": raw_text
        }