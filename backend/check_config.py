#!/usr/bin/env python3
"""
Check Configuration - Verify what settings are being loaded
"""

from app.core.config import settings
import os

def check_config():
    """Check current configuration values"""
    
    print("🔍 Configuration Check")
    print("=" * 50)
    
    print(f"Environment Variables:")
    print(f"  JWT_SECRET_KEY (env): {os.getenv('JWT_SECRET_KEY', 'NOT SET')}")
    print(f"  DATABASE_URL (env): {os.getenv('DATABASE_URL', 'NOT SET')}")
    print(f"  ENVIRONMENT (env): {os.getenv('ENVIRONMENT', 'NOT SET')}")
    
    print(f"\nSettings Values:")
    print(f"  JWT_SECRET_KEY: {settings.JWT_SECRET_KEY}")
    print(f"  JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"  DATABASE_URL: {settings.DATABASE_URL}")
    print(f"  ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"  DEBUG: {settings.DEBUG}")
    
    print(f"\nExpected vs Actual:")
    expected_secret = "af8634c8a6d1e120bd0e7a0d98520cc2"
    actual_secret = settings.JWT_SECRET_KEY
    
    print(f"  Expected JWT Secret: {expected_secret}")
    print(f"  Actual JWT Secret: {actual_secret}")
    print(f"  Match: {'✅' if expected_secret == actual_secret else '❌'}")

if __name__ == "__main__":
    check_config()