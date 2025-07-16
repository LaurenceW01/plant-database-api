#!/usr/bin/env python3
"""
Test real API call to see where fields are getting lost
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import requests
import json
import uuid

def test_real_api_call():
    """Test making a real API call with all fields"""
    
    # Start the test client
    from api.main import create_app
    app = create_app(testing=True)
    
    with app.test_client() as client:
        api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
        unique_name = f"FieldTest-{uuid.uuid4()}"
        
        # Create payload with all the problematic fields
        payload = {
            "Plant Name": unique_name,
            "Description": "Complete field test",
            "Location": "API Test Garden",
            "Light Requirements": "Full Sun",
            "Frost Tolerance": "Hardy to -10°C",  # This should appear
            "Watering Needs": "Moderate",
            "Soil Preferences": "Well-draining",  # This should appear
            "Pruning Instructions": "Prune in early spring",  # This should appear
            "Mulching Needs": "Apply 2-3 inch layer",  # This should appear
            "Fertilizing Schedule": "Monthly during growing season",  # This should appear
            "Winterizing Instructions": "Protect from frost",  # This should appear
            "Spacing Requirements": "18-24 inches apart",  # This should appear
            "Photo URL": "https://example.com/test-plant.jpg",  # This should appear
            "Care Notes": "Additional care information"
        }
        
        print("=== TESTING REAL API CALL ===")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print()
        
        # Make the POST request
        response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
        
        print(f"POST Response Status: {response.status_code}")
        print(f"POST Response: {response.get_json()}")
        print()
        
        if response.status_code == 201:
            # Retrieve the plant to see what was actually stored
            get_response = client.get(f'/api/plants/{unique_name}')
            print(f"GET Response Status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                plant_data = get_response.get_json()['plant']
                print("=== RETRIEVED PLANT DATA ===")
                
                # Check each field we sent
                for field_name, expected_value in payload.items():
                    actual_value = plant_data.get(field_name, '')
                    status = "✓ OK" if actual_value == expected_value else "✗ MISSING"
                    print(f"{status} {field_name}: '{actual_value}' (expected: '{expected_value}')")
                
                print("\n=== ALL FIELDS IN RESPONSE ===")
                for field_name, value in plant_data.items():
                    if value:  # Only show non-empty fields
                        print(f"{field_name}: '{value[:100]}{'...' if len(str(value)) > 100 else ''}'")
            else:
                print(f"Failed to retrieve plant: {get_response.get_json()}")
        else:
            print(f"Failed to create plant: {response.get_json()}")

if __name__ == "__main__":
    test_real_api_call() 