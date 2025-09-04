#!/usr/bin/env python3
"""
Test JWT Token Generator for Local Testing
Usage: python generate_test_token.py
"""

import jwt
from datetime import datetime, timedelta
import json

def generate_test_token(
    user_id="test_user_123", 
    email="test@example.com",
    firebase_uid=None,
    hours_valid=24
):
    """Generate a test JWT token for local API testing"""
    
    if firebase_uid is None:
        firebase_uid = f"firebase_{user_id}"
    
    payload = {
        "user_id": user_id,
        "email": email,
        "firebase_uid": firebase_uid,
        "exp": datetime.utcnow() + timedelta(hours=hours_valid),
        "iat": datetime.utcnow(),
        "sub": user_id,  # Standard JWT subject claim
        "aud": "klymate-ai-backend",  # Audience
        "iss": "klymate-ai-backend"  # Issuer
    }
    
    # Use the provided JWT secret for testing
    secret = "af8634c8a6d1e120bd0e7a0d98520cc2"
    
    try:
        token = jwt.encode(payload, secret, algorithm="HS256")
        return token, payload
    except Exception as e:
        print(f"Error generating token: {e}")
        return None, None

def main():
    print("🔐 Klymate AI - Test JWT Token Generator")
    print("=" * 50)
    
    # Generate default test token
    token, payload = generate_test_token()
    
    if token:
        print("✅ Test token generated successfully!")
        print(f"\n📋 Token Details:")
        print(f"User ID: {payload['user_id']}")
        print(f"Email: {payload['email']}")
        print(f"Firebase UID: {payload['firebase_uid']}")
        print(f"Expires: {datetime.fromtimestamp(payload['exp'])}")
        
        print(f"\n🎫 JWT Token:")
        print(f"{token}")
        
        print(f"\n📝 For Postman Environment:")
        postman_vars = {
            "access_token": token,
            "user_id": payload['user_id'],
            "test_email": payload['email'],
            "firebase_uid": payload['firebase_uid']
        }
        print(json.dumps(postman_vars, indent=2))
        
        print(f"\n🧪 Test Authorization Header:")
        print(f"Authorization: Bearer {token}")
        
        print(f"\n⚠️  Security Note:")
        print("This token is for LOCAL TESTING ONLY!")
        print("Never use this secret in production!")
        
    else:
        print("❌ Failed to generate token")

if __name__ == "__main__":
    main()