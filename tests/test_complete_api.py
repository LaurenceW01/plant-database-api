#!/usr/bin/env python3
"""
Complete API Testing Script - GOOGLE API RATE LIMIT SAFE VERSION

Tests BOTH existing plant management AND new plant logging functionality
without requiring ChatGPT integration.

✅ Google Sheets API Rate Limiting: 60 requests/minute (1 request/second)
✅ Automatic delays between requests (3-5 seconds)
✅ Rate limit error detection and recovery
✅ Test data cleanup to avoid accumulation
✅ Safe mode option for conservative testing
"""

import sys
import os
import requests
import json
from io import BytesIO
from PIL import Image
import tempfile
import time
import random
from datetime import datetime

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration
BASE_URL = "https://plant-database-api.onrender.com"  # Production Render server
API_KEY = os.getenv('API_KEY', 'kd0laksjdf-JljsdahUKjdenujiasdfOOKJSAFDooaisdf78923r')  # Your API key

# Rate limiting configuration (Google Sheets API safe limits)
API_DELAY_MIN = 3  # Minimum delay between API calls (seconds)
API_DELAY_MAX = 5  # Maximum delay between API calls (seconds)
RATE_LIMIT_RECOVERY = 30  # Wait time after hitting rate limit (seconds)
CATEGORY_DELAY = 10  # Delay between test categories (seconds)

class PlantAPITester:
    """Comprehensive tester for Plant Database API with Google API rate limiting protection"""
    
    def __init__(self, base_url: str, api_key: str, safe_mode: bool = True):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.safe_mode = safe_mode
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        self.test_results = []
        self.created_test_data = []  # Track data for cleanup
        
        # Rate limiting tracking
        self.request_count = 0
        self.start_time = datetime.now()
        
        if safe_mode:
            print("🛡️  SAFE MODE: Enabled with Google API rate limiting protection")
            print(f"   • {API_DELAY_MIN}-{API_DELAY_MAX}s delays between requests")
            print(f"   • {RATE_LIMIT_RECOVERY}s recovery on rate limit errors")
            print(f"   • Automatic test data cleanup")
        
    def safe_request_delay(self):
        """Add safe delay between API requests to respect Google Sheets API limits"""
        if self.safe_mode:
            delay = random.uniform(API_DELAY_MIN, API_DELAY_MAX)
            print(f"   ⏱️  API rate limit delay: {delay:.1f}s...")
            time.sleep(delay)
            self.request_count += 1
            
            # Log progress every 10 requests
            if self.request_count % 10 == 0:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = self.request_count / elapsed * 60  # requests per minute
                print(f"   📊 Request rate: {rate:.1f} requests/minute (limit: 60)")
    
    def handle_rate_limit_error(self, response):
        """Handle rate limiting errors with automatic recovery"""
        if response.status_code == 429 or "Quota exceeded" in response.text:
            print(f"   ⚠️  Rate limit detected! Waiting {RATE_LIMIT_RECOVERY}s for recovery...")
            time.sleep(RATE_LIMIT_RECOVERY)
            return True
        return False
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results with timestamp"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.test_results.append((test_name, success, details))
        print(f"[{timestamp}] {status}: {test_name}")
        if details and not success:
            print(f"    Details: {details}")
    
    def create_test_image(self) -> BytesIO:
        """Create a test image for upload testing (small size to reduce upload time)"""
        # Create smaller image to avoid upload timeouts
        img = Image.new('RGB', (200, 150), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)  # Reduced quality for faster upload
        img_bytes.seek(0)
        img_bytes.name = 'test_plant.jpg'
        return img_bytes

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        if not self.created_test_data:
            print("\n🧹 No test data to clean up")
            return
        
        print(f"\n🧹 Cleaning up {len(self.created_test_data)} test data items...")
        cleanup_count = 0
        
        for data_type, identifier in self.created_test_data:
            try:
                self.safe_request_delay()  # Respect rate limits during cleanup
                
                if data_type == "plant":
                    # Note: API may not have DELETE endpoint, so we'll update with cleanup marker
                    response = requests.put(
                        f"{self.base_url}/api/plants/{identifier}",
                        json={"Care Notes": "TEST DATA - SAFE TO IGNORE", "Description": "Cleanup marker"},
                        headers=self.headers
                    )
                    if response.status_code == 200:
                        cleanup_count += 1
                        print(f"   ✅ Marked plant '{identifier}' for cleanup")
                    
            except Exception as e:
                print(f"   ⚠️  Could not clean up {data_type} '{identifier}': {e}")
        
        print(f"   📊 Cleaned up {cleanup_count}/{len(self.created_test_data)} items")
        self.created_test_data.clear()

    # =============================================
    # EXISTING PLANT MANAGEMENT TESTS (RATE LIMITED)
    # =============================================
    
    def test_search_plants(self):
        """Test: Search/list plants (GET /api/plants) - READ ONLY"""
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            response = requests.get(f"{self.base_url}/api/plants", timeout=30)
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                response = requests.get(f"{self.base_url}/api/plants", timeout=30)
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                plant_count = data.get('count', 0)
                details = f"Found {plant_count} plants (read-only, safe)"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Search Plants (GET /api/plants)", success, details)
            return response.json() if success else None
            
        except Exception as e:
            self.log_test("Search Plants (GET /api/plants)", False, str(e))
            return None

    def test_add_plant(self):
        """Test: Add new plant (POST /api/plants) - CREATES TEST DATA"""
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            # Use timestamp to ensure unique plant names
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plant_name = f"Test_Basil_Plant_{timestamp}"
            
            plant_data = {
                "Plant Name": plant_name,
                "Description": "TEST DATA - API validation (safe to ignore)",
                "Location": "Test Garden",
                "Light Requirements": "Full Sun",
                "Watering Needs": "Regular watering",
                "Care Notes": "AUTOMATED TEST - Created for API validation"
            }
            
            response = requests.post(
                f"{self.base_url}/api/plants", 
                json=plant_data, 
                headers=self.headers,
                timeout=30
            )
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                response = requests.post(f"{self.base_url}/api/plants", json=plant_data, headers=self.headers, timeout=30)
            
            success = response.status_code in [200, 201]
            
            if success:
                # Track for cleanup
                self.created_test_data.append(("plant", plant_name))
                details = f"Plant '{plant_name}' added successfully (will be cleaned up)"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test("Add Plant (POST /api/plants)", success, details)
            return plant_name if success else None
            
        except Exception as e:
            self.log_test("Add Plant (POST /api/plants)", False, str(e))
            return None

    def test_get_plant(self, plant_name: str):
        """Test: Get specific plant (GET /api/plants/{name}) - READ ONLY"""
        if not plant_name:
            self.log_test("Get Plant (skipped)", False, "No plant name provided")
            return None
            
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            response = requests.get(f"{self.base_url}/api/plants/{plant_name}", timeout=30)
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                response = requests.get(f"{self.base_url}/api/plants/{plant_name}", timeout=30)
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                plant_info = data.get('plant', {})
                details = f"Retrieved plant: {plant_info.get('plant_name', 'Unknown')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test(f"Get Plant (GET /api/plants/{plant_name[:20]}...)", success, details)
            return response.json() if success else None
            
        except Exception as e:
            self.log_test(f"Get Plant (GET /api/plants/{plant_name[:20]}...)", False, str(e))
            return None

    def test_update_plant(self, plant_name: str):
        """Test: Update plant (PUT /api/plants/{name}) - MODIFIES DATA"""
        if not plant_name:
            self.log_test("Update Plant (skipped)", False, "No plant name provided")
            return False
            
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_data = {
                "Care Notes": f"Updated via API test at {timestamp} - AUTOMATED TEST",
                "Last Updated": timestamp
            }
            
            response = requests.put(
                f"{self.base_url}/api/plants/{plant_name}",
                json=update_data,
                headers=self.headers,
                timeout=30
            )
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                response = requests.put(f"{self.base_url}/api/plants/{plant_name}", json=update_data, headers=self.headers, timeout=30)
            
            success = response.status_code == 200
            details = "Plant updated successfully" if success else f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test(f"Update Plant (PUT /api/plants/{plant_name[:20]}...)", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Update Plant (PUT /api/plants/{plant_name[:20]}...)", False, str(e))
            return False

    # =============================================
    # NEW PLANT LOGGING TESTS (RATE LIMITED)
    # =============================================

    def test_analyze_plant(self, plant_name: str):
        """Test: Analyze plant photo with auto-logging (POST /api/analyze-plant) - CREATES LOG DATA"""
        if not plant_name:
            self.log_test("Analyze Plant Photo (skipped)", False, "No plant name provided")
            return None
            
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            # Create test image
            test_image = self.create_test_image()
            
            # Prepare multipart data with test plant name
            files = {'file': ('test_plant.jpg', test_image, 'image/jpeg')}
            data = {
                'plant_name': plant_name,
                'user_notes': 'AUTOMATED TEST - API image analysis validation',
                'analysis_type': 'health_assessment'
            }
            
            # Remove Content-Type header for multipart
            headers = {'x-api-key': self.api_key}
            
            response = requests.post(
                f"{self.base_url}/api/analyze-plant",
                files=files,
                data=data,
                headers=headers,
                timeout=60  # Longer timeout for image analysis
            )
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                test_image = self.create_test_image()  # Recreate image
                files = {'file': ('test_plant.jpg', test_image, 'image/jpeg')}
                response = requests.post(f"{self.base_url}/api/analyze-plant", files=files, data=data, headers=headers, timeout=60)
            
            success = response.status_code in [200, 201]  # Accept both 200 and 201 for creation
            
            if success:
                result = response.json()
                log_id = result.get('log_entry', {}).get('log_id', 'Unknown')
                # Track log for potential cleanup (if supported)
                self.created_test_data.append(("log", log_id))
                details = f"Analysis complete, Log ID: {log_id}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Analyze Plant Photo (POST /api/analyze-plant)", success, details)
            return response.json() if success else None
            
        except Exception as e:
            self.log_test("Analyze Plant Photo (POST /api/analyze-plant)", False, str(e))
            return None

    def test_create_manual_log(self, plant_name: str):
        """Test: Create manual plant log entry (POST /api/plants/log) - CREATES LOG DATA"""
        if not plant_name:
            self.log_test("Create Manual Log (skipped)", False, "No plant name provided")
            return None
            
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare multipart data with test plant name
            data = {
                'plant_name': plant_name,
                'log_title': f'AUTOMATED TEST - Manual Health Check {timestamp}',
                'user_notes': 'AUTOMATED TEST - Plant health validation for API testing',
                'diagnosis': 'Automated test entry - no real diagnosis',
                'treatment': 'No treatment needed - test data only',
                'follow_up_required': 'false',
                'analysis_type': 'general_care'
            }
            
            headers = {'x-api-key': self.api_key}
            
            response = requests.post(
                f"{self.base_url}/api/plants/log",
                data=data,
                headers=headers,
                timeout=30
            )
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                response = requests.post(f"{self.base_url}/api/plants/log", data=data, headers=headers, timeout=30)
            
            success = response.status_code in [200, 201]  # Accept both 200 and 201 for creation
            
            if success:
                result = response.json()
                log_id = result.get('log_id', 'Unknown')
                # Track log for potential cleanup
                self.created_test_data.append(("log", log_id))
                details = f"Manual log created, Log ID: {log_id}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Create Manual Log (POST /api/plants/log)", success, details)
            return response.json() if success else None
            
        except Exception as e:
            self.log_test("Create Manual Log (POST /api/plants/log)", False, str(e))
            return None

    def test_get_plant_log_history(self, plant_name: str):
        """Test: Get plant log history (GET /api/plants/{name}/log) - READ ONLY"""
        if not plant_name:
            self.log_test("Get Plant Log History (skipped)", False, "No plant name provided")
            return None
            
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            response = requests.get(f"{self.base_url}/api/plants/{plant_name}/log", timeout=30)
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                response = requests.get(f"{self.base_url}/api/plants/{plant_name}/log", timeout=30)
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                entry_count = data.get('total_entries', 0)
                details = f"Retrieved {entry_count} log entries (read-only)"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test(f"Get Plant Log History (GET /api/plants/{plant_name[:20]}...)", success, details)
            return response.json() if success else None
            
        except Exception as e:
            self.log_test(f"Get Plant Log History (GET /api/plants/{plant_name[:20]}...)", False, str(e))
            return None

    def test_search_plant_logs(self, plant_name: str):
        """Test: Search across plant logs (GET /api/plants/log/search) - READ ONLY"""
        if not plant_name:
            self.log_test("Search Plant Logs (skipped)", False, "No plant name provided")
            return None
            
        try:
            self.safe_request_delay()  # Rate limiting protection
            
            params = {
                'plant_name': plant_name,
                'q': 'test'  # Search for test entries we created
            }
            
            response = requests.get(f"{self.base_url}/api/plants/log/search", params=params, timeout=30)
            
            # Handle rate limiting
            if self.handle_rate_limit_error(response):
                response = requests.get(f"{self.base_url}/api/plants/log/search", params=params, timeout=30)
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                match_count = data.get('total_matches', 0)
                details = f"Found {match_count} matching log entries (read-only)"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Search Plant Logs (GET /api/plants/log/search)", success, details)
            return response.json() if success else None
            
        except Exception as e:
            self.log_test("Search Plant Logs (GET /api/plants/log/search)", False, str(e))
            return None

    # =============================================
    # INTEGRATION TESTS
    # =============================================

    def test_plant_log_integration(self):
        """Test: Integration between plant management and logging"""
        try:
            print(f"\n⏱️  Test category delay: {CATEGORY_DELAY}s...")
            time.sleep(CATEGORY_DELAY)  # Category-level delay
            
            # 1. Add a plant
            plant_name = self.test_add_plant()
            if not plant_name:
                self.log_test("Plant-Log Integration", False, "Failed to create test plant")
                return False
            
            # 2. Create log entries for that plant
            log_result = self.test_create_manual_log(plant_name)
            if not log_result:  # log_result will be a dict if successful, None if failed
                self.log_test("Plant-Log Integration", False, "Failed to create log entry")
                return False
            
            # 3. Verify log entries are linked to plant
            history = self.test_get_plant_log_history(plant_name)
            if not history or history.get('total_entries', 0) == 0:
                self.log_test("Plant-Log Integration", False, "No log entries found for plant")
                return False
            
            self.log_test("Plant-Log Integration", True, "Plant and log data properly linked")
            return True
            
        except Exception as e:
            self.log_test("Plant-Log Integration", False, str(e))
            return False

    # =============================================
    # COMPREHENSIVE TEST RUNNER (RATE LIMITED)
    # =============================================

    def run_all_tests(self):
        """Run complete test suite with Google API rate limiting protection"""
        print("🚀 Starting Complete Plant Database API Test Suite")
        print("=" * 60)
        
        # Track test plant for consistent usage across tests
        test_plant_name = None
        
        print("\n📋 EXISTING PLANT MANAGEMENT TESTS")
        print("-" * 40)
        
        # Read-only test first (safe)
        self.test_search_plants()
        
        # Add test plant (creates data for subsequent tests)
        test_plant_name = self.test_add_plant()
        
        # Use the created plant for remaining tests
        if test_plant_name:
            self.test_get_plant(test_plant_name)
            self.test_update_plant(test_plant_name)
        else:
            print("   ⚠️  Skipping get/update tests - no test plant created")
        
        print(f"\n⏱️  Test category delay: {CATEGORY_DELAY}s...")
        time.sleep(CATEGORY_DELAY)  # Inter-category delay
        
        print("\n📸 NEW PLANT LOGGING TESTS")
        print("-" * 40)
        
        if test_plant_name:
            # Use the same test plant for logging tests
            self.test_analyze_plant(test_plant_name)
            self.test_create_manual_log(test_plant_name)
            self.test_get_plant_log_history(test_plant_name)
            self.test_search_plant_logs(test_plant_name)
        else:
            print("   ⚠️  Skipping plant logging tests - no test plant available")
        
        print(f"\n⏱️  Test category delay: {CATEGORY_DELAY}s...")
        time.sleep(CATEGORY_DELAY)  # Inter-category delay
        
        print("\n🔗 INTEGRATION TESTS")
        print("-" * 40)
        self.test_plant_log_integration()
        
        # Clean up test data
        if self.safe_mode:
            print(f"\n⏱️  Final cleanup delay: {CATEGORY_DELAY}s...")
            time.sleep(CATEGORY_DELAY)
            self.cleanup_test_data()
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
            if details and not success:
                print(f"    {details}")
        
        # Rate limiting summary
        if self.safe_mode:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            avg_rate = self.request_count / elapsed * 60 if elapsed > 0 else 0
            print(f"\n📊 API Usage Summary:")
            print(f"   • Total requests: {self.request_count}")
            print(f"   • Average rate: {avg_rate:.1f} requests/minute (limit: 60)")
            print(f"   • Test duration: {elapsed:.1f} seconds")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if passed == total:
            print("🎉 All tests passed! Your API is ready for ChatGPT integration!")
        elif success_rate >= 80:  # 80% pass rate
            print("⚠️  Most tests passed. Review failed tests before ChatGPT integration.")
        else:
            print("❌ Multiple test failures. Fix issues before proceeding.")
        
        return passed == total

def main():
    """Main test execution with Google API rate limiting protection"""
    print("🧪 Plant Database API - Complete Test Suite (Production)")
    print("Testing both existing plant management AND new plant logging")
    print("🛡️  Google Sheets API protection: 60 requests/minute limit")
    print(f"🌐 Testing against: {BASE_URL}")
    print()
    
    # Use defaults directly - no prompting
    base_url = BASE_URL
    api_key = API_KEY
    safe_mode = True  # Always use safe mode for production testing
    
    print(f"🚀 Starting tests with SAFE MODE against production server")
    print("⏱️  Using rate limiting to protect Google Sheets API")
    print()
    
    # Run tests
    tester = PlantAPITester(base_url, api_key, safe_mode=safe_mode)
    success = tester.run_all_tests()
    
    if success:
        print("\n💡 Next Steps:")
        print("1. Your production API is working perfectly!")
        print("2. Upload chatgpt_actions_schema.yaml to ChatGPT")
        print("3. Configure ChatGPT with your API key")
        print("4. Test the ChatGPT integration")
        print("\n✅ Production deployment successful!")
    else:
        print("\n🔧 Next Steps:")
        print("1. Fix the failing API endpoints on production")
        print("2. Deploy fixes and re-run this test script")
        print("3. Once all tests pass, proceed to ChatGPT integration")
        
    if tester.created_test_data:
        print(f"\n🧹 Test data cleanup: {len(tester.created_test_data)} items cleaned up automatically")

if __name__ == "__main__":
    main() 