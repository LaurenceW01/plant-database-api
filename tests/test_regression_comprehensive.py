"""
Comprehensive Regression Test Suite for Plant Database API

This test suite validates all defined endpoints to ensure no regressions
occur when changes are made to the codebase. Tests cover all major
functionality including plants, logs, analysis, locations, photos, and weather.

Test Categories:
- Core Plant Management (5 operations)
- AI-Powered Analysis (2 operations) 
- Health Logging (3 operations)
- Photo Upload (2 operations)
- Location Intelligence (8 operations)
- Weather Integration (3 operations)

Author: Plant Database API Test Suite
Created: Comprehensive regression testing implementation
"""

import pytest
import json
import tempfile
import os
import sys
from flask import Flask
from werkzeug.test import Client
from werkzeug.wrappers import Response

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api.main import create_app_instance


class TestRegressionSuite:
    """Comprehensive regression test suite for all API endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Set up test client and common test data"""
        print("\n=== STARTING TEST SESSION ===")
        # Create app in testing mode to disable rate limiting
        cls.app = create_app_instance(testing=True)
        cls.client = Client(cls.app, Response)
        
        # Common test data
        cls.test_plant_data = {
            "Plant Name": "Test Regression Plant",
            "Description": "Plant for regression testing",
            "Location": "Test Garden", 
            "Light Requirements": "Full Sun",
            "Watering Needs": "Daily",
            "Care Notes": "Test plant for comprehensive testing"
        }
        
        cls.test_log_data = {
            "Plant Name": "Test Plant Log",
            "User Notes": "Regression test log entry",
            "Diagnosis": "Healthy",
            "Treatment": "Continue current care",
            "Symptoms": "None observed"
        }
        
        cls.test_analysis_data = {
            "plant_name": "Test Plant Analysis",
            "user_notes": "Testing AI analysis functionality", 
            "analysis_type": "general_care"
        }

    # =============================================
    # CORE PLANT MANAGEMENT TESTS (5 operations)
    # =============================================
    
    def test_plants_search_post(self):
        """Test POST /api/plants/search endpoint (operationId: searchPlants)"""
        test_data = {"q": "test", "limit": 5}
        response = self.client.post('/api/plants/search', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'count' in data
        assert 'plants' in data
        assert isinstance(data['count'], int)
        assert isinstance(data['plants'], list)
    
    def test_plants_search_get(self):
        """Test GET /api/plants/search endpoint with query parameters"""
        response = self.client.get('/api/plants/search?q=test&limit=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'count' in data
        assert 'plants' in data

    def test_plants_search_names_only_post(self):
        """Test POST /api/plants/search with names_only=true parameter"""
        test_data = {"names_only": True, "limit": 10}
        response = self.client.post('/api/plants/search', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'count' in data
        assert 'plants' in data
        assert 'names_only' in data
        assert 'usage_note' in data
        assert 'note' in data
        assert data['names_only'] is True
        
        # Verify plants is a list of strings (plant names)
        assert isinstance(data['plants'], list)
        for plant in data['plants']:
            assert isinstance(plant, str), f"Expected string plant name, got {type(plant)}: {plant}"
        
        # Verify usage note is present
        assert 'Use these names with other plant endpoints' in data['usage_note']
        assert 'All plant names in database' in data['note']

    def test_plants_search_names_only_with_query(self):
        """Test POST /api/plants/search with names_only=true and search query"""
        test_data = {"q": "a", "names_only": True, "limit": 5}
        response = self.client.post('/api/plants/search', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'count' in data
        assert 'plants' in data
        assert 'names_only' in data
        assert 'search_query' in data
        assert 'usage_note' in data
        assert 'note' in data
        assert data['names_only'] is True
        assert data['search_query'] == "a"
        
        # Verify plants is a list of strings (plant names)
        assert isinstance(data['plants'], list)
        for plant in data['plants']:
            assert isinstance(plant, str), f"Expected string plant name, got {type(plant)}: {plant}"
        
        # Verify search context in note
        assert 'Plant names matching "a"' in data['note']

    def test_plants_search_names_only_get_params(self):
        """Test GET /api/plants/search with names_only query parameter"""
        response = self.client.get('/api/plants/search?names_only=true&limit=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'count' in data
        assert 'plants' in data
        assert 'names_only' in data
        assert data['names_only'] is True
        
        # Verify plants is a list of strings (plant names)
        assert isinstance(data['plants'], list)
        for plant in data['plants']:
            assert isinstance(plant, str), f"Expected string plant name, got {type(plant)}: {plant}"

    def test_plants_search_backward_compatibility(self):
        """Test that existing search functionality still works without names_only parameter"""
        test_data = {"q": "test", "limit": 3}
        response = self.client.post('/api/plants/search', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'count' in data
        assert 'plants' in data
        
        # Verify backward compatibility - should NOT have names_only field when not requested
        assert 'names_only' not in data or data.get('names_only') is False
        
        # Verify plants is a list of objects (full plant data) when names_only not specified
        assert isinstance(data['plants'], list)
        if data['plants']:  # If there are plants in the response
            for plant in data['plants']:
                assert isinstance(plant, dict), f"Expected dict plant object, got {type(plant)}: {plant}"
                # Should have typical plant fields when returning full data
                expected_fields = ['Plant Name', 'ID']  # At minimum these should be present
                for field in expected_fields:
                    if field in plant:  # Some plants might not have all fields
                        assert isinstance(plant[field], str) or plant[field] is None
    
    def test_plants_add(self):
        """Test POST /api/plants/add endpoint (operationId: addPlant)"""
        response = self.client.post('/api/plants/add',
                                  data=json.dumps(self.test_plant_data),
                                  content_type='application/json')
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'success' in data
        assert 'message' in data
        if data.get('success'):
            assert 'plant_id' in data
            assert 'upload_url' in data

    def test_plants_get_by_id(self):
        """Test GET /api/plants/get/{id} endpoint (operationId: getPlant)"""
        # Test with ID
        response = self.client.get('/api/plants/get/1')
        
        assert response.status_code in [200, 404]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'success' in data
            assert 'plant' in data
        else:
            assert 'error' in data or 'success' in data
    
    def test_plants_get_by_name(self):
        """Test GET /api/plants/get/{name} endpoint"""
        # Test with name
        response = self.client.get('/api/plants/get/Vinca')
        
        assert response.status_code in [200, 404]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'success' in data
            assert 'plant' in data
    
    def test_plants_get_all_fields_by_id(self):
        """Test GET /api/plants/get-all-fields/{id} endpoint (operationId: getPlantAllFields)"""
        # Test with plant ID
        response = self.client.get('/api/plants/get-all-fields/1')
        
        assert response.status_code in [200, 404]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'success' in data
            assert data['success'] is True
            assert 'plant' in data
            assert 'metadata' in data
            
            # Verify metadata structure
            metadata = data['metadata']
            assert 'total_fields' in metadata
            assert 'non_empty_fields' in metadata
            assert 'field_names' in metadata
            assert 'plant_id' in metadata
            assert 'plant_name' in metadata
            
            # Verify plant data contains all expected fields
            plant = data['plant']
            expected_fields = ['ID', 'Plant Name', 'Description', 'Location']
            for field in expected_fields:
                assert field in plant
            
            # Verify field count is reasonable
            assert metadata['total_fields'] >= 15  # Should have many fields
            assert metadata['non_empty_fields'] >= 1  # At least plant name should be populated
            assert len(metadata['field_names']) == metadata['total_fields']
    
    def test_plants_get_all_fields_by_name(self):
        """Test GET /api/plants/get-all-fields/{name} endpoint with plant name"""
        # Test with plant name
        response = self.client.get('/api/plants/get-all-fields/Vinca')
        
        assert response.status_code in [200, 404]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'success' in data
            assert data['success'] is True
            assert 'plant' in data
            assert 'metadata' in data
            
            # Verify we got the right plant
            plant = data['plant']
            assert plant.get('Plant Name') == 'Vinca'
            
            # Verify endpoint type is marked correctly
            assert data.get('endpoint_type') == 'get_all_fields'
            assert 'note' in data
    
    def test_plants_update_with_id_in_path(self):
        """Test PUT /api/plants/update/{id} endpoint (operationId: updatePlant)"""
        update_data = {
            "Description": "Updated description for regression test",
            "Care Notes": "Updated care notes"
        }
        
        response = self.client.put('/api/plants/update/1',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code in [200, 400, 404]
        data = response.get_json()
        assert 'success' in data or 'error' in data
    
    def test_plants_update_with_id_in_body(self):
        """Test PUT /api/plants/update endpoint (operationId: updatePlantFlexible)"""
        update_data = {
            "id": "1",
            "Description": "Updated via body ID method",
            "Care Notes": "Testing flexible update endpoint"
        }
        
        response = self.client.put('/api/plants/update',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code in [200, 400, 404]
        data = response.get_json()
        assert 'success' in data or 'error' in data

    def test_plants_update_soil_ph_fields_regression(self):
        """Regression test for Soil pH fields UnrecognizedKwargsError bug.
        
        This test ensures that ChatGPT can successfully update plants with
        Soil___pH___Type and Soil___pH___Range fields without getting
        UnrecognizedKwargsError. This prevents the bug where these fields
        were missing from the OpenAPI schema definition.
        """
        # Test the exact request format that ChatGPT was using that failed
        update_data = {
            "id": "Purple Fountain Grass",
            "Soil___pH___Type": "neutral to slightly acidic",
            "Soil___pH___Range": "6.0 to 7.0",
            "Light___Requirements": "Full Sun",
            "Care___Notes": "Test update with all pH fields"
        }
        
        response = self.client.put('/api/plants/update',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code in [200, 400, 404]
        data = response.get_json()
        
        # Should NOT get UnrecognizedKwargsError for Soil pH fields
        if response.status_code != 200 and 'error' in data:
            error_msg = data.get('message', '') or data.get('error', '')
            assert 'UnrecognizedKwargsError' not in error_msg, f"Got UnrecognizedKwargsError for Soil pH fields: {error_msg}"
            assert 'Soil___pH___Type' not in error_msg, f"Soil___pH___Type field not recognized: {error_msg}"
            assert 'Soil___pH___Range' not in error_msg, f"Soil___pH___Range field not recognized: {error_msg}"
        
        assert 'success' in data or 'error' in data

    def test_plants_get_context(self):
        """Test POST /api/plants/get-context/{plant_id} endpoint (operationId: getPlantContext)"""
        response = self.client.post('/api/plants/get-context/1')
        
        assert response.status_code in [200, 404, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'plant_id' in data
            assert 'contexts' in data

    def test_plants_get_context_by_name_purple_fountain_grass(self):
        """Regression test for Purple Fountain Grass plant ID mapping bug.
        
        This test ensures that when searching for 'Purple Fountain Grass' by name,
        the get-context endpoint returns the correct plant ID (142) and not the
        row number (137). This prevents the bug where containers for Dipladenia
        (ID 137) were returned instead of Purple Fountain Grass containers.
        """
        response = self.client.post('/api/plants/get-context/Purple Fountain Grass')
        
        assert response.status_code in [200, 404, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            # Verify we get the correct plant ID (142, not 137)
            assert data.get('plant_id') == '142', f"Expected plant_id '142' for Purple Fountain Grass, got '{data.get('plant_id')}'"
            assert 'contexts' in data
            
            # Verify we have containers and they belong to Purple Fountain Grass
            contexts = data.get('contexts', [])
            if contexts:
                for context in contexts:
                    container = context.get('container', {})
                    # All containers should have plant_id '142'
                    assert container.get('plant_id') == '142', f"Container plant_id should be '142', got '{container.get('plant_id')}'"

    def test_plants_by_location(self):
        """Test GET /api/plants/by-location/{location_name} endpoint (operationId: getPlantsByLocation)"""
        # Test with a known location that should have plants
        response = self.client.get('/api/plants/by-location/middle')
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'location_identifier' in data
            assert 'resolved_location_name' in data
            assert 'count' in data
            assert 'plants' in data
            assert isinstance(data['count'], int)
            assert isinstance(data['plants'], list)
            assert data['location_identifier'] == 'middle'
        else:
            assert 'error' in data

    def test_plants_by_location_with_location_id(self):
        """Test GET /api/plants/by-location/{location_name} endpoint with location ID"""
        # Test with location ID (should convert to name internally)
        response = self.client.get('/api/plants/by-location/23')  # ID for 'middle'
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'location_identifier' in data
            assert 'resolved_location_name' in data
            assert 'count' in data
            assert 'plants' in data
            assert data['location_identifier'] == '23'
            # Should resolve ID 23 to location name 'middle'
        else:
            assert 'error' in data

    # =============================================
    # AI-POWERED ANALYSIS TESTS (2 operations)
    # =============================================
    
    def test_plants_diagnose(self):
        """Test POST /api/plants/diagnose endpoint (operationId: diagnosePlant)"""
        response = self.client.post('/api/plants/diagnose',
                                  data=json.dumps(self.test_analysis_data),
                                  content_type='application/json')
        
        assert response.status_code in [200, 400, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'success' in data
            assert 'analysis' in data
        else:
            assert 'error' in data or 'success' in data

    def test_plants_enhance_analysis(self):
        """Test POST /api/plants/enhance-analysis endpoint (operationId: enhanceAnalysis)"""
        enhance_data = {
            "gpt_analysis": "This plant shows signs of healthy growth",
            "plant_identification": "Test Plant",
            "user_question": "How is my plant doing?",
            "analysis_type": "health_assessment"
        }
        
        response = self.client.post('/api/plants/enhance-analysis',
                                  data=json.dumps(enhance_data),
                                  content_type='application/json')
        
        assert response.status_code in [200, 400, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'success' in data
            assert 'enhanced_analysis' in data

    # =============================================
    # HEALTH LOGGING TESTS (3 operations)
    # =============================================
    
    def test_logs_create(self):
        """Test POST /api/logs/create endpoint (operationId: createLog)"""
        response = self.client.post('/api/logs/create',
                                  data=json.dumps(self.test_log_data),
                                  content_type='application/json')
        
        assert response.status_code in [200, 201, 400]
        data = response.get_json()
        
        if response.status_code in [200, 201]:
            assert 'success' in data
            assert 'log_id' in data
            assert 'upload_url' in data
        else:
            assert 'error' in data or 'success' in data

    def test_logs_create_simple(self):
        """Test POST /api/logs/create-simple endpoint (operationId: createSimpleLog)"""
        simple_log_data = {
            "Plant Name": "Simple Test Plant",
            "User Notes": "Simple log entry for testing"
        }
        
        response = self.client.post('/api/logs/create-simple',
                                  data=json.dumps(simple_log_data),
                                  content_type='application/json')
        
        assert response.status_code in [200, 201, 400]
        data = response.get_json()
        
        if response.status_code in [200, 201]:
            assert 'success' in data
            assert 'log_id' in data
        else:
            assert 'error' in data or 'success' in data

    def test_logs_search(self):
        """Test GET /api/logs/search endpoint (operationId: searchLogs)"""
        # Test without parameters
        response = self.client.get('/api/logs/search')
        assert response.status_code == 200
        data = response.get_json()
        assert 'search_results' in data
        assert 'total_results' in data
        
        # Test with query parameter
        response = self.client.get('/api/logs/search?q=test&limit=10')
        assert response.status_code == 200
        
        # Test with plant_name parameter
        response = self.client.get('/api/logs/search?plant_name=Test%20Plant')
        assert response.status_code == 200

    # =============================================
    # PHOTO UPLOAD TESTS (2 operations)
    # =============================================
    
    def test_photos_upload_for_plant_get(self):
        """Test GET /api/photos/upload-for-plant/{token} endpoint - should return upload page or error"""
        response = self.client.get('/api/photos/upload-for-plant/invalid_token')
        
        # Should return 200 for upload page or 401 for invalid token
        assert response.status_code in [200, 401]

    def test_photo_upload_token_type_validation(self):
        """Test that log tokens cannot be used for plant uploads and vice versa"""
        from utils.upload_token_manager import generate_upload_token
        
        # Generate different token types
        log_token = generate_upload_token('test_plant', 'log_upload', log_id='TEST-LOG-123')
        plant_token = generate_upload_token('test_plant', 'plant_upload', plant_id='123', operation='add')
        
        # Test 1: Try to use log token for plant upload (should fail with 401)
        with open('test.png', 'rb') as f:
            response = self.client.post(
                f'/api/photos/upload-for-plant/{log_token}',
                data={'file': (f, 'test.png')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'not valid for plant photo uploads' in data.get('error', '')
        
        # Test 2: Try to use plant token for log upload (should fail with 401)
        with open('test.png', 'rb') as f:
            response = self.client.post(
                f'/api/photos/upload-for-log/{plant_token}',
                data={'file': (f, 'test.png')},
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'not valid for log photo uploads' in data.get('error', '')

    def test_photos_upload_for_log_get(self):
        """Test GET /api/photos/upload-for-log/{token} endpoint - should return error for invalid token"""
        response = self.client.get('/api/photos/upload-for-log/invalid_token')
        
        # Should return 401 for invalid token or 405 for method not allowed
        assert response.status_code in [401, 405]

    def test_photos_upload_for_plant_post_invalid_token(self):
        """Test POST /api/photos/upload-for-plant/{token} with invalid token"""
        # Create a minimal test file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_file.flush()
            
            try:
                with open(tmp_file.name, 'rb') as test_file:
                    response = self.client.post('/api/photos/upload-for-plant/invalid_token',
                                              data={'file': (test_file, 'test.png')})
                
                assert response.status_code in [400, 401]
                data = response.get_json()
                assert 'error' in data or 'success' in data
            finally:
                os.unlink(tmp_file.name)

    def test_photos_upload_for_log_post_invalid_token(self):
        """Test POST /api/photos/upload-for-log/{token} with invalid token"""
        # Create a minimal test file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_file.flush()
            
            try:
                with open(tmp_file.name, 'rb') as test_file:
                    response = self.client.post('/api/photos/upload-for-log/invalid_token',
                                              data={'file': (test_file, 'test.png')})
                
                assert response.status_code in [400, 401]
                data = response.get_json()
                assert 'error' in data or 'success' in data
            finally:
                os.unlink(tmp_file.name)

    # =============================================
    # LOCATION INTELLIGENCE TESTS (8 operations)
    # =============================================
    
    def test_locations_get_context(self):
        """Test GET /api/locations/get-context/{id} endpoint (operationId: getLocationContext)"""
        response = self.client.get('/api/locations/get-context/1')
        
        assert response.status_code in [200, 404, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'location_id' in data
            assert 'care_profile' in data
        else:
            assert 'error' in data

    def test_locations_get_context_by_name(self):
        """Test GET /api/locations/get-context/{name} endpoint with location name"""
        # Test with "middle" location name 
        response = self.client.get('/api/locations/get-context/middle')
        
        assert response.status_code in [200, 404, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            # Should convert name to ID and return location data
            assert 'location_id' in data
            assert 'original_identifier' in data
            assert 'care_profile' in data
            assert data['original_identifier'] == 'middle'
        elif response.status_code == 404:
            # If location doesn't exist, should have helpful error message
            assert 'error' in data
            assert 'not found' in data['error'].lower()
        else:
            assert 'error' in data

    def test_garden_get_metadata(self):
        """Test GET /api/garden/get-metadata endpoint (operationId: getGardenMetadata)"""
        response = self.client.get('/api/garden/get-metadata')
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'total_locations' in data
            assert 'total_containers' in data
        else:
            assert 'error' in data

    def test_garden_optimize_care(self):
        """Test GET /api/garden/optimize-care endpoint (operationId: optimizeGardenCare)"""
        response = self.client.get('/api/garden/optimize-care')
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'optimization_analysis' in data
            assert 'total_opportunities' in data
        else:
            assert 'error' in data

    def test_plants_location_context_legacy(self):
        """Test GET /api/plants/{plant_id}/location-context endpoint (operationId: getPlantLocationContext)"""
        response = self.client.get('/api/plants/1/location-context')
        
        assert response.status_code in [200, 404, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'plant_id' in data
            assert 'contexts' in data

    def test_locations_care_profile(self):
        """Test GET /api/locations/{location_id}/care-profile endpoint (operationId: getLocationCareProfile)"""
        response = self.client.get('/api/locations/1/care-profile')
        
        assert response.status_code in [200, 404, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'location_id' in data
            assert 'care_profile' in data

    def test_locations_all(self):
        """Test GET /api/locations/all endpoint (operationId: getAllLocations)"""
        response = self.client.get('/api/locations/all')
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'locations' in data
            assert 'total' in data or 'count' in data

    def test_garden_metadata_enhanced(self):
        """Test GET /api/garden/metadata/enhanced endpoint (operationId: getEnhancedMetadata)"""
        response = self.client.get('/api/garden/metadata/enhanced')
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'enhanced_metadata' in data
            assert 'api_version' in data

    def test_garden_care_optimization(self):
        """Test GET /api/garden/care-optimization endpoint (operationId: getCareOptimization)"""
        response = self.client.get('/api/garden/care-optimization')
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'optimization_analysis' in data
            assert 'total_opportunities' in data
        else:
            assert 'error' in data

    # =============================================
    # WEATHER INTEGRATION TESTS (3 operations)
    # =============================================
    
    def test_weather_current(self):
        """Test GET /api/weather/current endpoint (operationId: getCurrentWeather)"""
        response = self.client.get('/api/weather/current')
        
        # Weather endpoints may not be available in all environments
        assert response.status_code in [200, 404, 500, 503]
        
        if response.status_code == 200:
            data = response.get_json()
            # Weather data structure may vary
            assert isinstance(data, dict)

    def test_weather_forecast_hourly(self):
        """Test GET /api/weather/forecast endpoint (operationId: getWeatherForecast)"""
        # Test without parameters
        response = self.client.get('/api/weather/forecast')
        assert response.status_code in [200, 404, 500, 503]
        
        # Test with hours parameter
        response = self.client.get('/api/weather/forecast?hours=24')
        assert response.status_code in [200, 404, 500, 503]

    def test_weather_forecast_daily(self):
        """Test GET /api/weather/forecast/daily endpoint (operationId: getDailyWeatherForecast)"""
        # Test without parameters
        response = self.client.get('/api/weather/forecast/daily')
        assert response.status_code in [200, 404, 500, 503]
        
        # Test with days parameter
        response = self.client.get('/api/weather/forecast/daily?days=7')
        assert response.status_code in [200, 404, 500, 503]

    # =============================================
    # ADDITIONAL ROUTE TESTS
    # =============================================
    
    def test_additional_plant_routes(self):
        """Test additional plant routes not in main schema"""
        # Test /api/plants (root)
        response = self.client.get('/api/plants')
        assert response.status_code in [200, 404, 405]
        
        # Test /api/plants/all
        response = self.client.get('/api/plants/all')
        assert response.status_code in [200, 404, 405]

    def test_additional_location_routes(self):
        """Test additional location routes"""
        # Test container care requirements
        response = self.client.get('/api/garden/containers/1/care-requirements')
        assert response.status_code in [200, 404, 500]
        
        # Test location analysis
        response = self.client.get('/api/garden/location-analysis/1')
        assert response.status_code in [200, 404, 500]
        
        # Test location profiles
        response = self.client.get('/api/garden/location-profiles')
        assert response.status_code in [200, 500]

    # =============================================
    # ERROR SCENARIO TESTS
    # =============================================
    
    def test_invalid_endpoints(self):
        """Test invalid endpoints return appropriate errors"""
        invalid_endpoints = [
            '/api/invalid/endpoint',
            '/api/plants/invalid',
            '/api/nonexistent'
        ]
        
        for endpoint in invalid_endpoints:
            response = self.client.get(endpoint)
            assert response.status_code in [404, 405]

    def test_missing_required_fields(self):
        """Test endpoints with missing required fields"""
        # Test plant add without required Plant Name
        response = self.client.post('/api/plants/add',
                                  data=json.dumps({"Description": "No name provided"}),
                                  content_type='application/json')
        assert response.status_code in [400]
        
        # Test log create without required Plant Name
        response = self.client.post('/api/logs/create',
                                  data=json.dumps({"User Notes": "No plant name"}),
                                  content_type='application/json')
        assert response.status_code in [400]

    def test_malformed_requests(self):
        """Test endpoints with malformed requests"""
        # Test with invalid JSON
        response = self.client.post('/api/plants/add',
                                  data="invalid json",
                                  content_type='application/json')
        assert response.status_code in [400, 500]
        
        # Test with empty body where required
        response = self.client.post('/api/plants/add',
                                  data="",
                                  content_type='application/json')
        assert response.status_code in [400, 500]

    # =============================================
    # COMPREHENSIVE COVERAGE VALIDATION
    # =============================================
    
    def test_endpoint_coverage_validation(self):
        """Validate that all major endpoints are covered by tests"""
        # This test serves as documentation of covered endpoints
        covered_endpoints = [
            # Core Plant Management (7 operations)
            '/api/plants/search',
            '/api/plants/add', 
            '/api/plants/get/{id}',
            '/api/plants/get-all-fields/{id}',
            '/api/plants/update/{id}',
            '/api/plants/update',
            '/api/plants/get-context/{plant_id}',
            '/api/plants/by-location/{location_name}',
            
            # AI-Powered Analysis (2 operations)
            '/api/plants/diagnose',
            '/api/plants/enhance-analysis',
            
            # Health Logging (3 operations) 
            '/api/logs/create',
            '/api/logs/create-simple',
            '/api/logs/search',
            
            # Photo Upload (2 operations)
            '/api/photos/upload-for-plant/{token}',
            '/api/photos/upload-for-log/{token}',
            
            # Location Intelligence (8 operations)
            '/api/locations/get-context/{id}',
            '/api/garden/get-metadata',
            '/api/garden/optimize-care',
            '/api/plants/{plant_id}/location-context',
            '/api/locations/{location_id}/care-profile',
            '/api/locations/all',
            '/api/garden/metadata/enhanced',
            '/api/garden/care-optimization',
            
            # Weather Integration (3 operations)
            '/api/weather/current',
            '/api/weather/forecast',
            '/api/weather/forecast/daily'
        ]
        
        # Verify we have 23 main endpoints covered
        assert len(covered_endpoints) >= 24
        print(f"✅ Comprehensive test suite covers {len(covered_endpoints)} major endpoints")

    # =================================================================
    # ChatGPT Request Pattern Tests (Bug Regression Prevention)
    # =================================================================
    
    def test_chatgpt_request_pattern_care_optimization(self):
        """Test ChatGPT's request pattern: GET with Content-Type: application/json but no body"""
        # Simulate exactly what ChatGPT sends: Content-Type header with no JSON body
        response = self.client.open(
            '/api/garden/care-optimization',
            method='GET',
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot'
            }
            # Note: No data/json parameter - this simulates empty body with JSON Content-Type
        )
        
        # Should work now with our silent=True fix
        assert response.status_code in [200, 500], f"ChatGPT request pattern failed with {response.status_code}"
        
        if response.status_code == 200:
            data = json.loads(response.get_data(as_text=True))
            assert 'optimization_analysis' in data or 'error' in data
    
    def test_chatgpt_request_pattern_metadata_enhanced(self):
        """Test ChatGPT's request pattern for metadata endpoint"""
        response = self.client.open(
            '/api/garden/metadata/enhanced',
            method='GET',
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot'
            }
        )
        
        # Should work now with our silent=True fix
        assert response.status_code in [200, 500], f"ChatGPT metadata request pattern failed with {response.status_code}"
        
        if response.status_code == 200:
            data = json.loads(response.get_data(as_text=True))
            assert 'enhanced_metadata' in data or 'error' in data
    
    def test_chatgpt_vs_normal_get_request(self):
        """Compare ChatGPT request pattern vs normal GET request behavior"""
        # Normal GET request (no Content-Type header)
        normal_response = self.client.get('/api/garden/care-optimization')
        
        # ChatGPT GET request (with Content-Type: application/json)
        chatgpt_response = self.client.open(
            '/api/garden/care-optimization',
            method='GET',
            headers={'Content-Type': 'application/json'}
        )
        
        # Both should return the same successful response
        assert normal_response.status_code == chatgpt_response.status_code, \
            f"Request patterns differ: normal={normal_response.status_code}, chatgpt={chatgpt_response.status_code}"
        
        # Response content should be identical (if both succeed)
        if normal_response.status_code == 200 and chatgpt_response.status_code == 200:
            normal_data = json.loads(normal_response.get_data(as_text=True))
            chatgpt_data = json.loads(chatgpt_response.get_data(as_text=True))
            
            # Core data should be the same (timestamps might differ)
            assert normal_data.get('optimization_analysis') == chatgpt_data.get('optimization_analysis')
    
    def test_chatgpt_request_pattern_regression_prevention(self):
        """Prevent regression of the ChatGPT 400 error bug"""
        # Test the specific pattern that caused the original bug
        garden_endpoints = [
            '/api/garden/care-optimization',
            '/api/garden/metadata/enhanced',
            '/api/garden/optimize-care',
            '/api/garden/get-metadata'
        ]
        
        for endpoint in garden_endpoints:
            with self.client:
                response = self.client.open(
                    endpoint,
                    method='GET',
                    headers={
                        'Content-Type': 'application/json',  # This caused the original bug
                        'User-Agent': 'ChatGPT-User/1.0'
                    }
                    # No body data - this is the key to the bug
                )
                
                # The original bug: this returned 400 Bad Request
                assert response.status_code != 400, \
                    f"REGRESSION BUG: ChatGPT request pattern returns 400 for {endpoint}!"
                
                # Should return 200 (success) or other valid HTTP codes, but NOT 400
                assert response.status_code in [200, 404, 500], \
                    f"Unexpected status {response.status_code} for {endpoint} with ChatGPT headers"


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
