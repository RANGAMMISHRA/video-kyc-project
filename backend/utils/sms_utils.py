# backend/utils/sms_utils.py
import requests

def send_otp_via_sms(phone_number: str, otp: str, api_key: str) -> bool:
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        'authorization': api_key,
        'Content-Type': "application/json"
    }
    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": phone_number
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"SMS Response: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False
