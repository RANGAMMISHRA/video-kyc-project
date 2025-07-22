# backend/report_api.py

from flask import Blueprint, request, jsonify, send_file
from utils.report_utils import generate_pdf_report
from pathlib import Path
from datetime import datetime

report_bp = Blueprint("report", __name__)

@report_bp.route('/generate', methods=['POST'])
def generate_report():
    """
    Generates and returns a downloadable PDF report.
    Expects JSON with keys like:
        - Customer Name, Aadhaar, PAN, KYC ID, Decision, Face Match Score, Verifier, etc.
    """
    data = request.json
    if not data or "KYC ID" not in data or "Customer Name" not in data:
        return {"error": "Missing required fields"}, 400

    name = data.get("Customer Name").replace(" ", "_")
    kyc_id = data.get("KYC ID")
    file_name = f"{name}_{kyc_id}.pdf"

    save_path = Path("uploads/logs") / file_name
    save_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        generate_pdf_report(data, save_path)
        return send_file(str(save_path), as_attachment=True, download_name=file_name)
    except Exception as e:
        return {"error": str(e)}, 500
