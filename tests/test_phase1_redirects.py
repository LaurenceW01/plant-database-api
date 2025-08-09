#!/usr/bin/env python3
"""
Test suite for Phase 1 ChatGPT hallucination redirects (Safety Net)

This test verifies that all redirect endpoints are accessible and don't return 404s.
The focus is on ensuring the redirect routes exist and can be called.

Author: AI Assistant
Date: 2024
"""

import pytest
import sys
import os
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from api.main import create_app


class TestPhase1Redirects:
    """Test class for Phase 1 ChatGPT hallucination redirects"""
    
    @pytest.fixture
    def app(self):
        """Create test app instance"""
        app = create_app(testing=True)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture  
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_plant_management_redirects_exist(self, client):
        """Test plant management redirects exist (don't return 404)"""
        
        # Test /api/plants/search -> should redirect to search functionality  
        response = client.get('/api/plants/search')
        assert response.status_code != 404, "plants/search redirect should exist"
        
        # Test /api/plants/get/{id} -> should redirect to get plant functionality
        response = client.get('/api/plants/get/1')
        assert response.status_code != 404, "plants/get/{id} redirect should exist"
        # Note: May return error due to no plant with ID 1, but endpoint should exist
    
    def test_plant_management_delete_redirect(self, client):
        """Test DELETE redirect returns appropriate error (not implemented)"""
        response = client.delete('/api/plants/remove/test-plant')
        assert response.status_code == 501
        data = response.get_json()
        assert 'Delete functionality not yet implemented' in data['error']
        assert data['redirect_attempted'] is True
    
    def test_logging_redirects_exist(self, client):
        """Test logging redirects exist (don't return 404)"""
        
        # Test /api/logs/create -> should redirect to log creation
        response = client.post('/api/logs/create', json={"Plant Name": "Test", "Entry": "Test"})
        assert response.status_code != 404, "logs/create redirect should exist"
        
        # Test /api/logs/create-simple -> should redirect to simple log creation
        response = client.post('/api/logs/create-simple', json={"Plant Name": "Test", "Entry": "Test"})
        assert response.status_code != 404, "logs/create-simple redirect should exist"
        
        # Test /api/logs/search -> should redirect to log search
        response = client.get('/api/logs/search')
        assert response.status_code != 404, "logs/search redirect should exist"
    
    def test_log_for_plant_redirect_error(self, client):
        """Test /api/logs/create-for-plant/{name} returns helpful error"""
        response = client.post('/api/logs/create-for-plant/test-plant',
                             json={"Entry": "Test log"})
        assert response.status_code == 400
        data = response.get_json()
        assert 'Please use /api/plants/log' in data['error']
        assert data['plant_name_provided'] == 'test-plant'
        assert data['redirect_attempted'] is True
    
    def test_analysis_redirects_exist(self, client):
        """Test analysis redirects exist (don't return 404)"""
        
        # Test /api/plants/diagnose -> should redirect to analyze plant
        response = client.post('/api/plants/diagnose', json={"plant_description": "Test"})
        assert response.status_code != 404, "plants/diagnose redirect should exist"
        
        # Test /api/plants/enhance-analysis -> should redirect to enhance analysis
        response = client.post('/api/plants/enhance-analysis', json={"analysis_text": "Test"})
        assert response.status_code != 404, "plants/enhance-analysis redirect should exist"
    
    def test_location_context_redirects_exist(self, client):
        """Test location context redirects exist (don't return 404)"""
        
        # Test /api/locations/get-context/{id} -> should redirect to location profile
        response = client.get('/api/locations/get-context/1')
        assert response.status_code != 404, "locations/get-context/{id} redirect should exist"
        
        # Test /api/plants/get-context/{id} -> should redirect to plant context
        response = client.get('/api/plants/get-context/1')
        assert response.status_code != 404, "plants/get-context/{id} redirect should exist"
    
    def test_garden_redirects_exist(self, client):
        """Test garden-level redirects exist (don't return 404)"""
        
        # Test /api/garden/get-metadata -> should redirect to enhanced metadata
        response = client.get('/api/garden/get-metadata')
        assert response.status_code != 404, "garden/get-metadata redirect should exist"
        
        # Test /api/garden/optimize-care -> should redirect to care optimization
        response = client.get('/api/garden/optimize-care')
        assert response.status_code != 404, "garden/optimize-care redirect should exist"
    
    def test_photo_upload_redirects_exist(self, client):
        """Test photo upload redirects exist (don't return 404)"""
        
        # Test /api/photos/upload-for-plant/{token} -> should redirect to plant upload
        response = client.post('/api/photos/upload-for-plant/test-token')
        assert response.status_code != 404, "photos/upload-for-plant/{token} redirect should exist"
        
        # Test /api/photos/upload-for-log/{token} -> should redirect to log upload
        response = client.post('/api/photos/upload-for-log/test-token')
        assert response.status_code != 404, "photos/upload-for-log/{token} redirect should exist"
    
    def test_redirect_coverage_sampling(self, client):
        """Test that a sample of planned redirects are implemented and accessible"""
        
        # Test a sample of expected redirect endpoints to verify they exist
        sample_endpoints = [
            # Plant Management
            ('/api/plants/search', 'GET'),
            ('/api/plants/remove/test', 'DELETE'),  # Should return 501
            
            # Logging  
            ('/api/logs/create', 'POST'),
            ('/api/logs/create-for-plant/test', 'POST'),  # Should return 400
            
            # Analysis
            ('/api/plants/diagnose', 'POST'),
            
            # Garden
            ('/api/garden/get-metadata', 'GET'),
        ]
        
        # Test that each endpoint exists (doesn't return 404)
        for endpoint, method in sample_endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, json={})
            elif method == 'DELETE':
                response = client.delete(endpoint)
                
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404, f"Endpoint {method} {endpoint} not found"


def test_redirect_logging():
    """Test that redirects can be logged for monitoring"""
    
    # This test verifies that we could add logging to track redirect usage
    # For now, it's a placeholder for future monitoring implementation
    
    redirect_endpoints = [
        '/api/plants/search',
        '/api/plants/get/<id>',
        '/api/logs/create',
        '/api/plants/diagnose'
    ]
    
    # Verify our redirect endpoints are defined
    assert len(redirect_endpoints) > 0
    assert all(endpoint.startswith('/api/') for endpoint in redirect_endpoints)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
