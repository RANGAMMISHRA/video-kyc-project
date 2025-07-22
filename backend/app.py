# backend/app.py

from flask import Flask
from verify_api import verify_bp  # Main blueprint with all KYC endpoints
from log_api import log_bp        # Log-related routes
from ocr_api import ocr_bp        # OCR-only routes
from report_api import report_bp  # PDF report routes

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Register Blueprints
app.register_blueprint(verify_bp, url_prefix='/verify')
app.register_blueprint(log_bp, url_prefix='/log')
app.register_blueprint(ocr_bp, url_prefix='/ocr')
app.register_blueprint(report_bp, url_prefix='/report')

# ✅ Health-check route
@app.route('/')
def home():
    return {"status": "KYC API is running!"}

# ✅ Start the app
if __name__ == '__main__':
    print("🚀 Backend starting up...")
    app.run(debug=True, port=5000)
