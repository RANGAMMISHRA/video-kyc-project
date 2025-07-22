import pytesseract
import cv2
from utils.performance_utils import timeit

@timeit
def extract_fields_from_image(image_path):
    """
    Extract fields from an Aadhaar/PAN image using OCR.
    Returns (fields_dict, raw_text, confidence_score).
    """
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    custom_oem_psm = '--oem 3 --psm 6'
    raw_text = pytesseract.image_to_string(gray, config=custom_oem_psm)

    # Example dummy extraction logic
    fields = {}
    if "Aadhaar" in raw_text:
        fields["aadhaar"] = ''.join(filter(str.isdigit, raw_text))[:12]
    if "PAN" in raw_text:
        words = raw_text.split()
        for w in words:
            if len(w) == 10 and w[:5].isalpha() and w[5:9].isdigit() and w[9].isalpha():
                fields["pan"] = w

    # Confidence is mocked since pytesseract doesn't provide direct scores per field.
    conf_score = 0.85 if fields else 0.3

    return fields, raw_text, conf_score
