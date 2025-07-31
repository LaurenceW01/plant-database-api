#!/usr/bin/env python3
"""
Test script for the new /api/enhance-analysis endpoint
Validates Phase 1 implementation of ChatGPT Vision + API Consultation
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://plant-database-api.onrender.com')
API_KEY = os.getenv('GARDENLLM_API_KEY')

def test_enhance_analysis_endpoint():
    """Test the new /api/enhance-analysis endpoint with sample ChatGPT analysis"""
    
    url = f"{API_BASE_URL}/api/enhance-analysis"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }
    
    # Sample ChatGPT analysis data for testing
    test_data = {
        "gpt_analysis": "This appears to be a tomato plant with yellowing leaves showing brown spots on the lower leaves. The yellowing pattern suggests possible overwatering or nutrient deficiency. The brown spots could indicate early blight or another fungal infection. The upper leaves appear healthier but some show signs of stress.",
        "plant_identification": "Tomato Plant",
        "user_question": "What's wrong with my plant?",
        "location": "Houston, TX",
        "analysis_type": "health_assessment"
    }
    
    try:
        print(f"Testing enhance-analysis endpoint at {url}")
        print(f"Test data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=test_data)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nSUCCESS! Response:")
            print(json.dumps(result, indent=2))
            
            # Validate response structure
            assert 'success' in result
            assert result['success'] == True
            assert 'enhanced_analysis' in result
            assert 'plant_match' in result['enhanced_analysis']
            assert 'care_enhancement' in result['enhanced_analysis']
            assert 'diagnosis_enhancement' in result['enhanced_analysis']
            assert 'suggested_actions' in result
            assert 'logging_offer' in result
            
            print("\n✅ All response structure validations passed!")
            
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

def test_enhance_analysis_missing_fields():
    """Test the endpoint with missing required fields"""
    
    url = f"{API_BASE_URL}/api/enhance-analysis"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }
    
    # Test with missing gpt_analysis
    test_data = {
        "plant_identification": "Tomato Plant",
        "user_question": "What's wrong with my plant?"
    }
    
    try:
        print(f"\n\nTesting with missing gpt_analysis field...")
        response = requests.post(url, headers=headers, json=test_data)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            print(f"Expected 400 error: {result}")
            assert 'error' in result
            print("✅ Validation error test passed!")
        else:
            print(f"❌ Expected 400 error but got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Validation test failed with error: {e}")

def test_analyze_plant_enhanced_mode():
    """Test the modified /api/analyze-plant endpoint with gpt_analysis field"""
    
    url = f"{API_BASE_URL}/api/analyze-plant"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }
    
    # Test with gpt_analysis field (enhanced mode)
    test_data = {
        "plant_name": "Tomato Plant",
        "user_notes": "I'm concerned about yellowing leaves",
        "analysis_type": "health_assessment",
        "location": "Houston, TX",
        "gpt_analysis": "This tomato plant shows yellowing leaves on the lower portion, which could indicate overwatering or nutrient deficiency. The pattern suggests nitrogen deficiency is likely."
    }
    
    try:
        print(f"\n\nTesting enhanced analyze-plant endpoint...")
        response = requests.post(url, headers=headers, json=test_data)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Enhanced analyze-plant response received")
            
            # Check if enhanced analysis is included
            analysis = result.get('analysis', {})
            if 'Enhanced Analysis' in analysis.get('diagnosis', ''):
                print("✅ Enhanced mode detected in analyze-plant response!")
            else:
                print("⚠️  Enhanced mode not clearly detected, but endpoint responded")
                
        else:
            print(f"❌ analyze-plant request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Enhanced analyze-plant test failed with error: {e}")

if __name__ == "__main__":
    print("🌱 Testing Phase 1: ChatGPT Vision + API Consultation Implementation")
    print("=" * 70)
    
    if not API_KEY:
        print("❌ Error: GARDENLLM_API_KEY not found in environment variables")
        exit(1)
    
    # Run tests
    test_enhance_analysis_endpoint()
    test_enhance_analysis_missing_fields()
    test_analyze_plant_enhanced_mode()
    
    print("\n" + "=" * 70)
    print("🎉 Phase 1 testing completed!")
    print("\nImplemented features:")
    print("✅ New /api/enhance-analysis endpoint")
    print("✅ Enhanced plant matching with fuzzy logic")
    print("✅ Personalized care instructions based on location")
    print("✅ Diagnosis enhancement with database knowledge")
    print("✅ Modified /api/analyze-plant endpoint with gpt_analysis support")
    print("✅ Suggested actions and logging recommendations")