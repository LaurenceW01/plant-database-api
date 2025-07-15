# Import necessary modules for testing
import sys
import os
import pytest

# Add the project root directory to the Python path to import the Flask app and its dependencies
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add the api directory to the Python path to import the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))
from main import app  # Import the Flask app instance

# Define a pytest fixture to provide a test client for the Flask app
def pytest_configure():
    pass  # This is a placeholder for any pytest configuration if needed

@pytest.fixture
def client():
    # Set the Flask app in testing mode
    app.config['TESTING'] = True
    # Create a test client using Flask's built-in test_client method
    with app.test_client() as client:
        yield client  # Provide the test client to the test functions

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
    unique_name = f"TestPlant-{uuid.uuid4()}"
    # Prepare the payload for the new plant
    payload = {
        "Plant Name": unique_name,
        "Description": "A test plant.",
        "Location": "Test Garden",
        "Photo URL": "http://example.com/photo.jpg"
    }
    # Send a POST request to add the new plant
    response = client.post('/api/plants', json=payload)
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
    unique_name = f"TestPlantUpdate-{uuid.uuid4()}"
    payload = {
        "Plant Name": unique_name,
        "Description": "A plant to update.",
        "Location": "Test Garden",
        "Photo URL": "http://example.com/photo.jpg"
    }
    response = client.post('/api/plants', json=payload)
    assert response.status_code == 201
    # Update the plant's description
    update_payload = {
        "Description": "Updated description."
    }
    response = client.put(f'/api/plants/{unique_name}', json=update_payload)
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
    payload = {
        "Description": "Missing name.",
        "Location": "Test Garden"
    }
    response = client.post('/api/plants', json=payload)
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'Plant Name' in response.get_json()['error']

# Test POST /api/plants with invalid field
# This test ensures a 400 error is returned if an invalid field is present
def test_add_plant_invalid_field(client):
    payload = {
        "Plant Name": "InvalidFieldPlant",
        "NotAField": "Should fail"
    }
    response = client.post('/api/plants', json=payload)
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'NotAField' in response.get_json()['error']

# Test PUT /api/plants/<id_or_name> with invalid field
# This test ensures a 400 error is returned if an invalid field is present
def test_update_plant_invalid_field(client):
    # Add a plant to update
    import uuid
    unique_name = f"TestPlantUpdateInvalid-{uuid.uuid4()}"
    payload = {
        "Plant Name": unique_name,
        "Description": "A plant to update with invalid field."
    }
    response = client.post('/api/plants', json=payload)
    assert response.status_code == 201
    # Try to update with an invalid field
    update_payload = {
        "NotAField": "Should fail"
    }
    response = client.put(f'/api/plants/{unique_name}', json=update_payload)
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'NotAField' in response.get_json()['error']

# Test PUT /api/plants/<id_or_name> with no valid fields
# This test ensures a 400 error is returned if no valid fields are provided
def test_update_plant_no_valid_fields(client):
    # Add a plant to update
    import uuid
    unique_name = f"TestPlantUpdateNoValid-{uuid.uuid4()}"
    payload = {
        "Plant Name": unique_name,
        "Description": "A plant to update with no valid fields."
    }
    response = client.post('/api/plants', json=payload)
    assert response.status_code == 201
    # Try to update with an empty payload
    update_payload = {}
    response = client.put(f'/api/plants/{unique_name}', json=update_payload)
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'No valid fields' in response.get_json()['error']

# (DELETE endpoint test removed as per project requirements) 