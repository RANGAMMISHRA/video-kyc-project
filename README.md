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
├── backend/
│   ├── app.py
│   ├── verify_api.py
│   ├── ocr_api.py
│   ├── log_api.py
│   ├── report_api.py
│   └── utils/
│       ├── audio_extraction.py
│       ├── aws_transcribe_utils.py
│       ├── db_utils.py
│       ├── log_utils.py
│       ├── ocr_utils.py
│       ├── report_utils.py
│       ├── sms_utils.py
│       └── verification_utils.py
├── frontend/
│   ├── app.py
│   ├── app_verifier.py
│   ├── app_transcribe.py
│   ├── verifier_manage_ui.py
│   ├── verifier_admin_portal.py
│   ├── utils/
│   │   ├── api_client.py
│   │   └── helpers.py
├── database/
│   ├── verifier_system.db
│   └── kyc_records.db
├── uploads/
│   ├── kyc_docs/
│   ├── videos/
│   ├── transcripts/
│   ├── reports/
│   └── logs/
├── docs/
│   ├── Business_Case.docx
│   ├── BRD.docx
│   ├── FRD.docx
│   ├── TDD.docx
│   ├── Test_Plan.docx
│   ├── UAT_Sign_Off.docx
│   ├── Deployment_Checklist.docx
│   └── Report_Sample.pdf
└── README.md




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

