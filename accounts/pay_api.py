import requests
import uuid

# بيانات الاعتماد
CLIENT_ID = "1278490599"
USERNAME = "a61bacbc-3096-4e30-968c-f5124aa2a465"
PASSWORD = "ps6mURldytqeAuqgD3bbF7ORWL6MPkrA"

BASE_URL = "https://walletsit.neoleap.com.sa/merchantb2b"

def generate_token():
    url = f"{BASE_URL}/v1/payments/merchant/generatetoken"
    headers = {
        "X-Request-Id": str(uuid.uuid4()),
        "X-Client-Id": CLIENT_ID,
        "X-Session-Language": "EN",
        "Content-Type": "application/json"
    }
    body = {
        "userName": USERNAME,
        "password": PASSWORD
    }
    res = requests.post(url, json=body, headers=headers)
    if res.status_code == 200:
        return res.json(), res.headers
    else:
        raise Exception(f"Token Error: {res.text}")

def initiate_payment(token, session_id, amount=10.0, mobile="+966568595106"):
    url = f"{BASE_URL}/v1/payments/ecomm/initiate"
    headers = {
        "X-Request-Id": str(uuid.uuid4()),
        "X-Client-Id": CLIENT_ID,
        "X-Session-Language": "EN",
        "X-Security-Token": token,
        "X-Session-Id": session_id,
        "Content-Type": "application/json"
    }
    body = {
        "transactionInfo": {
            "amount": {
                "currency": "SAR",
                "value": amount
            },
            "externalTransactionId": str(uuid.uuid4()),
            "sourceConsumerMobileNumber": mobile,
            "targetMerchantId": "5",
            "targetMerchantWalletNumber": "500",
            "targetTerminalId": "1141"
        }
    }
    res = requests.post(url, json=body, headers=headers)
    if res.status_code == 200:
        return res.json(), res.headers
    else:
        raise Exception(f"Initiate Error: {res.text}")

def execute_payment(token, session_id, verification_token, otp_reference, otp="1234", amount=10.0, mobile="+966568595106"):
    url = f"{BASE_URL}/v1/payments/ecomm/execute"
    headers = {
        "X-Request-Id": str(uuid.uuid4()),
        "X-Client-Id": CLIENT_ID,
        "X-Session-Language": "EN",
        "X-Security-Token": token,
        "X-Session-Id": session_id,
        "X-Verification-Token": verification_token,
        "Content-Type": "application/json"
    }
    body = {
        "transactionInfo": {
            "amount": {
                "currency": "SAR",
                "value": amount
            },
            "externalTransactionId": str(uuid.uuid4()),
            "sourceConsumerMobileNumber": mobile,
            "targetMerchantId": "5",           # ✅ القيمة الصحيحة
            "targetMerchantWalletNumber": "500", # ✅ القيمة الصحيحة
            "targetTerminalId": "1141"         # ✅ القيمة الصحيحة
        },
        "OTPInfo": {
            "otp": otp,
            "otpReference": otp_reference
        }
    }
    res = requests.post(url, json=body, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(f"Execute Error: {res.text}")