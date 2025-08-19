#!/usr/bin/env python3
"""
Automated verification test suite for Plant Maintenance functionality.

This test suite runs comprehensive end-to-end tests on the live server
and automatically verifies results by checking Google Sheets data.

Tests include:
- Move operations (update existing container location)
- Add operations (create new container in new location) 
- Remove operations (delete container from location)
- Update in place operations (modify container details without moving)
- Error handling (invalid plants, invalid locations)
- Location sync verification (Plants table matches container data)

Usage:
    python tests/test_plant_maintenance_server_verification.py
"""

import os
import sys

# Set up environment for live server testing
os.environ['TESTING'] = 'false'

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.plant_maintenance_operations import process_plant_maintenance
from utils.container_operations import get_containers_for_plant
from utils.plant_database_operations import find_plant_by_id_or_name


class PlantMaintenanceTestVerifier:
    """Automated test verification class for plant maintenance operations."""
    
    def __init__(self, plant_name='Test Plant'):
        self.test_results = []
        self.plant_name = plant_name
        self.location_id_map = {
            '1': 'arboretum right',
            '2': 'patio', 
            '31': 'rear left',
            '38': 'lw rear of house',
            '22': 'basket area',
            '3': 'arboretum left',
            '4': 'front yard',
            '5': 'back yard'
        }
    
    def get_current_state(self):
        """Get current state from Google Sheets."""
        try:
            containers = get_containers_for_plant(self.plant_name)
            plant_row, plant_data = find_plant_by_id_or_name(self.plant_name)
            plants_location = plant_data[3] if plant_data and len(plant_data) > 3 else ''
            
            # Create location map for verification
            container_locations = []
            for container in containers:
                loc_id = str(container.get('location_id', ''))
                location_name = self.location_id_map.get(loc_id, f'location_{loc_id}')
                container_locations.append(location_name)
            
            return containers, plants_location, container_locations
            
        except Exception as e:
            print(f"Error getting current state: {e}")
            return [], '', []
    
    def verify_state(self, test_name, expected_container_count, expected_locations, expected_specific_updates=None):
        """Verify current state matches expectations."""
        containers, plants_location, container_locations = self.get_current_state()
        
        print(f'\n=== VERIFYING: {test_name} ===')
        
        # Check container count
        count_ok = len(containers) == expected_container_count
        print(f'Container count: {len(containers)} (expected {expected_container_count}) - {"PASS" if count_ok else "FAIL"}')
        
        # Check locations match
        expected_set = set([loc.lower() for loc in expected_locations])
        actual_set = set([loc.lower() for loc in container_locations])
        locations_ok = expected_set == actual_set
        print(f'Container locations: {sorted(container_locations)} (expected {sorted(expected_locations)}) - {"PASS" if locations_ok else "FAIL"}')
        
        # Check Plants table sync
        plants_location_normalized = plants_location.lower().replace(' ', '')
        expected_plants_location = ', '.join(sorted([loc.lower() for loc in expected_locations])).replace(' ', '')
        sync_ok = plants_location_normalized == expected_plants_location
        print(f'Plants table sync: "{plants_location}" - {"PASS" if sync_ok else "FAIL"}')
        
        # Check specific container updates if provided
        updates_ok = True
        if expected_specific_updates:
            for container in containers:
                container_id = str(container.get('container_id', ''))
                if container_id in expected_specific_updates:
                    expected = expected_specific_updates[container_id]
                    for field, expected_value in expected.items():
                        actual_value = container.get(field, '')
                        field_ok = actual_value.lower() == expected_value.lower()
                        if not field_ok:
                            print(f'Container {container_id} {field}: "{actual_value}" (expected "{expected_value}") - FAIL')
                            updates_ok = False
                        else:
                            print(f'Container {container_id} {field}: "{actual_value}" - PASS')
        
        # Overall result
        overall_ok = count_ok and locations_ok and sync_ok and updates_ok
        self.test_results.append((test_name, overall_ok))
        print(f'OVERALL: {"PASS" if overall_ok else "FAIL"}')
        
        if not overall_ok:
            print('DETAILED STATE:')
            for i, container in enumerate(containers, 1):
                loc_name = self.location_id_map.get(str(container.get('location_id', '')), f"loc_{container.get('location_id', '')}")
                print(f'  {i}. ID {container.get("container_id")}: {loc_name} ({container.get("container_size")} {container.get("container_type")}, {container.get("container_material")})')
        
        return overall_ok
    
    def run_operation(self, test_name, **kwargs):
        """Run operation and return success."""
        print(f'\n>>> RUNNING: {test_name}')
        try:
            result = process_plant_maintenance(**kwargs)
            success = result.get('success', False)
            message = result.get('message', result.get('error', 'No message'))
            print(f'Operation result: {"SUCCESS" if success else "FAILED"} - {message}')
            return success, result
        except Exception as e:
            print(f'Operation failed with exception: {e}')
            return False, {'error': str(e)}
    
    def run_comprehensive_tests(self):
        """Run the complete test suite."""
        print('AUTOMATED VERIFICATION TEST SUITE')
        print('=' * 50)
        print(f'Testing plant: {self.plant_name}')
        
        # Get initial state
        initial_containers, initial_location, initial_container_locations = self.get_current_state()
        print(f'INITIAL STATE: {len(initial_containers)} containers in {initial_container_locations}')
        print(f'Initial Plants table location: "{initial_location}"')
        
        if not initial_containers:
            print("ERROR: No initial containers found! Cannot run tests.")
            return False
        
        # Test 1: Move operation (should update existing container, not create new one)
        print(f'\n{"="*20} TEST 1: MOVE OPERATION {"="*20}')
        target_container_id = None
        source_location = None
        
        # Find a container to move
        for container in initial_containers:
            loc_id = str(container.get('location_id', ''))
            if loc_id in self.location_id_map:
                target_container_id = str(container.get('container_id', ''))
                source_location = self.location_id_map[loc_id]
                break
        
        if not target_container_id:
            print("SKIP: No suitable container found for move test")
        else:
            success1, result1 = self.run_operation(f'Move from {source_location} to patio',
                plant_name=self.plant_name,
                destination_location='patio',
                source_location=source_location,
                container_size='Large',
                container_type='Pot',
                container_material='Ceramic'
            )
            
            if success1:
                expected_locations_after_move = [loc for loc in initial_container_locations if loc.lower() != source_location.lower()] + ['patio']
                expected_updates = {target_container_id: {
                    'container_size': 'Large', 
                    'container_type': 'Pot', 
                    'container_material': 'Ceramic'
                }}
                self.verify_state('Move operation verification', 
                                 len(initial_containers),  # Same count, just moved
                                 expected_locations_after_move,
                                 expected_updates)
        
        # Test 2: Add operation (should create new container)
        print(f'\n{"="*20} TEST 2: ADD OPERATION {"="*20}')
        current_containers, _, current_locations = self.get_current_state()
        
        success2, result2 = self.run_operation('Add to basket area',
            plant_name=self.plant_name,
            destination_location='basket area',
            source_location=None,
            container_size='Medium',
            container_type='Basket',
            container_material='Wicker'
        )
        
        if success2:
            expected_locations_after_add = list(set([loc.lower() for loc in current_locations + ['basket area']]))
            self.verify_state('Add operation verification',
                             len(current_containers) + 1,  # One more container
                             expected_locations_after_add)
        
        # Test 3: Update in place operation
        print(f'\n{"="*20} TEST 3: UPDATE IN PLACE {"="*20}')
        current_containers, _, current_locations = self.get_current_state()
        
        # Find a container to update
        update_container_id = None
        update_location = None
        for container in current_containers:
            loc_id = str(container.get('location_id', ''))
            if loc_id in self.location_id_map:
                update_container_id = str(container.get('container_id', ''))
                update_location = self.location_id_map[loc_id]
                break
        
        if update_container_id:
            success3, result3 = self.run_operation(f'Update container in {update_location}',
                plant_name=self.plant_name,
                destination_location=None,
                source_location=update_location,
                container_size='Extra Large',
                container_type='Planter',
                container_material='Metal'
            )
            
            if success3:
                expected_updates = {update_container_id: {
                    'container_size': 'Extra Large',
                    'container_type': 'Planter', 
                    'container_material': 'Metal'
                }}
                self.verify_state('Update in place verification',
                                 len(current_containers),  # Same count
                                 current_locations,  # Same locations
                                 expected_updates)
        
        # Test 4: Remove operation (should delete container)
        print(f'\n{"="*20} TEST 4: REMOVE OPERATION {"="*20}')
        current_containers, _, current_locations = self.get_current_state()
        
        # Find a location to remove from (not the only location)
        remove_location = None
        if len(current_locations) > 1:
            remove_location = current_locations[0]  # Remove from first location
            
            success4, result4 = self.run_operation(f'Remove from {remove_location}',
                plant_name=self.plant_name,
                destination_location=None,
                source_location=remove_location,
                container_size=None,
                container_type=None,
                container_material=None
            )
            
            if success4:
                expected_locations_after_remove = [loc for loc in current_locations if loc.lower() != remove_location.lower()]
                self.verify_state('Remove operation verification',
                                 len(current_containers) - 1,  # One less container
                                 expected_locations_after_remove)
        else:
            print("SKIP: Cannot remove - plant only in one location")
        
        # Test 5: Error handling - invalid location
        print(f'\n{"="*20} TEST 5: ERROR HANDLING {"="*20}')
        success5, result5 = self.run_operation('Error test: Invalid location',
            plant_name=self.plant_name,
            destination_location='Nonexistent Location',
            source_location=None,
            container_size='Medium',
            container_type='Pot',
            container_material='Plastic'
        )
        
        error_test_ok = not success5 and 'not found' in result5.get('error', '').lower()
        self.test_results.append(('Error handling - invalid location', error_test_ok))
        print(f'Error handling test: {"PASS" if error_test_ok else "FAIL"} (should fail with location not found)')
        
        # Test 6: Error handling - plant not found
        success6, result6 = self.run_operation('Error test: Plant not found',
            plant_name='Nonexistent Plant',
            destination_location='patio',
            source_location=None,
            container_size='Medium',
            container_type='Pot',
            container_material='Plastic'
        )
        
        plant_error_test_ok = not success6 and 'not found' in result6.get('error', '').lower()
        self.test_results.append(('Error handling - plant not found', plant_error_test_ok))
        print(f'Plant error test: {"PASS" if plant_error_test_ok else "FAIL"} (should fail with plant not found)')
        
        # Print final summary
        print(f'\n{"="*20} FINAL TEST SUMMARY {"="*20}')
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        print(f'Tests passed: {passed}/{total}')
        print(f'Overall result: {"ALL TESTS PASSED" if passed == total else "SOME TESTS FAILED"}')
        
        if passed != total:
            print(f'\nFailed tests:')
            for test_name, result in self.test_results:
                if not result:
                    print(f'  - {test_name}')
        
        # Final state summary
        final_containers, final_location, final_container_locations = self.get_current_state()
        print(f'\nFINAL STATE: {len(final_containers)} containers in {final_container_locations}')
        print(f'Final Plants table location: "{final_location}"')
        
        return passed == total


def main():
    """Main test runner function."""
    try:
        verifier = PlantMaintenanceTestVerifier('Test Plant')
        success = verifier.run_comprehensive_tests()
        
        print(f'\n{"="*60}')
        print(f'AUTOMATED VERIFICATION: {"COMPLETE SUCCESS" if success else "FAILURES DETECTED"}')
        print(f'{"="*60}')
        
        return 0 if success else 1
        
    except Exception as e:
        print(f'Test suite failed with exception: {e}')
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
