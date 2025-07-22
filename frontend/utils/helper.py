# frontend/utils/helpers.py

from datetime import datetime
import re


def format_date(date_string):
    """Format a date string into a more readable format: DD-MM-YYYY HH:MM"""
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return date_string


def mask_sensitive_info(info, visible_chars=4):
    """Mask all but the last visible_chars characters of a string"""
    if not info:
        return info
    return '*' * max(len(info)-visible_chars, 0) + info[-visible_chars:]


def is_valid_aadhaar(aadhaar):
    """Check if Aadhaar number is valid (12 digits)"""
    return bool(re.fullmatch(r"\d{12}", aadhaar))


def is_valid_pan(pan):
    """Check if PAN number is valid (5 letters + 4 digits + 1 letter)"""
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan))


def is_valid_mobile(mobile):
    """Check if mobile number is valid (10 digits)"""
    return bool(re.fullmatch(r"\d{10}", mobile))


def capitalize_name(name):
    """Capitalize first letters of each part of a name"""
    return ' '.join(part.capitalize() for part in name.strip().split())
