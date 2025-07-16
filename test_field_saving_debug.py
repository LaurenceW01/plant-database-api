"""
Debug script to test field saving functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.plant_operations import add_plant_with_fields, find_plant_by_id_or_name
from models.field_config import get_all_field_names
from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
import uuid

def test_comprehensive_field_saving():
    """Test saving a plant with all possible fields"""
    
    # Create test data with all fields
    unique_id = str(uuid.uuid4())[:8]
    test_plant_name = f"DebugTest-{unique_id}"
    
    comprehensive_data = {
        "Plant Name": test_plant_name,
        "Description": "Debug test plant with all fields",
        "Location": "Debug Garden",
        "Light Requirements": "Full Sun",
        "Frost Tolerance": "Hardy to -10°C",
        "Watering Needs": "Moderate",
        "Soil Preferences": "Well-draining",
        "Pruning Instructions": "Prune in early spring",
        "Mulching Needs": "Apply 2-3 inch layer",
        "Fertilizing Schedule": "Monthly during growing season",
        "Winterizing Instructions": "Protect from frost",
        "Spacing Requirements": "18-24 inches apart",
        "Care Notes": "Special debug care instructions",
        "Photo URL": "https://example.com/debug-photo.jpg",
        "Raw Photo URL": "https://example.com/debug-raw.jpg"
    }
    
    print("=== COMPREHENSIVE FIELD SAVING TEST ===")
    print(f"Test plant name: {test_plant_name}")
    print(f"Input data fields: {list(comprehensive_data.keys())}")
    print()
    
    # Test the add_plant_with_fields function
    print("=== CALLING add_plant_with_fields ===")
    result = add_plant_with_fields(comprehensive_data)
    print(f"Add result: {result}")
    print()
    
    if result.get('success'):
        print("=== RETRIEVING SAVED PLANT ===")
        # Get the plant back from the database
        plant_row, plant_data = find_plant_by_id_or_name(test_plant_name)
        if plant_row and plant_data:
            # Get headers and create dict
            result = sheets_client.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            headers = result.get('values', [[]])[0]
            retrieved_plant = dict(zip(headers, plant_data))
            
            print("Retrieved plant data:")
            for field in get_all_field_names():
                value = retrieved_plant.get(field, "")
                print(f"  {field}: {value}")
            
            print()
            print("=== FIELD COMPARISON ===")
            missing_fields = []
            for field, expected_value in comprehensive_data.items():
                if field == "Photo URL":
                    # Photo URL gets converted to IMAGE formula
                    actual_value = retrieved_plant.get(field, "")
                    if expected_value and not actual_value:
                        missing_fields.append(f"{field} (expected IMAGE formula)")
                elif field == "Raw Photo URL":
                    actual_value = retrieved_plant.get(field, "")
                    if actual_value != expected_value:
                        missing_fields.append(f"{field} (expected: {expected_value}, got: {actual_value})")
                else:
                    actual_value = retrieved_plant.get(field, "")
                    if actual_value != expected_value:
                        missing_fields.append(f"{field} (expected: {expected_value}, got: {actual_value})")
            
            if missing_fields:
                print("❌ MISSING OR INCORRECT FIELDS:")
                for field in missing_fields:
                    print(f"  - {field}")
            else:
                print("✅ ALL FIELDS SAVED CORRECTLY!")
                
        else:
            print("❌ ERROR: Could not retrieve saved plant!")
    else:
        print("❌ ERROR: Failed to add plant!")

if __name__ == "__main__":
    test_comprehensive_field_saving() 