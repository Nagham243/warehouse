from accounts.pay_api import generate_token, initiate_payment, execute_payment

def test_payment_flow():
    try:
        print("1. Testing token generation...")
        token_data, token_headers = generate_token()
        print(f"✓ Token generated successfully")
        print(f"Token: {token_headers.get('X-Security-Token')[:20]}...")

        token = token_headers.get("X-Security-Token")
        session_id = token_headers.get("X-Session-Id")

        print("\n2. Testing payment initiation...")
        mobile = "+966568595106"
        amount = 99.0

        init_data, init_headers = initiate_payment(token, session_id, amount=amount, mobile=mobile)
        print(f"✓ Payment initiated successfully")
        print(f"OTP Reference: {init_data['body']['otpReference']}")

        otp_reference = init_data["body"]["otpReference"]
        verification_token = init_headers.get("X-Verification-Token")

        print("\n3. Testing payment execution...")
        test_otp = "1234"

        payment_result = execute_payment(
            token, session_id, verification_token,
            otp_reference, test_otp, amount, mobile
        )

        print(f"✓ Payment execution completed")
        print(f"Status: {payment_result.get('body', {}).get('status', 'Unknown')}")
        print(f"Transaction ID: {payment_result.get('body', {}).get('transactionId', 'N/A')}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Payment API Test ===")
    success = test_payment_flow()
    print(f"\n=== Test {'PASSED' if success else 'FAILED'} ===")