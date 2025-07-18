#!/usr/bin/env python3
"""
Debug test to examine field processing and Plant ID handling in detail.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from datetime import datetime
from zoneinfo import ZoneInfo
from models.field_config import get_canonical_field_name, get_all_field_names, is_valid_field
from utils.plant_operations import get_houston_timestamp

def test_field_processing():
    """Debug comprehensive field processing with step-by-step logging"""
    
    # Test payload similar to what API receives
    test_payload = {
        "Plant Name": "Test Plant",
        "Description": "Test description",
        "Location": "Test Garden",
        "Light Requirements": "Full Sun",
        "Frost Tolerance": "Hardy to -10°C",
        "Watering Needs": "Moderate",
        "Soil Preferences": "Well-draining",
        "Pruning Instructions": "Prune in early spring",
        "Mulching Needs": "Apply 2-3 inch layer",
        "Fertilizing Schedule": "Monthly during growing season",
        "Winterizing Instructions": "Protect from frost",
        "Spacing Requirements": "18-24 inches apart",
        "Photo URL": "https://example.com/test.jpg"
    }
    
    print("=== FIELD PROCESSING TEST ===")
    print(f"All field names: {get_all_field_names()}")
    print()
    
    print("=== PAYLOAD PROCESSING ===")
    for field_name, field_value in test_payload.items():
        canonical_field = get_canonical_field_name(field_name)
        is_valid = is_valid_field(field_name)
        
        print(f"Original: '{field_name}' -> Canonical: '{canonical_field}' -> Valid: {is_valid} -> Value: '{field_value}'")
    
    print()
    print("=== EXPECTED CANONICAL FIELDS ===")
    expected_fields = [
        'Frost Tolerance',
        'Soil Preferences', 
        'Pruning Instructions',
        'Mulching Needs',
        'Fertilizing Schedule',
        'Winterizing Instructions',
        'Spacing Requirements'
    ]
    
    for field in expected_fields:
        canonical = get_canonical_field_name(field)
        valid = is_valid_field(field)
        print(f"Field: '{field}' -> Canonical: '{canonical}' -> Valid: {valid}")

def simulate_add_plant_with_fields():
    """Simulate the exact process that add_plant_with_fields goes through"""
    
    print("\n" + "="*60)
    print("=== SIMULATING add_plant_with_fields PROCESS ===")
    print("="*60)
    
    # Test data similar to API call
    plant_data_dict = {
        "Plant Name": "DebugTest Plant",
        "Description": "Testing field storage",
        "Location": "Debug Garden",
        "Light Requirements": "Full Sun",
        "Frost Tolerance": "Hardy to -10°C",
        "Watering Needs": "Moderate",
        "Soil Preferences": "Well-draining",
        "Pruning Instructions": "Prune in early spring",
        "Mulching Needs": "Apply 2-3 inch layer",
        "Fertilizing Schedule": "Monthly during growing season",
        "Winterizing Instructions": "Protect from frost",
        "Spacing Requirements": "18-24 inches apart"
    }
    
    print(f"Input data: {plant_data_dict}")
    print()
    
    # Step 1: Initialize plant_data
    plant_data = {
        get_canonical_field_name('ID'): "999",
        get_canonical_field_name('Last Updated'): get_houston_timestamp()
    }
    
    print(f"Step 1 - Initial plant_data: {plant_data}")
    print()
    
    # Step 2: Process all provided fields
    print("Step 2 - Processing provided fields:")
    for field_name, field_value in plant_data_dict.items():
        canonical_field = get_canonical_field_name(field_name)
        if canonical_field:
            if canonical_field == get_canonical_field_name('Photo URL'):
                # Handle photo URL specially
                photo_formula = f'=IMAGE("{field_value}")' if field_value else ''
                plant_data[canonical_field] = photo_formula
                plant_data[get_canonical_field_name('Raw Photo URL')] = field_value
                print(f"  Photo URL: '{field_name}' -> '{canonical_field}' = '{photo_formula}'")
                print(f"  Raw Photo URL: '{field_name}' -> 'Raw Photo URL' = '{field_value}'")
            else:
                plant_data[canonical_field] = field_value
                print(f"  '{field_name}' -> '{canonical_field}' = '{field_value}'")
        else:
            print(f"  WARNING: No canonical field found for '{field_name}'")
    
    print(f"\nAfter Step 2 - plant_data: {plant_data}")
    print()
    
    # Step 3: Add empty values for missing fields
    print("Step 3 - Adding empty values for missing fields:")
    all_fields = get_all_field_names()
    for field in all_fields:
        if field not in plant_data:
            plant_data[field] = ""
            print(f"  Adding empty field: '{field}' = ''")
        else:
            print(f"  Field already present: '{field}' = '{plant_data[field][:50]}{'...' if len(str(plant_data[field])) > 50 else ''}'")
    
    print(f"\nAfter Step 3 - Final plant_data keys: {list(plant_data.keys())}")
    print()
    
    # Step 4: Create row data
    print("Step 4 - Creating row data:")
    headers = get_all_field_names()
    row_data = [plant_data.get(field, "") for field in headers]
    
    for i, (header, value) in enumerate(zip(headers, row_data)):
        if value:  # Only show non-empty values
            print(f"  {i}: {header} = '{value[:50]}{'...' if len(str(value)) > 50 else ''}'")
        elif header in ['Frost Tolerance', 'Soil Preferences', 'Pruning Instructions', 'Mulching Needs', 'Fertilizing Schedule', 'Winterizing Instructions', 'Spacing Requirements']:
            print(f"  {i}: {header} = '' <-- PROBLEM: This should have a value!")
    
    print(f"\nRow data length: {len(row_data)}")
    print(f"Headers length: {len(headers)}")
    
    return plant_data, row_data

if __name__ == "__main__":
    test_field_processing()
    simulate_add_plant_with_fields() 