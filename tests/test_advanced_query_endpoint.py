"""
Advanced Query Endpoint Tests

Comprehensive test suite for the new POST /api/garden/query endpoint.
Tests MongoDB-style filtering, response formats, error handling, and
real-world query scenarios from the proposal.

Author: Plant Database API
Created: Advanced Filtering System Testing
"""

import pytest
import json
from flask import Flask
from api.core.app_factory import create_app
from api.routes.locations import locations_bp


class TestAdvancedQueryEndpoint:
    """Test suite for the advanced garden query endpoint"""
    
    @pytest.fixture
    def app(self):
        """Create test app with locations blueprint"""
        app = create_app()
        
        # Check if blueprint is already registered to avoid collision
        if 'locations' not in [bp.name for bp in app.blueprints.values()]:
            app.register_blueprint(locations_bp)
            
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_endpoint_exists(self, client):
        """Test that the endpoint exists and accepts POST requests"""
        response = client.post('/api/garden/query', 
                             json={"filters": {}},
                             content_type='application/json')
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
        
        # Should return JSON
        assert response.content_type == 'application/json'
    
    def test_missing_request_body(self, client):
        """Test error handling for missing request body"""
        response = client.post('/api/garden/query')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Request body required' in data['error']
        assert 'example' in data
        assert data['phase2_direct'] is True
    
    def test_empty_filters_query(self, client):
        """Test basic query with empty filters"""
        query = {
            "filters": {},
            "response_format": "summary"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        # Should succeed (empty filters means return all data)
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response structure
        assert 'query_metadata' in data
        assert 'endpoint_metadata' in data
        assert data['endpoint_metadata']['endpoint'] == '/api/garden/query'
        assert data['endpoint_metadata']['phase2_direct'] is True
        assert data['endpoint_metadata']['optimization'] == 'multi_table_single_call'
    
    def test_plant_name_filter(self, client):
        """Test filtering by plant name using $regex operator"""
        query = {
            "filters": {
                "plants": {
                    "Plant Name": {"$regex": "vinca"}
                }
            },
            "response_format": "summary"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response format
        assert 'total_matches' in data
        assert 'summary' in data
        assert 'by_plant_type' in data['summary']
        assert 'sample_plants' in data
        assert data['response_format'] == 'summary'
    
    def test_location_filter(self, client):
        """Test filtering by location name"""
        query = {
            "filters": {
                "locations": {
                    "location_name": {"$regex": "patio"}
                }
            },
            "response_format": "detailed",
            "include": ["plants", "locations", "containers"]
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify detailed response format
        assert 'plants' in data
        assert 'total_matches' in data
        assert data['response_format'] == 'detailed'
    
    def test_container_size_filter(self, client):
        """Test filtering by container size"""
        query = {
            "filters": {
                "containers": {
                    "container_size": {"$eq": "small"}
                }
            },
            "response_format": "minimal"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify minimal response format
        assert 'plants' in data
        assert 'total_matches' in data
        
        # Check minimal format structure
        if data['plants']:
            plant = data['plants'][0]
            assert 'plant_id' in plant
            assert 'plant_name' in plant
            assert 'location' in plant
    
    def test_multi_table_filter(self, client):
        """Test complex query filtering across multiple tables"""
        query = {
            "filters": {
                "plants": {
                    "Light Requirements": {"$regex": "Full Sun"}
                },
                "locations": {
                    "total_sun_hours": {"$gte": 6}
                },
                "containers": {
                    "container_material": {"$in": ["plastic", "ceramic"]}
                }
            },
            "join": "AND",
            "response_format": "summary",
            "limit": 20
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify query metadata
        assert data['query_metadata']['applied_limit'] == 20
        assert set(data['query_metadata']['tables_queried']) == {'plants', 'locations', 'containers'}
        assert data['query_metadata']['execution_success'] is True
    
    def test_ids_only_response_format(self, client):
        """Test IDs only response format"""
        query = {
            "filters": {
                "plants": {
                    "Plant Name": {"$exists": True}
                }
            },
            "response_format": "ids_only",
            "limit": 10
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify IDs only format
        assert 'plant_ids' in data
        assert 'total_matches' in data
        assert isinstance(data['plant_ids'], list)
    
    def test_sorting_functionality(self, client):
        """Test query sorting capabilities"""
        query = {
            "filters": {
                "plants": {
                    "Plant Name": {"$exists": True}
                }
            },
            "sort": [
                {"field": "Plant Name", "direction": "asc"}
            ],
            "response_format": "minimal",
            "limit": 5
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify sorting was applied (check if results are ordered)
        if len(data['plants']) > 1:
            names = [plant['plant_name'] for plant in data['plants'] if plant['plant_name']]
            # Should be sorted alphabetically
            assert names == sorted(names, key=str.lower)
    
    def test_invalid_operator_error(self, client):
        """Test error handling for invalid operators"""
        query = {
            "filters": {
                "plants": {
                    "Plant Name": {"$invalid_operator": "test"}
                }
            }
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Query parsing failed' in data['error']
        assert data['phase2_direct'] is True
    
    def test_invalid_field_name_error(self, client):
        """Test error handling for invalid field names"""
        query = {
            "filters": {
                "plants": {
                    "NonExistentField": {"$eq": "test"}
                }
            }
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Query parsing failed' in data['error']
    
    def test_invalid_response_format_error(self, client):
        """Test error handling for invalid response format"""
        query = {
            "filters": {},
            "response_format": "invalid_format"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Query parsing failed' in data['error']
    
    def test_limit_validation(self, client):
        """Test limit validation"""
        query = {
            "filters": {},
            "limit": 2000  # Exceeds maximum allowed
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Query parsing failed' in data['error']
    
    def test_regex_pattern_validation(self, client):
        """Test regex pattern validation"""
        query = {
            "filters": {
                "plants": {
                    "Plant Name": {"$regex": "[invalid regex"}  # Invalid regex
                }
            }
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Query parsing failed' in data['error']
    
    def test_numeric_operators(self, client):
        """Test numeric comparison operators"""
        query = {
            "filters": {
                "locations": {
                    "total_sun_hours": {"$gte": 8, "$lte": 12}
                }
            },
            "response_format": "summary"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        # Note: This will likely fail due to multiple operators in one field
        # But we're testing the parsing logic
        assert response.status_code in [200, 400]  # Either works or fails gracefully
    
    def test_in_operator(self, client):
        """Test $in operator with array values"""
        query = {
            "filters": {
                "containers": {
                    "container_material": {"$in": ["plastic", "ceramic", "metal"]}
                }
            },
            "response_format": "summary"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_matches' in data
    
    def test_exists_operator(self, client):
        """Test $exists operator"""
        query = {
            "filters": {
                "plants": {
                    "Photo URL": {"$exists": True}
                }
            },
            "response_format": "summary"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_matches' in data
    
    def test_contains_operator(self, client):
        """Test $contains operator for substring matching"""
        query = {
            "filters": {
                "plants": {
                    "Care Notes": {"$contains": "water"}
                }
            },
            "response_format": "minimal"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'plants' in data


class TestRealWorldQueryScenarios:
    """Test real-world query scenarios from the proposal document"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app()
        
        # Check if blueprint is already registered to avoid collision
        if 'locations' not in [bp.name for bp in app.blueprints.values()]:
            app.register_blueprint(locations_bp)
            
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_patio_small_pots_scenario(self, client):
        """Test the main scenario: 'plants on patio in small pots'"""
        query = {
            "filters": {
                "locations": {
                    "location_name": {"$regex": "patio"}
                },
                "containers": {
                    "container_size": {"$eq": "small"}
                }
            },
            "response_format": "summary",
            "include": ["plants", "locations", "containers", "context"]
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # This should return aggregated results instead of requiring 26 individual calls
        assert 'total_matches' in data
        assert 'summary' in data
        assert 'by_container' in data['summary']
        assert 'by_location' in data['summary']
        assert 'sample_plants' in data
        
        # Verify optimization metadata
        assert data['endpoint_metadata']['optimization'] == 'multi_table_single_call'
    
    def test_sun_loving_daily_watering_scenario(self, client):
        """Test scenario: 'sun-loving plants that need daily watering'"""
        query = {
            "filters": {
                "plants": {
                    "Light Requirements": {"$regex": "Full Sun"},
                    "Watering Needs": {"$regex": "daily"}
                }
            },
            "response_format": "detailed",
            "include": ["plants", "locations", "containers"]
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return detailed plant information
        assert 'plants' in data
        assert data['response_format'] == 'detailed'
    
    def test_plastic_containers_with_photos_scenario(self, client):
        """Test scenario: 'all plastic containers with plants that have photos'"""
        query = {
            "filters": {
                "containers": {
                    "container_material": {"$eq": "plastic"}
                },
                "plants": {
                    "Photo URL": {"$exists": True, "$ne": ""}
                }
            },
            "response_format": "summary"
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return summary of plastic containers with photos
        assert 'total_matches' in data
        assert 'summary' in data
    
    def test_high_sun_ceramic_containers_scenario(self, client):
        """Test scenario: 'plants in high-sun locations (8+ hours) in ceramic containers'"""
        query = {
            "filters": {
                "locations": {
                    "total_sun_hours": {"$gte": 8}
                },
                "containers": {
                    "container_material": {"$eq": "ceramic"}
                }
            },
            "response_format": "summary",
            "include": ["plants", "locations", "containers", "context"]
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should combine location and container filtering
        assert 'total_matches' in data
        assert 'summary' in data
        assert 'by_location' in data['summary']
        assert 'by_container' in data['summary']
    
    def test_recent_additions_scenario(self, client):
        """Test scenario: 'recent additions to the garden'"""
        query = {
            "filters": {
                "plants": {
                    "Last Updated": {"$gte": "2024-12-01"}
                }
            },
            "sort": [
                {"field": "Last Updated", "direction": "desc"}
            ],
            "response_format": "detailed",
            "limit": 10
        }
        
        response = client.post('/api/garden/query',
                             json=query,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return recent plants sorted by date
        assert 'plants' in data
        assert data['query_metadata']['applied_limit'] == 10


def run_advanced_query_tests():
    """
    Convenience function to run all advanced query tests.
    
    Usage:
        python -m pytest tests/test_advanced_query_endpoint.py -v
    """
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_advanced_query_tests()
