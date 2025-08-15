"""
Advanced Query Test Runner

Standalone test runner for the advanced query endpoint tests.
Keeps these tests separate from regression tests during development.

Usage:
    python tests/run_advanced_query_tests.py
    
Or with pytest directly:
    pytest tests/test_advanced_query_endpoint.py -v
"""

import sys
import os
import pytest

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_tests():
    """Run the advanced query endpoint tests"""
    
    print("🔍 Running Advanced Query Endpoint Tests")
    print("=" * 50)
    
    # Test file path
    test_file = os.path.join(os.path.dirname(__file__), 'test_advanced_query_endpoint.py')
    
    # Run pytest with specific options
    args = [
        test_file,
        '-v',                    # Verbose output
        '--tb=short',           # Short traceback format
        '--color=yes',          # Colored output
        '-x',                   # Stop on first failure
        '--durations=10'        # Show 10 slowest tests
    ]
    
    print(f"Running: pytest {' '.join(args)}")
    print("-" * 50)
    
    # Execute tests
    exit_code = pytest.main(args)
    
    print("-" * 50)
    if exit_code == 0:
        print("✅ All advanced query tests passed!")
    else:
        print("❌ Some tests failed. Check output above.")
    
    return exit_code

def run_basic_smoke_test():
    """Run a basic smoke test to verify the endpoint is working"""
    
    print("\n🚀 Running Basic Smoke Test")
    print("=" * 30)
    
    try:
        # Import test dependencies
        from flask import Flask
        from api.core.app_factory import create_app
        from api.routes.locations import locations_bp
        
        # Create test app
        app = create_app()
        
        # Check if blueprint is already registered to avoid collision
        if 'locations' not in [bp.name for bp in app.blueprints.values()]:
            app.register_blueprint(locations_bp)
        
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test endpoint exists
            response = client.post('/api/garden/query', 
                                 json={"filters": {}},
                                 content_type='application/json')
            
            if response.status_code != 404:
                print("✅ Endpoint exists and responds")
                
                if response.status_code == 200:
                    print("✅ Basic query succeeds")
                else:
                    print(f"⚠️  Endpoint responds but with status {response.status_code}")
                    
                return True
            else:
                print("❌ Endpoint not found")
                return False
                
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False

if __name__ == '__main__':
    print("Advanced Query System Test Suite")
    print("=" * 40)
    
    # Run smoke test first
    if run_basic_smoke_test():
        print("\n" + "=" * 40)
        # Run full test suite
        exit_code = run_tests()
        sys.exit(exit_code)
    else:
        print("\n❌ Smoke test failed, skipping full test suite")
        sys.exit(1)
