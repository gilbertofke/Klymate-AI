#!/usr/bin/env python3
"""
Simple test runner for CI/CD pipeline components
"""

import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def run_test(test_func, test_name):
    """Run a single test function"""
    try:
        test_func()
        print(f"✅ {test_name} - PASSED")
        return True
    except Exception as e:
        print(f"❌ {test_name} - FAILED: {str(e)}")
        return False

def main():
    """Run all CI/CD pipeline tests"""
    print("🚀 Testing CI/CD Pipeline Components")
    print("=" * 50)
    
    from tests.test_cicd_pipeline import TestCICDPipeline, TestDeploymentScripts
    
    # Initialize test classes
    cicd_test = TestCICDPipeline()
    deploy_test = TestDeploymentScripts()
    
    # Define tests to run
    tests = [
        (cicd_test.test_github_workflows_exist, "GitHub Workflows Exist"),
        (cicd_test.test_dockerfile_exists_and_valid, "Dockerfile Valid"),
        (cicd_test.test_environment_files_exist, "Environment Files Exist"),
        (cicd_test.test_deployment_scripts_exist, "Deployment Scripts Exist"),
        (deploy_test.test_deploy_script_validation, "Deploy Script Validation"),
        (deploy_test.test_rollback_script_validation, "Rollback Script Validation"),
    ]
    
    # Run tests
    passed = 0
    total = len(tests)
    
    for test_func, test_name in tests:
        if run_test(test_func, test_name):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CI/CD pipeline tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())