import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
from io import StringIO
from datetime import datetime
from pathlib import Path

# DB path setup
DB_PATH = Path("C:/Users/Hp/Preplaced/VKYC/video-kyc-project/backend/database/verifier_system.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                org_code TEXT PRIMARY KEY,
                org_name TEXT NOT NULL,
                contact_no TEXT,
                contact_email TEXT,
                customer_service_no TEXT,
                customer_service_email TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_code TEXT NOT NULL,
                emp_code TEXT NOT NULL UNIQUE,
                verifier_name TEXT NOT NULL,
                email TEXT NOT NULL,
                mobile TEXT NOT NULL,
                department TEXT,
                designation TEXT,
                password_hash TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                FOREIGN KEY (org_code) REFERENCES organizations (org_code)
            )
        ''')

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def validate_date(date_str):
    try:
        if date_str and date_str.strip().upper() != "NONE":
            datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False

def load_verifiers_from_csv(uploaded_file):
    expected_cols = [
        'org_code', 'org_name', 'contact_no', 'contact_email',
        'customer_service_no', 'customer_service_email',
        'emp_code', 'verifier_name', 'email', 'mobile',
        'department', 'designation',
        'password', 'start_date', 'end_date'
    ]

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        return 0, [], "CSV unreadable"

    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        return 0, [], f"Missing: {', '.join(missing)}"

    success, failed = 0, []
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        for i, row in df.iterrows():
            try:
                vals = {k: str(row[k]).strip() for k in expected_cols}
                if not all([vals['org_code'], vals['org_name'], vals['emp_code'], vals['verifier_name'],
                            vals['email'], vals['mobile'], vals['password'], vals['start_date']]):
                    raise ValueError("Missing required fields")

                if not validate_date(vals['start_date']) or (vals['end_date'] and not validate_date(vals['end_date'])):
                    raise ValueError("Invalid date format. Use YYYY-MM-DD")

                cur.execute('''
                    INSERT OR IGNORE INTO organizations (
                        org_code, org_name, contact_no, contact_email,
                        customer_service_no, customer_service_email
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    vals['org_code'], vals['org_name'], vals['contact_no'], vals['contact_email'],
                    vals['customer_service_no'], vals['customer_service_email']
                ))

                cur.execute("SELECT 1 FROM employees WHERE org_code=? AND emp_code=?",
                            (vals['org_code'], vals['emp_code']))
                if cur.fetchone():
                    raise ValueError("Duplicate emp_code")

                password_hash = hash_password(vals['password'])

                cur.execute('''
                    INSERT INTO employees (
                        org_code, emp_code, verifier_name, email, mobile,
                        department, designation,
                        password_hash, start_date, end_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vals['org_code'], vals['emp_code'], vals['verifier_name'], vals['email'], vals['mobile'],
                    vals['department'], vals['designation'],
                    password_hash, vals['start_date'], vals['end_date'] or None
                ))
                success += 1

            except Exception as e:
                failed.append({"row": i + 2, "emp_code": row.get("emp_code", ""), "error": str(e)})

        conn.commit()

    return success, failed, None

def load_organizations_from_csv(uploaded_file):
    expected_cols = [
        'org_code', 'org_name', 'contact_no', 'contact_email',
        'customer_service_no', 'customer_service_email'
    ]

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        return 0, "Uploaded Org CSV is empty or unreadable."

    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        return 0, f"Missing required columns: {', '.join(missing_cols)}"

    success_count = 0
    failed_rows = []

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for i, row in df.iterrows():
            try:
                values = tuple(str(row[col]).strip() for col in expected_cols)

                if not values[0] or not values[1]:
                    raise ValueError("org_code and org_name are required")

                cursor.execute("""
                    INSERT OR IGNORE INTO organizations (
                        org_code, org_name, contact_no, contact_email,
                        customer_service_no, customer_service_email
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, values)

                success_count += 1

            except Exception as e:
                failed_rows.append({
                    "row": i + 2,
                    "org_code": row.get('org_code', ''),
                    "error": str(e)
                })

        conn.commit()

    return success_count, failed_rows

def get_verifier_csv_template():
    df_template = pd.DataFrame(columns=[
        'org_code', 'org_name', 'contact_no', 'contact_email',
        'customer_service_no', 'customer_service_email',
        'emp_code', 'verifier_name', 'email', 'mobile',
        'department', 'designation',
        'password', 'start_date', 'end_date'
    ])
    buffer = StringIO()
    df_template.to_csv(buffer, index=False)
    return buffer.getvalue()

def get_org_csv_template():
    df_template = pd.DataFrame(columns=[
        'org_code', 'org_name', 'contact_no', 'contact_email',
        'customer_service_no', 'customer_service_email'
    ])
    buffer = StringIO()
    df_template.to_csv(buffer, index=False)
    return buffer.getvalue()

def display_verifiers():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("""
            SELECT e.org_code, o.org_name, emp_code, verifier_name, email, mobile,
                   department, designation, start_date, end_date
            FROM employees e
            JOIN organizations o ON e.org_code = o.org_code
        """, conn)

    st.subheader("📋 View Registered Verifiers")
    if df.empty:
        st.info("No verifiers found.")
    else:
        org_filter = st.text_input("🔎 Filter by Org Code (optional)").strip().upper()
        if org_filter:
            df = df[df['org_code'] == org_filter]
        st.dataframe(df)


def main():
    st.set_page_config(page_title="Verifier Management", layout="wide")
    st.title("🏢 Verifier & Organization Management Dashboard")

    init_db()

    # --- Org Upload ---
    st.header("1️⃣ Download & Upload Organizations")
    st.download_button("⬇️ Download Org CSV Template", get_org_csv_template(), file_name="organization_template.csv", mime="text/csv")

    org_file = st.file_uploader("📤 Upload Organizations CSV", type=["csv"], key="org_csv")

    if org_file:
        st.subheader("🔍 Preview Organizations")
        try:
            df_org = pd.read_csv(org_file)
            st.dataframe(df_org)

            if st.button("📥 Upload Organizations"):
                org_file.seek(0)
                success_count, failed_rows = load_organizations_from_csv(org_file)
                st.success(f"✅ {success_count} organizations uploaded.")
                if failed_rows:
                    st.warning(f"⚠️ {len(failed_rows)} rows failed.")
                    st.dataframe(pd.DataFrame(failed_rows))
        except Exception as e:
            st.error(f"❌ Failed to read CSV: {e}")

    # --- Verifier Upload ---
    st.header("2️⃣ Download & Upload Verifiers")
    st.download_button("⬇️ Download Verifier CSV Template", get_verifier_csv_template(), file_name="verifier_template.csv", mime="text/csv")

    verifier_file = st.file_uploader("📤 Upload Verifier CSV", type=["csv"], key="verifier_csv")

    if verifier_file:
        st.subheader("🔍 Preview Verifiers")
        try:
            df = pd.read_csv(verifier_file)
            st.dataframe(df)

            if st.button("📥 Upload Verifiers"):
                verifier_file.seek(0)  # Reset file pointer to the beginning
                success_count, failed_rows, error_msg = load_verifiers_from_csv(verifier_file)
                if error_msg:
                    st.error(f"❌ {error_msg}")
                else:
                    st.success(f"✅ {success_count} verifiers uploaded.")
                    if failed_rows:
                        st.warning(f"⚠️ {len(failed_rows)} rows failed.")
                        st.dataframe(pd.DataFrame(failed_rows))
        except Exception as e:
            st.error(f"❌ Failed to read CSV: {e}")

    # --- View Verifiers ---
    st.header("3️⃣ View Existing Verifiers")
    display_verifiers()

    # --- View Orgs ---
    st.header("4️⃣ View Existing Organizations")
    with sqlite3.connect(DB_PATH) as conn:
        df_orgs = pd.read_sql_query("SELECT * FROM organizations", conn)
    if df_orgs.empty:
        st.info("ℹ️ No organizations found.")
    else:
        st.dataframe(df_orgs)

if __name__ == "__main__":
    main()
