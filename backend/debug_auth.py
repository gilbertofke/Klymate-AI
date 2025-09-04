#!/usr/bin/env python3
"""
Debug Authentication - Test JWT token validation directly
"""

import jwt
from datetime import datetime, timedelta
from app.utils.jwt_handler import JWTHandler
from app.utils.auth_integration import AuthIntegration

def test_jwt_validation():
    """Test JWT token generation and validation"""
    
    print("🔍 Debugging JWT Authentication")
    print("=" * 50)
    
    # Generate test token
    payload = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "firebase_uid": "firebase_test_user_123",
        "token_type": "access",
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
        "sub": "test_user_123",
        "iss": "klymate-ai-backend"
    }
    
    secret = "af8634c8a6d1e120bd0e7a0d98520cc2"
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    print(f"✅ Generated Token: {token[:50]}...")
    print(f"📋 Payload: {payload}")
    
    # Test 1: Direct JWT verification
    print(f"\n🧪 Test 1: Direct JWT Verification")
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"], issuer="klymate-ai-backend")
        print(f"✅ Direct verification successful: {decoded}")
    except Exception as e:
        print(f"❌ Direct verification failed: {e}")
    
    # Test 2: JWTHandler verification
    print(f"\n🧪 Test 2: JWTHandler Verification")
    try:
        result = JWTHandler.verify_token(token, "access")
        print(f"✅ JWTHandler verification successful: {result}")
    except Exception as e:
        print(f"❌ JWTHandler verification failed: {e}")
    
    # Test 3: AuthIntegration validation
    print(f"\n🧪 Test 3: AuthIntegration Validation")
    try:
        auth_header = f"Bearer {token}"
        result = AuthIntegration.validate_request_token(auth_header)
        print(f"✅ AuthIntegration validation successful: {result}")
    except Exception as e:
        print(f"❌ AuthIntegration validation failed: {e}")
    
    print(f"\n🎯 Debug Complete!")

if __name__ == "__main__":
    test_jwt_validation()