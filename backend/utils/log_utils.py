# backend/utils/log_utils.py

import pandas as pd
from pathlib import Path
from datetime import datetime

# ✅ Absolute log file path relative to project
LOG_PATH = Path(__file__).resolve().parents[2]/"frontend"/"uploads"/"logs"/"kyc_log.csv"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def append_kyc_log(row: dict) -> dict:
    """
    Append a new KYC log entry to the CSV log.
    Creates the file with header if it doesn't exist.
    Returns the saved row.
    """
    df_new = pd.DataFrame([row])
    if LOG_PATH.exists():
        df_new.to_csv(LOG_PATH, mode="a", index=False, header=False, encoding="utf-8")
    else:
        df_new.to_csv(LOG_PATH, index=False, header=True, encoding="utf-8")
    print(f"✅ Appended KYC log entry to {LOG_PATH}")
    return row

def get_all_logs() -> pd.DataFrame:
    """
    Read and return all KYC log entries as a DataFrame.
    Returns empty DataFrame if log file doesn't exist.
    """
    if LOG_PATH.exists():
        return pd.read_csv(LOG_PATH)
    return pd.DataFrame()

def generate_log_row(
    customer_info: dict,
    verifier_info: dict,
    kyc_type: str,
    kyc_id: str,
    results: dict,
    decision: str,
    risk_category: str = "Low",
    last_kyc_date: str = "",
    profiler_file: str = "",  # 👈 ADD THIS PARAMETER
) -> dict:
    """
    Generate a dictionary with fixed columns for consistent CSV logs.
    Missing fields use sensible defaults.
    """
    return {
        # ✅ Metadata
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "KYC Type": kyc_type,
        "KYC ID": kyc_id,
        "Decision": decision,

        # ✅ Verifier Details
        "Verifier": verifier_info.get("verifier_name", ""),
        "Organization": verifier_info.get("organization", ""),
        "Department": verifier_info.get("department", ""),
        "Employee ID": verifier_info.get("employee_id", ""),
        "Verifier Contact": verifier_info.get("verifier_contact", ""),
        "Verifier Email": verifier_info.get("verifier_email", ""),

        # ✅ Customer Details
        "Customer Name": customer_info.get("name", ""),
        "Aadhaar": customer_info.get("aadhaar", ""),
        "PAN": customer_info.get("pan", ""),
        "Mobile": customer_info.get("mobile", ""),
        "Email": customer_info.get("email", ""),

        # ✅ KYC Risk Info
        "Risk Category": risk_category,
        "Last KYC Date": last_kyc_date,

        # ✅ OCR Results
        "OCR Verified": results.get("ocr_verified", False),
        "Aadhaar Confidence": results.get("aadhaar_conf_score", 0),
        "PAN Confidence": results.get("pan_conf_score", 0),

        # ✅ Face Verification Results
        "Face Match Score": results.get("score", 0),
        "Blinks": results.get("blinks", 0),
        "Max Face Angle": results.get("max_angle", 0),
        "Smile Detected": results.get("smile", False),

        # ✅ Profiler Document
        "Profiler File": profiler_file,  # 👈 ADD THIS FIELD TO LOG ROW
    }
