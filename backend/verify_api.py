# backend/verify_api.py
from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
from datetime import datetime, timedelta
import traceback
import pandas as pd

from utils.verification_utils import run_face_verification
from utils.ocr_utils import extract_fields_from_image
from utils.db_utils import get_kyc_record, save_kyc_record
from utils.log_utils import generate_log_row, append_kyc_log
from utils.report_utils import generate_pdf_report
from utils.performance_utils import timeit

verify_bp = Blueprint("verify", __name__)

# ===========================
# 📄 Upload KYC Files
# ===========================
@verify_bp.route('/upload_files', methods=['POST'])
def upload_files():
    try:
        aadhaar_doc = request.files.get('aadhaar_doc')
        pan_doc = request.files.get('pan_doc')
        video_file = request.files.get('video')
        name = request.form.get('name')
        pan = request.form.get('pan')
        aadhaar = request.form.get('aadhaar')

        if not all([aadhaar_doc, pan_doc, video_file, name, pan, aadhaar]):
            return jsonify({"error": "Missing required file or field"}), 400

        base_dir = Path(__file__).resolve().parent
        uploads_dir = base_dir / "uploads"
        kyc_dir, video_dir = uploads_dir / "kyc_docs", uploads_dir / "videos"
        kyc_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)

        aadhaar_path = kyc_dir / f"{aadhaar}_aadhaar.png"
        pan_path = kyc_dir / f"{pan}_pan.png"
        video_path = video_dir / f"{aadhaar}_video.mp4"

        aadhaar_doc.save(aadhaar_path)
        pan_doc.save(pan_path)
        video_file.save(video_path)

        return jsonify({
            "status": "uploaded",
            "aadhaar_doc_path": str(aadhaar_path.relative_to(base_dir.parent)),
            "pan_doc_path": str(pan_path.relative_to(base_dir.parent)),
            "video_path": str(video_path.relative_to(base_dir.parent)),
            "name": name,
            "pan": pan,
            "aadhaar": aadhaar,
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error uploading files: {e}"}), 500

# ===========================
# 📄 KYC Verification
# ===========================
@verify_bp.route('/verify_kyc', methods=['POST'])
def verify_kyc():
    try:
        payload = request.json or {}
        base_dir = Path(__file__).resolve().parent.parent
        aadhaar_path = base_dir / payload.get('aadhaar_doc_path', '')
        pan_path = base_dir / payload.get('pan_doc_path', '')
        video_path = base_dir / payload.get('video_path', '')

        for fpath, label in [(aadhaar_path, "Aadhaar"), (pan_path, "PAN"), (video_path, "Video")]:
            if not fpath.exists():
                return jsonify({"error": f"{label} file not found at {fpath}"}), 404

        aadhaar_fields, aadhaar_text, aadhaar_conf = extract_fields_from_image(aadhaar_path)
        pan_fields, pan_text, pan_conf = extract_fields_from_image(pan_path)
        face_result = run_face_verification(aadhaar_path, video_path)

        ocr_verified = (
            aadhaar_fields.get('aadhaar') == payload.get('aadhaar') and
            pan_fields.get('pan') == payload.get('pan')
        )

        result = {
            "kyc_id": f"KYC{datetime.now():%Y%m%d%H%M%S}",
            "customer_name": payload.get("name"),
            "aadhaar": payload.get("aadhaar"),
            "pan": payload.get("pan"),
            "ocr_verified": ocr_verified,
            "aadhaar_conf_score": aadhaar_conf,
            "pan_conf_score": pan_conf,
            "ocr_fields_aadhaar": aadhaar_fields,
            "ocr_fields_pan": pan_fields,
            "raw_aadhaar_text": aadhaar_text,
            "raw_pan_text": pan_text,
            **face_result,
            "message": "KYC verification completed."
        }
        return jsonify(result), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error during verification: {e}"}), 500

# ===========================
# ✅ Finalize KYC
# ===========================
@verify_bp.route('/finalize_kyc', methods=['POST'])
@timeit
def finalize_kyc():
    try:
        data = request.json or {}
        kyc_id = data.get('kyc_id', f"KYC{datetime.now():%Y%m%d%H%M%S}")
        decision = data.get('status', 'Accepted')

        #downloads_dir = Path(__file__).resolve().parent.parent / "downloads"
        #downloads_dir.mkdir(parents=True, exist_ok=True)
        #report_path = downloads_dir / f"KYC_Report_{kyc_id}.pdf"
        

        reports_dir = Path(__file__).resolve().parents[1] / "frontend" / "uploads" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / f"KYC_Report_{kyc_id}.pdf"

        generate_pdf_report(data, report_path)

        log_row = generate_log_row(
            customer_info={
                "name": data.get("customer_name"),
                "aadhaar": data.get("aadhaar"),
                "pan": data.get("pan"),
                "mobile": data.get("mobile"),
                "email": data.get("email")
            },
            verifier_info={
                "verifier_name": data.get("verifier_name"),
                "organization": data.get("organization"),
                "department": data.get("department"),
                "employee_id": data.get("employee_id"),
                "verifier_contact": data.get("verifier_contact"),
                "verifier_email": data.get("verifier_email"),
            },
            kyc_type=data.get("kyc_type", "new_kyc"),
            kyc_id=kyc_id,
            results=data,
            decision=decision
        )

        append_kyc_log(log_row)
        save_kyc_record(log_row)

        return jsonify({"status": "ok", "kyc_id": kyc_id, "report_path": str(report_path)}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error finalizing KYC: {e}"}), 500

# ===========================
# 📄 Download Report
# ===========================
@verify_bp.route('/download_report/<kyc_id>', methods=['GET'])
def download_report(kyc_id):
    #report_path = Path(__file__).resolve().parent.parent / "downloads" / f"KYC_Report_{kyc_id}.pdf"
    report_path = Path(__file__).resolve().parents[1] / "frontend" / "uploads" / "reports" / f"KYC_Report_{kyc_id}.pdf"
    
    if report_path.exists():
        return send_file(report_path, as_attachment=True)
    return jsonify({"error": f"Report {kyc_id} not found"}), 404

@verify_bp.route('/check_existing_kyc', methods=['POST'])
def check_existing_kyc():
    try:
        data = request.json or {}
        aadhaar, pan = data.get("aadhaar"), data.get("pan")
        record = get_kyc_record(aadhaar, pan)

        if not record:
            return jsonify({
                "status": "new_user",
                "message": "No existing KYC found. Please proceed with fresh KYC."
            }), 200

        last_kyc_date_str = record["last_kyc_date"]
        risk_category = record["risk_category"]

        if not last_kyc_date_str:
            return jsonify({
                "status": "rekYC_due",
                "message": "Last KYC date is missing or empty. Please proceed with fresh KYC."
            }), 200

        try:
            last_kyc_dt = datetime.fromisoformat(last_kyc_date_str)
        except ValueError:
            try:
                last_kyc_dt = datetime.strptime(last_kyc_date_str, "%Y-%m-%d")
            except ValueError:
                return jsonify({
                    "status": "rekYC_due",
                    "message": f"Invalid last KYC date format: '{last_kyc_date_str}'. Please proceed with re-KYC."
                }), 200

        expiry_days = {"Low": 365, "Medium": 180, "High": 90}.get(risk_category, 365)
        valid_until = last_kyc_dt + timedelta(days=expiry_days)

        days_since_kyc = (datetime.now() - last_kyc_dt).days
        months, days = days_since_kyc // 30, days_since_kyc % 30

        if datetime.now() <= valid_until:
            return jsonify({
                "status": "valid_kyc",
                "risk_category": risk_category,
                "last_kyc_date": last_kyc_dt.isoformat(),
                "kyc_age": f"{months} months and {days} days ago",
                "valid_until": valid_until.isoformat(),
                "message": (
                    f"KYC done on {last_kyc_dt.strftime('%Y-%m-%d')} "
                    f"({months} months {days} days ago), "
                    f"Risk Category: {risk_category}, "
                    f"valid until {valid_until.strftime('%Y-%m-%d')}."
                )
            }), 200
        else:
            return jsonify({
                "status": "rekYC_due",
                "risk_category": risk_category,
                "last_kyc_date": last_kyc_dt.isoformat(),
                "kyc_age": f"{months} months and {days} days ago",
                "valid_until": valid_until.isoformat(),
                "message": (
                    f"KYC expired. Last KYC was on {last_kyc_dt.strftime('%Y-%m-%d')} "
                    f"({months} months {days} days ago), "
                    f"Risk Category: {risk_category}, "
                    f"KYC expired on {valid_until.strftime('%Y-%m-%d')}. Please proceed with re-KYC."
                )
            }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error checking KYC: {e}"}), 500

# ===========================
# 📄 Download KYC Logs
# ===========================
@verify_bp.route('/download_kyc_log_csv', methods=['GET'])
def download_kyc_log_csv():
    log_path = Path(__file__).resolve().parent / "uploads/logs/kyc_log.csv"
    if log_path.exists():
        return send_file(log_path, as_attachment=True, download_name='kyc_log.csv', mimetype='text/csv')
    return jsonify({"error": "KYC log CSV not found"}), 404

@verify_bp.route('/download_kyc_log_xlsx', methods=['GET'])
def download_kyc_log_xlsx():
    log_path = Path(__file__).resolve().parent / "uploads/logs/kyc_log.csv"
    if log_path.exists():
        df = pd.read_csv(log_path)
        xlsx_path = log_path.with_suffix(".xlsx")
        df.to_excel(xlsx_path, index=False)
        return send_file(xlsx_path, as_attachment=True, download_name='kyc_log.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return jsonify({"error": "KYC log CSV not found"}), 404

# ===========================
# 🔐 Save Verifier Details
# ===========================
@verify_bp.route('/verifier', methods=['POST'])
def verifier():
    try:
        data = request.json or {}
        return jsonify({"status": "ok", "message": "Verifier details saved", "data": data}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error saving verifier details: {e}"}), 500

# ===========================
# 🔄 Simulate OTP
# ===========================
@verify_bp.route('/simulate_otp', methods=['POST'])
def simulate_otp():
    payload = request.json or {}
    return jsonify({
        "status": "success",
        "message": f"OTP sent successfully (simulated) for Aadhaar {payload.get('aadhaar')}",
        "payload": payload
    }), 200
