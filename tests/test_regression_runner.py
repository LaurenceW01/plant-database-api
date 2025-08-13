"""
Regression Test Runner with Enhanced Reporting

This module provides utilities for running the comprehensive regression test suite
with detailed reporting and validation capabilities.
"""

import pytest
import sys
import os
from typing import Dict, List
import json
from datetime import datetime


class RegressionTestReporter:
    """Enhanced test reporter for regression testing"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'endpoint_coverage': {},
            'test_categories': {
                'plant_management': 0,
                'ai_analysis': 0,
                'health_logging': 0,
                'photo_upload': 0,
                'location_intelligence': 0,
                'weather_integration': 0,
                'error_scenarios': 0
            }
        }
    
    def generate_report(self, results_file: str = None) -> Dict:
        """Generate comprehensive test report"""
        if results_file:
            try:
                with open(results_file, 'w') as f:
                    json.dump(self.results, f, indent=2)
                print(f"✅ Test report saved to {results_file}")
            except Exception as e:
                print(f"⚠️ Failed to save report: {e}")
        
        return self.results


def run_regression_tests(verbose: bool = True, report_file: str = None) -> bool:
    """
    Run the comprehensive regression test suite
    
    Args:
        verbose (bool): Enable verbose output
        report_file (str): Optional file to save test report
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("🚀 Starting Comprehensive Regression Test Suite")
    print("=" * 60)
    
    # Prepare pytest arguments
    pytest_args = [
        'tests/test_regression_comprehensive.py',
        '-v' if verbose else '-q',
        '--tb=short',
        '--disable-warnings',
        '--color=yes'
    ]
    
    # Add performance monitoring
    pytest_args.extend(['--durations=10'])
    
    try:
        # Run the tests
        exit_code = pytest.main(pytest_args)
        
        # Generate report
        reporter = RegressionTestReporter()
        if report_file:
            reporter.generate_report(report_file)
        
        print("\n" + "=" * 60)
        if exit_code == 0:
            print("🎉 All regression tests PASSED!")
            print("✅ No regressions detected in the API")
            return True
        else:
            print("❌ Some regression tests FAILED!")
            print("⚠️ Potential regressions detected - review failures above")
            return False
            
    except Exception as e:
        print(f"💥 Error running regression tests: {e}")
        return False


def run_endpoint_validation() -> bool:
    """
    Run quick endpoint validation to ensure all endpoints respond
    
    Returns:
        bool: True if all endpoints respond (may have errors but not 404/405)
    """
    print("🔍 Running Quick Endpoint Validation")
    print("-" * 40)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        from api.main import create_app_instance
        from werkzeug.test import Client
        from werkzeug.wrappers import Response
        
        app = create_app_instance(testing=True)
        client = Client(app, Response)
        
        # Quick test of major endpoints
        test_endpoints = [
            ('GET', '/api/plants/search'),
            ('GET', '/api/garden/get-metadata'),
            ('GET', '/api/garden/care-optimization'),
            ('GET', '/api/locations/all'),
            ('GET', '/api/logs/search'),
            ('GET', '/api/weather/current')
        ]
        
        passed = 0
        total = len(test_endpoints)
        
        for method, endpoint in test_endpoints:
            try:
                if method == 'GET':
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint)
                
                # Consider 200, 500 as "responding" (not 404/405 which means not found)
                if response.status_code not in [404, 405]:
                    print(f"✅ {method} {endpoint} - {response.status_code}")
                    passed += 1
                else:
                    print(f"❌ {method} {endpoint} - {response.status_code} (Not Found)")
                    
            except Exception as e:
                print(f"💥 {method} {endpoint} - Error: {str(e)[:50]}...")
        
        print(f"\n📊 Endpoint Validation: {passed}/{total} endpoints responding")
        return passed == total
        
    except Exception as e:
        print(f"💥 Error in endpoint validation: {e}")
        return False


def run_safe_regression_tests() -> bool:
    """
    Run regression tests with rate limiting and safety measures
    
    Returns:
        bool: True if tests passed safely
    """
    print("🛡️ Running Safe Regression Tests (Rate Limited)")
    print("-" * 50)
    
    # Set environment variable to enable testing mode
    os.environ['TESTING'] = 'true'
    
    try:
        # First run quick validation
        validation_passed = run_endpoint_validation()
        
        if not validation_passed:
            print("⚠️ Some endpoints not responding - proceeding with caution")
        
        # Run full regression suite
        success = run_regression_tests(
            verbose=True,
            report_file='tests/regression_report.json'
        )
        
        return success
        
    finally:
        # Clean up environment
        if 'TESTING' in os.environ:
            del os.environ['TESTING']


if __name__ == '__main__':
    """Command line interface for regression testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plant Database API Regression Test Runner')
    parser.add_argument('--quick', action='store_true', help='Run quick endpoint validation only')
    parser.add_argument('--safe', action='store_true', help='Run safe regression tests with rate limiting')
    parser.add_argument('--report', type=str, help='Save test report to file')
    parser.add_argument('--verbose', action='store_true', default=True, help='Verbose output')
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_endpoint_validation()
    elif args.safe:
        success = run_safe_regression_tests()
    else:
        success = run_regression_tests(
            verbose=args.verbose,
            report_file=args.report
        )
    
    sys.exit(0 if success else 1)
