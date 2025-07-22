# backend/ocr_api.py

from flask import Blueprint, request, jsonify
from utils.ocr_utils import extract_fields_from_image

ocr_bp = Blueprint("ocr", __name__)

@ocr_bp.route('/extract', methods=['POST'])
def extract_ocr():
    """
    Perform OCR on a single uploaded image (Aadhaar or PAN).
    Expects a multipart/form-data request with 'image' key.
    Returns raw text and extracted fields as JSON.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    # Safely unpack all three values from extract_fields_from_image
    fields, raw_text, conf_score = extract_fields_from_image(file)

    return jsonify({
        "ocr_text": raw_text,
        "fields": fields,
        "confidence": conf_score
    })
