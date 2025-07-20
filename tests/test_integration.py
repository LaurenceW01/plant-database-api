# Integration tests for Phase 5: Testing & Quality Assurance
# These tests verify end-to-end functionality and integration between components

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))

import pytest
import time
import uuid
from api.main import create_app

# Use the app factory to create a test app instance with no rate limiting
app = create_app(testing=True)

# Define a pytest fixture to provide a test client for the Flask app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def api_key():
    """Fixture to provide API key for authenticated requests"""
    return os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')

# === CACHE BEHAVIOR INTEGRATION TESTS ===

def test_plant_list_cache_behavior(client, api_key):
    """Test that plant list caching works correctly and invalidates appropriately"""
    from utils.plant_operations import get_plant_list_cache_info, invalidate_plant_list_cache
    
    # Start with a fresh cache
    invalidate_plant_list_cache()
    
    # First request should populate the cache
    response1 = client.get('/api/plants')
    assert response1.status_code == 200
    plants1 = response1.get_json()['plants']
    
    # Check cache status
    cache_info = get_plant_list_cache_info()
    assert cache_info['is_valid'] == True
    assert cache_info['plant_count'] >= 0
    
    # Add a new plant
    unique_name = f"CacheTest-{uuid.uuid4()}"
    payload = {
        "Plant Name": unique_name,
        "Description": "Testing cache invalidation",
        "Location": "Test Garden"
    }
    
    add_response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert add_response.status_code == 201
    
    # Cache should be invalidated after adding a plant
    cache_info_after = get_plant_list_cache_info()
    assert cache_info_after['is_valid'] == False
    
    # Next request should rebuild cache
    response2 = client.get('/api/plants')
    assert response2.status_code == 200
    plants2 = response2.get_json()['plants']
    
    # Should have more plants than before
    assert len(plants2) >= len(plants1)
    
    # Verify the new plant is in the list
    plant_names = [plant.get('Plant Name', '') for plant in plants2]
    assert unique_name in plant_names

def test_crud_operations_end_to_end(client, api_key):
    """Test complete CRUD cycle maintains data integrity"""
    unique_id = str(uuid.uuid4())[:8]
    plant_name = f"FullCRUDTest-{unique_id}"
    
    # === CREATE ===
    create_payload = {
        "Plant Name": plant_name,
        "Description": "Full CRUD test plant",
        "Location": "Test Garden",
        "Light Requirements": "Full Sun",
        "Watering Needs": "Moderate",
        "Soil Preferences": "Well-draining",
        "Care Notes": "Initial care notes"
    }
    
    create_response = client.post('/api/plants', json=create_payload, headers={"x-api-key": api_key})
    assert create_response.status_code == 201
    
    # === READ ===
    read_response = client.get(f'/api/plants/{plant_name}')
    assert read_response.status_code == 200
    plant_data = read_response.get_json()['plant']
    
    # Verify all data was stored correctly
    assert plant_data['Plant Name'] == plant_name
    assert plant_data['Description'] == "Full CRUD test plant"
    assert plant_data['Location'] == "Test Garden"
    assert plant_data['Light Requirements'] == "Full Sun"
    assert plant_data['Watering Needs'] == "Moderate"
    assert plant_data['Soil Preferences'] == "Well-draining"
    assert plant_data['Care Notes'] == "Initial care notes"
    
    # Verify metadata fields are populated
    assert 'ID' in plant_data
    assert 'Last Updated' in plant_data
    assert plant_data['Last Updated'] != ''
    
    # === UPDATE ===
    update_payload = {
        "Description": "Updated CRUD test plant",
        "Care Notes": "Updated care notes with new information",
        "Pruning Instructions": "Prune in early spring"
    }
    
    update_response = client.put(f'/api/plants/{plant_name}', json=update_payload, headers={"x-api-key": api_key})
    assert update_response.status_code == 200
    
    # Verify updates were applied
    updated_read_response = client.get(f'/api/plants/{plant_name}')
    assert updated_read_response.status_code == 200
    updated_plant_data = updated_read_response.get_json()['plant']
    
    # Updated fields should have new values
    assert updated_plant_data['Description'] == "Updated CRUD test plant"
    assert updated_plant_data['Care Notes'] == "Updated care notes with new information"
    assert updated_plant_data['Pruning Instructions'] == "Prune in early spring"
    
    # Non-updated fields should remain unchanged
    assert updated_plant_data['Plant Name'] == plant_name
    assert updated_plant_data['Location'] == "Test Garden"
    assert updated_plant_data['Light Requirements'] == "Full Sun"
    assert updated_plant_data['Watering Needs'] == "Moderate"
    assert updated_plant_data['Soil Preferences'] == "Well-draining"
    
    # === SEARCH ===
    # Test search finds the plant
    search_response = client.get(f'/api/plants?q={plant_name}')
    assert search_response.status_code == 200
    search_results = search_response.get_json()['plants']
    assert len(search_results) >= 1
    
    found_plant = next((p for p in search_results if p['Plant Name'] == plant_name), None)
    assert found_plant is not None
    assert found_plant['Description'] == "Updated CRUD test plant"

def test_field_validation_integration(client, api_key):
    """Test comprehensive field validation across the entire system"""
    from models.field_config import get_all_field_names, FIELD_ALIASES
    
    unique_name = f"FieldValidationTest-{uuid.uuid4()}"
    
    # Test 1: All valid canonical field names should work
    valid_payload = {}
    for field_name in get_all_field_names():
        if field_name not in ['ID', 'Last Updated']:  # Skip auto-generated fields
            valid_payload[field_name] = f"Test value for {field_name}"
    
    valid_payload['Plant Name'] = unique_name  # Ensure required field
    
    response = client.post('/api/plants', json=valid_payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    
    # Test 2: Field aliases should be accepted
    alias_name = f"AliasTest-{uuid.uuid4()}"
    alias_payload = {
        "name": alias_name,  # Alias for Plant Name
        "desc": "Using aliases",  # Alias for Description
        "location": "Test Garden",  # Canonical field
        "light": "Partial Shade",  # Alias for Light Requirements
        "water": "High"  # Alias for Watering Needs
    }
    
    alias_response = client.post('/api/plants', json=alias_payload, headers={"x-api-key": api_key})
    assert alias_response.status_code == 201
    
    # Verify data was stored with canonical field names
    read_response = client.get(f'/api/plants/{alias_name}')
    assert read_response.status_code == 200
    stored_data = read_response.get_json()['plant']
    
    assert stored_data['Plant Name'] == alias_name
    assert stored_data['Description'] == "Using aliases"
    assert stored_data['Location'] == "Test Garden"
    assert stored_data['Light Requirements'] == "Partial Shade"
    assert stored_data['Watering Needs'] == "High"
    
    # Test 3: Invalid field names should be rejected
    invalid_payload = {
        "Plant Name": f"InvalidTest-{uuid.uuid4()}",
        "InvalidFieldName": "Should be rejected",
        "AnotherInvalidField": "Also rejected"
    }
    
    invalid_response = client.post('/api/plants', json=invalid_payload, headers={"x-api-key": api_key})
    assert invalid_response.status_code == 400
    error_data = invalid_response.get_json()
    assert 'error' in error_data
    assert 'InvalidFieldName' in error_data['error']

def test_photo_url_integration(client, api_key):
    """Test photo URL handling end-to-end with IMAGE formula preservation"""
    unique_name = f"PhotoURLTest-{uuid.uuid4()}"
    test_photo_url = "https://example.com/test-plant-photo.jpg"
    
    # Create plant with photo URL
    payload = {
        "Plant Name": unique_name,
        "Description": "Plant with photo for testing",
        "Photo URL": test_photo_url
    }
    
    create_response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert create_response.status_code == 201
    
    # Verify photo URL storage
    read_response = client.get(f'/api/plants/{unique_name}')
    assert read_response.status_code == 200
    plant_data = read_response.get_json()['plant']
    
    # Both Photo URL and Raw Photo URL fields should be present
    assert 'Photo URL' in plant_data
    assert 'Raw Photo URL' in plant_data
    
    # Photo URL should contain the IMAGE formula
    assert plant_data.get('Photo URL', '').startswith('=IMAGE("')
    assert plant_data.get('Photo URL', '').endswith('")')
    assert test_photo_url in plant_data.get('Photo URL', '')
    
    # Raw Photo URL should contain the original URL
    assert plant_data.get('Raw Photo URL') == test_photo_url
    
    # Update photo URL
    new_photo_url = "https://example.com/updated-plant-photo.jpg"
    update_payload = {
        "Photo URL": new_photo_url
    }
    
    update_response = client.put(f'/api/plants/{unique_name}', json=update_payload, headers={"x-api-key": api_key})
    assert update_response.status_code == 200
    
    # Verify photo URL was updated
    updated_read_response = client.get(f'/api/plants/{unique_name}')
    assert updated_read_response.status_code == 200
    updated_plant_data = updated_read_response.get_json()['plant']
    
    # Verify updated Photo URL has IMAGE formula
    assert updated_plant_data.get('Photo URL', '').startswith('=IMAGE("')
    assert updated_plant_data.get('Photo URL', '').endswith('")')
    assert new_photo_url in updated_plant_data.get('Photo URL', '')
    
    # Raw Photo URL should contain the new URL without formula
    assert updated_plant_data.get('Raw Photo URL') == new_photo_url

def test_search_integration_comprehensive(client, api_key):
    """Test comprehensive search functionality with various query types"""
    test_id = str(uuid.uuid4())[:8]
    
    # Create test plants with specific searchable content
    test_plants = [
        {
            "Plant Name": f"SearchRose-{test_id}",
            "Description": f"Beautiful red climbing rose {test_id}",
            "Location": f"Front Garden {test_id}",
            "Light Requirements": "Full Sun"
        },
        {
            "Plant Name": f"SearchTomato-{test_id}",
            "Description": f"Heirloom tomato variety {test_id}",
            "Location": f"Vegetable Garden {test_id}",
            "Light Requirements": "Full Sun"
        },
        {
            "Plant Name": f"SearchFern-{test_id}",
            "Description": f"Shade-loving fern {test_id}",
            "Location": f"Shade Garden {test_id}",
            "Light Requirements": "Partial Shade"
        }
    ]
    
    # Add all test plants
    for plant in test_plants:
        response = client.post('/api/plants', json=plant, headers={"x-api-key": api_key})
        assert response.status_code == 201
    
    # Test 1: Search by exact plant name
    response = client.get(f'/api/plants?q=SearchRose-{test_id}')
    assert response.status_code == 200
    results = response.get_json()['plants']
    assert len(results) >= 1
    assert any(plant['Plant Name'] == f"SearchRose-{test_id}" for plant in results)
    
    # Test 2: Search by partial name
    response = client.get(f'/api/plants?q=SearchRose')
    assert response.status_code == 200
    results = response.get_json()['plants']
    rose_results = [p for p in results if f"SearchRose-{test_id}" in p['Plant Name']]
    assert len(rose_results) >= 1
    
    # Test 3: Search by description keyword
    response = client.get(f'/api/plants?q=climbing')
    assert response.status_code == 200
    results = response.get_json()['plants']
    climbing_results = [p for p in results if 'climbing' in p.get('Description', '').lower()]
    assert len(climbing_results) >= 1
    
    # Test 4: Search by location
    response = client.get(f'/api/plants?q=Front Garden {test_id}')
    assert response.status_code == 200
    results = response.get_json()['plants']
    front_garden_results = [p for p in results if f"Front Garden {test_id}" in p.get('Location', '')]
    assert len(front_garden_results) >= 1
    
    # Test 5: Search by test ID should find all test plants
    response = client.get(f'/api/plants?q={test_id}')
    assert response.status_code == 200
    results = response.get_json()['plants']
    test_results = [p for p in results if test_id in p.get('Plant Name', '') or test_id in p.get('Description', '')]
    assert len(test_results) >= 3
    
    # Test 6: Empty search should return all plants
    response = client.get('/api/plants?q=')
    assert response.status_code == 200
    results = response.get_json()['plants']
    assert len(results) >= 3  # At least our test plants

def test_error_handling_integration(client, api_key):
    """Test comprehensive error handling across the API"""
    
    # Test 1: Missing required field
    response = client.post('/api/plants', json={"Description": "Missing name"}, headers={"x-api-key": api_key})
    assert response.status_code == 400
    assert 'Plant Name' in response.get_json()['error']
    
    # Test 2: Invalid field name
    response = client.post('/api/plants', json={"Plant Name": "Test", "InvalidField": "Bad"}, headers={"x-api-key": api_key})
    assert response.status_code == 400
    assert 'InvalidField' in response.get_json()['error']
    
    # Test 3: Missing API key
    response = client.post('/api/plants', json={"Plant Name": "Test"})
    assert response.status_code == 401
    assert response.get_json()['error'] == 'Unauthorized'
    
    # Test 4: Invalid API key
    response = client.post('/api/plants', json={"Plant Name": "Test"}, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401
    assert response.get_json()['error'] == 'Unauthorized'
    
    # Test 5: Plant not found
    response = client.get('/api/plants/nonexistent-plant-12345')
    assert response.status_code == 404
    assert 'not found' in response.get_json()['error'].lower()
    
    # Test 6: Update nonexistent plant
    response = client.put('/api/plants/nonexistent-plant-12345', json={"Description": "Test"}, headers={"x-api-key": api_key})
    assert response.status_code == 400  # Should return error when plant not found
    
    # Test 7: Empty JSON payload
    response = client.post('/api/plants', json={}, headers={"x-api-key": api_key})
    assert response.status_code == 400

def test_data_consistency_after_operations(client, api_key):
    """Test that data remains consistent after multiple operations"""
    unique_id = str(uuid.uuid4())[:8]
    plant_name = f"ConsistencyTest-{unique_id}"
    
    # Create initial plant
    initial_data = {
        "Plant Name": plant_name,
        "Description": "Initial description",
        "Location": "Initial location",
        "Light Requirements": "Full Sun",
        "Watering Needs": "Moderate"
    }
    
    create_response = client.post('/api/plants', json=initial_data, headers={"x-api-key": api_key})
    assert create_response.status_code == 201
    
    # Perform multiple updates
    updates = [
        {"Description": "First update"},
        {"Location": "Updated location"},
        {"Care Notes": "Added care notes"},
        {"Pruning Instructions": "Added pruning info"},
        {"Description": "Final description update"}
    ]
    
    for update in updates:
        response = client.put(f'/api/plants/{plant_name}', json=update, headers={"x-api-key": api_key})
        assert response.status_code == 200
    
    # Verify final state
    final_response = client.get(f'/api/plants/{plant_name}')
    assert final_response.status_code == 200
    final_data = final_response.get_json()['plant']
    
    # Check that all updates were applied correctly
    assert final_data['Plant Name'] == plant_name
    assert final_data['Description'] == "Final description update"  # Last update
    assert final_data['Location'] == "Updated location"
    assert final_data['Light Requirements'] == "Full Sun"  # Unchanged
    assert final_data['Watering Needs'] == "Moderate"  # Unchanged
    assert final_data['Care Notes'] == "Added care notes"
    assert final_data['Pruning Instructions'] == "Added pruning info"
    
    # Verify Last Updated timestamp was updated
    assert final_data['Last Updated'] != ''
    
    # Verify the plant appears in search results
    search_response = client.get(f'/api/plants?q={plant_name}')
    assert search_response.status_code == 200
    search_results = search_response.get_json()['plants']
    found_plant = next((p for p in search_results if p['Plant Name'] == plant_name), None)
    assert found_plant is not None
    assert found_plant['Description'] == "Final description update" 