"""
Test Coverage Configuration - Task 10 Implementation

This module provides test coverage configuration and reporting utilities
for comprehensive code coverage analysis and quality gates.
"""

import coverage
import os
import json
from typing import Dict, Any, List
from datetime import datetime
import pytest


class CoverageManager:
    """Manages code coverage collection and reporting."""
    
    def __init__(self, config_file: str = None):
        """Initialize coverage manager."""
        self.config_file = config_file or '.coveragerc'
        self.coverage = None
        self.coverage_data = {}
    
    def start_coverage(self):
        """Start coverage collection."""
        self.coverage = coverage.Coverage(
            config_file=self.config_file,
            source=['app'],
            omit=[
                '*/tests/*',
                '*/test_*',
                '*/conftest.py',
                '*/migrations/*',
                '*/alembic/*',
                '*/__pycache__/*',
                '*/venv/*',
                '*/env/*'
            ]
        )
        self.coverage.start()
    
    def stop_coverage(self):
        """Stop coverage collection."""
        if self.coverage:
            self.coverage.stop()
            self.coverage.save()
    
    def generate_report(self, output_format: str = 'html') -> Dict[str, Any]:
        """Generate coverage report."""
        if not self.coverage:
            raise RuntimeError("Coverage not initialized")
        
        # Generate different report formats
        reports = {}
        
        if output_format in ['html', 'all']:
            html_dir = 'htmlcov'
            self.coverage.html_report(directory=html_dir)
            reports['html'] = html_dir
        
        if output_format in ['xml', 'all']:
            xml_file = 'coverage.xml'
            self.coverage.xml_report(outfile=xml_file)
            reports['xml'] = xml_file
        
        if output_format in ['json', 'all']:
            json_file = 'coverage.json'
            self.coverage.json_report(outfile=json_file)
            reports['json'] = json_file
        
        # Get coverage statistics
        total_coverage = self.coverage.report(show_missing=False)
        
        # Get detailed coverage data
        coverage_data = self.coverage.get_data()
        
        report_data = {
            'total_coverage': total_coverage,
            'timestamp': datetime.utcnow().isoformat(),
            'files': {},
            'reports': reports
        }
        
        # Analyze per-file coverage
        for filename in coverage_data.measured_files():
            analysis = self.coverage.analysis2(filename)
            report_data['files'][filename] = {
                'statements': len(analysis.statements),
                'missing': len(analysis.missing),
                'excluded': len(analysis.excluded),
                'coverage': (len(analysis.statements) - len(analysis.missing)) / len(analysis.statements) * 100 if analysis.statements else 0
            }
        
        return report_data
    
    def check_coverage_threshold(self, threshold: float = 80.0) -> bool:
        """Check if coverage meets minimum threshold."""
        if not self.coverage:
            return False
        
        total_coverage = self.coverage.report(show_missing=False)
        return total_coverage >= threshold
    
    def get_uncovered_lines(self, filename: str) -> List[int]:
        """Get list of uncovered line numbers for a file."""
        if not self.coverage:
            return []
        
        try:
            analysis = self.coverage.analysis2(filename)
            return list(analysis.missing)
        except coverage.misc.NoSource:
            return []


class QualityGateManager:
    """Manages quality gates for test execution."""
    
    def __init__(self):
        """Initialize quality gate manager."""
        self.gates = {
            'coverage_threshold': 80.0,
            'max_test_duration': 300.0,  # 5 minutes
            'max_memory_usage': 500 * 1024 * 1024,  # 500MB
            'max_failed_tests': 0,
            'min_test_count': 10
        }
        self.results = {}
    
    def set_gate(self, gate_name: str, threshold: float):
        """Set quality gate threshold."""
        self.gates[gate_name] = threshold
    
    def check_coverage_gate(self, coverage_manager: CoverageManager) -> bool:
        """Check coverage quality gate."""
        threshold = self.gates['coverage_threshold']
        passed = coverage_manager.check_coverage_threshold(threshold)
        
        self.results['coverage'] = {
            'passed': passed,
            'threshold': threshold,
            'actual': coverage_manager.coverage.report(show_missing=False) if coverage_manager.coverage else 0
        }
        
        return passed
    
    def check_test_duration_gate(self, duration: float) -> bool:
        """Check test duration quality gate."""
        threshold = self.gates['max_test_duration']
        passed = duration <= threshold
        
        self.results['duration'] = {
            'passed': passed,
            'threshold': threshold,
            'actual': duration
        }
        
        return passed
    
    def check_memory_usage_gate(self, memory_usage: int) -> bool:
        """Check memory usage quality gate."""
        threshold = self.gates['max_memory_usage']
        passed = memory_usage <= threshold
        
        self.results['memory'] = {
            'passed': passed,
            'threshold': threshold,
            'actual': memory_usage
        }
        
        return passed
    
    def check_test_results_gate(self, passed: int, failed: int, total: int) -> bool:
        """Check test results quality gate."""
        max_failed = self.gates['max_failed_tests']
        min_total = self.gates['min_test_count']
        
        failed_gate_passed = failed <= max_failed
        count_gate_passed = total >= min_total
        passed_gate = failed_gate_passed and count_gate_passed
        
        self.results['test_results'] = {
            'passed': passed_gate,
            'max_failed_threshold': max_failed,
            'min_count_threshold': min_total,
            'actual_failed': failed,
            'actual_total': total,
            'actual_passed': passed
        }
        
        return passed_gate
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        all_passed = all(result['passed'] for result in self.results.values())
        
        return {
            'overall_passed': all_passed,
            'timestamp': datetime.utcnow().isoformat(),
            'gates': self.gates,
            'results': self.results,
            'summary': {
                'total_gates': len(self.results),
                'passed_gates': sum(1 for result in self.results.values() if result['passed']),
                'failed_gates': sum(1 for result in self.results.values() if not result['passed'])
            }
        }


# Pytest hooks for coverage integration

def pytest_configure(config):
    """Configure pytest with coverage."""
    if config.getoption('--cov'):
        coverage_manager = CoverageManager()
        coverage_manager.start_coverage()
        config._coverage_manager = coverage_manager


def pytest_unconfigure(config):
    """Clean up coverage after tests."""
    if hasattr(config, '_coverage_manager'):
        coverage_manager = config._coverage_manager
        coverage_manager.stop_coverage()
        
        # Generate coverage report
        report = coverage_manager.generate_report('all')
        
        # Check quality gates
        quality_manager = QualityGateManager()
        quality_manager.check_coverage_gate(coverage_manager)
        
        # Save quality report
        quality_report = quality_manager.generate_quality_report()
        with open('quality_report.json', 'w') as f:
            json.dump(quality_report, f, indent=2)
        
        print(f"\nCoverage Report Generated:")
        print(f"Total Coverage: {report['total_coverage']:.1f}%")
        print(f"Quality Gates: {'PASSED' if quality_report['overall_passed'] else 'FAILED'}")


# Coverage configuration for .coveragerc file
COVERAGE_CONFIG = """
[run]
source = app
omit = 
    */tests/*
    */test_*
    */conftest.py
    */migrations/*
    */alembic/*
    */__pycache__/*
    */venv/*
    */env/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\\bProtocol\\):
    @(abc\\.)?abstractmethod

[html]
directory = htmlcov

[xml]
output = coverage.xml

[json]
output = coverage.json
"""


def create_coverage_config():
    """Create .coveragerc configuration file."""
    with open('.coveragerc', 'w') as f:
        f.write(COVERAGE_CONFIG)


# Test performance monitoring

class TestPerformanceMonitor:
    """Monitor test performance and resource usage."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.test_metrics = {}
        self.start_time = None
        self.start_memory = None
    
    def start_monitoring(self, test_name: str):
        """Start monitoring a test."""
        import time
        import psutil
        import os
        
        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        self.start_memory = process.memory_info().rss
        
        self.test_metrics[test_name] = {
            'start_time': self.start_time,
            'start_memory': self.start_memory
        }
    
    def stop_monitoring(self, test_name: str):
        """Stop monitoring a test and record metrics."""
        import time
        import psutil
        import os
        
        if test_name not in self.test_metrics:
            return
        
        end_time = time.time()
        process = psutil.Process(os.getpid())
        end_memory = process.memory_info().rss
        
        metrics = self.test_metrics[test_name]
        metrics.update({
            'end_time': end_time,
            'end_memory': end_memory,
            'duration': end_time - metrics['start_time'],
            'memory_delta': end_memory - metrics['start_memory']
        })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all monitored tests."""
        total_duration = sum(metrics.get('duration', 0) for metrics in self.test_metrics.values())
        max_memory_delta = max(metrics.get('memory_delta', 0) for metrics in self.test_metrics.values()) if self.test_metrics else 0
        
        return {
            'total_tests': len(self.test_metrics),
            'total_duration': total_duration,
            'average_duration': total_duration / len(self.test_metrics) if self.test_metrics else 0,
            'max_memory_delta': max_memory_delta,
            'slow_tests': [
                name for name, metrics in self.test_metrics.items()
                if metrics.get('duration', 0) > 5.0  # Tests taking more than 5 seconds
            ],
            'memory_intensive_tests': [
                name for name, metrics in self.test_metrics.items()
                if metrics.get('memory_delta', 0) > 50 * 1024 * 1024  # Tests using more than 50MB
            ],
            'detailed_metrics': self.test_metrics
        }


# Global performance monitor instance
performance_monitor = TestPerformanceMonitor()


@pytest.fixture(autouse=True)
def monitor_test_performance(request):
    """Automatically monitor test performance."""
    test_name = request.node.name
    performance_monitor.start_monitoring(test_name)
    
    yield
    
    performance_monitor.stop_monitoring(test_name)


def pytest_sessionfinish(session, exitstatus):
    """Generate performance report at end of test session."""
    report = performance_monitor.get_performance_report()
    
    with open('performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nPerformance Report:")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Total Duration: {report['total_duration']:.2f}s")
    print(f"Average Duration: {report['average_duration']:.2f}s")
    
    if report['slow_tests']:
        print(f"Slow Tests: {', '.join(report['slow_tests'])}")
    
    if report['memory_intensive_tests']:
        print(f"Memory Intensive Tests: {', '.join(report['memory_intensive_tests'])}")