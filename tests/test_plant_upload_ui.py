"""
Tests for plant photo upload UI components.
"""

import pytest
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

@pytest.fixture(autouse=True)
def clear_token_storage():
    """Clear token storage before each test"""
    _token_storage.clear()
    yield
    _token_storage.clear()

def test_serve_upload_page_valid_token(client):
    """Test serving upload page with valid token"""
    # Generate valid token
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    # Get upload page
    response = client.get(f'/upload/plant/{token}')
    
    assert response.status_code == 200
    assert b'Upload Plant Photo' in response.data
    assert b'Take Photo' in response.data
    assert b'Choose from Gallery' in response.data

def test_serve_upload_page_invalid_token(client):
    """Test serving upload page with invalid token"""
    response = client.get('/upload/plant/invalid_token')
    
    assert response.status_code == 401
    assert b'Invalid Upload Token' in response.data
    assert b'Invalid or expired token' in response.data

def test_serve_upload_page_wrong_token_type(client):
    """Test serving upload page with log token"""
    # Generate log token
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="log_upload",
        log_id="LOG-123"
    )
    
    # Get upload page
    response = client.get(f'/upload/plant/{token}')
    
    assert response.status_code == 400
    assert b'Invalid Token Type' in response.data
    assert b'not for plant photo uploads' in response.data

def test_get_token_info_valid(client):
    """Test getting token info with valid token"""
    # Generate valid token
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    # Get token info
    response = client.get(f'/api/upload/info/{token}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['plant_name'] == "Test Plant"
    assert data['plant_id'] == "PLANT-123"
    assert data['operation'] == "add"
    assert data['token_type'] == "plant_upload"

def test_get_token_info_invalid(client):
    """Test getting token info with invalid token"""
    response = client.get('/api/upload/info/invalid_token')
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid' in data['error']

def test_get_token_info_wrong_type(client):
    """Test getting token info with log token"""
    # Generate log token
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="log_upload",
        log_id="LOG-123"
    )
    
    # Get token info
    response = client.get(f'/api/upload/info/{token}')
    
    assert response.status_code == 200  # Still returns info, UI handles type check
    data = response.get_json()
    assert data['success'] is True
    assert data['token_type'] == "log_upload" 