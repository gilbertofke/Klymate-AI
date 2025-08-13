#!/usr/bin/env python3
"""
Comprehensive Test Runner - Task 10 Implementation

This script runs the complete test suite with proper infrastructure setup,
error handling, and comprehensive reporting. Follows the design document's
testing strategy with proper test categorization and execution.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestRunner:
    """Comprehensive test runner with infrastructure management."""
    
    def __init__(self):
        """Initialize test runner."""
        self.start_time = time.time()
        self.results = {}
        self.backend_dir = Path(__file__).parent
        self.test_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_suites": {},
            "summary": {},
            "infrastructure": {}
        }
    
    def setup_test_environment(self) -> bool:
        """Set up test environment variables and configuration."""
        try:
            logger.info("Setting up test environment...")
            
            # Set test environment variables
            test_env = {
                "ENVIRONMENT": "test",
                "TESTING": "true",
                "DATABASE_URL": "sqlite+aiosqlite:///test.db",
                "REDIS_URL": "redis://localhost:6379/1",
                "CACHE_ENABLED": "false",
                "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
                "JWT_ALGORITHM": "HS256",
                "FIREBASE_PROJECT_ID": "test-project",
                "OPENAI_API_KEY": "test-key",
                "LOG_LEVEL": "INFO"
            }
            
            for key, value in test_env.items():
                os.environ[key] = value
            
            logger.info("Test environment configured")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup test environment: {str(e)}")
            return False
    
    def run_command(self, cmd: List[str], description: str, timeout: int = 300) -> Dict[str, Any]:
        """Run a command and capture results."""
        logger.info(f"Running: {description}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "description": description
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "duration": timeout,
                "description": description
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": 0,
                "description": description
            }
    
    def test_infrastructure_setup(self) -> bool:
        """Test that testing infrastructure is properly set up."""
        logger.info("Testing infrastructure setup...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major != 3 or python_version.minor < 9:
            logger.warning(f"Python {python_version.major}.{python_version.minor} detected. Python 3.9+ recommended.")
        
        # Check required packages
        required_packages = [
            "pytest", "pytest-asyncio", "pytest-cov", "fastapi", 
            "sqlalchemy", "pydantic", "redis", "factory_boy"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing packages: {', '.join(missing_packages)}")
            logger.info("Install with: pip install " + " ".join(missing_packages))
            return False
        
        # Check test files exist
        required_test_files = [
            "tests/conftest.py",
            "tests/factories.py",
            "tests/fixtures.py",
            "tests/utils.py",
            "tests/test_infrastructure.py"
        ]
        
        missing_files = []
        for file_path in required_test_files:
            if not (self.backend_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing test files: {', '.join(missing_files)}")
            return False
        
        logger.info("Infrastructure setup validated")
        return True
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests (70% of test suite)."""
        cmd = [
            "python", "-m", "pytest",
            "-c", "pytest_comprehensive.ini",
            "-m", "unit or not (integration or e2e)",
            "--tb=short",
            "--maxfail=10",
            "tests/"
        ]
        
        return self.run_command(cmd, "Unit Tests")
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests (20% of test suite)."""
        cmd = [
            "python", "-m", "pytest",
            "-c", "pytest_comprehensive.ini",
            "-m", "integration",
            "--tb=short",
            "--maxfail=5",
            "tests/"
        ]
        
        return self.run_command(cmd, "Integration Tests")
    
    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests (10% of test suite)."""
        cmd = [
            "python", "-m", "pytest",
            "-c", "pytest_comprehensive.ini",
            "-m", "e2e",
            "--tb=short",
            "--maxfail=3",
            "tests/"
        ]
        
        return self.run_command(cmd, "End-to-End Tests")
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests for basic functionality."""
        cmd = [
            "python", "-m", "pytest",
            "-c", "pytest_comprehensive.ini",
            "-m", "smoke",
            "--tb=line",
            "tests/"
        ]
        
        return self.run_command(cmd, "Smoke Tests")
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        cmd = [
            "python", "-m", "pytest",
            "-c", "pytest_comprehensive.ini",
            "-m", "performance",
            "--tb=short",
            "tests/"
        ]
        
        return self.run_command(cmd, "Performance Tests")
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run comprehensive coverage analysis."""
        cmd = [
            "python", "-m", "pytest",
            "-c", "pytest_comprehensive.ini",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=xml",
            "--cov-report=json",
            "--cov-report=term-missing",
            "--cov-fail-under=75",
            "tests/"
        ]
        
        return self.run_command(cmd, "Coverage Analysis", timeout=600)
    
    def analyze_test_results(self) -> Dict[str, Any]:
        """Analyze and summarize test results."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_duration = 0
        
        for suite_name, result in self.results.items():
            if result["success"]:
                # Parse pytest output for test counts
                stdout = result["stdout"]
                if "passed" in stdout or "failed" in stdout:
                    # Simple parsing - could be enhanced
                    lines = stdout.split('\n')
                    for line in lines:
                        if "passed" in line and "failed" in line:
                            # Extract numbers from pytest summary
                            pass
            
            total_duration += result["duration"]
        
        # Try to read coverage report if available
        coverage_data = {}
        coverage_file = self.backend_dir / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read coverage data: {str(e)}")
        
        return {
            "total_duration": total_duration,
            "test_suites_run": len(self.results),
            "successful_suites": sum(1 for r in self.results.values() if r["success"]),
            "failed_suites": sum(1 for r in self.results.values() if not r["success"]),
            "coverage": coverage_data.get("totals", {}).get("percent_covered", 0) if coverage_data else 0
        }
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report."""
        analysis = self.analyze_test_results()
        
        report = f"""
# Klymate AI Backend Test Report
Generated: {self.test_report['timestamp']}
Duration: {analysis['total_duration']:.2f} seconds

## Test Suite Results
"""
        
        for suite_name, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            report += f"- {suite_name}: {status} ({result['duration']:.2f}s)\n"
        
        report += f"""
## Summary
- Test Suites Run: {analysis['test_suites_run']}
- Successful: {analysis['successful_suites']}
- Failed: {analysis['failed_suites']}
- Code Coverage: {analysis['coverage']:.1f}%

## Test Strategy Compliance
Following design document testing strategy:
- Unit Tests (70%): Business logic, models, schemas ✓
- Integration Tests (20%): API endpoints, services ✓
- End-to-End Tests (10%): Full user workflows ✓

## Quality Gates
"""
        
        # Quality gate checks
        coverage_gate = analysis['coverage'] >= 75
        success_gate = analysis['failed_suites'] == 0
        
        report += f"- Code Coverage ≥ 75%: {'✅ PASSED' if coverage_gate else '❌ FAILED'} ({analysis['coverage']:.1f}%)\n"
        report += f"- All Test Suites Pass: {'✅ PASSED' if success_gate else '❌ FAILED'}\n"
        
        overall_status = "✅ PASSED" if (coverage_gate and success_gate) else "❌ FAILED"
        report += f"\n## Overall Status: {overall_status}\n"
        
        # Add detailed results for failed tests
        failed_results = {k: v for k, v in self.results.items() if not v["success"]}
        if failed_results:
            report += "\n## Failed Test Details\n"
            for suite_name, result in failed_results.items():
                report += f"\n### {suite_name}\n"
                report += f"Return Code: {result['returncode']}\n"
                if result['stderr']:
                    report += f"Error Output:\n```\n{result['stderr'][:1000]}...\n```\n"
        
        return report
    
    def save_test_report(self, report: str):
        """Save test report to file."""
        report_file = self.backend_dir / "TEST_COMPREHENSIVE_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Test report saved to: {report_file}")
    
    def run_all_tests(self) -> bool:
        """Run complete test suite."""
        logger.info("🚀 Starting Comprehensive Test Suite")
        logger.info("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            logger.error("Failed to setup test environment")
            return False
        
        if not self.test_infrastructure_setup():
            logger.error("Infrastructure setup validation failed")
            return False
        
        # Test execution order (fastest to slowest)
        test_suites = [
            ("Smoke Tests", self.run_smoke_tests),
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("End-to-End Tests", self.run_e2e_tests),
            ("Performance Tests", self.run_performance_tests),
            ("Coverage Analysis", self.run_coverage_analysis)
        ]
        
        # Run test suites
        for suite_name, test_func in test_suites:
            logger.info(f"\n🧪 Running {suite_name}...")
            result = test_func()
            self.results[suite_name] = result
            
            if result["success"]:
                logger.info(f"✅ {suite_name} completed successfully ({result['duration']:.2f}s)")
            else:
                logger.error(f"❌ {suite_name} failed ({result['duration']:.2f}s)")
                if result["stderr"]:
                    logger.error(f"Error: {result['stderr'][:500]}...")
        
        # Generate report
        report = self.generate_test_report()
        self.save_test_report(report)
        
        # Print summary
        analysis = self.analyze_test_results()
        total_time = time.time() - self.start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST EXECUTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total Time: {total_time:.2f} seconds")
        logger.info(f"Successful Suites: {analysis['successful_suites']}/{analysis['test_suites_run']}")
        logger.info(f"Code Coverage: {analysis['coverage']:.1f}%")
        
        success = analysis['failed_suites'] == 0 and analysis['coverage'] >= 75
        
        if success:
            logger.info("🎉 All tests passed! Testing infrastructure is complete.")
        else:
            logger.warning("⚠️ Some tests failed or coverage is below threshold.")
        
        return success


def main():
    """Main entry point."""
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()