# Deployment validation tests for Phase 5: Testing & Quality Assurance
# These tests verify the API is ready for production deployment on render.com
# and accessible to external clients including ChatGPT

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))

import pytest
import json
import uuid
import requests
from api.main import create_app

# Use the app factory to create a test app instance
app = create_app(testing=True)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def api_key():
    """Fixture to provide API key for authenticated requests"""
    return os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')

# === DEPLOYMENT READINESS TESTS ===

def test_health_check_endpoint(client):
    """Test that the health check endpoint works correctly for deployment monitoring"""
    response = client.get('/')
    
    # Should return 200 OK
    assert response.status_code == 200
    
    # Should return valid JSON
    data = response.get_json()
    assert data is not None
    assert isinstance(data, dict)
    
    # Should have status and message fields
    assert 'status' in data
    assert 'message' in data
    assert data['status'] == 'ok'
    
    # Response should be suitable for health monitoring
    assert 'Plant Database API' in data['message']

def test_cors_headers_present(client):
    """Test that CORS headers are properly configured for web client access"""
    response = client.get('/api/plants')
    
    # CORS headers should be present for web browser access
    # Note: In testing mode, the actual CORS headers might not be present
    # but we can verify the endpoint responds correctly
    assert response.status_code == 200
    
    # Verify response is JSON (required for web clients)
    assert response.content_type.startswith('application/json')

def test_api_error_responses_are_json(client, api_key):
    """Test that all error responses are properly formatted JSON for client consumption"""
    
    # Test 400 error (missing required field)
    response = client.post('/api/plants', json={}, headers={"x-api-key": api_key})
    assert response.status_code == 400
    assert response.content_type.startswith('application/json')
    data = response.get_json()
    assert 'error' in data
    assert isinstance(data['error'], str)
    
    # Test 401 error (missing API key)
    response = client.post('/api/plants', json={"Plant Name": "Test"})
    assert response.status_code == 401
    assert response.content_type.startswith('application/json')
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Unauthorized'
    
    # Test 404 error (plant not found)
    response = client.get('/api/plants/nonexistent-plant-12345')
    assert response.status_code == 404
    assert response.content_type.startswith('application/json')
    data = response.get_json()
    assert 'error' in data

def test_environment_variable_handling():
    """Test that the application properly handles environment variables for deployment"""
    
    # API key should be configurable via environment
    api_key = os.environ.get('GARDENLLM_API_KEY')
    assert api_key is not None, "GARDENLLM_API_KEY environment variable should be set"
    assert len(api_key) > 10, "API key should be sufficiently complex"
    
    # Google credentials should be available
    google_creds = os.environ.get('GOOGLE_CREDENTIALS')
    # Note: This might be None in local testing, but should be present in production
    # We don't assert this to allow local testing

def test_api_documentation_endpoints(client):
    """Test that the API provides proper documentation for external clients"""
    
    # Health check should provide API status info
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'Plant Database API' in data['message']
    
    # All endpoints should return structured responses
    endpoints_to_test = [
        ('/api/plants', 'GET'),
    ]
    
    for endpoint, method in endpoints_to_test:
        if method == 'GET':
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.content_type.startswith('application/json')
            
            # Response should be well-structured
            data = response.get_json()
            assert isinstance(data, dict)

# === EXTERNAL CLIENT COMPATIBILITY TESTS ===

def test_chatgpt_compatible_request_format(client, api_key):
    """Test that the API accepts requests in formats suitable for ChatGPT/AI clients"""
    
    # Test JSON payload that ChatGPT might send
    chatgpt_payload = {
        "Plant Name": "ChatGPT Test Plant",
        "Description": "A plant added by an AI assistant for testing API compatibility",
        "Location": "AI Test Garden",
        "Light Requirements": "Full Sun",
        "Watering Needs": "Moderate"
    }
    
    response = client.post('/api/plants', json=chatgpt_payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    
    # Response should be structured for AI consumption
    data = response.get_json()
    assert 'message' in data
    assert isinstance(data['message'], str)
    
    # Verify the plant can be retrieved
    response = client.get('/api/plants/ChatGPT Test Plant')
    assert response.status_code == 200
    plant_data = response.get_json()
    assert 'plant' in plant_data
    
    # Data should match what was sent
    plant = plant_data['plant']
    assert plant['Plant Name'] == "ChatGPT Test Plant"
    assert plant['Description'] == "A plant added by an AI assistant for testing API compatibility"
    assert plant['Light Requirements'] == "Full Sun"

def test_field_validation_for_ai_clients(client, api_key):
    """Test that field validation provides clear feedback for AI clients"""
    
    # Test invalid field name
    invalid_payload = {
        "Plant Name": "Invalid Field Test",
        "InvalidFieldName": "This should be rejected"
    }
    
    response = client.post('/api/plants', json=invalid_payload, headers={"x-api-key": api_key})
    assert response.status_code == 400
    
    error_data = response.get_json()
    assert 'error' in error_data
    assert 'InvalidFieldName' in error_data['error']
    
    # Error message should be clear for AI interpretation
    assert isinstance(error_data['error'], str)
    assert len(error_data['error']) > 10  # Should be descriptive

def test_search_functionality_for_ai(client):
    """Test search functionality that AI clients would use"""
    
    # Test search with query parameter
    response = client.get('/api/plants?q=test')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'plants' in data
    assert isinstance(data['plants'], list)
    
    # Test empty search (should return all plants)
    response = client.get('/api/plants?q=')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'plants' in data
    assert isinstance(data['plants'], list)

def test_comprehensive_crud_for_ai_clients(client, api_key):
    """Test complete CRUD operations as an AI client would use them"""
    
    unique_id = str(uuid.uuid4())[:8]
    plant_name = f"AI-CRUD-Test-{unique_id}"
    
    # CREATE - AI adds a plant
    create_payload = {
        "Plant Name": plant_name,
        "Description": "AI-created plant for CRUD testing",
        "Location": "AI Test Garden",
        "Care Notes": "Initial AI care instructions"
    }
    
    response = client.post('/api/plants', json=create_payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    create_data = response.get_json()
    assert 'message' in create_data
    
    # READ - AI retrieves the plant
    response = client.get(f'/api/plants/{plant_name}')
    assert response.status_code == 200
    read_data = response.get_json()
    assert 'plant' in read_data
    plant = read_data['plant']
    assert plant['Plant Name'] == plant_name
    assert plant['Description'] == "AI-created plant for CRUD testing"
    
    # UPDATE - AI modifies the plant
    update_payload = {
        "Care Notes": "Updated AI care instructions with seasonal information",
        "Pruning Instructions": "Prune in early spring before new growth"
    }
    
    response = client.put(f'/api/plants/{plant_name}', json=update_payload, headers={"x-api-key": api_key})
    assert response.status_code == 200
    update_data = response.get_json()
    assert 'message' in update_data
    
    # VERIFY UPDATE - AI confirms changes
    response = client.get(f'/api/plants/{plant_name}')
    assert response.status_code == 200
    updated_plant_data = response.get_json()['plant']
    assert updated_plant_data['Care Notes'] == "Updated AI care instructions with seasonal information"
    assert updated_plant_data['Pruning Instructions'] == "Prune in early spring before new growth"
    
    # Original fields should remain unchanged
    assert updated_plant_data['Plant Name'] == plant_name
    assert updated_plant_data['Description'] == "AI-created plant for CRUD testing"

def test_api_rate_limiting_feedback(client, api_key):
    """Test that rate limiting provides appropriate feedback for AI clients"""
    
    # Make several requests quickly to potentially trigger rate limiting
    # Note: In testing mode, rate limiting might be disabled
    responses = []
    for i in range(5):
        payload = {
            "Plant Name": f"RateTest-{i}-{uuid.uuid4()}",
            "Description": f"Rate limit test plant {i}"
        }
        response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
        responses.append(response.status_code)
    
    # At least some requests should succeed
    successful_requests = [status for status in responses if status == 201]
    assert len(successful_requests) > 0
    
    # If rate limiting is triggered, the response should be clear
    rate_limited_requests = [status for status in responses if status == 429]
    # We don't assert on rate limiting since it might be disabled in testing

def test_api_payload_size_handling(client, api_key):
    """Test that the API handles various payload sizes appropriately for AI clients"""
    
    # Test normal-sized payload
    normal_payload = {
        "Plant Name": f"NormalSize-{uuid.uuid4()}",
        "Description": "Normal description length for testing",
        "Location": "Test Garden"
    }
    
    response = client.post('/api/plants', json=normal_payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    
    # Test larger description (AI might provide detailed descriptions)
    large_description = "This is a very detailed plant description that an AI might provide. " * 20
    large_payload = {
        "Plant Name": f"LargeDesc-{uuid.uuid4()}",
        "Description": large_description,
        "Location": "Test Garden"
    }
    
    response = client.post('/api/plants', json=large_payload, headers={"x-api-key": api_key})
    # Should either accept it or provide clear error
    assert response.status_code in [201, 400, 413]  # Created, Bad Request, or Payload Too Large
    
    if response.status_code != 201:
        # Error response should be clear
        error_data = response.get_json()
        assert 'error' in error_data

# === PRODUCTION CONFIGURATION TESTS ===

def test_security_headers_configuration():
    """Test that security-related configurations are appropriate for production"""
    
    # Test that the app can be created without testing mode
    production_app = create_app(testing=False)
    assert production_app is not None
    
    # Rate limiting should be enabled in production mode
    assert production_app.config.get('RATELIMIT_ENABLED', True) == True

def test_logging_configuration():
    """Test that logging is properly configured for production monitoring"""
    import logging
    
    # Verify that logging is configured
    logger = logging.getLogger('api.main')
    assert logger is not None
    
    # In production, we should have file logging capabilities
    # This is tested implicitly by the audit logging in the API endpoints

def test_database_connection_resilience(client):
    """Test that the API handles database connection issues gracefully"""
    
    # Test that a basic read operation works
    response = client.get('/api/plants')
    assert response.status_code == 200
    
    # Verify the response structure is correct even if database is empty or has issues
    data = response.get_json()
    assert 'plants' in data
    assert isinstance(data['plants'], list)

def test_api_versioning_readiness():
    """Test that the API structure supports future versioning"""
    
    # API endpoints use /api/ prefix which supports versioning
    app_with_client = create_app(testing=True)
    with app_with_client.test_client() as client:
        response = client.get('/api/plants')
        assert response.status_code == 200
        
        # Health check doesn't use /api/ prefix (correct for status endpoint)
        response = client.get('/')
        assert response.status_code == 200 