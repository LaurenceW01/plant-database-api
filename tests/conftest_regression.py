"""
Regression Test Configuration and Fixtures

This module provides common test fixtures and configuration
for the comprehensive regression test suite.
"""

import pytest
import os
import logging
from typing import Generator
from flask import Flask
from werkzeug.test import Client
from werkzeug.wrappers import Response


@pytest.fixture(scope='session')
def test_app() -> Flask:
    """Create Flask app instance for testing"""
    # Set testing environment
    os.environ['TESTING'] = 'true'
    
    # Import and create app
    from api.main import create_app_instance
    app = create_app_instance(testing=True)
    
    # Configure for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    yield app
    
    # Cleanup
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture(scope='session')
def test_client(test_app: Flask) -> Client:
    """Create test client for making requests"""
    return Client(test_app, Response)


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Set up test environment and logging"""
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Disable external API calls during testing
    os.environ['TESTING'] = 'true'
    
    # Set test-specific configurations
    original_env = {}
    test_env_vars = {
        'API_KEY': 'test_api_key',
        'TESTING': 'true'
    }
    
    # Set test environment variables
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def sample_plant_data():
    """Sample plant data for testing"""
    return {
        "Plant Name": "Test Regression Plant",
        "Description": "Plant for comprehensive regression testing",
        "Location": "Test Garden Bed",
        "Light Requirements": "Full Sun",
        "Watering Needs": "Daily watering required",
        "Soil Preferences": "Well-draining soil",
        "Care Notes": "Monitor for pests during summer months"
    }


@pytest.fixture
def sample_log_data():
    """Sample log entry data for testing"""
    return {
        "Plant Name": "Test Plant for Logging",
        "Log Title": "Weekly Health Check",
        "User Notes": "Plant appears healthy with good growth",
        "Diagnosis": "Healthy - no issues observed",
        "Treatment": "Continue current care routine",
        "Symptoms": "None observed",
        "Follow-up Required": False
    }


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing"""
    return {
        "plant_name": "Test Plant for Analysis",
        "user_notes": "Testing AI-powered plant analysis functionality",
        "analysis_type": "general_care",
        "location": "Test Garden Location"
    }


@pytest.fixture
def sample_enhance_data():
    """Sample enhancement analysis data"""
    return {
        "gpt_analysis": "This plant shows healthy green foliage with strong stem structure",
        "plant_identification": "Test Plant Species",
        "user_question": "How is my plant's overall health?",
        "location": "Indoor Garden",
        "analysis_type": "health_assessment"
    }


# Marks for organizing tests
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "regression: mark test as part of regression suite"
    )
    config.addinivalue_line(
        "markers", "plant_management: mark test as plant management functionality"
    )
    config.addinivalue_line(
        "markers", "ai_analysis: mark test as AI analysis functionality"
    )
    config.addinivalue_line(
        "markers", "health_logging: mark test as health logging functionality"
    )
    config.addinivalue_line(
        "markers", "photo_upload: mark test as photo upload functionality"
    )
    config.addinivalue_line(
        "markers", "location_intelligence: mark test as location intelligence"
    )
    config.addinivalue_line(
        "markers", "weather_integration: mark test as weather integration"
    )
    config.addinivalue_line(
        "markers", "error_scenarios: mark test as error scenario testing"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add regression marker to all tests in regression suite
        if "test_regression" in item.nodeid:
            item.add_marker(pytest.mark.regression)
        
        # Add specific markers based on test name patterns
        test_name = item.name.lower()
        
        if any(keyword in test_name for keyword in ['plant', 'add', 'search', 'update', 'get']):
            item.add_marker(pytest.mark.plant_management)
        
        if any(keyword in test_name for keyword in ['diagnose', 'enhance', 'analysis']):
            item.add_marker(pytest.mark.ai_analysis)
        
        if any(keyword in test_name for keyword in ['log', 'create']):
            item.add_marker(pytest.mark.health_logging)
        
        if any(keyword in test_name for keyword in ['photo', 'upload']):
            item.add_marker(pytest.mark.photo_upload)
        
        if any(keyword in test_name for keyword in ['location', 'garden', 'metadata', 'optimize']):
            item.add_marker(pytest.mark.location_intelligence)
        
        if any(keyword in test_name for keyword in ['weather', 'forecast']):
            item.add_marker(pytest.mark.weather_integration)
        
        if any(keyword in test_name for keyword in ['error', 'invalid', 'malformed']):
            item.add_marker(pytest.mark.error_scenarios)


@pytest.fixture
def skip_external_apis():
    """Fixture to skip tests that require external APIs"""
    import pytest
    if os.getenv('SKIP_EXTERNAL_APIS', 'false').lower() == 'true':
        pytest.skip("Skipping test that requires external APIs")


# Test data validation helpers
def validate_plant_response(data: dict) -> bool:
    """Validate plant API response structure"""
    required_fields = ['success']
    return all(field in data for field in required_fields)


def validate_log_response(data: dict) -> bool:
    """Validate log API response structure"""
    if data.get('success'):
        return 'log_id' in data
    return 'error' in data


def validate_analysis_response(data: dict) -> bool:
    """Validate analysis API response structure"""
    if data.get('success'):
        return 'analysis' in data or 'enhanced_analysis' in data
    return 'error' in data


def validate_location_response(data: dict) -> bool:
    """Validate location API response structure"""
    return any(key in data for key in ['location_id', 'locations', 'care_profile', 'optimization_analysis'])


# Export validation helpers
__all__ = [
    'validate_plant_response',
    'validate_log_response', 
    'validate_analysis_response',
    'validate_location_response'
]
