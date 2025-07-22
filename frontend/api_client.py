#api_client.py
import os
import requests
from pathlib import Path
from typing import Union, Tuple

# ===========================
# ⚙️ Config
# ===========================
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:5000/verify")
UPLOADS_DIR = Path("downloads")
UPLOADS_DIR.mkdir(exist_ok=True)


# ===========================
# 🔗 Verifier & Customer APIs
# ===========================
def send_verifier_details(verifier_data: dict) -> dict:
    """
    Send verifier metadata to the backend.
    """
    response = requests.post(f"{API_BASE_URL}/verifier", json=verifier_data)
    response.raise_for_status()
    return response.json()


def send_customer_details(customer_data: dict) -> dict:
    """
    Send customer metadata to the backend.
    """
    response = requests.post(f"{API_BASE_URL}/customer", json=customer_data)
    response.raise_for_status()
    return response.json()


def simulate_otp_verification(aadhaar_number: str, mobile_number: str) -> dict:
    """
    Simulate Aadhaar OTP verification with backend's mock endpoint.
    """
    payload = {"aadhaar": aadhaar_number, "mobile": mobile_number}
    response = requests.post(f"{API_BASE_URL}/simulate_otp", json=payload)
    response.raise_for_status()
    return response.json()


# ===========================
# 🔗 Document & Video Upload
# ===========================
def prepare_file(file_input: Union[Tuple[str, bytes, str], object]) -> Tuple[str, bytes, str]:
    """
    Prepare file for uploading:
    - Accepts Streamlit UploadedFile, (filename, bytes, mimetype) tuples, or open file handles.
    - Returns a tuple (filename, file_bytes, mime_type) for requests.
    """
    # Case 1: Streamlit UploadedFile
    if hasattr(file_input, "name") and hasattr(file_input, "read") and hasattr(file_input, "type"):
        return file_input.name, file_input.read(), file_input.type

    # Case 2: (filename, bytes, mimetype) tuple
    if isinstance(file_input, tuple) and len(file_input) == 3:
        return file_input

    # Case 3: Open file handle (e.g., open("file.png", "rb"))
    if hasattr(file_input, "read"):
        filename = getattr(file_input, "name", "uploaded_file")
        file_bytes = file_input.read()
        ext = Path(filename).suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                    ".mp4": "video/mp4", ".avi": "video/x-msvideo", ".webm": "video/webm"}
        mimetype = mime_map.get(ext, "application/octet-stream")
        return filename, file_bytes, mimetype

    raise ValueError(f"Unsupported file input: {type(file_input)}")


def upload_kyc_documents(aadhaar_doc, pan_doc, video_file, name: str, pan: str, aadhaar: str) -> dict:
    """
    Upload Aadhaar, PAN, and KYC video files to the backend.
    Returns JSON response with saved paths.
    """
    files = {
        "aadhaar_doc": prepare_file(aadhaar_doc),
        "pan_doc": prepare_file(pan_doc),
        "video": prepare_file(video_file),
    }
    data = {"name": name, "pan": pan, "aadhaar": aadhaar}
    response = requests.post(f"{API_BASE_URL}/upload_files", files=files, data=data)
    response.raise_for_status()
    return response.json()


# ===========================
# 🔗 KYC Verification & Finalization
# ===========================
def trigger_ocr_and_verification(payload: dict) -> dict:
    """
    Trigger OCR and face verification using uploaded file paths.
    """
    resp = requests.post(f"{API_BASE_URL}/verify_kyc", json=payload)
    if resp.status_code != 200:
        print(f"Server error {resp.status_code}: {resp.text}")
        resp.raise_for_status()
    try:
        return resp.json()
    except requests.exceptions.JSONDecodeError:
        print("Server returned non-JSON response:\n", resp.text)
        raise


def finalize_kyc(kyc_data: dict) -> dict:
    """
    Finalize the KYC process (accept or reject).
    """
    response = requests.post(f"{API_BASE_URL}/finalize_kyc", json=kyc_data)
    response.raise_for_status()
    return response.json()


# ===========================
# 🔗 KYC Report & Logs
# ===========================
def download_report(kyc_id: str) -> Union[Path, None]:
    """
    Download the final PDF report for a given KYC ID.
    Saves it to downloads/ folder and returns the Path or None if not found.
    """
    response = requests.get(f"{API_BASE_URL}/download_report/{kyc_id}", stream=True)
    if response.status_code == 200:
        file_path = UPLOADS_DIR / f"KYC_Report_{kyc_id}.pdf"
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        return file_path
    return None


def check_existing_kyc(aadhaar: str, pan: str) -> dict:
    """
    Check if KYC already exists for the given Aadhaar and PAN.
    """
    payload = {"aadhaar": aadhaar, "pan": pan}
    response = requests.post(f"{API_BASE_URL}/check_existing_kyc", json=payload)
    response.raise_for_status()
    return response.json()
# ===========================
# 🔍 Org Info Lookup
# ===========================
def get_customer_service_info(org_code: str) -> dict:
    """
    Fetch customer service contact info for the organization.
    """
    import sqlite3
    from pathlib import Path

    DB_PATH = Path(__file__).resolve().parents[1] / "backend" / "database" / "verifier_system.db"
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT customer_service_no, customer_service_email 
            FROM organizations 
            WHERE org_code = ?
        """, (org_code,))
        row = cursor.fetchone()

    if row:
        return {
            "customer_service_no": row[0] or "Not Available",
            "customer_service_email": row[1] or "Not Available"
        }
    else:
        return {
            "customer_service_no": "Not Available",
            "customer_service_email": "Not Available"
        }
