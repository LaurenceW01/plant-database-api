# Set up sys.path before any imports so relative imports work
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))
import pytest
from main import create_app  # Import the app factory

# Use the app factory to create a test app instance with no rate limiting
app = create_app(testing=True)

# Define a pytest fixture to provide a test client for the Flask app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test the health check endpoint
# This test ensures the root endpoint returns status 200 and the correct JSON
def test_health_check(client):
    # Send a GET request to the root endpoint
    response = client.get('/')
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON contains the expected status
    assert response.get_json()['status'] == 'ok'

# Test the /api/plants endpoint
# This test ensures the endpoint returns status 200 and a 'plants' key in the JSON
def test_list_plants(client):
    # Send a GET request to the /api/plants endpoint
    response = client.get('/api/plants')
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON contains the 'plants' key
    assert 'plants' in response.get_json()

# Test the /api/plants/<id_or_name> endpoint
# This test ensures the endpoint returns status 200 for a valid plant and 404 for an invalid one
def test_get_plant_by_id_or_name(client):
    # First, get the list of plants to find a valid ID or name
    response = client.get('/api/plants')
    assert response.status_code == 200
    plants = response.get_json().get('plants', [])
    if plants:
        # Use the first plant's name or ID for a valid test
        plant = plants[0]
        # Try by name if available
        plant_name = plant.get('Plant Name') or plant.get('name') or None
        if plant_name:
            response = client.get(f'/api/plants/{plant_name}')
            assert response.status_code == 200
            assert 'plant' in response.get_json()
        # Try by ID if available
        plant_id = plant.get('ID') or plant.get('id') or None
        if plant_id:
            response = client.get(f'/api/plants/{plant_id}')
            assert response.status_code == 200
            assert 'plant' in response.get_json()
    # Test with an invalid ID or name
    response = client.get('/api/plants/thisplantdoesnotexist12345')
    assert response.status_code == 404
    assert 'error' in response.get_json()

# Test the POST /api/plants endpoint
# This test ensures a new plant can be added and returns the correct status and message
def test_add_plant(client):
    # Prepare a unique plant name to avoid conflicts
    import uuid
    import os  # Import os to access environment variables
    unique_name = f"TestPlant-{uuid.uuid4()}"
    # Prepare the payload for the new plant
    payload = {
        "Plant Name": unique_name,
        "Description": "A test plant.",
        "Location": "Test Garden",
        "Photo URL": "http://example.com/photo.jpg"
    }
    # Retrieve the API key from environment or use default for testing
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Send a POST request to add the new plant, including the x-api-key header
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201
    # Assert that the response JSON contains a success message
    assert 'message' in response.get_json()
    # Verify the plant was added by retrieving it
    response = client.get(f'/api/plants/{unique_name}')
    assert response.status_code == 200
    assert 'plant' in response.get_json()

# Test the PUT /api/plants/<id_or_name> endpoint
# This test ensures an existing plant can be updated and returns the correct status and message
def test_update_plant(client):
    # First, add a new plant to update
    import uuid
    import os  # Import os to access environment variables
    unique_name = f"TestPlantUpdate-{uuid.uuid4()}"
    payload = {
        "Plant Name": unique_name,
        "Description": "A plant to update.",
        "Location": "Test Garden",
        "Photo URL": "http://example.com/photo.jpg"
    }
    # Retrieve the API key from environment or use default for testing
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Add the plant with the x-api-key header
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    # Update the plant's description
    update_payload = {
        "Description": "Updated description."
    }
    # Send the PUT request with the x-api-key header
    response = client.put(f'/api/plants/{unique_name}', json=update_payload, headers={"x-api-key": api_key})
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON contains a success message
    assert 'message' in response.get_json()
    # Verify the plant was updated by retrieving it
    response = client.get(f'/api/plants/{unique_name}')
    assert response.status_code == 200
    plant = response.get_json().get('plant', {})
    # Assert that the description was updated
    assert plant.get('Description') == "Updated description." 

# Test POST /api/plants with missing required field
# This test ensures a 400 error is returned if 'Plant Name' is missing
def test_add_plant_missing_required(client):
    import os  # Import os to access environment variables
    payload = {
        "Description": "Missing name.",
        "Location": "Test Garden"
    }
    # Retrieve the API key from environment or use default for testing
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Send the POST request with the x-api-key header
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'Plant Name' in response.get_json()['error']

# Test POST /api/plants with invalid field
# This test ensures a 400 error is returned if an invalid field is present
def test_add_plant_invalid_field(client):
    import os  # Import os to access environment variables
    payload = {
        "Plant Name": "InvalidFieldPlant",
        "NotAField": "Should fail"
    }
    # Retrieve the API key from environment or use default for testing
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Send the POST request with the x-api-key header
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'NotAField' in response.get_json()['error']

# Test PUT /api/plants/<id_or_name> with invalid field
# This test ensures a 400 error is returned if an invalid field is present
def test_update_plant_invalid_field(client):
    import os  # Import os to access environment variables
    # Add a plant to update
    import uuid
    unique_name = f"TestPlantUpdateInvalid-{uuid.uuid4()}"
    payload = {
        "Plant Name": unique_name,
        "Description": "A plant to update with invalid field."
    }
    # Retrieve the API key from environment or use default for testing
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Add the plant with the x-api-key header
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    # Try to update with an invalid field
    update_payload = {
        "NotAField": "Should fail"
    }
    # Send the PUT request with the x-api-key header
    response = client.put(f'/api/plants/{unique_name}', json=update_payload, headers={"x-api-key": api_key})
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'NotAField' in response.get_json()['error']

# Test PUT /api/plants/<id_or_name> with no valid fields
# This test ensures a 400 error is returned if no valid fields are provided
def test_update_plant_no_valid_fields(client):
    import os  # Import os to access environment variables
    # Add a plant to update
    import uuid
    unique_name = f"TestPlantUpdateNoValid-{uuid.uuid4()}"
    payload = {
        "Plant Name": unique_name,
        "Description": "A plant to update with no valid fields."
    }
    # Retrieve the API key from environment or use default for testing
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Add the plant with the x-api-key header
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    # Try to update with an empty payload
    update_payload = {}
    # Send the PUT request with the x-api-key header
    response = client.put(f'/api/plants/{unique_name}', json=update_payload, headers={"x-api-key": api_key})
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'No valid fields' in response.get_json()['error']

# (DELETE endpoint test removed as per project requirements) 

# Test POST /api/plants with missing API key
def test_add_plant_missing_api_key(client):
    import uuid
    unique_name = f"TestPlantNoKey-{uuid.uuid4()}"
    payload = {"Plant Name": unique_name}
    response = client.post('/api/plants', json=payload)
    assert response.status_code == 401
    assert 'error' in response.get_json()
    assert response.get_json()['error'] == 'Unauthorized'

# Test POST /api/plants with invalid API key
def test_add_plant_invalid_api_key(client):
    import uuid
    unique_name = f"TestPlantBadKey-{uuid.uuid4()}"
    payload = {"Plant Name": unique_name}
    response = client.post('/api/plants', json=payload, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401
    assert 'error' in response.get_json()
    assert response.get_json()['error'] == 'Unauthorized'

# Test POST /api/plants with valid API key
def test_add_plant_valid_api_key(client):
    import uuid
    import os
    unique_name = f"TestPlantGoodKey-{uuid.uuid4()}"
    payload = {"Plant Name": unique_name}
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    assert response.status_code == 201
    assert 'message' in response.get_json()

# Test PUT /api/plants/<id_or_name> with missing API key
def test_update_plant_missing_api_key(client):
    import uuid
    unique_name = f"TestPlantUpdateNoKey-{uuid.uuid4()}"
    payload = {"Plant Name": unique_name}
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Add the plant first with valid key
    client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    # Try to update without API key
    update_payload = {"Description": "Should not work"}
    response = client.put(f'/api/plants/{unique_name}', json=update_payload)
    assert response.status_code == 401
    assert 'error' in response.get_json()
    assert response.get_json()['error'] == 'Unauthorized'

# Test PUT /api/plants/<id_or_name> with invalid API key
def test_update_plant_invalid_api_key(client):
    import uuid
    unique_name = f"TestPlantUpdateBadKey-{uuid.uuid4()}"
    payload = {"Plant Name": unique_name}
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Add the plant first with valid key
    client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    # Try to update with wrong key
    update_payload = {"Description": "Should not work"}
    response = client.put(f'/api/plants/{unique_name}', json=update_payload, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401
    assert 'error' in response.get_json()
    assert response.get_json()['error'] == 'Unauthorized'

# Test PUT /api/plants/<id_or_name> with valid API key
def test_update_plant_valid_api_key(client):
    import uuid
    import os
    unique_name = f"TestPlantUpdateGoodKey-{uuid.uuid4()}"
    # Provide all required fields for plant creation
    payload = {
        "Plant Name": unique_name,
        "Description": "Initial description.",
        "Location": "Test Garden"
    }
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Add the plant first with valid key and all required fields
    post_response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    print("POST response:", post_response.status_code, post_response.get_json())
    # Update with valid key
    update_payload = {"Description": "Should work"}
    response = client.put(f'/api/plants/{unique_name}', json=update_payload, headers={"x-api-key": api_key})
    # Print error message if not 200 for debugging
    if response.status_code != 200:
        print("Update error response:", response.get_json())
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    assert 'message' in response.get_json()

# Test POST /api/plants with JSON injection attempt
# This test ensures the API does not execute or mishandle injected JSON
def test_add_plant_json_injection(client):
    import os
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    payload = {
        "Plant Name": "InjectionTest",
        "Description": "Injected payload: {\"$ne\": null}",
        "Location": "Test Garden"
    }
    # Attempt to inject JSON-like string in a field
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    # Should be treated as a string, not as code or query
    assert response.status_code in (201, 200, 400)  # Acceptable: created, ok, or validation error
    # Ensure no server error
    assert response.status_code != 500

# Test POST /api/plants with malformed JSON
# This test ensures the API returns a 400 error for malformed JSON
def test_add_plant_malformed_json(client):
    import os
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    # Send a malformed JSON payload (as data, not json=)
    response = client.post(
        '/api/plants',
        data='{"Plant Name": "MalformedTest", "Description": "Missing end brace"',
        headers={"x-api-key": api_key, "Content-Type": "application/json"}
    )
    # Should return 400 Bad Request
    assert response.status_code == 400 or response.status_code == 415  # Accept 415 Unsupported Media Type if Flask handles it that way

# Test POST /api/plants with a very large payload
# This test ensures the API handles or rejects large payloads gracefully
def test_add_plant_large_payload(client):
    import os
    api_key = os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')
    large_description = "A" * 100_000  # 100 KB string
    payload = {
        "Plant Name": "LargePayloadTest",
        "Description": large_description
    }
    response = client.post('/api/plants', json=payload, headers={"x-api-key": api_key})
    # Should not crash the server; accept 201, 400, or 413 (Payload Too Large)
    assert response.status_code in (201, 400, 413)
    assert response.status_code != 500 