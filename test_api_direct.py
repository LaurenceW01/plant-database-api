"""
Direct API test to verify comprehensive field processing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from api.main import create_app
import uuid
import json
import os

def test_api_comprehensive_fields():
    """Test that the API endpoint correctly processes comprehensive field data"""
    
    # Create test app
    app = create_app(testing=True)
    client = app.test_client()
    
    # Create comprehensive test data (same as debug script)
    unique_id = str(uuid.uuid4())[:8]
    test_plant_name = f"API-Test-{unique_id}"
    
    comprehensive_data = {
        "Plant Name": test_plant_name,
        "Description": "API test plant with all fields",
        "Location": "API Test Garden",
        "Light Requirements": "Full Sun",
        "Frost Tolerance": "Hardy to -10°C",
        "Watering Needs": "Moderate",
        "Soil Preferences": "Well-draining",
        "Pruning Instructions": "Prune in early spring",
        "Mulching Needs": "Apply 2-3 inch layer",
        "Fertilizing Schedule": "Monthly during growing season",
        "Winterizing Instructions": "Protect from frost",
        "Spacing Requirements": "18-24 inches apart",
        "Care Notes": "API test care instructions",
        "Photo URL": "https://example.com/api-test.jpg",
        "Raw Photo URL": "https://example.com/api-raw.jpg"
    }
    
    print("=== DIRECT API ENDPOINT TEST ===")
    print(f"Test plant name: {test_plant_name}")
    print(f"Sending fields: {list(comprehensive_data.keys())}")
    print()
    
    # Make POST request to API endpoint
    print("=== CALLING API ENDPOINT ===")
    # Use the same API key logic as the tests
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    print(f"Using API key: {api_key}")
    response = client.post('/api/plants', 
                          json=comprehensive_data,
                          headers={"x-api-key": api_key})
    
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.get_json()}")
    print()
    
    if response.status_code == 201:
        print("✅ API endpoint accepted the data")
        
        # Retrieve the plant via API to see what was actually saved
        print("=== RETRIEVING VIA API ===")
        get_response = client.get(f'/api/plants/{test_plant_name}')
        print(f"GET response status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            plant_data = get_response.get_json()['plant']
            print("Retrieved plant data via API:")
            
            missing_fields = []
            for field, expected_value in comprehensive_data.items():
                actual_value = plant_data.get(field, "")
                if field == "Photo URL":
                    # Photo URL gets converted to IMAGE formula
                    if expected_value and not actual_value:
                        missing_fields.append(f"{field} (expected IMAGE formula)")
                elif field == "Raw Photo URL":
                    if actual_value != expected_value:
                        missing_fields.append(f"{field} (expected: {expected_value}, got: {actual_value})")
                else:
                    if actual_value != expected_value:
                        missing_fields.append(f"{field} (expected: {expected_value}, got: {actual_value})")
                        
                print(f"  {field}: {actual_value}")
            
            print()
            if missing_fields:
                print("❌ API ENDPOINT ISSUES:")
                for field in missing_fields:
                    print(f"  - {field}")
            else:
                print("✅ API ENDPOINT WORKS PERFECTLY!")
                
        else:
            print(f"❌ Error retrieving plant via API: {get_response.get_json()}")
    else:
        print(f"❌ API endpoint failed: {response.get_json()}")

if __name__ == "__main__":
    test_api_comprehensive_fields() 