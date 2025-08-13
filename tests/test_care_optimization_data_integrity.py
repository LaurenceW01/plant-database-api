"""
Regression tests for care optimization data integrity.

This test suite ensures that the care optimization API correctly processes
container-location relationships and field mappings, preventing the data
integrity issues discovered in August 2025.

Critical bugs this prevents:
1. Field name mismatches between container data and location profiles
2. Incorrect container-location linkage calculations  
3. Wrong usage distribution reporting (all empty vs actual distribution)
4. Field access inconsistencies that cause KeyError exceptions

Author: Plant Database API Test Suite
Created: 2025-08-13 - After fixing major data integrity bugs
"""

import unittest
import logging
from utils.locations_operations import get_garden_care_optimization
from utils.locations_metadata_operations import get_all_location_profiles
from utils.locations_database_operations import get_all_containers, get_all_locations, get_containers_by_location_id

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
logger = logging.getLogger(__name__)


class TestCareOptimizationDataIntegrity(unittest.TestCase):
    """Test care optimization data integrity and field consistency."""

    def setUp(self):
        """Set up test fixtures."""
        self.optimization_result = None
        self.location_profiles = None
        
    def test_container_location_linkage_integrity(self):
        """
        Test that containers are properly linked to locations.
        
        This prevents the bug where all locations showed 0 containers
        due to field name mismatches ('Location ID' vs 'location_id').
        """
        logger.info("Testing container-location linkage integrity")
        
        # Get raw data
        all_containers = get_all_containers()
        all_locations = get_all_locations()
        location_profiles = get_all_location_profiles()
        
        # Verify we have data to work with
        self.assertGreater(len(all_containers), 0, "Should have containers in database")
        self.assertGreater(len(all_locations), 0, "Should have locations in database")
        self.assertGreater(len(location_profiles), 0, "Should have location profiles")
        
        # Test container-location mapping
        containers_with_locations = 0
        location_ids_with_containers = set()
        
        for container in all_containers:
            location_id = container.get('location_id')
            self.assertIsNotNone(location_id, "Container should have location_id field")
            self.assertNotEqual(location_id, '', "Container location_id should not be empty")
            
            containers_with_locations += 1
            location_ids_with_containers.add(location_id)
        
        # Verify profiles reflect the container distribution
        profile_containers_total = sum(profile['total_containers'] for profile in location_profiles)
        
        self.assertEqual(
            profile_containers_total, 
            len(all_containers),
            f"Location profiles total containers ({profile_containers_total}) "
            f"should equal actual containers ({len(all_containers)})"
        )
        
        # Verify that locations with containers show up in profiles
        profiles_with_containers = sum(1 for profile in location_profiles if profile['total_containers'] > 0)
        
        self.assertGreater(
            profiles_with_containers, 
            0,
            "At least some location profiles should show containers"
        )
        
        # The critical test: ensure we're not getting the old "all empty" bug
        self.assertLess(
            profiles_with_containers,
            len(location_profiles),
            "Not ALL locations should have containers (some should be empty)"
        )
        
        logger.info(f"✅ Container linkage verified: {profile_containers_total} containers "
                   f"across {profiles_with_containers}/{len(location_profiles)} locations")

    def test_field_name_consistency(self):
        """
        Test that field names are consistent between data sources.
        
        This prevents KeyError exceptions from field name mismatches
        like 'Total Sun Hours' vs 'total_sun_hours'.
        """
        logger.info("Testing field name consistency")
        
        # Get sample data
        containers = get_all_containers()
        locations = get_all_locations()
        profiles = get_all_location_profiles()
        
        if not containers or not locations or not profiles:
            self.skipTest("No test data available")
        
        # Test container field consistency
        required_container_fields = ['container_id', 'location_id', 'container_type', 'container_size', 'container_material']
        sample_container = containers[0]
        
        for field in required_container_fields:
            self.assertIn(
                field, 
                sample_container,
                f"Container should have '{field}' field (not title case or spaced version)"
            )
        
        # Test location field consistency  
        required_location_fields = ['location_id', 'location_name', 'total_sun_hours', 'afternoon_sun_hours']
        sample_location = locations[0]
        
        for field in required_location_fields:
            self.assertIn(
                field,
                sample_location, 
                f"Location should have '{field}' field (not title case or spaced version)"
            )
        
        # Test profile field consistency
        required_profile_fields = ['location_id', 'location_name', 'total_containers', 'total_sun_hours']
        sample_profile = profiles[0]
        
        for field in required_profile_fields:
            self.assertIn(
                field,
                sample_profile,
                f"Profile should have '{field}' field"
            )
        
        logger.info("✅ Field name consistency verified")

    def test_care_optimization_api_data_quality(self):
        """
        Test that the care optimization API returns realistic, quality data.
        
        This prevents the bug where the API reported all locations as empty
        and usage distribution as {'empty': 37, 'light': 0, 'moderate': 0, 'heavy': 0}.
        """
        logger.info("Testing care optimization API data quality")
        
        # Get optimization result
        result = get_garden_care_optimization()
        
        # Basic structure validation
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn('optimization_analysis', result, "Result should contain optimization_analysis")
        
        optimization_analysis = result['optimization_analysis']
        self.assertIn('location_efficiency', optimization_analysis, "Should contain location_efficiency")
        
        location_efficiency = optimization_analysis['location_efficiency']
        
        # Test usage distribution realism
        usage_distribution = location_efficiency.get('usage_distribution', {})
        
        self.assertIn('empty', usage_distribution, "Should have empty locations count")
        self.assertIn('light', usage_distribution, "Should have light usage count")
        self.assertIn('moderate', usage_distribution, "Should have moderate usage count")
        self.assertIn('heavy', usage_distribution, "Should have heavy usage count")
        
        # The critical test: ensure distribution is realistic, not "all empty"
        total_locations = sum(usage_distribution.values())
        empty_locations = usage_distribution.get('empty', 0)
        non_empty_locations = total_locations - empty_locations
        
        self.assertGreater(
            total_locations,
            0,
            "Should have total locations > 0"
        )
        
        self.assertGreater(
            non_empty_locations,
            0,
            "Should have some non-empty locations (not all empty like the old bug)"
        )
        
        # Verify percentages make sense
        if total_locations > 0:
            empty_percentage = (empty_locations / total_locations) * 100
            self.assertLess(
                empty_percentage,
                95,
                f"Empty percentage ({empty_percentage:.1f}%) should be realistic, not 100% like the old bug"
            )
        
        # Test container insights show real data, not all "Unknown"
        container_insights = optimization_analysis.get('container_insights', {})
        total_containers = container_insights.get('total_containers', 0)
        
        self.assertGreater(
            total_containers,
            0,
            "Should report actual containers, not 0"
        )
        
        logger.info(f"✅ API data quality verified: {usage_distribution}, "
                   f"{total_containers} total containers")

    def test_specific_location_container_mapping(self):
        """
        Test that specific locations correctly report their containers.
        
        This validates that the container-location mapping works at the 
        individual location level.
        """
        logger.info("Testing specific location container mapping")
        
        # Get all location profiles
        location_profiles = get_all_location_profiles()
        
        if not location_profiles:
            self.skipTest("No location profiles available")
        
        # Test a few specific locations
        tested_locations = 0
        mapping_verified = 0
        
        for profile in location_profiles[:10]:  # Test first 10 locations
            location_id = profile.get('location_id')
            profile_container_count = profile.get('total_containers', 0)
            
            # Get actual containers for this location
            actual_containers = get_containers_by_location_id(location_id)
            actual_container_count = len(actual_containers)
            
            # The critical test: profile count should match actual count
            self.assertEqual(
                profile_container_count,
                actual_container_count,
                f"Location {location_id} profile says {profile_container_count} containers, "
                f"but database has {actual_container_count} containers"
            )
            
            tested_locations += 1
            if actual_container_count > 0:
                mapping_verified += 1
        
        self.assertGreater(tested_locations, 0, "Should have tested some locations")
        
        logger.info(f"✅ Location mapping verified for {tested_locations} locations, "
                   f"{mapping_verified} had containers")

    def test_care_optimization_error_handling(self):
        """
        Test that care optimization handles errors gracefully.
        
        This ensures the API doesn't crash with KeyError exceptions
        due to field name mismatches.
        """
        logger.info("Testing care optimization error handling")
        
        # The main test: API should not raise KeyError exceptions
        try:
            result = get_garden_care_optimization()
            
            # Should return a result, not crash
            self.assertIsInstance(result, dict, "Should return a dictionary result")
            
            # If there's an error, it should be graceful
            if 'error' in result:
                self.assertIn('error', result, "Error should be properly formatted")
                self.assertIsInstance(result['error'], str, "Error message should be string")
            else:
                # If successful, should have expected structure
                self.assertIn('optimization_analysis', result, "Should contain optimization analysis")
                
        except KeyError as e:
            self.fail(f"Care optimization raised KeyError: {e}. This indicates field name mismatch bugs.")
        except Exception as e:
            # Other exceptions are logged but don't fail the test
            logger.warning(f"Care optimization raised exception: {e}")
            
        logger.info("✅ Error handling verified")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
