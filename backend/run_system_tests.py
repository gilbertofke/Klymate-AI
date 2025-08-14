"""
System Test Runner

This script runs comprehensive system tests and generates detailed reports
for the Klymate AI backend system.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import subprocess
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SystemTestRunner:
    """Comprehensive system test runner"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_info': self._get_system_info(),
            'test_suites': {},
            'summary': {},
            'performance_metrics': {}
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total // (1024**3),  # GB
            'disk_free': psutil.disk_usage('.').free // (1024**3)  # GB
        }
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("🔄 Running integration tests...")
        
        start_time = time.time()
        
        try:
            # Run integration tests using pytest
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/test_system_integration.py',
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd='.')
            
            execution_time = time.time() - start_time
            
            test_result = {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Integration tests passed")
            else:
                print("❌ Integration tests failed")
                print(f"Error: {result.stderr}")
            
            return test_result
            
        except Exception as e:
            return {
                'status': 'error',
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("🔄 Running performance tests...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/test_performance.py',
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd='.')
            
            execution_time = time.time() - start_time
            
            test_result = {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Performance tests passed")
            else:
                print("❌ Performance tests failed")
                print(f"Error: {result.stderr}")
            
            return test_result
            
        except Exception as e:
            return {
                'status': 'error',
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    async def run_api_tests(self) -> Dict[str, Any]:
        """Run API documentation and structure tests"""
        print("🔄 Running API tests...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/test_api_documentation.py',
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd='.')
            
            execution_time = time.time() - start_time
            
            test_result = {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ API tests passed")
            else:
                print("❌ API tests failed")
                print(f"Error: {result.stderr}")
            
            return test_result
            
        except Exception as e:
            return {
                'status': 'error',
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    async def run_carbon_credits_tests(self) -> Dict[str, Any]:
        """Run carbon credits specific tests"""
        print("🔄 Running carbon credits tests...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/test_carbon_credits_integration.py',
                'tests/test_carbon_credits_service.py',
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd='.')
            
            execution_time = time.time() - start_time
            
            test_result = {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Carbon credits tests passed")
            else:
                print("❌ Carbon credits tests failed")
                print(f"Error: {result.stderr}")
            
            return test_result
            
        except Exception as e:
            return {
                'status': 'error',
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def test_system_imports(self) -> Dict[str, Any]:
        """Test that all system components can be imported"""
        print("🔄 Testing system imports...")
        
        import_tests = {
            'models': [
                'app.models.user',
                'app.models.habit',
                'app.models.carbon_credit',
                'app.models.badge',
                'app.models.ai_conversation'
            ],
            'services': [
                'app.services.habit_service',
                'app.services.carbon_credits_service',
                'app.services.gamification_service',
                'app.services.analytics_service',
                'app.services.ai_coach_service'
            ],
            'repositories': [
                'app.repositories.user_repository',
                'app.repositories.habit_repository',
                'app.repositories.carbon_credit_repository',
                'app.repositories.badge_repository'
            ],
            'api_endpoints': [
                'app.api.v1.endpoints.users',
                'app.api.v1.endpoints.habits',
                'app.api.v1.endpoints.carbon_credits',
                'app.api.v1.endpoints.gamification',
                'app.api.v1.endpoints.analytics'
            ]
        }
        
        results = {}
        all_passed = True
        
        for category, modules in import_tests.items():
            category_results = []
            
            for module in modules:
                try:
                    __import__(module)
                    category_results.append({
                        'module': module,
                        'status': 'success'
                    })
                except Exception as e:
                    category_results.append({
                        'module': module,
                        'status': 'failed',
                        'error': str(e)
                    })
                    all_passed = False
            
            results[category] = category_results
        
        if all_passed:
            print("✅ All system imports successful")
        else:
            print("❌ Some system imports failed")
        
        return {
            'status': 'passed' if all_passed else 'failed',
            'results': results
        }
    
    def generate_api_documentation(self) -> Dict[str, Any]:
        """Generate API documentation"""
        print("🔄 Generating API documentation...")
        
        try:
            from tests.test_api_documentation import generate_api_documentation_file
            
            docs = generate_api_documentation_file()
            
            # Save documentation
            with open('API_DOCUMENTATION.json', 'w') as f:
                json.dump(docs, f, indent=2)
            
            print("✅ API documentation generated")
            
            return {
                'status': 'success',
                'file': 'API_DOCUMENTATION.json',
                'endpoints_documented': len(docs.get('endpoints', {}))
            }
            
        except Exception as e:
            print(f"❌ API documentation generation failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all system tests"""
        print("🚀 Starting comprehensive system tests...")
        print("=" * 60)
        
        total_start_time = time.time()
        
        # 1. Test system imports
        self.test_results['test_suites']['imports'] = self.test_system_imports()
        
        # 2. Generate API documentation
        self.test_results['test_suites']['api_docs'] = self.generate_api_documentation()
        
        # 3. Run integration tests
        self.test_results['test_suites']['integration'] = await self.run_integration_tests()
        
        # 4. Run performance tests
        self.test_results['test_suites']['performance'] = await self.run_performance_tests()
        
        # 5. Run API tests
        self.test_results['test_suites']['api'] = await self.run_api_tests()
        
        # 6. Run carbon credits tests
        self.test_results['test_suites']['carbon_credits'] = await self.run_carbon_credits_tests()
        
        total_execution_time = time.time() - total_start_time
        
        # Generate summary
        self.test_results['summary'] = self._generate_summary(total_execution_time)
        
        print("=" * 60)
        print("📊 Test Summary:")
        print(f"Total execution time: {total_execution_time:.2f} seconds")
        
        for suite_name, suite_result in self.test_results['test_suites'].items():
            status = suite_result.get('status', 'unknown')
            emoji = "✅" if status == 'passed' or status == 'success' else "❌"
            print(f"{emoji} {suite_name.title()}: {status}")
        
        return self.test_results
    
    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(self.test_results['test_suites'])
        passed_tests = sum(
            1 for result in self.test_results['test_suites'].values()
            if result.get('status') in ['passed', 'success']
        )
        
        return {
            'total_test_suites': total_tests,
            'passed_test_suites': passed_tests,
            'failed_test_suites': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'total_execution_time': total_time,
            'overall_status': 'passed' if passed_tests == total_tests else 'failed'
        }
    
    def save_results(self, filename: str = 'SYSTEM_TEST_RESULTS.json'):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Test results saved to {filename}")


async def main():
    """Main test runner function"""
    runner = SystemTestRunner()
    
    try:
        results = await runner.run_all_tests()
        runner.save_results()
        
        # Exit with appropriate code
        overall_status = results['summary']['overall_status']
        exit_code = 0 if overall_status == 'passed' else 1
        
        print(f"\n🏁 System tests completed with status: {overall_status}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())