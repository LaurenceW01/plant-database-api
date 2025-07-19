"""
Tests for the upload token manager module.
"""

import pytest
from datetime import datetime, timedelta
from utils.upload_token_manager import (
    generate_upload_token,
    validate_upload_token,
    mark_token_used,
    cleanup_expired_tokens,
    get_token_info,
    get_active_token_count,
    _token_storage  # for testing only
)

@pytest.fixture(autouse=True)
def clear_token_storage():
    """Clear token storage before each test"""
    _token_storage.clear()
    yield
    _token_storage.clear()

def test_generate_log_upload_token():
    """Test generating a token for log entry photo upload"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="log_upload",
        log_id="LOG-123",
        expiration_hours=24
    )
    
    assert token is not None
    assert len(token) > 0
    assert token in _token_storage
    
    token_data = _token_storage[token]
    assert token_data['token_type'] == 'log_upload'
    assert token_data['plant_name'] == 'Test Plant'
    assert token_data['log_id'] == 'LOG-123'
    assert not token_data['used']
    assert 'expires_at' in token_data

def test_generate_plant_upload_token():
    """Test generating a token for plant photo upload"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add",
        expiration_hours=24
    )
    
    assert token is not None
    assert len(token) > 0
    assert token in _token_storage
    
    token_data = _token_storage[token]
    assert token_data['token_type'] == 'plant_upload'
    assert token_data['plant_name'] == 'Test Plant'
    assert token_data['plant_id'] == 'PLANT-123'
    assert token_data['operation'] == 'add'
    assert not token_data['used']
    assert 'expires_at' in token_data

def test_validate_valid_token():
    """Test validating a valid token"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="update"
    )
    
    is_valid, token_data, error = validate_upload_token(token)
    assert is_valid
    assert token_data is not None
    assert error is None
    assert token_data['plant_name'] == 'Test Plant'
    assert token_data['operation'] == 'update'

def test_validate_expired_token():
    """Test validating an expired token"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="log_upload",
        log_id="LOG-123",
        expiration_hours=24
    )
    
    # Manually expire the token
    _token_storage[token]['expires_at'] = (
        datetime.now() - timedelta(hours=1)
    ).isoformat()
    
    is_valid, token_data, error = validate_upload_token(token)
    assert not is_valid
    assert token_data is None
    assert "expired" in error.lower()
    assert token not in _token_storage  # Should be removed

def test_validate_used_token():
    """Test validating a used token"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    # Mark token as used
    mark_token_used(token, "127.0.0.1")
    
    is_valid, token_data, error = validate_upload_token(token)
    assert not is_valid
    assert token_data is None
    assert "used" in error.lower()

def test_missing_required_parameters():
    """Test error handling for missing required parameters"""
    # Test log upload without log_id
    with pytest.raises(ValueError) as exc:
        generate_upload_token(
            plant_name="Test Plant",
            token_type="log_upload"
        )
    assert "log_id is required" in str(exc.value)
    
    # Test plant upload without operation
    with pytest.raises(ValueError) as exc:
        generate_upload_token(
            plant_name="Test Plant",
            token_type="plant_upload",
            plant_id="PLANT-123"
        )
    assert "operation is required" in str(exc.value)

def test_cleanup_expired_tokens():
    """Test cleaning up expired tokens"""
    # Generate some tokens
    valid_token = generate_upload_token(
        plant_name="Test Plant 1",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    expired_token = generate_upload_token(
        plant_name="Test Plant 2",
        token_type="log_upload",
        log_id="LOG-123"
    )
    
    # Manually expire one token
    _token_storage[expired_token]['expires_at'] = (
        datetime.now() - timedelta(hours=1)
    ).isoformat()
    
    # Run cleanup
    cleaned = cleanup_expired_tokens()
    assert cleaned == 1
    assert valid_token in _token_storage
    assert expired_token not in _token_storage

def test_get_token_info():
    """Test retrieving token information"""
    token = generate_upload_token(
        plant_name="Test Plant",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="update"
    )
    
    info = get_token_info(token)
    assert info is not None
    assert info['plant_name'] == 'Test Plant'
    assert info['token_type'] == 'plant_upload'
    assert info['operation'] == 'update'

def test_active_token_count():
    """Test counting active tokens"""
    # Generate some tokens
    generate_upload_token(
        plant_name="Test Plant 1",
        token_type="plant_upload",
        plant_id="PLANT-123",
        operation="add"
    )
    
    expired_token = generate_upload_token(
        plant_name="Test Plant 2",
        token_type="log_upload",
        log_id="LOG-123"
    )
    
    # Manually expire one token
    _token_storage[expired_token]['expires_at'] = (
        datetime.now() - timedelta(hours=1)
    ).isoformat()
    
    count = get_active_token_count()
    assert count == 1  # Only one valid token should remain 