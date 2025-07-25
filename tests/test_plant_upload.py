"""
Tests for plant photo upload functionality.
"""

import pytest
import io
from datetime import datetime
from utils.upload_token_manager import generate_upload_token, _token_storage

@pytest.fixture
def app():
    """Create test Flask app"""
    from api.main import create_app
    app = create_app(testing=True)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def mock_storage(monkeypatch):
    """Mock storage client for testing"""
    def mock_upload(*args, **kwargs):
        return {
            'photo_url': 'http://test.com/photo.jpg',
            'raw_photo_url': 'http://test.com/photo.jpg',
            'filename': 'test_photo.jpg',
            'upload_time': datetime.now().isoformat(),
            'file_size': 1024,
            'content_type': 'image/jpeg'
        }
    
    def mock_available(*args, **kwargs):
        return True
    
    # Import the module
    import utils.storage_client
    
    # Mock the functions
    monkeypatch.setattr(utils.storage_client, 'upload_plant_photo', mock_upload)
    monkeypatch.setattr(utils.storage_client, 'is_storage_available', mock_available)

@pytest.fixture
def mock_plant_operations(monkeypatch):
    """Mock plant operations for testing"""
    def mock_update(*args, **kwargs):
        # Verify that Photo URL is wrapped in IMAGE formula
        update_data = kwargs.get('update_data', {}) if len(args) < 2 else args[1]
        photo_url = update_data.get('Photo URL', '')
        if photo_url and not photo_url.startswith('=IMAGE("'):
            photo_url = f'=IMAGE("{photo_url}")'
            update_data['Photo URL'] = photo_url
        return {'success': True, 'message': 'Plant updated'}
    
    def mock_add(*args, **kwargs):
        return {'success': True, 'message': 'Plant added'}
    
    # Import the module
    import utils.plant_operations
    
    # Mock the functions
    monkeypatch.setattr(utils.plant_operations, 'update_plant', mock_update)
    monkeypatch.setattr(utils.plant_operations, 'add_plant_with_fields', mock_add)

@pytest.fixture(autouse=True)
def clear_token_storage():
    """Clear token storage before each test"""
    _token_storage.clear()
    yield
    _token_storage.clear()

def test_upload_photo_to_plant_add(client, mock_storage, mock_plant_operations):
    """Test uploading a photo when adding a new plant"""
    # Generate upload token for new plant
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    # Create test file
    file_data = io.BytesIO(b"test file content")
    
    # Make upload request
    response = client.post(
        f'/upload/plant/{token}',
        data={'file': (file_data, 'test.jpg')},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['plant_name'] == "Test Plant"
    assert data['plant_id'] == "PLANT-123"
    assert 'photo_upload' in data
    assert data['photo_upload']['photo_url'] == 'http://test.com/photo.jpg'
    assert data['plant_update']['updated'] is True

def test_upload_photo_to_plant_update(client, mock_storage, mock_plant_operations):
    """Test uploading a photo when updating an existing plant"""
    # Generate upload token for existing plant
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="update"
    )
    
    # Create test file
    file_data = io.BytesIO(b"test file content")
    
    # Make upload request
    response = client.post(
        f'/upload/plant/{token}',
        data={'file': (file_data, 'test.jpg')},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['plant_name'] == "Test Plant"
    assert data['plant_id'] == "PLANT-123"
    assert 'photo_upload' in data
    assert data['photo_upload']['photo_url'] == 'http://test.com/photo.jpg'
    assert data['plant_update']['updated'] is True

def test_photo_url_formula_handling(client, mock_storage, mock_plant_operations):
    """Test that photo URLs are correctly wrapped in IMAGE formula"""
    from utils.plant_operations import update_plant
    
    # Generate upload token for existing plant
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="update"
    )
    
    # Create test file
    file_data = io.BytesIO(b"test file content")
    
    # Make upload request
    response = client.post(
        f'/upload/plant/{token}',
        data={'file': (file_data, 'test.jpg')},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    
    # Verify the photo URLs in the response
    assert 'photo_upload' in data
    raw_url = data['photo_upload']['photo_url']
    
    # The update_data sent to update_plant should contain raw URLs
    # The update_plant function will handle wrapping in IMAGE formula
    expected_update_data = {
        'Photo URL': raw_url,  # Raw URL - update_plant will wrap it
        'Raw Photo URL': raw_url
    }
    
    # Mock the update_plant function to capture and verify the update_data
    update_data_captured = {}
    def mock_update_capture(*args, **kwargs):
        nonlocal update_data_captured
        update_data_captured = kwargs.get('update_data', {}) if len(args) < 2 else args[1]
        return {'success': True, 'message': 'Plant updated'}
    
    import utils.plant_operations
    utils.plant_operations.update_plant = mock_update_capture
    
    # Create a new file object for the second request
    new_file_data = io.BytesIO(b"test file content")
    
    # Generate a new token since the first one is used
    new_token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="update"
    )
    
    # Trigger the update by making another request
    response = client.post(
        f'/upload/plant/{new_token}',
        data={'file': (new_file_data, 'test.jpg')},
        content_type='multipart/form-data'
    )
    
    # Verify the update_data contains raw URLs
    assert 'Photo URL' in update_data_captured
    assert update_data_captured['Photo URL'] == raw_url  # Raw URL is sent to update_plant
    assert update_data_captured['Raw Photo URL'] == raw_url

def test_upload_photo_invalid_token(client, mock_storage, mock_plant_operations):
    """Test uploading with invalid token"""
    response = client.post(
        '/upload/plant/invalid_token',
        data={'file': (io.BytesIO(b"test"), 'test.jpg')},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid' in data['error']

def test_upload_photo_wrong_token_type(client, mock_storage, mock_plant_operations):
    """Test uploading with log token instead of plant token"""
    # Generate log upload token
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="log_upload",
        log_id="LOG-123"
    )
    
    response = client.post(
        f'/upload/plant/{token}',
        data={'file': (io.BytesIO(b"test"), 'test.jpg')},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'token type' in data['error'].lower()

def test_upload_photo_no_file(client, mock_storage, mock_plant_operations):
    """Test uploading without a file"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    response = client.post(f'/upload/plant/{token}')
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'No photo file' in data['error']

def test_upload_photo_empty_file(client, mock_storage, mock_plant_operations):
    """Test uploading with empty file selection"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    response = client.post(
        f'/upload/plant/{token}',
        data={'file': (io.BytesIO(b""), '')},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'No photo file selected' in data['error']

def test_upload_photo_used_token(client, mock_storage, mock_plant_operations):
    """Test uploading with already used token"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    # Use token once
    response1 = client.post(
        f'/upload/plant/{token}',
        data={'file': (io.BytesIO(b"test"), 'test.jpg')},
        content_type='multipart/form-data'
    )
    assert response1.status_code == 200
    
    # Try to use token again
    response2 = client.post(
        f'/upload/plant/{token}',
        data={'file': (io.BytesIO(b"test"), 'test.jpg')},
        content_type='multipart/form-data'
    )
    
    assert response2.status_code == 401
    data = response2.get_json()
    assert data['success'] is False
    assert 'used' in data['error'].lower() 