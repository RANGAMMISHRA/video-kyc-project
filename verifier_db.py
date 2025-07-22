#verifier_db.py
# This script sets up the database for the verifier system, creates necessary tables,
import sqlite3
from pathlib import Path
import bcrypt

# -------------------------------
# 📍 Setup database path
# -------------------------------
DB_PATH = Path(__file__).resolve().parent /"backend"/ "database" / "verifier_system.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# -------------------------------
# 🔐 Hash password
# -------------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# -------------------------------
# ✅ Create tables
# -------------------------------
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()

    # Create organizations table with new fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS organizations (
        org_code TEXT PRIMARY KEY,
        org_name TEXT NOT NULL,
        contact_no TEXT,
        contact_email TEXT,
        customer_service_no TEXT,
        customer_service_email TEXT
    )
    """)

    # Create employees (verifiers) table with new fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_code TEXT NOT NULL,
        emp_code TEXT NOT NULL UNIQUE,
        verifier_name TEXT NOT NULL,
        email TEXT NOT NULL,
        mobile TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        department TEXT,
        designation TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (org_code) REFERENCES organizations(org_code)
    )
    """)

    print("✅ Tables 'organizations' and 'employees' created successfully!")

# -------------------------------
# ✅ Insert sample data
# -------------------------------
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()

    # Insert sample organizations
    cursor.execute("""
    INSERT OR IGNORE INTO organizations (
        org_code, org_name, contact_no, contact_email,
        customer_service_no, customer_service_email
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "BANK001", "NewAge Bank Ltd", "011-12345678", "contact@newagebank.com",
        "1800123456", "support@newagebank.com"
    ))

    cursor.execute("""
    INSERT OR IGNORE INTO organizations (
        org_code, org_name, contact_no, contact_email,
        customer_service_no, customer_service_email
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "BANK002", "Secure Finance Corp", "022-98765432", "help@securefinance.com",
        "1800987654", "care@securefinance.com"
    ))

    # Insert sample verifiers
    default_hashed = hash_password("password")

    cursor.execute("""
    INSERT OR IGNORE INTO employees (
        org_code, emp_code, verifier_name, email, mobile,
        password_hash, department, designation, start_date, end_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "BANK001", "EMP001", "Alice Johnson", "alice@newagebank.com", "9876543210",
        default_hashed, "Operations", "KYC Officer", "2025-07-01", "2025-12-31"
    ))

    cursor.execute("""
    INSERT OR IGNORE INTO employees (
        org_code, emp_code, verifier_name, email, mobile,
        password_hash, department, designation, start_date, end_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "BANK002", "EMP002", "Bob Smith", "bob@securefinance.com", "9876543211",
        default_hashed, "Compliance", "Senior Verifier", "2025-07-01", "2025-12-31"
    ))

    print("✅ Sample organizations and verifiers inserted successfully!")
