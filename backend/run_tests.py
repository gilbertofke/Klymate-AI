#!/usr/bin/env python3
"""
Test runner for Klymate AI Backend

This script ensures proper environment setup before running tests.
Usage: python run_tests.py
"""

import sys
import os
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the Python environment for testing."""
    # Get the backend directory
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    
    # Add to Python path
    sys.path.insert(0, str(backend_dir))
    sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = f"{backend_dir}{os.pathsep}{project_root}"
    
    print("🔧 Environment setup complete")
    print(f"   Backend dir: {backend_dir}")
    print(f"   Project root: {project_root}")
    print(f"   Python path: {os.environ.get('PYTHONPATH', 'Not set')}")

def run_tests():
    """Run the test suite."""
    print("\n🧪 Running Klymate AI Backend Tests...")
    
    # Run pytest with proper configuration
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "tests/",
        "--disable-warnings"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    setup_environment()
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    sys.exit(exit_code)