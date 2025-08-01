#!/usr/bin/env python3
"""
Safe test runner that respects Google Sheets API rate limits
"""
import subprocess
import sys
import time
from datetime import datetime

def run_tests_safely():
    """Run tests with proper rate limiting and monitoring"""
    
    print("🚀 SAFE TEST RUNNER - Google Sheets API Rate Limit Aware")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("API Limit: 60 requests/minute (1 request/second)")
    print("Safety measures: 3-5 second delays between tests")
    print("=" * 60)
    
    # Test categories in order of priority
    test_categories = [
        {
            "name": "Core API Functionality",
            "path": "tests/test_api.py::test_health_check tests/test_api.py::test_list_plants tests/test_api.py::test_add_plant",
            "description": "Essential API endpoints"
        },
        {
            "name": "Comprehensive Field Testing", 
            "path": "tests/test_comprehensive_fields.py::test_comprehensive_field_saving_and_retrieval",
            "description": "Verify ALL fields are saved correctly"
        },
        {
            "name": "Integration Tests",
            "path": "tests/test_integration.py::test_crud_operations_end_to_end",
            "description": "End-to-end functionality"
        },
        {
            "name": "ChatGPT Compatibility",
            "path": "tests/test_deployment.py::test_field_validation_for_ai_clients",
            "description": "AI client compatibility"
        }
    ]
    
    total_categories = len(test_categories)
    passed_categories = 0
    
    for i, category in enumerate(test_categories, 1):
        print(f"\n🧪 [{i}/{total_categories}] {category['name']}")
        print(f"   {category['description']}")
        print(f"   Path: {category['path']}")
        
        # Add extra delay between categories
        if i > 1:
            print("   ⏱️  Inter-category delay (10 seconds)...")
            time.sleep(10)
        
        try:
            # Run the test category
            cmd = [
                sys.executable, "-m", "pytest", 
                "-v", "--tb=short",
                "--timeout=300"
            ] + category['path'].split()
            
            print("   🏃 Running tests...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=False)
            
            if result.returncode == 0:
                print("   ✅ PASSED")
                passed_categories += 1
            else:
                print("   ❌ FAILED")
                print(f"   Error output: {result.stderr}")
                
                # Check if it's a rate limit error
                if "429" in result.stderr or "Quota exceeded" in result.stderr:
                    print("   ⚠️  Rate limit detected - adding extra delay")
                    time.sleep(30)  # Wait 30 seconds on rate limit
                    
        except subprocess.TimeoutExpired:
            print("   ⏰ TIMEOUT - Test took longer than 10 minutes")
        except (OSError, subprocess.SubprocessError) as e:
            print(f"   💥 ERROR - {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed_categories}/{total_categories} test categories")
    print(f"❌ Failed: {total_categories - passed_categories}/{total_categories} test categories")
    
    success_rate = (passed_categories / total_categories) * 100
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 OVERALL SUCCESS - API is ready for deployment!")
        return 0
    elif success_rate >= 60:
        print("⚠️  PARTIAL SUCCESS - Some issues need attention")
        return 1
    else:
        print("❌ SIGNIFICANT ISSUES - Further debugging required")
        return 2

if __name__ == "__main__":
    exit_code = run_tests_safely()
    sys.exit(exit_code) 