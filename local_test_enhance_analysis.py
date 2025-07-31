#!/usr/bin/env python3
"""
Local test script for Phase 1 implementation
Tests the enhance-analysis functionality without making HTTP requests
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_enhanced_plant_matching():
    """Test the enhanced plant matching function"""
    try:
        from utils.plant_operations import enhanced_plant_matching, find_best_plant_match
        
        print("🔍 Testing enhanced plant matching...")
        
        # Test the fuzzy matching logic
        plant_names = ["Tomato Plant", "Roma Tomato", "Cherry Tomato", "Bell Pepper", "Basil"]
        
        # Test exact match
        result = find_best_plant_match("Tomato Plant", plant_names)
        print(f"Exact match test: {result}")
        assert result['found'] == True
        assert result['plant_name'] == "Tomato Plant"
        assert result['score'] == 1.0
        
        # Test fuzzy match
        result = find_best_plant_match("tomato", plant_names)
        print(f"Fuzzy match test: {result}")
        assert result['found'] == True  # Should find a match
        
        # Test no match
        result = find_best_plant_match("Orchid", plant_names)
        print(f"No match test: {result}")
        
        print("✅ Enhanced plant matching tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced plant matching test failed: {e}")
        return False

def test_helper_functions():
    """Test the helper functions for enhanced analysis"""
    try:
        # Import main.py to test helper functions
        sys.path.insert(0, 'api')
        
        # Test utility functions
        from api.main import (
            extract_symptoms_from_analysis, 
            determine_urgency_level,
            get_seasonal_advice_for_month,
            extract_plant_name_from_analysis
        )
        
        print("\n🧪 Testing helper functions...")
        
        # Test symptom extraction
        gpt_analysis = "This tomato plant shows yellowing leaves with brown spots. The wilting suggests overwatering issues."
        symptoms = extract_symptoms_from_analysis(gpt_analysis)
        print(f"Symptom extraction: {symptoms}")
        assert 'yellowing leaves' in symptoms['symptoms_list']
        assert 'overwatering' in symptoms['likely_causes']
        
        # Test urgency determination
        urgency = determine_urgency_level(symptoms, gpt_analysis)
        print(f"Urgency level: {urgency}")
        assert urgency in ['urgent', 'moderate', 'monitor']
        
        # Test seasonal advice
        seasonal_advice = get_seasonal_advice_for_month(7, "Tomato")  # July
        print(f"Seasonal advice: {seasonal_advice}")
        assert "Summer" in seasonal_advice
        
        # Test plant name extraction
        plant_name = extract_plant_name_from_analysis("**PLANT IDENTIFICATION:** Tomato Plant (Solanum lycopersicum)")
        print(f"Extracted plant name: {plant_name}")
        assert "Tomato Plant" in plant_name
        
        print("✅ Helper function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Helper function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure():
    """Test that the API structure is correct"""
    try:
        # Test importing the main functions
        from api.main import enhance_analysis, analyze_plant
        
        print("\n🏗️  Testing API structure...")
        
        # Check if functions are callable
        assert callable(enhance_analysis)
        assert callable(analyze_plant)
        
        print("✅ API structure tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

def main():
    """Run all local tests"""
    print("🧪 Local Testing - Phase 1 Implementation")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_enhanced_plant_matching())
    results.append(test_helper_functions())
    results.append(test_api_structure())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All local tests passed! Phase 1 implementation is ready.")
        print("\nImplemented features:")
        print("✅ Enhanced plant matching with fuzzy logic")
        print("✅ Symptom extraction and urgency determination")
        print("✅ Seasonal advice generation")
        print("✅ Plant name extraction from analysis")
        print("✅ API endpoint structure")
        
        print("\n📋 Next steps:")
        print("• Deploy to staging environment")
        print("• Test with actual API calls")
        print("• Update ChatGPT schema files")
        print("• Run integration tests")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Review implementation.")

if __name__ == "__main__":
    main()