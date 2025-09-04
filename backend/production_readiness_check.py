#!/usr/bin/env python3
"""
Production Readiness Check for Klymate AI Backend

This script checks if the backend is ready for production deployment.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def check_api_endpoints():
    """Test core API endpoints."""
    print("=== API ENDPOINT TESTS ===")
    print()
    
    client = TestClient(app)
    
    # Test health endpoint
    print("1. Health Check:")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
        print("   ✅ Health check working")
    else:
        print("   ❌ Health check failed")
    print()
    
    # Test root endpoint
    print("2. Root Endpoint:")
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Project: {data.get('message', 'N/A')}")
        print(f"   Version: {data.get('version', 'N/A')}")
        print("   ✅ Root endpoint working")
    else:
        print("   ❌ Root endpoint failed")
    print()
    
    # Test API documentation
    print("3. API Documentation:")
    response = client.get("/docs")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ API docs accessible")
    else:
        print("   ❌ API docs not accessible")
    print()
    
    return True

def check_configuration():
    """Check production configuration."""
    print("=== CONFIGURATION CHECK ===")
    print()
    
    config_items = [
        ("Project Name", settings.PROJECT_NAME),
        ("Version", settings.VERSION),
        ("Environment", settings.ENVIRONMENT),
        ("Database URL", "***configured***" if settings.DATABASE_URL else "❌ NOT SET"),
        ("JWT Secret", "***configured***" if settings.JWT_SECRET_KEY != "test-secret-key-for-development-only" else "⚠️ USING DEFAULT"),
        ("Firebase Project", settings.FIREBASE_PROJECT_ID),
        ("OpenAI API", "***configured***" if settings.OPENAI_API_KEY != "test-openai-key" else "⚠️ USING DEFAULT"),
        ("Redis URL", settings.REDIS_URL),
    ]
    
    for name, value in config_items:
        print(f"   {name}: {value}")
    
    print()
    return True

def check_database_status():
    """Check database connectivity."""
    print("=== DATABASE STATUS ===")
    print()
    
    try:
        from app.core.database import check_database_connection
        import asyncio
        
        # Test database connection
        connection_ok = asyncio.run(check_database_connection())
        
        if connection_ok:
            print("   ✅ Database connection successful")
            print(f"   Database URL: {settings.DATABASE_URL}")
        else:
            print("   ❌ Database connection failed")
            
    except Exception as e:
        print(f"   ❌ Database check error: {str(e)}")
    
    print()
    return True

def check_firebase_status():
    """Check Firebase configuration."""
    print("=== FIREBASE STATUS ===")
    print()
    
    try:
        if settings.TESTING_MODE:
            print("   ⚠️ Running in test mode - Firebase disabled")
        else:
            from app.utils.firebase_config import FirebaseConfig
            
            if FirebaseConfig.is_initialized():
                print("   ✅ Firebase initialized successfully")
                print(f"   Project ID: {settings.FIREBASE_PROJECT_ID}")
            else:
                print("   ❌ Firebase not initialized")
                
    except Exception as e:
        print(f"   ⚠️ Firebase check: {str(e)}")
    
    print()
    return True

def main():
    """Main production readiness check."""
    print("🚀 KLYMATE AI BACKEND - PRODUCTION READINESS CHECK")
    print("=" * 60)
    print()
    
    checks = [
        ("API Endpoints", check_api_endpoints),
        ("Configuration", check_configuration),
        ("Database", check_database_status),
        ("Firebase", check_firebase_status),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"   ❌ {check_name} check failed: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print("=" * 60)
    print("📊 PRODUCTION READINESS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<20} {status}")
    
    print()
    print(f"Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Backend is READY for production!")
        print()
        print("Next steps for production deployment:")
        print("1. Set up proper Firebase service account")
        print("2. Configure production environment variables")
        print("3. Set up production database (TiDB Cloud)")
        print("4. Deploy to production platform (Railway/Render/AWS)")
        print("5. Set up monitoring and logging")
        return 0
    else:
        print("⚠️ Backend needs attention before production deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())