#!/usr/bin/env python3
"""
Test script to verify AI integration works for the plant maintenance utility.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plant_maintenance_utility import PlantMaintenanceUtility

def test_ai_integration():
    """Test the AI integration with a mock plant."""
    
    # Create utility instance (with dummy API key since we're only testing AI)
    utility = PlantMaintenanceUtility("dummy_key")
    
    # Test plant data
    test_plant = {
        'plant_name': 'Blueberry Bush',
        'id': 'test-123'
    }
    
    # Test columns
    test_columns = ['soil_ph_type', 'soil_ph_range']
    
    print("Testing AI integration...")
    print(f"Plant: {test_plant['plant_name']}")
    print(f"Columns: {test_columns}")
    print()
    
    try:
        # Test AI value determination
        ai_values = utility._get_ai_plant_values(test_plant['plant_name'], test_columns)
        
        print("AI Response:")
        for column, value in ai_values.items():
            print(f"  {column}: {value}")
        
        print("\nAI integration test successful!")
        return True
        
    except Exception as e:
        print(f"AI integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_integration()
    sys.exit(0 if success else 1)

