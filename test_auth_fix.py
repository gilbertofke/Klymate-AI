#!/usr/bin/env python3
"""
Quick test script to verify authentication is working after Firebase fix.
"""

import requests
import json
import sys

def test_backend_health():
    """Test if backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not running: {e}")
        return False

def test_firebase_status():
    """Test Firebase configuration status."""
    try:
        response = requests.get("http://localhost:8000/api/v1/auth/firebase-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"🔥 Firebase Status: {data}")
            return data.get("firebase_initialized", False)
        else:
            print(f"❌ Firebase status check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Firebase status check failed: {e}")
        return False

def test_email_registration():
    """Test email registration (fallback method)."""
    try:
        test_data = {
            "email": "test@klymate.ai",
            "password": "testpassword123",
            "name": "Test User"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register-email",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Email registration works")
            data = response.json()
            return data.get("tokens", {}).get("access_token")
        else:
            print(f"❌ Email registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Email registration failed: {e}")
        return None

def test_email_login():
    """Test email login (fallback method)."""
    try:
        test_data = {
            "email": "test@klymate.ai",
            "password": "testpassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login-email",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Email login works")
            return True
        else:
            print(f"❌ Email login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Email login failed: {e}")
        return False

def main():
    """Run all authentication tests."""
    print("🧪 Testing Klymate AI Authentication Fix")
    print("=" * 50)
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it with:")
        print("cd backend && python -m uvicorn app.main:app --reload")
        return False
    
    # Test 2: Firebase status
    firebase_working = test_firebase_status()
    if firebase_working:
        print("✅ Firebase is properly configured")
    else:
        print("⚠️  Firebase is not configured (fallback mode active)")
    
    # Test 3: Email registration
    access_token = test_email_registration()
    if not access_token:
        return False
    
    # Test 4: Email login
    if not test_email_login():
        return False
    
    print("\n🎉 All tests passed!")
    print("\nNext steps:")
    if not firebase_working:
        print("1. Follow FIREBASE_AUTHENTICATION_SETUP.md to configure Firebase")
        print("2. Users can still register/login with email while you set up Firebase")
    print("3. Start frontend: cd frontend && npm run dev")
    print("4. Visit http://localhost:3000 and test the registration flow")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)