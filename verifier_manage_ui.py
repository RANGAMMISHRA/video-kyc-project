# verifier_manage_ui.py

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import bcrypt

# ---------------------
# 🔐 Hash password
# ---------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# ---------------------
# 📍 DB Path
# ---------------------
DB_PATH = Path("C:/Users/Hp/Preplaced/VKYC/video-kyc-project/backend/database/verifier_system.db")

# ---------------------
# 📥 Fetch all verifiers
# ---------------------
def fetch_all_verifiers():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("""
            SELECT e.org_code, o.org_name, e.emp_code, e.verifier_name,
                   e.email, e.mobile, e.department, e.designation,
                   e.start_date, e.end_date
            FROM employees e
            JOIN organizations o ON e.org_code = o.org_code
        """, conn)
    return df

# ---------------------
# 🔎 Get Single Verifier
# ---------------------
def get_verifier(org_code, emp_code):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT verifier_name, email, mobile, department, designation, start_date, end_date
            FROM employees
            WHERE org_code=? AND emp_code=?
        ''', (org_code, emp_code))
        return cursor.fetchone()

# ---------------------
# 💾 Update Verifier Info
# ---------------------
def update_verifier(org_code, emp_code, name, email, mobile, dept, desig, start_date, end_date):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE employees
            SET verifier_name=?, email=?, mobile=?, department=?, designation=?, start_date=?, end_date=?
            WHERE org_code=? AND emp_code=?
        ''', (name, email, mobile, dept, desig, start_date, end_date, org_code, emp_code))
        conn.commit()

# ---------------------
# ❌ Delete Verifier
# ---------------------
def delete_verifier(org_code, emp_code):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM employees WHERE org_code=? AND emp_code=?', (org_code, emp_code))
        conn.commit()

# ---------------------
# ➕ Add New Verifier
# ---------------------
def add_new_verifier(org_code, emp_code, name, email, mobile, dept, desig, start_date, end_date):
    password_hash = hash_password("password")  # ✅ hash the default password
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO employees (org_code, emp_code, verifier_name, email, mobile,
                                   department, designation, start_date, end_date, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (org_code, emp_code, name, email, mobile, dept, desig, start_date, end_date, password_hash))
        conn.commit()

# ---------------------
# 🌐 Streamlit UI
# ---------------------
def main():
    st.set_page_config(page_title="Manage Verifiers", layout="wide")
    st.title("🧑‍💼 Manage Verifier Records")

    st.header("📋 Existing Verifiers")
    df = fetch_all_verifiers()

    # 🔍 Filter by Org Code
    filter_org = st.text_input("Filter by Org Code").strip().upper()
    if filter_org:
        df = df[df["org_code"] == filter_org]

    st.dataframe(df)

    if not df.empty:
        # ===================
        st.subheader("✏️ Edit or Delete Verifier")
        df["label"] = df["org_code"] + " | " + df["emp_code"] + " | " + df["verifier_name"]
        selected = st.selectbox("Select Verifier", df["label"].tolist())

        selected_row = df[df["label"] == selected].iloc[0]
        org_code = selected_row["org_code"]
        emp_code = selected_row["emp_code"]
        result = get_verifier(org_code, emp_code)

        if result:
            name, email, mobile, dept, desig, start, end = result
            new_name = st.text_input("Name", name)
            new_email = st.text_input("Email", email)
            new_mobile = st.text_input("Mobile", mobile)
            new_dept = st.text_input("Department", dept or "")
            new_desig = st.text_input("Designation", desig or "")
            new_start = st.date_input("Start Date", datetime.strptime(start, "%Y-%m-%d").date())
            new_end = st.date_input("End Date", datetime.strptime(end, "%Y-%m-%d").date() if end else datetime.today())

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes"):
                    update_verifier(org_code, emp_code, new_name, new_email, new_mobile,
                                    new_dept, new_desig, new_start.strftime("%Y-%m-%d"),
                                    new_end.strftime("%Y-%m-%d"))
                    st.success("✅ Verifier updated.")
                    st.rerun()

            with col2:
                if st.button("❌ Delete Verifier"):
                    delete_verifier(org_code, emp_code)
                    st.warning("Verifier deleted.")
                    st.rerun()

    # ===================
    st.header("➕ Add New Verifier")
    with st.form("add_verifier_form"):
        org_code = st.text_input("Org Code")
        emp_code = st.text_input("Emp Code")
        name = st.text_input("Name")
        email = st.text_input("Email")
        mobile = st.text_input("Mobile")
        dept = st.text_input("Department")
        desig = st.text_input("Designation")
        start = st.date_input("Start Date", datetime.today())
        end = st.date_input("End Date", datetime.today())

        if st.form_submit_button("✅ Add Verifier"):
            if all([org_code, emp_code, name, email, mobile]):
                add_new_verifier(org_code, emp_code, name, email, mobile, dept, desig,
                                 start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
                st.success("✅ Verifier added successfully. Default password is 'password'")
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields.")

if __name__ == "__main__":
    main()
