#backend/utils/db_utils.py
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import pandas as pd  # ✅ Add this at the top



# ✅ Absolute path to SQLite DB file
# ✅ Save DB in 'database' folder at the root of project
DB_PATH = Path(__file__).resolve().parents[1] / "database" / "kyc_records.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # ensure folder exists

def init_db():
    """
    Initialize the SQLite database and create kyc_records table if it doesn't exist.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kyc_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                verifier TEXT,
                organization TEXT,
                department TEXT,
                employee_id TEXT,
                verifier_contact TEXT,
                verifier_email TEXT,
                customer_name TEXT,
                aadhaar TEXT NOT NULL,
                pan TEXT NOT NULL,
                mobile TEXT,
                email TEXT,
                kyc_type TEXT,
                kyc_id TEXT,
                risk_category TEXT DEFAULT 'Low',
                last_kyc_date TEXT,
                ocr_verified INTEGER,
                aadhaar_confidence REAL,
                pan_confidence REAL,
                face_match_score REAL,
                blinks INTEGER,
                max_face_angle REAL,
                smile_detected INTEGER,
                decision TEXT,
                UNIQUE(aadhaar, pan)
            )
        """)
    print(f"✅ Database initialized with full KYC schema at {DB_PATH}")

def save_kyc_record(full_data: Dict) -> dict:
    """
    Insert or update a full KYC record matching the log fields.
    Expects a dict with all KYC details (same as log row).
    Returns status dict.
    """
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        # Add current timestamp if not provided
        full_data.setdefault("Timestamp", now)

        # ✅ Safely map Smile Detected: "Yes"→1, everything else→0
        smile_value = str(full_data.get("Smile Detected", "No")).strip().lower()
        smile_detected_int = 1 if smile_value == "yes" else 0
        
        try:
            cursor.execute("""
                INSERT INTO kyc_records (
                    timestamp, verifier, organization, department, employee_id,
                    verifier_contact, verifier_email, customer_name, aadhaar, pan,
                    mobile, email, kyc_type, kyc_id, risk_category, last_kyc_date,
                    ocr_verified, aadhaar_confidence, pan_confidence, face_match_score,
                    blinks, max_face_angle, smile_detected, decision, profiler_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                full_data.get("Timestamp"),
                full_data.get("Verifier"),
                full_data.get("Organization"),
                full_data.get("Department"),
                full_data.get("Employee ID"),
                full_data.get("Verifier Contact"),
                full_data.get("Verifier Email"),
                full_data.get("Customer Name"),
                full_data.get("Aadhaar"),
                full_data.get("PAN"),
                full_data.get("Mobile"),
                full_data.get("Email"),
                full_data.get("KYC Type"),
                full_data.get("KYC ID"),
                full_data.get("Risk Category", "Low"),
                full_data.get("Last KYC Date"),
                int(full_data.get("OCR Verified", 0)),
                float(full_data.get("Aadhaar Confidence", 0)),
                float(full_data.get("PAN Confidence", 0)),
                float(full_data.get("Face Match Score", 0)),
                int(full_data.get("Blinks", 0)),
                float(full_data.get("Max Face Angle", 0)),
                smile_detected_int,
                full_data.get("Decision"),
                full_data.get("Profiler File"),  # ✅ NEW: profiler_file path
            ))
        except sqlite3.IntegrityError:
            cursor.execute("""
                UPDATE kyc_records SET
                    timestamp=?, verifier=?, organization=?, department=?, employee_id=?,
                    verifier_contact=?, verifier_email=?, customer_name=?, mobile=?, email=?,
                    kyc_type=?, kyc_id=?, risk_category=?, last_kyc_date=?,
                    ocr_verified=?, aadhaar_confidence=?, pan_confidence=?, face_match_score=?,
                    blinks=?, max_face_angle=?, smile_detected=?, decision=?, profiler_file=?
                WHERE aadhaar=? AND pan=?
            """, (
                full_data.get("Timestamp"),
                full_data.get("Verifier"),
                full_data.get("Organization"),
                full_data.get("Department"),
                full_data.get("Employee ID"),
                full_data.get("Verifier Contact"),
                full_data.get("Verifier Email"),
                full_data.get("Customer Name"),
                full_data.get("Mobile"),
                full_data.get("Email"),
                full_data.get("KYC Type"),
                full_data.get("KYC ID"),
                full_data.get("Risk Category", "Low"),
                full_data.get("Last KYC Date"),
                int(full_data.get("OCR Verified", 0)),
                float(full_data.get("Aadhaar Confidence", 0)),
                float(full_data.get("PAN Confidence", 0)),
                float(full_data.get("Face Match Score", 0)),
                int(full_data.get("Blinks", 0)),
                float(full_data.get("Max Face Angle", 0)),
                smile_detected_int,
                full_data.get("Decision"),
                full_data.get("Profiler File"),  # ✅ NEW: profiler_file path
                full_data.get("Aadhaar"),
                full_data.get("PAN")
            ))
        conn.commit()
        print(f"✅ Full KYC record saved/updated for Aadhaar: {full_data.get('Aadhaar')}, PAN: {full_data.get('PAN')}")
        return {"status": "ok", "message": f"KYC record saved/updated for {full_data.get('Aadhaar')}/{full_data.get('PAN')}"}


def get_kyc_record(aadhaar: str, pan: str) -> Optional[Dict]:
    """
    Fetch full existing KYC record by Aadhaar and PAN.
    Returns dict if record exists, otherwise None.
    """
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM kyc_records WHERE aadhaar=? AND pan=?
        """, (aadhaar, pan))
        row = cursor.fetchone()
        if not row:
            return None
        
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
def init_qa_table():
    """
    Create kyc_qa table if not exists, to store extracted Q&A answers.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kyc_qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aadhaar TEXT NOT NULL,
                pan TEXT NOT NULL,
                question TEXT,
                answer TEXT,
                kyc_id TEXT,
                timestamp TEXT
            )
        """)
    print("✅ QA table initialized in DB.")



def save_qa_to_db(aadhaar, pan, kyc_id, answers: dict):
    """
    Save each question-answer pair as a row in kyc_qa table.
    """
    init_qa_table()
    now = datetime.now().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        for question, answer_obj in answers.items():
            print(f"🟨 Raw answer_obj: {answer_obj}")  # DEBUG

            if isinstance(answer_obj, dict):
                answer_text = answer_obj.get("answer", "")
            else:
                answer_text = str(answer_obj)

            print(f"🟩 Inserting: Q={question}, A={answer_text}")  # DEBUG

            conn.execute("""
                INSERT INTO kyc_qa (aadhaar, pan, question, answer, kyc_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (aadhaar, pan, question, answer_text, kyc_id, now))
    
    print(f"✅ Saved Q&A for Aadhaar: {aadhaar}, PAN: {pan} in DB.")

def init_history_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kyc_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                verifier TEXT,
                organization TEXT,
                department TEXT,
                employee_id TEXT,
                verifier_contact TEXT,
                verifier_email TEXT,
                customer_name TEXT,
                aadhaar TEXT NOT NULL,
                pan TEXT NOT NULL,
                mobile TEXT,
                email TEXT,
                kyc_type TEXT,
                kyc_id TEXT,
                risk_category TEXT,
                last_kyc_date TEXT,
                ocr_verified INTEGER,
                aadhaar_confidence REAL,
                pan_confidence REAL,
                face_match_score REAL,
                blinks INTEGER,
                max_face_angle REAL,
                smile_detected INTEGER,
                decision TEXT,
                profiler_file TEXT
            )
        """)
    print("✅ KYC History table initialized.")



def save_kyc_history(full_data: Dict):
    init_history_table()
    smile_detected_int = 1 if str(full_data.get("Smile Detected", "No")).strip().lower() == "yes" else 0
    now = datetime.now().isoformat()
    full_data.setdefault("Timestamp", now)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO kyc_history (
                timestamp, verifier, organization, department, employee_id,
                verifier_contact, verifier_email, customer_name, aadhaar, pan,
                mobile, email, kyc_type, kyc_id, risk_category, last_kyc_date,
                ocr_verified, aadhaar_confidence, pan_confidence, face_match_score,
                blinks, max_face_angle, smile_detected, decision, profiler_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_data.get("Timestamp"), full_data.get("Verifier"), full_data.get("Organization"),
            full_data.get("Department"), full_data.get("Employee ID"), full_data.get("Verifier Contact"),
            full_data.get("Verifier Email"), full_data.get("Customer Name"), full_data.get("Aadhaar"),
            full_data.get("PAN"), full_data.get("Mobile"), full_data.get("Email"),
            full_data.get("KYC Type"), full_data.get("KYC ID"), full_data.get("Risk Category", "Low"),
            full_data.get("Last KYC Date"), int(full_data.get("OCR Verified", 0)),
            float(full_data.get("Aadhaar Confidence", 0)), float(full_data.get("PAN Confidence", 0)),
            float(full_data.get("Face Match Score", 0)), int(full_data.get("Blinks", 0)),
            float(full_data.get("Max Face Angle", 0)), smile_detected_int,
            full_data.get("Decision"), full_data.get("Profiler File")
        ))
    print("✅ Full history logged for Aadhaar:", full_data.get("Aadhaar"))

def get_kyc_history(aadhaar: str, pan: str) -> pd.DataFrame:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("""
            SELECT * FROM kyc_history
            WHERE aadhaar = ? AND pan = ?
            ORDER BY timestamp DESC
        """, conn, params=(aadhaar, pan))
    return df

