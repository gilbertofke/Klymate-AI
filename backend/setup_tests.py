#!/usr/bin/env python3
"""
Test environment setup for Klymate AI Backend

Run this script to verify your test environment is properly configured.
Usage: python setup_tests.py
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 9:
        print("⚠️  Warning: Python 3.9+ recommended")
        return False
    
    print("✅ Python version compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'pytest',
        'fastapi',
        'firebase_admin',
        'jwt',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} missing")
    
    if missing:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def check_project_structure():
    """Check if project structure is correct."""
    backend_dir = Path(__file__).parent
    required_dirs = [
        'utils',
        'tests',
        'app',
        'app/core',
        'app/api',
        'app/models'
    ]
    
    required_files = [
        'utils/firebase_auth.py',
        'utils/jwt_handler.py',
        'config.py',
        'tests/test_firebase_auth.py',
        'tests/test_jwt_handler.py'
    ]
    
    print("\n📁 Checking project structure...")
    
    for dir_path in required_dirs:
        full_path = backend_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")

def test_imports():
    """Test if critical imports work."""
    print("\n🔍 Testing imports...")
    
    # Add backend to path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    try:
        from utils.firebase_auth import FirebaseAuth
        print("✅ Firebase auth import successful")
    except Exception as e:
        print(f"❌ Firebase auth import failed: {e}")
    
    try:
        from utils.jwt_handler import JWTHandler
        print("✅ JWT handler import successful")
    except Exception as e:
        print(f"❌ JWT handler import failed: {e}")
    
    try:
        from app.main import app
        print("✅ FastAPI app import successful")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")

def main():
    """Run all checks."""
    print("🔧 Klymate AI Backend Test Environment Setup")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
    ]
    
    check_project_structure()
    test_imports()
    
    if all(checks):
        print("\n✅ Environment setup complete! You can now run tests.")
        print("\nTo run tests:")
        print("  python run_tests.py")
        print("  OR")
        print("  python -m pytest tests/ -v")
    else:
        print("\n❌ Environment setup incomplete. Please fix the issues above.")

if __name__ == "__main__":
    main()