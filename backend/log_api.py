# backend/log_api.py

from flask import Blueprint, request, jsonify
from utils.log_utils import append_kyc_log, generate_log_row, get_all_logs

log_bp = Blueprint("log", __name__)

@log_bp.route('/save', methods=['POST'])
def save_log():
    """
    Save a new KYC log entry.
    Expects JSON with:
        - customer_info (dict)
        - verifier_info (dict)
        - kyc_type (str)
        - kyc_id (str)
        - results (dict from face verification)
        - decision (str)
    """
    data = request.json

    required = ['customer_info', 'verifier_info', 'kyc_type', 'kyc_id', 'results', 'decision']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        row = generate_log_row(
            customer_info=data["customer_info"],
            verifier_info=data["verifier_info"],
            kyc_type=data["kyc_type"],
            kyc_id=data["kyc_id"],
            results=data["results"],
            decision=data["decision"]
        )
        append_kyc_log(row)
        return jsonify({"status": "KYC record logged", "record": row}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@log_bp.route('/all', methods=['GET'])
def get_logs():
    """
    Returns all logged KYC entries as JSON.
    """
    try:
        df = get_all_logs()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

