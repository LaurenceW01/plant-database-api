#!/usr/bin/env python3
"""
Test script for AI care generation functionality.
Tests the enhanced add_plant_with_fields function to ensure all fields are populated.
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
API_KEY = os.getenv("GARDENLLM_API_KEY", "test-secret-key")  # Test API key

def test_ai_care_generation():
    """Test adding a plant with minimal data to verify AI care generation works."""
    
    print("🧪 Testing AI Care Generation Functionality")
    print("=" * 50)
    
    # Test data - minimal plant information (should trigger AI generation)
    test_plant_data = {
        "Plant Name": f"Test Lavender {datetime.now().strftime('%H%M%S')}",
        "Location": "Test Herb Garden"
    }
    
    print(f"📤 Sending minimal plant data:")
    print(json.dumps(test_plant_data, indent=2))
    print()
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        # Make the API request
        print("🌐 Making API request to /api/plants...")
        response = requests.post(
            f"{API_BASE_URL}/api/plants",
            json=test_plant_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print("✅ Plant added successfully!")
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Get the plant ID to verify the data was saved correctly
            plant_id = response_data.get('plant_id')
            if plant_id:
                print(f"\n🔍 Verifying plant data for ID: {plant_id}")
                verify_plant_data(plant_id, test_plant_data["Plant Name"])
            
        else:
            print("❌ Failed to add plant!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def verify_plant_data(plant_id, plant_name):
    """Verify that the plant was saved with AI-generated care information."""
    
    try:
        # Get the plant data back from the API
        response = requests.get(
            f"{API_BASE_URL}/api/plants/{plant_name}",
            timeout=10
        )
        
        if response.status_code == 200:
            plant_data = response.json().get('plant', {})
            
            print("🔍 Verifying AI-generated fields:")
            
            # Check key fields that should be populated by AI
            ai_fields_to_check = [
                'Description',
                'Light Requirements', 
                'Watering Needs',
                'Soil Preferences',
                'Care Notes',
                'Pruning Instructions',
                'Fertilizing Schedule'
            ]
            
            populated_fields = 0
            total_fields = len(ai_fields_to_check)
            
            for field in ai_fields_to_check:
                value = plant_data.get(field, '').strip()
                if value:
                    print(f"  ✅ {field}: {value[:50]}{'...' if len(value) > 50 else ''}")
                    populated_fields += 1
                else:
                    print(f"  ❌ {field}: [EMPTY]")
            
            print(f"\n📈 AI Generation Results: {populated_fields}/{total_fields} fields populated")
            
            if populated_fields >= 5:  # At least 5 out of 7 key fields should be populated
                print("🎉 AI care generation is working correctly!")
                return True
            else:
                print("⚠️  AI care generation may not be working properly - few fields populated")
                return False
                
        else:
            print(f"❌ Failed to retrieve plant data: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying plant data: {e}")
        return False

def test_update_functionality():
    """Test that plant updates still work correctly."""
    
    print("\n🔄 Testing Plant Update Functionality")
    print("=" * 40)
    
    # Test updating a plant (should work as before)
    test_plant_name = f"Test Update Plant {datetime.now().strftime('%H%M%S')}"
    
    # First create a plant
    create_data = {
        "Plant Name": test_plant_name,
        "Location": "Test Garden"
    }
    
    headers = {
        "Content-Type": "application/json", 
        "x-api-key": API_KEY
    }
    
    try:
        # Create plant
        create_response = requests.post(
            f"{API_BASE_URL}/api/plants",
            json=create_data,
            headers=headers,
            timeout=30
        )
        
        if create_response.status_code in [200, 201]:
            print("✅ Test plant created for update test")
            
            # Now test updating it
            update_data = {
                "Watering Needs": "Water twice weekly in summer",
                "Care Notes": "This is a test update to verify update functionality still works"
            }
            
            update_response = requests.put(
                f"{API_BASE_URL}/api/plants/{test_plant_name}",
                json=update_data,
                headers=headers,
                timeout=10
            )
            
            if update_response.status_code == 200:
                print("✅ Plant update functionality working correctly!")
                print(f"📄 Update response: {update_response.json()}")
            else:
                print(f"❌ Plant update failed: {update_response.status_code}")
                print(f"Error: {update_response.text}")
        else:
            print(f"❌ Failed to create test plant for update: {create_response.status_code}")
            
    except Exception as e:
        print(f"❌ Update test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting AI Care Generation Tests")
    print("Make sure your local server is running on http://localhost:5000")
    print("And that you have a valid API_KEY environment variable set")
    print()
    
    # Test AI care generation
    test_ai_care_generation()
    
    # Test update functionality
    test_update_functionality()
    
    print("\n🏁 Testing complete!")
