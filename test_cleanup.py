"""
Test cleanup utility to remove accumulated test data from Google Sheets
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
from models.field_config import get_canonical_field_name
import re

def clean_test_plants():
    """Remove all test plants from the database"""
    
    # Test plant name patterns to identify and remove
    test_patterns = [
        r'.*Test.*',  # Any plant with "Test" in the name
        r'.*DEBUG.*',  # Debug plants
        r'.*API.*',   # API test plants
        r'.*CRUD.*',  # CRUD test plants  
        r'.*Rate.*',  # Rate limiting test plants
        r'.*Search.*', # Search test plants
        r'.*ChatGPT.*', # ChatGPT test plants
        r'.*AI.*',    # AI test plants
        r'.*Concurrent.*', # Concurrent test plants
        r'.*Sequential.*', # Sequential test plants
        r'.*Validation.*', # Validation test plants
        r'.*Consistency.*', # Consistency test plants
        r'.*Photo.*Test.*', # Photo test plants
        r'.*Field.*', # Field test plants
        r'.*Injection.*', # Injection test plants
        r'.*Schema.*', # Schema test plants
        r'.*Cache.*',  # Cache test plants
        r'.*Performance.*', # Performance test plants
        r'.*Integration.*', # Integration test plants
        r'.*Deployment.*', # Deployment test plants
    ]
    
    try:
        print("=== CLEANING TEST PLANTS ===")
        
        # Get all data
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found in sheet")
            return
            
        headers = values[0]
        plant_name_field = get_canonical_field_name('Plant Name')
        name_idx = headers.index(plant_name_field) if plant_name_field in headers else 1
        
        # Find test plants
        test_plant_rows = []
        total_plants = len(values) - 1  # Exclude header
        
        for i, row in enumerate(values[1:], start=2):  # Start at row 2 (1-indexed)
            if len(row) > name_idx and row[name_idx]:
                plant_name = row[name_idx]
                
                # Check if it matches any test pattern
                for pattern in test_patterns:
                    if re.match(pattern, plant_name, re.IGNORECASE):
                        test_plant_rows.append((i, plant_name))
                        break
        
        if not test_plant_rows:
            print(f"✅ No test plants found. Total plants: {total_plants}")
            return
            
        print(f"Found {len(test_plant_rows)} test plants out of {total_plants} total plants:")
        for row_num, plant_name in test_plant_rows:
            print(f"  Row {row_num}: {plant_name}")
        
        # Remove test plants (in reverse order to maintain row numbers)
        test_plant_rows.reverse()
        
        print(f"\n=== REMOVING {len(test_plant_rows)} TEST PLANTS ===")
        for row_num, plant_name in test_plant_rows:
            try:
                # Delete the row
                requests = [{
                    'deleteDimension': {
                        'range': {
                            'sheetId': 0,  # First sheet
                            'dimension': 'ROWS',
                            'startIndex': row_num - 1,  # Convert to 0-indexed
                            'endIndex': row_num
                        }
                    }
                }]
                
                sheets_client.spreadsheets().batchUpdate(
                    spreadsheetId=SPREADSHEET_ID,
                    body={'requests': requests}
                ).execute()
                
                print(f"✅ Removed: {plant_name}")
                
            except Exception as e:
                print(f"❌ Failed to remove {plant_name}: {e}")
        
        # Get final count
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        final_values = result.get('values', [])
        final_count = len(final_values) - 1 if final_values else 0
        
        print(f"\n=== CLEANUP COMPLETE ===")
        print(f"Removed: {len(test_plant_rows)} test plants")
        print(f"Remaining plants: {final_count}")
        
        # Invalidate cache after cleanup
        from utils.plant_operations import invalidate_plant_list_cache
        invalidate_plant_list_cache()
        print("Cache invalidated")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    print("WARNING: This will remove all test plants from the database!")
    response = input("Are you sure you want to proceed? (y/N): ")
    
    if response.lower() == 'y':
        clean_test_plants()
    else:
        print("Cleanup cancelled") 