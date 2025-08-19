#!/usr/bin/env python3
"""
Robust Plant Maintenance Feature Verification Test

This test creates its own test data, runs comprehensive verification,
and cleans up after itself to ensure reliable testing.
"""

import os
import time
import random

# Set environment before imports
os.environ['TESTING'] = 'false'  # Use live environment

from utils.plant_maintenance_operations import process_plant_maintenance
from utils.container_operations import get_containers_for_plant, add_container, remove_container
from utils.plant_database_operations import find_plant_by_id_or_name, update_plant
from utils.locations_database_operations import get_all_locations

class RobustTestVerifier:
    def __init__(self):
        self.test_results = []
        self.test_plant_name = 'Test Plant'
        self.test_plant_id = None
        self.created_containers = []  # Track containers we create for cleanup
        self.test_locations = {}  # Will store test location data
        
    def setup_test_data(self):
        """Create dedicated test data for this test run."""
        print("SETTING UP TEST DATA")
        print("=" * 50)
        
        # 1. Find or ensure we have a test plant
        plant_row, plant_data = find_plant_by_id_or_name(self.test_plant_name)
        if plant_data:
            self.test_plant_id = plant_data[0]
            print(f"Using existing test plant: {self.test_plant_name} (ID: {self.test_plant_id})")
        else:
            print(f"ERROR: Test plant '{self.test_plant_name}' not found!")
            return False
            
        # 2. Get available locations for our tests
        all_locations = get_all_locations()
        if len(all_locations) < 3:
            print("ERROR: Need at least 3 locations for testing")
            return False
            
        # Select 3 different locations for our tests
        available_locations = [loc for loc in all_locations if loc.get('location_name') and loc.get('location_id')]
        if len(available_locations) < 3:
            print("ERROR: Need at least 3 valid locations for testing")
            return False
            
        # Use first 3 locations as our test locations
        self.test_locations = {
            'location_a': {
                'name': available_locations[0]['location_name'],
                'id': available_locations[0]['location_id']
            },
            'location_b': {
                'name': available_locations[1]['location_name'],
                'id': available_locations[1]['location_id']
            },
            'location_c': {
                'name': available_locations[2]['location_name'],
                'id': available_locations[2]['location_id']
            }
        }
        
        print(f"Selected test locations:")
        for key, loc in self.test_locations.items():
            print(f"  {key}: {loc['name']} (ID: {loc['id']})")
            
        # 3. Clean up any existing containers for this plant
        existing_containers = get_containers_for_plant(self.test_plant_name)
        if existing_containers:
            print(f"Cleaning up {len(existing_containers)} existing containers...")
            for container in existing_containers:
                container_id = container.get('container_id')
                if container_id:
                    remove_result = remove_container(container_id)
                    if remove_result.get('success'):
                        print(f"  Removed container {container_id}")
                    else:
                        print(f"  WARNING: Failed to remove container {container_id}")
                        
        # 4. Create initial test container in location_a
        print(f"Creating initial container in {self.test_locations['location_a']['name']}...")
        add_result = add_container(
            plant_name=self.test_plant_name,
            location_id=self.test_locations['location_a']['id'],
            container_details={
                'container_size': 'Medium',
                'container_type': 'Test Pot',
                'container_material': 'Plastic'
            }
        )
        
        if add_result.get('success'):
            container_id = add_result.get('container_id')
            self.created_containers.append(container_id)
            print(f"  Created container {container_id}")
        else:
            print(f"ERROR: Failed to create initial container: {add_result.get('error')}")
            return False
            
        print("Test data setup completed successfully!")
        print()
        return True
        
    def cleanup_test_data(self):
        """Clean up all test data created during this test."""
        print()
        print("CLEANING UP TEST DATA")
        print("=" * 50)
        
        # Remove all containers we created
        cleanup_containers = get_containers_for_plant(self.test_plant_name)
        for container in cleanup_containers:
            container_id = container.get('container_id')
            if container_id:
                remove_result = remove_container(container_id)
                if remove_result.get('success'):
                    print(f"Cleaned up container {container_id}")
                else:
                    print(f"WARNING: Failed to clean up container {container_id}")
                    
        # Reset plant location to empty
        if self.test_plant_id:
            update_result = update_plant(self.test_plant_id, {'location': ''})
            if update_result.get('success'):
                print(f"Reset plant location for {self.test_plant_name}")
            else:
                print(f"WARNING: Failed to reset plant location")
                
        print("Cleanup completed!")
        
    def get_current_state(self):
        """Get current state of test plant containers and location."""
        containers = get_containers_for_plant(self.test_plant_name)
        plant_row, plant_data = find_plant_by_id_or_name(self.test_plant_name)
        plant_location = plant_data[3] if plant_data and len(plant_data) > 3 else ""
        
        # Map container location_ids to location names
        container_locations = []
        for container in containers:
            location_id = str(container.get('location_id', '')).strip()
            # Find the location name for this ID
            location_name = None
            for key, loc_data in self.test_locations.items():
                if str(loc_data['id']).strip() == location_id:
                    location_name = loc_data['name']
                    break
            if not location_name:
                location_name = f"location_id_{location_id}"
            container_locations.append(location_name)
            
        return {
            'container_count': len(containers),
            'container_locations': container_locations,
            'plant_location': plant_location,
            'containers': containers
        }
        
    def verify_state(self, test_name, expected_container_count, expected_locations, expected_plant_location=None):
        """Verify current state matches expectations."""
        current_state = self.get_current_state()
        
        print(f"=== VERIFYING: {test_name} ===")
        
        # Check container count
        count_pass = current_state['container_count'] == expected_container_count
        print(f"Container count: {current_state['container_count']} (expected {expected_container_count}) - {'PASS' if count_pass else 'FAIL'}")
        
        # Check container locations
        locations_pass = set(current_state['container_locations']) == set(expected_locations)
        print(f"Container locations: {current_state['container_locations']} (expected {expected_locations}) - {'PASS' if locations_pass else 'FAIL'}")
        
        # Check plant location sync if specified
        plant_sync_pass = True
        if expected_plant_location is not None:
            plant_sync_pass = current_state['plant_location'] == expected_plant_location
            print(f"Plants table sync: \"{current_state['plant_location']}\" (expected \"{expected_plant_location}\") - {'PASS' if plant_sync_pass else 'FAIL'}")
        
        overall_pass = count_pass and locations_pass and plant_sync_pass
        print(f"OVERALL: {'PASS' if overall_pass else 'FAIL'}")
        
        # Show detailed state
        print("DETAILED STATE:")
        for i, container in enumerate(current_state['containers'], 1):
            location_name = current_state['container_locations'][i-1] if i-1 < len(current_state['container_locations']) else 'Unknown'
            print(f"  {i}. ID {container.get('container_id', 'Unknown')}: {location_name} ({container.get('container_size', 'Unknown')} {container.get('container_type', 'Unknown')}, {container.get('container_material', 'Unknown')})")
        print()
        
        return overall_pass
        
    def run_operation(self, test_name, **kwargs):
        """Run a maintenance operation and return result."""
        print(f">>> RUNNING: {test_name}")
        
        try:
            result = process_plant_maintenance(**kwargs)
            success = result.get('success', False)
            message = result.get('message', result.get('error', 'Unknown result'))
            
            print(f"Operation result: {'SUCCESS' if success else 'FAILED'} - {message}")
            return success, result
            
        except Exception as e:
            print(f"Operation result: ERROR - {str(e)}")
            return False, {'error': str(e)}
            
    def run_comprehensive_tests(self):
        """Run all maintenance operation tests."""
        print("COMPREHENSIVE PLANT MAINTENANCE TESTS")
        print("=" * 50)
        
        test_passed = 0
        test_total = 0
        
        # Get test location names
        loc_a = self.test_locations['location_a']['name']
        loc_b = self.test_locations['location_b']['name']
        loc_c = self.test_locations['location_c']['name']
        
        print(f"Testing with locations:")
        print(f"  Location A: {loc_a}")
        print(f"  Location B: {loc_b}")
        print(f"  Location C: {loc_c}")
        print()
        
        # Show initial state
        initial_state = self.get_current_state()
        print(f"INITIAL STATE: {initial_state['container_count']} containers in {initial_state['container_locations']}")
        print(f"Initial Plants table location: \"{initial_state['plant_location']}\"")
        print()
        
        # TEST 1: Move operation
        print("=" * 20 + " TEST 1: MOVE OPERATION " + "=" * 20)
        test_total += 1
        success1, result1 = self.run_operation(
            f'Move from {loc_a} to {loc_b}',
            plant_name=self.test_plant_name,
            destination_location=loc_b,
            source_location=loc_a,
            container_size='Large',
            container_type='Pot',
            container_material='Ceramic'
        )
        
        if success1:
            test1_pass = self.verify_state(
                'Move operation verification',
                expected_container_count=1,
                expected_locations=[loc_b],
                expected_plant_location=loc_b
            )
            if test1_pass:
                test_passed += 1
        else:
            print("Move operation failed, skipping verification")
        print()
        
        # TEST 2: Add operation
        print("=" * 20 + " TEST 2: ADD OPERATION " + "=" * 20)
        test_total += 1
        success2, result2 = self.run_operation(
            f'Add to {loc_c}',
            plant_name=self.test_plant_name,
            destination_location=loc_c,
            container_size='Medium',
            container_type='Basket',
            container_material='Wicker'
        )
        
        if success2:
            expected_plant_location = f"{loc_b}, {loc_c}" if loc_b < loc_c else f"{loc_c}, {loc_b}"
            test2_pass = self.verify_state(
                'Add operation verification',
                expected_container_count=2,
                expected_locations=[loc_b, loc_c],
                expected_plant_location=expected_plant_location
            )
            if test2_pass:
                test_passed += 1
        else:
            print("Add operation failed, skipping verification")
        print()
        
        # TEST 3: Update in place operation
        print("=" * 20 + " TEST 3: UPDATE IN PLACE " + "=" * 20)
        test_total += 1
        success3, result3 = self.run_operation(
            f'Update container in {loc_c}',
            plant_name=self.test_plant_name,
            source_location=loc_c,
            container_size='Extra Large',
            container_type='Planter',
            container_material='Metal'
        )
        
        if success3:
            # Expected plant location should remain the same as TEST 2
            expected_plant_location = f"{loc_b}, {loc_c}" if loc_b < loc_c else f"{loc_c}, {loc_b}"
            test3_pass = self.verify_state(
                'Update in place verification',
                expected_container_count=2,
                expected_locations=[loc_b, loc_c],
                expected_plant_location=expected_plant_location
            )
            if test3_pass:
                test_passed += 1
        else:
            print("Update operation failed, skipping verification")
        print()
        
        # TEST 4: Remove operation
        print("=" * 20 + " TEST 4: REMOVE OPERATION " + "=" * 20)
        test_total += 1
        success4, result4 = self.run_operation(
            f'Remove from {loc_c}',
            plant_name=self.test_plant_name,
            source_location=loc_c
        )
        
        if success4:
            test4_pass = self.verify_state(
                'Remove operation verification',
                expected_container_count=1,
                expected_locations=[loc_b],
                expected_plant_location=loc_b
            )
            if test4_pass:
                test_passed += 1
        else:
            print("Remove operation failed, skipping verification")
        print()
        
        # TEST 5: Error handling
        print("=" * 20 + " TEST 5: ERROR HANDLING " + "=" * 20)
        test_total += 1
        
        # Test invalid location
        success5a, result5a = self.run_operation(
            'Error test: Invalid location',
            plant_name=self.test_plant_name,
            destination_location='Nonexistent Location XYZ',
            container_size='Medium',
            container_type='Pot',
            container_material='Plastic'
        )
        
        error_pass_1 = not success5a  # Should fail
        print(f"Error handling test 1: {'PASS' if error_pass_1 else 'FAIL'} (should fail with location not found)")
        
        # Test invalid plant
        success5b, result5b = self.run_operation(
            'Error test: Plant not found',
            plant_name='Nonexistent Plant XYZ',
            destination_location=loc_a,
            container_size='Medium',
            container_type='Pot',
            container_material='Plastic'
        )
        
        error_pass_2 = not success5b  # Should fail
        print(f"Error handling test 2: {'PASS' if error_pass_2 else 'FAIL'} (should fail with plant not found)")
        
        if error_pass_1 and error_pass_2:
            test_passed += 1
        print()
        
        # Final summary
        print("=" * 20 + " FINAL TEST SUMMARY " + "=" * 20)
        print(f"Tests passed: {test_passed}/{test_total}")
        
        final_state = self.get_current_state()
        print(f"FINAL STATE: {final_state['container_count']} containers in {final_state['container_locations']}")
        print(f"Final Plants table location: \"{final_state['plant_location']}\"")
        print()
        
        if test_passed == test_total:
            print("=" * 60)
            print("ALL TESTS PASSED! PLANT MAINTENANCE FEATURE WORKING CORRECTLY")
            print("=" * 60)
            return True
        else:
            print("=" * 60)
            print("SOME TESTS FAILED - ISSUES DETECTED")
            print("=" * 60)
            return False

def main():
    verifier = RobustTestVerifier()
    
    try:
        # Setup test data
        if not verifier.setup_test_data():
            print("Failed to setup test data!")
            return 1
            
        # Run comprehensive tests
        success = verifier.run_comprehensive_tests()
        
        # Return appropriate exit code
        return 0 if success else 1
        
    except Exception as e:
        print(f"Test execution failed with error: {e}")
        return 1
        
    finally:
        # Always cleanup
        verifier.cleanup_test_data()

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
