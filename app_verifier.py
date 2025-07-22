# app_verifier.py (logic only)

import sqlite3
import bcrypt
import random
import smtplib
import os
import requests
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load secrets
load_dotenv()
EMAIL_SENDER = os.getenv("GMAIL_USER")
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")

DB_PATH = Path("C:/Users/Hp/Preplaced/VKYC/video-kyc-project/backend/database/verifier_system.db")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def authenticate_verifier(org_code, emp_code, password):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.emp_code, e.password_hash, e.verifier_name, e.org_code, e.department,
                   e.designation, e.mobile, e.email, o.org_name
            FROM employees e
            JOIN organizations o ON e.org_code = o.org_code
            WHERE e.org_code=? AND e.emp_code=?
        """, (org_code, emp_code))
        row = cursor.fetchone()
        if row and verify_password(password, row[1]):
            return dict(
                emp_code=row[0],
                verifier_name=row[2],
                org_code=row[3],
                department=row[4],
                designation=row[5],
                mobile=row[6],
                email=row[7],
                org_name=row[8]
            )
    return None


def update_password(emp_code, new_password):
    hashed = hash_password(new_password)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE employees SET password_hash=? WHERE emp_code=?", (hashed, emp_code))
        return cursor.rowcount > 0

def send_otp_email(recipient_email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP for Password Reset"
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient_email
    msg.set_content(f"Your OTP is: {otp}\nDo not share it with anyone.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

def send_otp_sms(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "authorization": FAST2SMS_API_KEY,
        "route": "q",
        "message": f"Your OTP for KYC password reset is: {otp}",
        "language": "english",
        "flash": 0,
        "numbers": mobile
    }
    response = requests.post(url, data=payload)
    return response.status_code == 200

def generate_otp():
    return str(random.randint(100000, 999999))

def get_employee_contact(emp_code):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email, mobile FROM employees WHERE emp_code=?", (emp_code,))
        row = cursor.fetchone()
        return row if row else (None, None)
