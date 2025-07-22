# backend/utils/report_utils.py
from fpdf import FPDF
from pathlib import Path
from datetime import datetime

from utils.performance_utils import timeit

@timeit
class PDF(FPDF):
    def header(self):
        # Add logo if exists
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            self.image(str(logo_path), 10, 8, 33)
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, "KYC Verification Report", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, title, ln=True, fill=True)

    def section_body(self, data_dict):
        self.set_font("Arial", size=11)
        for label, value in data_dict.items():
            if value not in (None, "", "Not Available"):
                self.cell(60, 8, f"{label}:", border=1)
                self.cell(0, 8, str(value), border=1, ln=True)

def generate_pdf_report(data: dict, save_path: Path) -> str:
    pdf = PDF()
    pdf.add_page()

    # Customer Info
    pdf.section_title("Customer Details")
    customer_fields = {
        "KYC ID": data.get("kyc_id"),
        "Customer Name": data.get("customer_name"),
        "Aadhaar Number": data.get("aadhaar"),
        "PAN Number": data.get("pan"),
        "OCR Verified": data.get("ocr_verified"),
        "Face Match Score": data.get("face_match_score"),
        "Blinks Count": data.get("blinks"),
        "Smile Detected": data.get("smile"),
        "Max Head Angle": data.get("max_angle"),
        "Decision": data.get("status"),
        "Message": data.get("message"),
    }
    pdf.section_body(customer_fields)

    # Verifier Info
    pdf.ln(5)
    pdf.section_title("Verifier Details")
    verifier_fields = {
        "Verifier Name": data.get("verifier_name"),
        "Organization": data.get("organization"),
        "Department": data.get("department"),
        "Employee ID": data.get("employee_id"),
        #"Verifier Contact": data.get("verifier_contact"),
        #"Verifier Email": data.get("verifier_email"),
    }
    pdf.section_body(verifier_fields)

    # Customer Support Info
    pdf.ln(5)
    pdf.section_title("Customer Support")
    support_fields = {
        "Phone": data.get("customer_service_no", "N/A"),
        "Email": data.get("customer_service_email", "N/A")
    }
    pdf.section_body(support_fields)

    # Signature placeholder
    pdf.ln(10)
    pdf.cell(0, 10, "Verifier Signature: ____________________", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f"Report Generated on {datetime.now():%Y-%m-%d %H:%M:%S}", ln=True, align='R')

    pdf.output(str(save_path))
    return str(save_path)
