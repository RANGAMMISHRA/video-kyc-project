#  AI-Powered Video KYC Verification System

A full-stack, AI-driven solution to streamline and digitize the customer onboarding and KYC verification process using facial recognition, OCR, liveness detection, speech transcription, and LLM-based Q&A. Built with **Streamlit**, **Flask**, and **SQLite**, this project ensures compliance, security, and auditability for financial institutions.



##  Project Overview

The Video KYC Verification System enables financial institutions to remotely onboard customers by verifying documents and live video interactions. The system supports both file upload and live webcam capture for ID and video, automates the verification using AI tools, and generates signed PDF reports.



# 🔍 AI-Powered Video KYC Verification System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Backend-Flask-red?logo=flask)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-orange?logo=streamlit)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)
![AWS](https://img.shields.io/badge/Speech%20API-AWS%20Transcribe-yellow?logo=amazon-aws)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI-blueviolet?logo=openai)
![OCR](https://img.shields.io/badge/OCR-Tesseract-informational?logo=tesseract)
![Face Match](https://img.shields.io/badge/Face%20Verification-Dlib%20%7C%20face_recognition-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-success)

## Key Features

- Streamlit-based Frontend for Verifiers & Admins
-  Flask-based Backend with Modular APIs
-  Verifier Login with OTP-based Reset
-  Upload or Capture ID Documents and Video
-  Face Matching & Liveness Detection (OpenCV + Dlib)
-  OCR from Aadhaar/PAN using Tesseract
-  Speech Transcription using AWS Transcribe
-  LLM-based Answer Extraction (OpenAI GPT)
-  Editable Answer Review and KYC Finalization
-  PDF + DOCX Report Generation
-  Email and SMS Integration
-  Secure SQLite Logs & Audit Trail



## Project Structure


video-kyc-project/


|**Dir**   |**Files/Subdirs**                           |**Purpose**                  |
|----------|--------------------------------------------|-----------------------------|
|frontend  |app.py                                      |Streamlit KYC UI             |
|          |app_transcribe.py                           |Transcription flow           |
|          |app_verifier.py                             |Verifier login               |
|          |verifier_manage_ui.py                       |Manage verifiers             |
|          |verifier_admin_portal.py                    |Admin dashboard              |
|backend   |app.py                                      |Flask main entry             |
|          |verify_api.py                               |KYC verification API         |
|          |ocr_api.py                                  |OCR processing API           |
|          |log_api.py                                  |Log saving & fetch API       |
|          |report_api.py                               |PDF report generation API    |
|utils     |audio_extraction.py                         |Audio from video             |
|(under    |aws_transcribe_utils.py                     |AWS Transcribe integration   |
| backend) |ocr_utils.py                                |OCR Aadhaar/PAN              |
|          |sms_utils.py                                |OTP via Fast2SMS             |
|          |report_utils.py                             |FPDF, DOCX report logic      |
|          |log_utils.py                                |Log CSV & storage            |
|          |db_utils.py                                 |SQLite ops                   |
|          |verification_utils.py                       |Face match, smile, blink     |
|database  |verifier_system.db                          |Verifier login DB            |
|(under    |kyc_records.db                              |KYC logs & history DB        |
| backend) |                                            |                             |
|uploads   |kyc_docs/, videos/, transcripts/, logs/     |Uploaded user files          |
|          |reports/                                    |PDF reports                  |
|assets    |shape_predictor_68_face_landmarks.dat       |dlib facial landmark model   |
|docs      |BRD.docx, FRD.docx, TDD.docx                |Tech specs                   |
|          |Business_Case.docx, Test_Plan.docx          |Planning docs                |
|          |UAT_Sign_Off.docx, Deployment_Checklist.docx|Deployment checklists        |
|          |Report_Sample.pdf                           |Sample output                |
|*root*    |README.md, .gitignore                       |Project metadata             |
|          |requirements.txt, environment.yml           |Python dependencies          |
|          |app_verifier.py                             |Verifier logic entrypoint    |



## Tech Stack

| Layer     | Technology              |
|-----------|--------------------------|
| Frontend  | Streamlit                |
| Backend   | Flask + Flask-CORS       |
| Database  | SQLite + CSV             |
| AI/NLP    | OpenAI GPT-4             |
| Speech    | AWS Transcribe           |
| OCR       | Tesseract                |
| Face Match| face_recognition, dlib   |
| Reports   | FPDF, python-docx        |
| OTP       | Fast2SMS, Gmail SMTP     |



##  How to Run Locally

###  1. Clone the Repo

git clone https://github.com/RANGAMMISHRA/video-kyc-project.git
cd video-kyc-project


### 2. Create & Activate Virtual Environment
##-1.)
conda create --prefix vkycenv python=3.11
conda activate vkycenv
##2.)
conda env create -f environment.yml
conda activate vkycenv
###  3. Install Dependencies

pip install -r requirements.txt


### 4. Setup Environment
Create a `.env` file:

GMAIL_APP_PASSWORD=your_app_password
FAST2SMS_API_KEY=your_api_key
OPENAI_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### 5. Run Backend

cd backend
python app.py


### 6. Run Frontend

cd frontend
streamlit run app.py




## Sample Credentials

| Org Code | Emp Code | Password   | Role     |
|----------|----------|------------|----------|
| BB001  | EMP001   | password   | Verifier |
| HD001  | ADMIN01  | PASSWORD   | Admin    |

> On first login, password change is enforced via OTP.
---

## Test Coverage

- [x] Unit Tests for All Utility Functions
- [x] Manual UAT with Edge Cases
- [x] PDF/Docx Report Validation
- [x] Live KYC Flow: Upload + Capture
- [x] Speech to Text & QA Extraction
- [x] Logs + Audit Trail Tested

---

##  Documentation

All key documents are in the `/docs` folder:

- Business Case
- BRD (Business Requirements)
- FRD (Functional Requirements)
- TDD (Technical Design)
- Test Strategy & UAT
- Deployment Checklist
- Report Samples



## 🧑‍💼 Contributors

- **Rangam Kumar Mishra** — Project Lead  
- Verifier UI Design – [Streamlit]
- Backend API Development – [Flask]
- AI/NLP Integration – [OpenAI, AWS]
- Documentation – [MS Word, Docx]



## 📜 License

This project is licensed under the MIT License.

---

## 📞 Support

For support or integration requests, contact:

📧 rangammishra@gmail.com  
📞 +91 9934315080  
🌐 [LinkedIn Profile](https://www.linkedin.com/in/rangammishra)

