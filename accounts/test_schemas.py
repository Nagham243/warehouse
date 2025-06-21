import requests
import uuid
import json
import base64
from datetime import datetime

# Your credentials
CLIENT_ID = "1278490599"
USERNAME = "a61bacbc-3096-4e30-968c-f5124aa2a465"
PASSWORD = "ps6mURldytqeAuqgD3bbF7ORWL6MPkrA"
BASE_URL = "https://walletsit.neoleap.com.sa/merchantb2b"

# Merchant info
MERCHANT_ID = "5"
WALLET_NUMBER = "99001"
TERMINAL_ID = "2446"

def generate_token():
    """Generate authentication token"""
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

    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        return response.json(), response.headers
    else:
        raise Exception(f"Token Error: {response.status_code} - {response.text}")

def format_mobile_number(mobile):
    """Format mobile number correctly"""
    clean_mobile = ''.join(filter(str.isdigit, str(mobile)))

    if clean_mobile.startswith('966'):
        return clean_mobile
    elif clean_mobile.startswith('05'):
        return '966' + clean_mobile[1:]
    elif clean_mobile.startswith('5') and len(clean_mobile) == 9:
        return '966' + clean_mobile
    elif len(clean_mobile) == 10 and clean_mobile.startswith('05'):
        return '966' + clean_mobile[1:]
    else:
        return '966' + clean_mobile.lstrip('0')

def test_with_different_headers(token, session_id, amount=10.0, mobile="+966550000000"):
    """Test with different header combinations to handle empty responses"""

    formatted_mobile = format_mobile_number(mobile)
    transaction_id = str(uuid.uuid4())

    print(f"Testing payment with different header combinations:")
    print(f"- Amount: {amount} SAR")
    print(f"- Mobile: {mobile} -> {formatted_mobile}")
    print(f"- Transaction ID: {transaction_id}")

    # Working endpoint from previous tests
    url = f"{BASE_URL}/api/v1/payments/initiate"

    # Test payload (using the simplest schema that worked)
    payload = {
        "amount": float(amount),
        "currency": "SAR",
        "mobileNumber": formatted_mobile,
        "transactionId": transaction_id
    }

    # Different header combinations to try
    header_combinations = [
        # Combination 1: Standard headers with different Accept
        {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "EN",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        },

        # Combination 2: Without Accept header
        {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "EN",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json"
        },

        # Combination 3: With text/plain Accept
        {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "EN",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json",
            "Accept": "text/plain"
        },

        # Combination 4: With wildcard Accept
        {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "EN",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json",
            "Accept": "*/*"
        },

        # Combination 5: With XML Accept (some APIs prefer XML)
        {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "EN",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json",
            "Accept": "application/xml"
        },

        # Combination 6: Arabic language
        {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "AR",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    ]

    for i, headers in enumerate(header_combinations, 1):
        try:
            print(f"\n--- Header Combination {i} ---")
            print(f"Headers: {json.dumps(headers, indent=2)}")

            response = requests.post(url, json=payload, headers=headers, timeout=15)

            print(f"Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Length: {len(response.text)} characters")
            print(f"Response Content: '{response.text}'")

            # Check if response is not empty
            if response.status_code == 200 and response.text.strip():
                print(f"🎉 SUCCESS! Non-empty response with header combination {i}")
                try:
                    response_data = response.json()
                    print(f"JSON Response: {json.dumps(response_data, indent=2)}")
                    return response_data, headers
                except:
                    print(f"Plain text response: {response.text}")
                    return response.text, headers
            elif response.status_code == 200:
                print(f"⚠️ Empty response (likely a stub API)")
            else:
                print(f"❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ Exception: {e}")
            continue

    return None

def test_payment_status_endpoints(token, session_id):
    """Test payment status/inquiry endpoints"""
    print(f"\n{'='*60}")
    print("TESTING PAYMENT STATUS ENDPOINTS")
    print(f"{'='*60}")

    headers = {
        "X-Request-Id": str(uuid.uuid4()),
        "X-Client-Id": CLIENT_ID,
        "X-Session-Language": "EN",
        "X-Security-Token": token,
        "X-Session-Id": session_id,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Common status endpoint patterns
    status_endpoints = [
        "/api/v1/payments/status",
        "/api/v2/payments/status",
        "/payments/v1/status",
        "/payments/v2/status",
        "/api/v1/payments/inquiry",
        "/api/v2/payments/inquiry",
        "/payments/v1/inquiry",
        "/payments/v2/inquiry"
    ]

    # Test with GET requests (common for status)
    for endpoint in status_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, headers=headers, timeout=10)

            print(f"{endpoint}: Status {response.status_code}, Length: {len(response.text)}")
            if response.status_code == 200 and response.text.strip():
                print(f"  Content: {response.text[:200]}...")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

def analyze_empty_response_issue():
    """Analyze why we're getting empty responses"""
    print(f"\n{'='*60}")
    print("ANALYZING EMPTY RESPONSE ISSUE")
    print(f"{'='*60}")

    try:
        # Generate token
        token_data, token_headers = generate_token()
        token = token_headers.get("X-Security-Token")
        session_id = token_headers.get("X-Session-Id")

        print("Possible reasons for empty responses:")
        print("1. API is a stub/mock implementation")
        print("2. Wrong Content-Type or Accept headers")
        print("3. Missing required parameters")
        print("4. Sandbox vs Production environment issue")
        print("5. API expects different request format")

        # Test different header combinations
        result = test_with_different_headers(token, session_id, amount=1.0)

        if not result:
            print("\n🔍 Testing status endpoints...")
            test_payment_status_endpoints(token, session_id)

        # Test with different HTTP methods
        print(f"\n{'='*40}")
        print("TESTING DIFFERENT HTTP METHODS")
        print(f"{'='*40}")

        url = f"{BASE_URL}/api/v1/payments/initiate"
        headers = {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "EN",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json"
        }

        # Try GET method
        try:
            response = requests.get(url, headers=headers)
            print(f"GET: Status {response.status_code}, Length: {len(response.text)}")
            if response.text.strip():
                print(f"GET Response: {response.text[:200]}...")
        except Exception as e:
            print(f"GET Error: {e}")

        # Try PUT method
        try:
            response = requests.put(url, json={"test": True}, headers=headers)
            print(f"PUT: Status {response.status_code}, Length: {len(response.text)}")
            if response.text.strip():
                print(f"PUT Response: {response.text[:200]}...")
        except Exception as e:
            print(f"PUT Error: {e}")

    except Exception as e:
        print(f"Analysis failed: {e}")

def check_raw_response_details():
    """Check raw HTTP response details"""
    print(f"\n{'='*60}")
    print("RAW HTTP RESPONSE ANALYSIS")
    print(f"{'='*60}")

    try:
        token_data, token_headers = generate_token()
        token = token_headers.get("X-Security-Token")
        session_id = token_headers.get("X-Session-Id")

        url = f"{BASE_URL}/api/v1/payments/initiate"
        headers = {
            "X-Request-Id": str(uuid.uuid4()),
            "X-Client-Id": CLIENT_ID,
            "X-Session-Language": "EN",
            "X-Security-Token": token,
            "X-Session-Id": session_id,
            "Content-Type": "application/json"
        }

        payload = {
            "amount": 1.0,
            "currency": "SAR",
            "mobileNumber": "966550000000",
            "transactionId": str(uuid.uuid4())
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)

        print(f"HTTP Status: {response.status_code}")
        print(f"HTTP Reason: {response.reason}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print(f"\nResponse Body Details:")
        print(f"  Length: {len(response.content)} bytes")
        print(f"  Text Length: {len(response.text)} characters")
        print(f"  Raw Content: {response.content}")
        print(f"  Text Content: '{response.text}'")
        print(f"  Is Empty: {not response.text.strip()}")

        # Check if it's actually a redirect or something
        print(f"\nRequest Details:")
        print(f"  Final URL: {response.url}")
        print(f"  History: {response.history}")

    except Exception as e:
        print(f"Raw analysis failed: {e}")

def main():
    """Main diagnostic function"""
    print("=" * 80)
    print("NEOLEAP API - EMPTY RESPONSE DIAGNOSTIC")
    print("=" * 80)

    try:
        analyze_empty_response_issue()
        check_raw_response_details()

        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")
        print("1. Contact Neoleap support - the API might be in stub/demo mode")
        print("2. Verify if you're using the correct environment (sandbox vs production)")
        print("3. Check if your merchant account needs activation")
        print("4. Request a working example or Postman collection")
        print("5. The empty responses suggest the API accepts requests but doesn't process them")

    except Exception as e:
        print(f"Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()