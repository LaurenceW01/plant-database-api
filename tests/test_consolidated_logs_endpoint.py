"""
Test suite for the consolidated logs endpoint.

Tests Create, Read, Update, and Search operations through the unified /api/logs endpoint.
Includes backward compatibility testing for legacy endpoints.
"""

import pytest
import json
from datetime import datetime
from api.core.app_factory import create_app
from models.field_config import generate_log_id


class TestConsolidatedLogsEndpoint:
    """Test cases for the unified logs endpoint"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app(testing=True)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_create_log_operation(self, client):
        """Test log creation via consolidated endpoint"""
        # Test create operation
        response = client.get('/api/logs', query_string={
            'action': 'create',
            'plant_name': 'Test Plant for Logs',
            'diagnosis': 'Test diagnosis for consolidated endpoint',
            'user_notes': 'Test notes for unified logging',
            'symptoms_observed': 'Test symptoms',
            'treatment_recommendation': 'Test treatment'
        })
        
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['operation'] == 'create'
        assert 'log_id' in data
        assert 'upload_url' in data
        assert data['message']
        
        # Store log ID for later tests
        return data['log_id']
    
    def test_get_log_operation(self, client):
        """Test getting specific log entry"""
        # First create a log
        log_id = self.test_create_log_operation(client)
        
        # Test get operation
        response = client.get('/api/logs', query_string={
            'log_id': log_id
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['operation'] == 'get'
        assert 'log_entry' in data
        assert data['log_entry']['log_id'] == log_id
        assert data['log_entry']['plant_name'] == 'Test Plant for Logs'
        assert data['log_entry']['diagnosis'] == 'Test diagnosis for consolidated endpoint'
    
    def test_update_log_operation(self, client):
        """Test log update functionality"""
        # First create a log
        log_id = self.test_create_log_operation(client)
        
        # Test update operation
        response = client.get('/api/logs', query_string={
            'action': 'update',
            'log_id': log_id,
            'diagnosis': 'Updated diagnosis via consolidated endpoint',
            'user_notes': 'Updated notes - plant is recovering well',
            'treatment_recommendation': 'Continue current treatment for 2 more weeks'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['operation'] == 'update'
        assert data['log_id'] == log_id
        assert 'updated_fields' in data
        assert 'diagnosis' in data['updated_fields']
        assert 'user_notes' in data['updated_fields']
        assert 'treatment_recommendation' in data['updated_fields']
        assert 'last_updated' in data['updated_fields']  # Should auto-update timestamp
        
        # Verify the update by getting the log
        get_response = client.get('/api/logs', query_string={'log_id': log_id})
        get_data = json.loads(get_response.data)
        assert get_data['log_entry']['diagnosis'] == 'Updated diagnosis via consolidated endpoint'
        assert get_data['log_entry']['user_notes'] == 'Updated notes - plant is recovering well'
    
    def test_search_logs_operation(self, client):
        """Test log search functionality"""
        # Create some test logs with different content
        test_logs = [
            {'plant_name': 'Search Test Plant 1', 'diagnosis': 'Nitrogen deficiency detected', 'symptoms_observed': 'Yellow leaves'},
            {'plant_name': 'Search Test Plant 2', 'diagnosis': 'Pest issues found', 'symptoms_observed': 'Holes in leaves'},
            {'plant_name': 'Search Test Plant 1', 'diagnosis': 'Recovery progress', 'symptoms_observed': 'New green growth'}
        ]
        
        created_log_ids = []
        for log_data in test_logs:
            response = client.get('/api/logs', query_string={
                'action': 'create',
                **log_data
            })
            data = json.loads(response.data)
            created_log_ids.append(data['log_id'])
        
        # Test search by plant name
        response = client.get('/api/logs', query_string={
            'plant_name': 'Search Test Plant 1'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['operation'] == 'search'
        assert len(data['search_results']) == 2  # Should find 2 logs for Plant 1
        assert data['total_results'] == 2
        
        # Test search by query term
        response = client.get('/api/logs', query_string={
            'query': 'nitrogen'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['search_results']) >= 1  # Should find logs with "nitrogen"
        
        # Test search by symptoms
        response = client.get('/api/logs', query_string={
            'symptoms': 'yellow'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['search_results']) >= 1  # Should find logs with "yellow" symptoms
    
    def test_legacy_endpoint_redirects(self, client):
        """Test that legacy endpoints redirect to consolidated endpoint"""
        # Test /create redirect
        response = client.get('/api/logs/create', query_string={
            'plant_name': 'Legacy Test Plant',
            'diagnosis': 'Legacy test'
        })
        assert response.status_code == 301  # Redirect
        assert '/api/logs?action=create&' in response.location
        
        # Test /create-simple redirect
        response = client.get('/api/logs/create-simple', query_string={
            'plant_name': 'Legacy Simple Test',
            'user_notes': 'Simple test notes'
        })
        assert response.status_code == 301
        assert '/api/logs?action=create&' in response.location
        
        # Test /search redirect
        response = client.get('/api/logs/search', query_string={
            'plant_name': 'Legacy Search Test'
        })
        assert response.status_code == 301
        assert '/api/logs?' in response.location
    
    def test_error_handling(self, client):
        """Test error handling for various scenarios"""
        # Test update without log_id
        response = client.get('/api/logs', query_string={
            'action': 'update',
            'diagnosis': 'Test diagnosis'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'log_id is required' in data['error']
        
        # Test update without any fields
        response = client.get('/api/logs', query_string={
            'action': 'update',
            'log_id': 'LOG-NONEXISTENT-001'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No fields provided for update' in data['error']
        
        # Test get nonexistent log
        response = client.get('/api/logs', query_string={
            'log_id': 'LOG-NONEXISTENT-001'
        })
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error']
        
        # Test create without plant_name
        response = client.get('/api/logs', query_string={
            'action': 'create',
            'diagnosis': 'Test without plant name'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'plant_name is required' in data['error']
    
    def test_field_validation(self, client):
        """Test field validation and normalization"""
        # Test legacy field name support
        response = client.get('/api/logs', query_string={
            'action': 'create',
            'plant_name': 'Field Test Plant',
            'treatment': 'Legacy treatment field',  # Legacy name
            'symptoms': 'Legacy symptoms field'      # Legacy name
        })
        
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify the log was created with proper field names
        log_id = data['log_id']
        get_response = client.get('/api/logs', query_string={'log_id': log_id})
        get_data = json.loads(get_response.data)
        
        # Should be stored with canonical field names
        assert get_data['log_entry']['treatment_recommendation'] == 'Legacy treatment field'
        assert get_data['log_entry']['symptoms_observed'] == 'Legacy symptoms field'
    
    def test_partial_updates(self, client):
        """Test updating only specific fields"""
        # Create initial log
        log_id = self.test_create_log_operation(client)
        
        # Get initial values
        get_response = client.get('/api/logs', query_string={'log_id': log_id})
        initial_data = json.loads(get_response.data)['log_entry']
        
        # Update only diagnosis
        response = client.get('/api/logs', query_string={
            'action': 'update',
            'log_id': log_id,
            'diagnosis': 'Only diagnosis updated'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'diagnosis' in data['updated_fields']
        assert len(data['updated_fields']) == 2  # diagnosis + last_updated
        
        # Verify other fields remain unchanged
        get_response = client.get('/api/logs', query_string={'log_id': log_id})
        updated_data = json.loads(get_response.data)['log_entry']
        
        assert updated_data['diagnosis'] == 'Only diagnosis updated'
        assert updated_data['user_notes'] == initial_data['user_notes']  # Should be unchanged
        assert updated_data['symptoms_observed'] == initial_data['symptoms_observed']  # Should be unchanged
    
    def test_comprehensive_workflow(self, client):
        """Test a complete workflow: create, read, update, search"""
        # 1. Create a log entry
        create_response = client.get('/api/logs', query_string={
            'action': 'create',
            'plant_name': 'Workflow Test Plant',
            'diagnosis': 'Initial diagnosis: yellowing leaves',
            'symptoms_observed': 'Yellow edges on lower leaves',
            'user_notes': 'First observation - plant seems stressed',
            'follow_up_required': 'true',
            'follow_up_date': '2024-01-22'
        })
        
        create_data = json.loads(create_response.data)
        log_id = create_data['log_id']
        
        # 2. Read the log entry
        read_response = client.get('/api/logs', query_string={'log_id': log_id})
        read_data = json.loads(read_response.data)
        
        assert read_data['log_entry']['follow_up_required'] == 'TRUE'
        assert read_data['log_entry']['follow_up_date'] == '2024-01-22'
        
        # 3. Update with follow-up observations
        update_response = client.get('/api/logs', query_string={
            'action': 'update',
            'log_id': log_id,
            'diagnosis': 'Follow-up: Improvement noted after fertilizer application',
            'user_notes': 'New green growth visible, yellow leaves dropping naturally',
            'follow_up_required': 'false'
        })
        
        update_data = json.loads(update_response.data)
        assert 'follow_up_required' in update_data['updated_fields']
        
        # 4. Search for this log
        search_response = client.get('/api/logs', query_string={
            'query': 'fertilizer application'
        })
        
        search_data = json.loads(search_response.data)
        found_log = next((log for log in search_data['search_results'] if log['log_id'] == log_id), None)
        assert found_log is not None
        assert 'fertilizer application' in found_log['diagnosis']


class TestLogUpdateFunctionality:
    """Specific tests for the new update functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app(testing=True)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_update_all_updateable_fields(self, client):
        """Test updating all possible fields"""
        # Create initial log
        response = client.get('/api/logs', query_string={
            'action': 'create',
            'plant_name': 'Update All Fields Test Plant',
            'diagnosis': 'Initial diagnosis',
            'symptoms_observed': 'Initial symptoms',
            'user_notes': 'Initial notes',
            'treatment_recommendation': 'Initial treatment',
            'log_title': 'Initial title',
            'location': 'Initial location',
            'follow_up_required': 'false',
            'follow_up_date': ''
        })
        
        data = json.loads(response.data)
        log_id = data['log_id']
        
        # Update all fields
        update_response = client.get('/api/logs', query_string={
            'action': 'update',
            'log_id': log_id,
            'plant_name': 'Updated Plant Name',
            'diagnosis': 'Updated diagnosis - plant is recovering',
            'symptoms_observed': 'Updated symptoms - new growth visible',
            'user_notes': 'Updated notes - significant improvement',
            'treatment_recommendation': 'Updated treatment - continue current care',
            'log_title': 'Updated title - Recovery Progress',
            'location': 'Updated location - moved to sunny spot',
            'follow_up_required': 'true',
            'follow_up_date': '2024-02-01'
        })
        
        assert update_response.status_code == 200
        update_data = json.loads(update_response.data)
        
        # Check that all fields were updated
        expected_fields = [
            'plant_name', 'diagnosis', 'symptoms_observed', 'user_notes',
            'treatment_recommendation', 'log_title', 'location',
            'follow_up_required', 'follow_up_date', 'last_updated'
        ]
        
        for field in expected_fields:
            assert field in update_data['updated_fields'], f"Field {field} should be in updated_fields"
        
        # Verify all updates were applied
        get_response = client.get('/api/logs', query_string={'log_id': log_id})
        get_data = json.loads(get_response.data)['log_entry']
        
        assert get_data['plant_name'] == 'Updated Plant Name'
        assert get_data['diagnosis'] == 'Updated diagnosis - plant is recovering'
        assert get_data['follow_up_required'] == 'TRUE'
        assert get_data['follow_up_date'] == '2024-02-01'


if __name__ == '__main__':
    pytest.main([__file__])
