import streamlit as st
import os
from pathlib import Path
from io import BytesIO
import pandas as pd
import cv2
import time
import requests
import sys
import streamlit as st
import os
import re
from pathlib import Path
from io import BytesIO
import pandas as pd
import cv2
import time
import requests
import sys 
import sqlite3
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from backend.utils.audio_extraction import extract_audio_from_video
from backend.parse_transcript import ( extract_answers_llm, PREDEFINED_QUESTIONS) 
from backend.utils.log_utils import generate_log_row, append_kyc_log
from backend.utils.profiler_utils import generate_profiler_doc
from backend.utils.db_utils import save_kyc_history


from api_client import (
       
    check_existing_kyc,
    upload_kyc_documents,
    trigger_ocr_and_verification,
    finalize_kyc,
    download_report,
)

from backend.utils.audio_extraction import extract_audio_from_video
from backend.utils.aws_transcribe_utils import upload_audio_to_s3, start_transcription_job, get_transcription_status
from backend.parse_transcript import extract_answers_llm
from app_verifier import send_otp_email, send_otp_sms, generate_otp
 

from app_verifier import authenticate_verifier

# ===========================
# ⚙️ Config
# ===========================
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ✅ Central DB path definition
DB_PATH = PROJECT_ROOT / "backend" / "database" / "verifier_system.db"

# add project root to sys.path dynamically
sys.path.append(str(Path(__file__).resolve().parents[1]))


st.set_page_config(page_title="Video KYC App", layout="wide")

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOC_DIR = PROJECT_ROOT / "frontend" / "uploads" / "kyc_docs"
VID_DIR = PROJECT_ROOT / "frontend" / "uploads" / "videos"
AUDIO_DIR = PROJECT_ROOT / "frontend" / "uploads" / "audio"
PROFILER_DIR = PROJECT_ROOT / "frontend" / "uploads" / "profilers"
TRANSCRIPT_DIR = PROJECT_ROOT / "frontend" / "uploads" / "transcripts"

DOC_DIR.mkdir(parents=True, exist_ok=True)
VID_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
PROFILER_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

# ================================
# 🔐 Verifier Login Section
# ================================

from datetime import datetime, timedelta
from app_verifier import (
    authenticate_verifier, update_password,
    generate_otp, send_otp_email, send_otp_sms)



if "verifier_logged_in" not in st.session_state:
    st.session_state.verifier_logged_in = False




# ✅ LOGIN FORM
if not st.session_state.verifier_logged_in and not st.session_state.get("show_password_reset"):
# Streamlit login panel with native layout (no CSS)

    col1, col2, col3 = st.columns([1, 2, 1])  # center column is wider

    with col2:
        st.markdown("### 🔐 Verifier Login Panel")

        org_code = st.text_input("Organization Code", key="login_org_code")
        emp_code = st.text_input("Employee Code", key="login_emp_code")
        password = st.text_input("Password", type="password", key="login_password")

        # Buttons row
        login_col, forgot_col = st.columns([1, 1])
        with login_col:
            if st.button("🔓 Login"):
                verifier = authenticate_verifier(org_code, emp_code, password)
                if verifier:
                    if password == "password":
                        st.session_state.temp_user = verifier
                        st.session_state.show_password_reset = True
                        st.warning("⚠️ First-time login — please reset your password.")
                    else:
                        st.session_state.verifier_logged_in = True
                        st.session_state.update(verifier)
                        st.success(f"✅ Welcome {verifier['verifier_name']}!")
                        st.rerun()
                else:
                    st.error("❌ Invalid credentials")

        with forgot_col:
            if st.button("❓ Forgot Password?"):
                st.session_state.show_password_reset = True
                st.rerun()


# ✅ PASSWORD RESET UI
if st.session_state.get("show_password_reset"):
    st.subheader("🔁 Reset Password via OTP")

    if "temp_user" in st.session_state:
        # First-time login
        reset_emp_code = st.session_state.temp_user["emp_code"]
        st.info(f"🔐 Password reset for: {reset_emp_code}")
    else:
        reset_emp_code = st.text_input("Employee Code for OTP", key="reset_emp_code")

    if st.button("📨 Send OTP"):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email, mobile FROM employees WHERE emp_code=?", (reset_emp_code,))
            row = cursor.fetchone()
            if row:
                email, mobile = row
                otp = generate_otp()
                st.session_state.generated_otp = otp
                st.session_state.otp_user = reset_emp_code
                st.session_state.otp_time = datetime.now()
                send_otp_email(email, otp)
                send_otp_sms(mobile, otp)
                st.success("✅ OTP sent to registered Email and Mobile.")
            else:
                st.error("❌ Employee not found.")

    if "generated_otp" in st.session_state:
        entered_otp = st.text_input("Enter OTP")
        new_pass = st.text_input("New Password", type="password")
        if st.button("🔄 Confirm Password Reset"):
            if datetime.now() - st.session_state.otp_time > timedelta(minutes=5):
                st.error("❌ OTP expired. Please resend.")
                st.session_state.pop("generated_otp", None)
            elif entered_otp == st.session_state.generated_otp:
                if update_password(st.session_state.otp_user, new_pass):
                    st.success("✅ Password updated. Please login again.")
                    time.sleep(2)
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to update password.")
            else:
                st.error("❌ Incorrect OTP.")
    
    st.stop()



# ================================
# ✅ Logged-in Verifier Info
# ================================
if st.session_state.get("verifier_logged_in"):
    st.sidebar.title("👤 Verifier Info")
    st.sidebar.markdown(f"**Name:** {st.session_state.verifier_name}")
    st.sidebar.markdown(f"**Emp Code:** {st.session_state.emp_code}")
    st.sidebar.markdown(f"**Org:** {st.session_state.org_name}")
    st.sidebar.markdown(f"**Dept:** {st.session_state.department}")
    st.sidebar.markdown(f"**Designation:** {st.session_state.designation}")
    st.sidebar.markdown(f"**Mobile:** {st.session_state.mobile}")
    st.sidebar.markdown(f"**Email:** {st.session_state.email}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()


# ===========================
# 📋 Step 1: Customer Info
# ===========================
if not st.session_state.get("verifier_logged_in"):
    st.stop()




st.title("📋 Video KYC Capture and Verification")
st.subheader("Step 1: Customer Basic Details")

# ✅ Initialize allow_continue only once at top of the script
if "allow_continue" not in st.session_state:
    st.session_state.allow_continue = False

# ===========================
# 📝 Customer details form
# ===========================
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("Customer Full Name")
    aadhaar_number = st.text_input("Aadhaar Number")
    pan_number = st.text_input("PAN Number")
with col2:
    customer_mobile = st.text_input("Customer Mobile")
    customer_email = st.text_input("Customer Email")

# ===========================
# ✅ OTP & Existing KYC check
# ===========================
from app_verifier import send_otp_email, send_otp_sms, generate_otp
from datetime import datetime, timedelta

# ===========================
# ✅ OTP & Existing KYC Check
# ===========================
st.markdown("#### 🔐 Step: Verify OTP & Check Existing KYC")

if st.button("📨 Send OTP to Customer"):
    if not aadhaar_number or not customer_mobile or not customer_email:
        st.warning("❗ Please enter Aadhaar, Mobile, and Email first.")
    else:
        otp = generate_otp()
        st.session_state.customer_otp = otp
        st.session_state.otp_sent_time = datetime.now()

        send_otp_sms(customer_mobile, otp)
        send_otp_email(customer_email, otp)

        st.success("✅ OTP sent to customer's mobile and email.")

entered_otp = st.text_input("🔢 Enter OTP sent to Customer")

if st.button("✅ Verify OTP and Check KYC"):
    if "customer_otp" not in st.session_state:
        st.error("❗ OTP not sent yet.")
    elif datetime.now() - st.session_state.otp_sent_time > timedelta(minutes=5):
        st.error("❌ OTP expired. Please resend.")
    elif entered_otp == st.session_state.customer_otp:
        st.success("🎉 OTP verified. Checking existing KYC...")

        # Now proceed to check existing KYC
        kyc_status = check_existing_kyc(aadhaar_number, pan_number)
        status = kyc_status.get("status")

        if status == "valid_kyc":
            st.success(f"KYC valid until {kyc_status.get('valid_until', 'N/A')}.")
            st.warning("⚠️ Existing KYC is still valid. If you still want to perform a fresh KYC, click below:")
        elif status == "rekYC_due":
            st.warning("KYC expired — please proceed with re-KYC!")
            st.session_state.allow_continue = True
            st.rerun()
        else:
            st.info("No existing KYC found — proceed with fresh KYC.")
            st.session_state.allow_continue = True
            st.rerun()
    else:
        st.error("❌ Incorrect OTP.")

# ===========================
# 🚨 Manual override: Continue Anyway button
# ===========================
if st.button("🚨 Continue Anyway"):
    st.session_state.allow_continue = True
    st.rerun()

# ===========================
# 🚫 Prevent moving forward unless allowed
# ===========================
if not st.session_state.allow_continue:
    st.warning("🛑 Verification incomplete. Complete verification or click 'Continue Anyway'.")
    st.stop()

# ✅ Allowed to continue
st.success("🎉 Verification complete or override accepted. Proceed with document & video upload!")

# ===========================
# 📄 Step 2: Aadhaar & PAN Capture/Upload
# ===========================
st.subheader("Step 2: Upload or Capture Aadhaar & PAN")

col_aadhaar, col_pan = st.columns(2)
with col_aadhaar:
    st.markdown("### 🆔 Aadhaar Document")
    aadhaar_mode = st.radio("Mode:", ["Upload", "Live Capture"], horizontal=True, key="aadhaar_mode")
    aadhaar_save_path = DOC_DIR / f"{aadhaar_number}_aadhaar.png"
    aadhaar_file = None
    if aadhaar_mode == "Upload":
        uploaded = st.file_uploader("Upload Aadhaar", type=["jpg", "jpeg", "png"], key="aadhaar_upload")
        if uploaded:
            with open(aadhaar_save_path, "wb") as f:
                f.write(uploaded.read())
            aadhaar_file = aadhaar_save_path.open("rb")
            st.success(f"✅ Aadhaar saved: {aadhaar_save_path}")
    else:
        captured = st.camera_input("Capture Aadhaar", key="aadhaar_capture")
        if captured:
            with open(aadhaar_save_path, "wb") as f:
                f.write(captured.read())
            aadhaar_file = aadhaar_save_path.open("rb")
            st.success(f"✅ Aadhaar captured: {aadhaar_save_path}")

with col_pan:
    st.markdown("### 💳 PAN Document")
    pan_mode = st.radio("Mode:", ["Upload", "Live Capture"], horizontal=True, key="pan_mode")
    pan_save_path = DOC_DIR / f"{pan_number}_pan.png"
    pan_file = None
    if pan_mode == "Upload":
        uploaded = st.file_uploader("Upload PAN", type=["jpg", "jpeg", "png"], key="pan_upload")
        if uploaded:
            with open(pan_save_path, "wb") as f:
                f.write(uploaded.read())
            pan_file = pan_save_path.open("rb")
            st.success(f"✅ PAN saved: {pan_save_path}")
    else:
        captured = st.camera_input("Capture PAN", key="pan_capture")
        if captured:
            with open(pan_save_path, "wb") as f:
                f.write(captured.read())
            pan_file = pan_save_path.open("rb")
            st.success(f"✅ PAN captured: {pan_save_path}")

# ===========================
# 🎥 KYC Video Upload or Record
# ===========================

st.markdown("#### 🎥 KYC Video Capture")
video_input_mode = st.radio("Input Mode", ["Upload Existing Video", "Record Live Video"], horizontal=True)

if video_input_mode == "Upload Existing Video":
    uploaded_video = st.file_uploader("Upload KYC Video", type=["mp4", "avi", "webm"], key="video_upload")
    if uploaded_video:
        video_path = VID_DIR / f"{aadhaar_number}_kycvideo{Path(uploaded_video.name).suffix}"
        with open(video_path, "wb") as f:
            f.write(uploaded_video.read())
        st.session_state.video_path = video_path
        st.success(f"✅ Uploaded video saved: {video_path}")
        st.video(str(video_path))
else:
    st.markdown("### 🎥 Live Video Recording")
    duration, fps, total_frames = st.slider("Recording Duration (seconds)", 10, 300, 30, 5), 20, 0
    total_frames = duration * fps
    if st.button("🎥 Start & Save Live Video Recording"):
        cap, stframe, status_msg = cv2.VideoCapture(0), st.empty(), st.empty()
        video_path = VID_DIR / f"{aadhaar_number}_kycvideo.webm"
        fourcc, out = cv2.VideoWriter_fourcc(*'VP80'), cv2.VideoWriter(str(video_path), fourcc, fps, (640, 480))
        if not cap.isOpened(): st.error("❌ Could not open webcam.")
        else:
            st.info("🔴 Recording started...")
            for frame in range(total_frames):
                ret, frame_data = cap.read()
                if not ret: break
                out.write(frame_data)
                stframe.image(cv2.resize(frame_data, (640, 480)), channels="BGR")
                status_msg.info(f"Recording... {frame//fps}s / {duration}s")
            cap.release(), out.release()
            st.session_state.video_path = video_path
            status_msg.success(f"✅ KYC video recorded: {video_path}")
            st.video(str(video_path))

if st.session_state.get("video_path") and st.button("🗣️ Extract & Analyze Speech"):
    with st.spinner("🔄 Processing speech-to-text..."):
        audio_path = AUDIO_DIR / f"{aadhaar_number}_kyc_audio.wav"
        success, msg = extract_audio_from_video(str(st.session_state.video_path), str(audio_path))
        if not success:
            st.error(msg)
            st.stop()
        st.success(msg)

        s3_key = f"kyc-audio/{aadhaar_number}_kyc_audio.wav"
        bucket_name = "my-vkyc-audio-bucket"
        success, audio_s3_url = upload_audio_to_s3(audio_path, bucket_name, s3_key)
        if not success:
            st.error(audio_s3_url)
            st.stop()

        unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
        job_name = f"kyc-job-{aadhaar_number.replace(' ', '')}-{unique_suffix}"

        _, error = start_transcription_job(job_name, audio_s3_url)
        if error:
            st.error(error)
            st.stop()

        st.info("🕒 Waiting for transcription job...")
        while True:
            status, transcript_uri, err = get_transcription_status(job_name)
            if err:
                st.error(err)
                st.stop()
            if status == "COMPLETED":
                st.success("✅ Transcription done!")
                break
            elif status == "FAILED":
                st.error("❌ Transcription failed.")
                st.stop()
            time.sleep(5)

        response = requests.get(transcript_uri)
        if response.status_code != 200:
            st.error("❌ Failed to download transcript.")
            st.stop()

        raw_transcript = response.json()['results']['transcripts'][0]['transcript']
        transcript_text = raw_transcript
        st.text_area("📝 Transcript", transcript_text, height=200)

        # ✅ Step 1: Create folder for saving per-case files

        
        
        transcript_folder = TRANSCRIPT_DIR/ f"{aadhaar_number}_{unique_suffix}"
        transcript_folder.mkdir(parents=True, exist_ok=True)
        st.session_state.transcript_folder = transcript_folder


        # ✅ Step 2: Save raw transcript
        with open(transcript_folder / "raw_transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # ✅ Step 3: LLM Extraction and Save
        from backend.parse_transcript import extract_answers_llm
        st.info("🤖 Extracting answers from transcript using LLM...")
        with st.spinner("⏳ Extracting answers..."):
            try:
                extracted_answers = extract_answers_llm(transcript_text)
                st.session_state.extracted_answers = extracted_answers

                # Save raw LLM JSON
                with open(transcript_folder / "llm_extracted_answers.json", "w", encoding="utf-8") as f:
                    import json
                    json.dump(extracted_answers, f, indent=2)

                st.success("✅ Answers extracted and saved!")
            except Exception as e:
                st.error(f"❌ LLM failed to extract answers.\n{e}")
                st.stop()

    # ✅ Display extracted raw LLM output
    st.markdown("### 🧾 Full Extracted Answer JSON (Before Editing)")
    st.json(st.session_state.extracted_answers)

# ============================
# 🔍 Display and Edit Answers
# ============================

if st.session_state.get("extracted_answers"):
    st.markdown("### ✏️ Review & Edit Extracted Answers")
    edited_answers = {}

    with st.form("edit_answers_form"):
        for predefined_q, info in st.session_state.extracted_answers.items():
            # Extract parsed question and answer
            parsed_q = info.get("parsed_question", "(Parsed question not available)") if isinstance(info, dict) else "(Parsed question not available)"
            ans = info.get("answer", "") if isinstance(info, dict) else info

            # Show inputs for review
            st.markdown(f"**🟩 Predefined Question:** {predefined_q}")
            st.text_input("🔎 Parsed Question", value=parsed_q, key=f"{predefined_q}_parsed", disabled=True)
            edited_answer = st.text_input("✏️ Answer", value=ans, key=f"{predefined_q}_answer")

            # Save edited answer
            edited_answers[predefined_q] = {
                "parsed_question": parsed_q,
                "answer": edited_answer
            }
            st.markdown("---")

        # On save button press
        if st.form_submit_button("💾 Save Edited Answers"):
            st.session_state.edited_answers = edited_answers

            # Validate transcript folder
            transcript_folder = st.session_state.get("transcript_folder")
            if transcript_folder is None:
                st.error("Transcript folder not found. Please re-run speech transcription.")
                st.stop()

            # Define save paths
            final_json_path = transcript_folder / "kyc_answers_final.json"
            final_csv_path = transcript_folder / "kyc_answers_final.csv"

            # Save as JSON
            import json, csv
            with open(final_json_path, "w", encoding="utf-8") as f:
                json.dump(edited_answers, f, indent=2)

            # Save as CSV
            with open(final_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Predefined Question", "Parsed Question", "Answer"])
                for q, qa in edited_answers.items():
                    writer.writerow([q, qa.get("parsed_question", ""), qa.get("answer", "")])

            st.success("✅ Final reviewed answers saved!")

# ===========================
# ✅ Submit for Verification
# ===========================
# ===========================
# ✅ Submit for Verification
# ===========================
if st.button("Submit for Verification"):
    video_path = st.session_state.get("video_path")
    if not (aadhaar_file and pan_file and video_path):
        st.warning("Provide Aadhaar, PAN, and KYC video before submitting!")
    else:
        with st.spinner("🔄 Verifying KYC data..."):
            with open(video_path, "rb") as video_f:
                upload_result = upload_kyc_documents(
                    aadhaar_doc=aadhaar_file,
                    pan_doc=pan_file,
                    video_file=(video_f.name, video_f.read(), "video/webm"),
                    name=customer_name, pan=pan_number, aadhaar=aadhaar_number
                )
            if upload_result.get("status") == "uploaded":
                st.session_state.update({
                    'aadhaar_doc_path': upload_result["aadhaar_doc_path"],
                    'pan_doc_path': upload_result["pan_doc_path"],
                    'video_path': upload_result["video_path"],
                })
                verify_payload = {
                    "name": customer_name, "pan": pan_number, "aadhaar": aadhaar_number,
                    "aadhaar_doc_path": upload_result["aadhaar_doc_path"],
                    "pan_doc_path": upload_result["pan_doc_path"],
                    "video_path": upload_result["video_path"],
                }
                verify_result = trigger_ocr_and_verification(verify_payload)
                st.session_state.verify_result = verify_result
                st.success("KYC uploaded & verified!")


# ===========================
# 🧠 Verification Result
# ===========================
from api_client import get_customer_service_info


if st.session_state.get("verify_result"):
    vr = st.session_state.verify_result
    st.markdown("### 🧠 Verification Result")
    st.json(vr)
    col_accept, col_reject = st.columns(2)

    with col_accept:
        if st.button("✅ Accept & Finalize KYC"):
            finalize_payload = {
                **vr,
                "mobile": customer_mobile,
                "email": customer_email,
                "verifier_name": st.session_state.verifier_name,
                "organization": st.session_state.org_name,
                "department": st.session_state.department,
                "employee_id": st.session_state.emp_code,
                "verifier_contact":st.session_state.mobile,
                "verifier_email": st.session_state.email,
                "status": "Accepted",
            }
            org_code = st.session_state.org_code
            service_info = get_customer_service_info(org_code)

            finalize_payload["customer_service_no"] = service_info["customer_service_no"]
            finalize_payload["customer_service_email"] = service_info["customer_service_email"]
            
            resp = finalize_kyc(finalize_payload)
            if resp.get("status") == "ok":
                st.success(f"KYC finalized: {resp['kyc_id']}")

                # ✅ Collect info for logs
                customer_info = {
                    "name": customer_name,
                    "aadhaar": aadhaar_number,
                    "pan": pan_number,
                    "mobile": customer_mobile,
                    "email": customer_email,
                }
                verifier_info = {
                    "verifier_name": st.session_state.verifier_name,
                    "organization": st.session_state.org_name,
                    "department": st.session_state.department,
                    "employee_id": st.session_state.emp_code,
                    "verifier_contact": st.session_state.mobile,
                    "verifier_email": st.session_state.email,
                }

                # ✅ Generate overview using LLM BEFORE profiler doc
                from backend.utils.profiler_utils import generate_kyc_overview_llm
                overview_text = generate_kyc_overview_llm(
                    customer_info=customer_info,
                    verifier_info=verifier_info,
                    extracted_answers=st.session_state["extracted_answers"],
                )

                # ✅ Now create profiler doc
                profiler_file_path = PROJECT_ROOT / "frontend/uploads/profilers" / f"{aadhaar_number}_profiler.docx"
                generate_profiler_doc(
                    customer_info=customer_info,
                    verifier_info=verifier_info,
                    extracted_answers=st.session_state["extracted_answers"],
                    overview_text=overview_text,
                    save_path=profiler_file_path,
                )
                st.session_state.profiler_file = profiler_file_path

                # ✅ Generate log row
                log_row = generate_log_row(
                    customer_info=customer_info,
                    verifier_info=verifier_info,
                    kyc_type="VideoKYC",
                    kyc_id=resp['kyc_id'],
                    results=vr,
                    decision="Accepted",
                    risk_category=vr.get("risk_category", "Low"),
                    last_kyc_date=datetime.now().strftime("%Y-%m-%d"),
                    profiler_file=str(profiler_file_path),
                )

                # ✅ Append logs & save to database as before...
                append_kyc_log(log_row)

                qa_log_path = PROJECT_ROOT / "frontend/uploads/logs/kyc_qa.csv"
                integrated_log_path = PROJECT_ROOT / "frontend/uploads/logs/kyc_integrated.csv"

                qa_df = pd.DataFrame([st.session_state.extracted_answers])
                if qa_log_path.exists():
                    qa_df.to_csv(qa_log_path, mode="a", index=False, header=False)
                else:
                    qa_df.to_csv(qa_log_path, index=False, header=True)

                integrated_data = {**log_row, **st.session_state.extracted_answers}
                integrated_df = pd.DataFrame([integrated_data])
                if integrated_log_path.exists():
                    integrated_df.to_csv(integrated_log_path, mode="a", index=False, header=False)
                else:
                    integrated_df.to_csv(integrated_log_path, index=False, header=True)

                st.success("✅ QA and Integrated logs updated!")

                from backend.utils.db_utils import save_kyc_record, save_qa_to_db, save_kyc_history
                save_kyc_record(log_row) #To save unique KYC record(Aadhar,PAN) in database
                save_kyc_history(log_row)# To save history of KYC records in database with unique timestams ID

                if st.session_state.get("extracted_answers"):
                    save_qa_to_db(
                        aadhaar=aadhaar_number,
                        pan=pan_number,
                        kyc_id=resp['kyc_id'],
                        answers=st.session_state["extracted_answers"],
                    )

                st.success("✅ Log entry saved to both CSVs and database.")

            else:
                st.error(resp.get("error", "Finalization error"))

    with col_reject:
        if st.button("❌ Reject KYC"):
            reject_payload = {**vr, "status": "Rejected"}
            resp = finalize_kyc(reject_payload)
            if resp.get("status") == "ok":
                st.warning(f"KYC rejected: {resp['kyc_id']}")
                st.session_state.verify_result = None
                st.session_state.video_path = None

    # ✅ Download Profiler outside accept/reject, after main block
    if st.session_state.get("profiler_file") and Path(st.session_state.profiler_file).exists():
        with open(st.session_state.profiler_file, "rb") as f:
            st.download_button(
                "📄 Download Customer Profiler",
                f,
                file_name=Path(st.session_state.profiler_file).name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )


# ===========================
# 📄 Download Report
# ===========================
if st.session_state.get("verify_result") and st.button("Download Report"):
    file_path = download_report(st.session_state.verify_result["kyc_id"])
    if file_path and file_path.exists():
        with open(file_path, "rb") as f:
            st.download_button("Download PDF Report", f, file_name=file_path.name)
    else:
        st.error("Report not found or not generated yet.")
# ===========================
# 📧 Send Report via Email to Customer
# ===========================
st.markdown("### 📧 Send Report to Customer Email")

if st.session_state.get("verify_result"):
    file_path = download_report(st.session_state.verify_result["kyc_id"])

    if file_path and file_path.exists():
        # Autofill email from session (fallback to blank if not found)
        default_email = st.session_state.get("email", "")
        confirmed_email = st.text_input("📧 Confirm Customer Email", value=default_email)

        if st.button("📤 Email Report to Customer"):
            from email.message import EmailMessage
            import smtplib
            import traceback
            import os

            org_email = os.getenv("GMAIL_USER")
            org_password = os.getenv("GMAIL_APP_PASSWORD")

            if not confirmed_email:
                st.error("❌ Please enter a valid customer email.")
            elif not org_email or not org_password:
                st.error("❌ Missing SMTP credentials. Please check environment variables.")
            else:
                try:
                    msg = EmailMessage()
                    kyc_id = st.session_state.verify_result.get("kyc_id", "KYC_Report")

                    msg["Subject"] = f"KYC Verification Report - {kyc_id}"
                    msg["From"] = org_email
                    msg["To"] = confirmed_email
                    msg.set_content(
                        "Dear Customer,\n\n"
                        "Please find attached your KYC verification report.\n\n"
                        "Regards,\n"
                        "Your Bank"
                    )

                    with open(file_path, "rb") as f:
                        file_data = f.read()
                        file_name = file_path.name
                    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                        smtp.login(org_email, org_password)
                        smtp.send_message(msg)

                    st.success(f"✅ Report emailed successfully to {confirmed_email}")

                except Exception as e:
                    st.error(f"❌ Failed to send email: {e}")
                    st.text(traceback.format_exc())
    else:
        st.error("❌ Report not found or not generated yet.")


# ===========================
# 📋 KYC Log Viewer with Table Selection
# ===========================
st.markdown("---")
st.markdown("### 📋 View and Filter KYC Logs")

log_options = {
    "KYCInformation": PROJECT_ROOT / "backend/database/kyc_records.db",
    "KYCHistory": PROJECT_ROOT / "backend/database/kyc_records.db",
    "KYC_QA": PROJECT_ROOT / "frontend/uploads/logs/kyc_qa.csv",
    "KYCIntegrated": PROJECT_ROOT / "frontend/uploads/logs/kyc_integrated.csv",
}
selected_log = st.selectbox("Select Log Table to View", list(log_options.keys()))
log_path = log_options[selected_log]

if log_path.exists():
    try:
        if log_path.suffix == ".db":
            table_name = "kyc_records" if selected_log == "KYCInformation" else "kyc_history"
            with sqlite3.connect(log_path) as conn:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

        else:
            df = pd.read_csv(log_path)
        if df.empty:
            st.warning(f"⚠️ {selected_log} log exists but is empty.")
        else:
            st.success(f"✅ {selected_log} loaded successfully.")
            filter_columns = st.multiselect(
                "Select columns to display:",
                options=df.columns.tolist(),
                default=df.columns.tolist()
            )
            filtered_df = df[filter_columns]
            st.dataframe(filtered_df, use_container_width=True)

            # 📥 CSV download
            csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                f"Download {selected_log} as CSV",
                csv_bytes,
                file_name=f"{selected_log.lower()}_log.csv",
                mime="text/csv"
            )

            # 📥 Excel download
            excel_output = BytesIO()
            with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False)
            excel_output.seek(0)
            st.download_button(
                f"Download {selected_log} as Excel",
                excel_output,
                file_name=f"{selected_log.lower()}_log.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"❌ Failed to read {selected_log}: {e}")
else:
    st.error(f"❌ Selected log file not found at: {log_path}")



    