"""
Advanced Query Components Unit Tests

Unit tests for individual components of the advanced query system:
- Query Parser
- Query Operations  
- Query Formatter
- Query Executor

These tests can run without a full Flask app context.

Author: Plant Database API
Created: Advanced Filtering System Testing
"""

import pytest
import json
from unittest.mock import Mock, patch

# Import the components to test
from utils.advanced_query_parser import (
    AdvancedQueryParser, 
    parse_advanced_query, 
    QueryParseError
)
from utils.advanced_query_operations import (
    filter_table_data,
    evaluate_condition,
    get_field_value,
    apply_operator
)
from utils.advanced_query_formatter import (
    format_query_response,
    format_summary_response,
    format_minimal_response,
    format_detailed_response
)


class TestQueryParser:
    """Test the query parser component"""
    
    def test_basic_query_parsing(self):
        """Test basic query structure parsing"""
        query_data = {
            "filters": {
                "plants": {
                    "Plant Name": {"$eq": "Vinca"}
                }
            },
            "response_format": "summary"
        }
        
        parser = AdvancedQueryParser()
        result = parser.parse_query(query_data)
        
        assert result['is_valid'] is True
        assert result['response_format'] == 'summary'
        assert result['join_type'] == 'AND'  # Default
        assert 'plants' in result['filters']
    
    def test_operator_validation(self):
        """Test operator validation"""
        parser = AdvancedQueryParser()
        
        # Valid operator
        condition = parser.parse_field_condition('plants', 'Plant Name', {'$eq': 'test'})
        assert condition['operator'] == '$eq'
        assert condition['value'] == 'test'
        
        # Invalid operator should raise error
        with pytest.raises(QueryParseError):
            parser.parse_field_condition('plants', 'Plant Name', {'$invalid': 'test'})
    
    def test_field_validation(self):
        """Test field name validation"""
        parser = AdvancedQueryParser()
        
        # Valid plant field
        field = parser.validate_field_for_table('plants', 'Plant Name')
        assert field == 'Plant Name'
        
        # Valid plant field alias
        field = parser.validate_field_for_table('plants', 'name')
        assert field == 'Plant Name'
        
        # Invalid field should raise error
        with pytest.raises(QueryParseError):
            parser.validate_field_for_table('plants', 'InvalidField')
    
    def test_numeric_operator_validation(self):
        """Test numeric operator value validation"""
        parser = AdvancedQueryParser()
        
        # Valid numeric value
        parser.validate_operator_value('$gt', 5)
        parser.validate_operator_value('$gte', 5.5)
        parser.validate_operator_value('$lt', "10")  # String numbers should work
        
        # Invalid numeric value should raise error
        with pytest.raises(QueryParseError):
            parser.validate_operator_value('$gt', 'not_a_number')
    
    def test_regex_validation(self):
        """Test regex pattern validation"""
        parser = AdvancedQueryParser()
        
        # Valid regex
        parser.validate_operator_value('$regex', 'test.*pattern')
        
        # Invalid regex should raise error
        with pytest.raises(QueryParseError):
            parser.validate_operator_value('$regex', '[invalid')
    
    def test_array_operator_validation(self):
        """Test array operator validation"""
        parser = AdvancedQueryParser()
        
        # Valid array
        parser.validate_operator_value('$in', ['value1', 'value2'])
        
        # Invalid - not an array
        with pytest.raises(QueryParseError):
            parser.validate_operator_value('$in', 'not_an_array')
        
        # Invalid - empty array
        with pytest.raises(QueryParseError):
            parser.validate_operator_value('$in', [])


class TestQueryOperations:
    """Test query operations component"""
    
    def test_get_field_value(self):
        """Test field value extraction with different formats"""
        record = {
            'Plant Name': 'Vinca',
            'plant_name': 'Trailing Vinca',
            'care_notes': 'Water daily'
        }
        
        # Exact match
        assert get_field_value(record, 'Plant Name') == 'Vinca'
        
        # Underscore format
        assert get_field_value(record, 'plant_name') == 'Trailing Vinca'
        
        # Field not found
        assert get_field_value(record, 'NonExistent') is None
    
    def test_apply_operator_equals(self):
        """Test equality operator"""
        assert apply_operator('Vinca', '$eq', 'Vinca') is True
        assert apply_operator('Vinca', '$eq', 'vinca') is True  # Case insensitive
        assert apply_operator('Vinca', '$eq', 'Petunia') is False
        assert apply_operator('Vinca', '$ne', 'Petunia') is True
    
    def test_apply_operator_numeric(self):
        """Test numeric operators"""
        assert apply_operator('10', '$gt', 5) is True
        assert apply_operator('10', '$gt', 15) is False
        assert apply_operator('10.5', '$gte', 10.5) is True
        assert apply_operator('5', '$lt', 10) is True
        assert apply_operator('15', '$lte', 15) is True
    
    def test_apply_operator_in(self):
        """Test $in operator"""
        assert apply_operator('red', '$in', ['red', 'blue', 'green']) is True
        assert apply_operator('yellow', '$in', ['red', 'blue', 'green']) is False
        assert apply_operator('RED', '$in', ['red', 'blue']) is True  # Case insensitive
    
    def test_apply_operator_regex(self):
        """Test regex operator"""
        assert apply_operator('Trailing Vinca', '$regex', 'vinca') is True  # Case insensitive default
        assert apply_operator('Trailing Vinca', '$regex', '^Trailing') is True
        assert apply_operator('Trailing Vinca', '$regex', 'Petunia') is False
    
    def test_apply_operator_exists(self):
        """Test exists operator"""
        assert apply_operator('some value', '$exists', True) is True
        assert apply_operator('', '$exists', False) is True
        assert apply_operator(None, '$exists', False) is True
        assert apply_operator('some value', '$exists', False) is False
    
    def test_apply_operator_contains(self):
        """Test contains operator"""
        assert apply_operator('Water daily in morning', '$contains', 'daily') is True
        assert apply_operator('Water daily in morning', '$contains', 'DAILY') is True  # Case insensitive
        assert apply_operator('Water weekly', '$contains', 'daily') is False
    
    def test_evaluate_condition(self):
        """Test complete condition evaluation"""
        record = {
            'Plant Name': 'Trailing Vinca',
            'Light Requirements': 'Full Sun',
            'total_sun_hours': '8'
        }
        
        condition = {
            'field': 'Plant Name',
            'operator': '$regex',
            'value': 'vinca'
        }
        
        assert evaluate_condition(record, condition) is True
        
        numeric_condition = {
            'field': 'total_sun_hours',
            'operator': '$gte',
            'value': 6
        }
        
        assert evaluate_condition(record, numeric_condition) is True
    
    def test_filter_table_data_and_join(self):
        """Test filtering with AND join"""
        data = [
            {'Plant Name': 'Vinca', 'Light Requirements': 'Full Sun'},
            {'Plant Name': 'Hostas', 'Light Requirements': 'Shade'},
            {'Plant Name': 'Trailing Vinca', 'Light Requirements': 'Full Sun'}
        ]
        
        filters = [
            {
                'field': 'Light Requirements',
                'operator': '$eq',
                'value': 'Full Sun'
            },
            {
                'field': 'Plant Name',
                'operator': '$contains',
                'value': 'Vinca'
            }
        ]
        
        result = filter_table_data(data, filters, 'AND')
        
        # Should return both Vinca entries that have Full Sun
        assert len(result) == 2
        assert all('Vinca' in plant['Plant Name'] for plant in result)
        assert all(plant['Light Requirements'] == 'Full Sun' for plant in result)
    
    def test_filter_table_data_or_join(self):
        """Test filtering with OR join"""
        data = [
            {'Plant Name': 'Vinca', 'Light Requirements': 'Full Sun'},
            {'Plant Name': 'Hostas', 'Light Requirements': 'Shade'},
            {'Plant Name': 'Petunia', 'Light Requirements': 'Full Sun'}
        ]
        
        filters = [
            {
                'field': 'Plant Name',
                'operator': '$eq',
                'value': 'Vinca'
            },
            {
                'field': 'Light Requirements',
                'operator': '$eq',
                'value': 'Shade'
            }
        ]
        
        result = filter_table_data(data, filters, 'OR')
        
        # Should return Vinca (matches name) and Hostas (matches shade)
        assert len(result) == 2
        plant_names = [plant['Plant Name'] for plant in result]
        assert 'Vinca' in plant_names
        assert 'Hostas' in plant_names


class TestQueryFormatter:
    """Test query response formatter component"""
    
    def test_format_ids_only(self):
        """Test IDs only response format"""
        results = [
            {'plant_id': '1', 'plant_data': {'Plant Name': 'Vinca'}},
            {'plant_id': '2', 'plant_data': {'Plant Name': 'Petunia'}}
        ]
        
        response = format_query_response(results, 'ids_only', [])
        
        assert 'plant_ids' in response
        assert response['plant_ids'] == ['1', '2']
        assert response['total_matches'] == 2
    
    def test_format_minimal(self):
        """Test minimal response format"""
        results = [
            {
                'plant_id': '1',
                'plant_data': {'Plant Name': 'Vinca'},
                'location_data': {'location_name': 'Patio'}
            }
        ]
        
        response = format_query_response(results, 'minimal', [])
        
        assert 'plants' in response
        assert len(response['plants']) == 1
        
        plant = response['plants'][0]
        assert plant['plant_id'] == '1'
        assert plant['plant_name'] == 'Vinca'
        assert plant['location'] == 'Patio'
    
    def test_format_summary(self):
        """Test summary response format"""
        results = [
            {
                'plant_id': '1',
                'plant_data': {'plant_name': 'Vinca'},
                'containers': [{'container_size': 'small', 'container_material': 'plastic'}],
                'location_data': {'location_name': 'Patio'}
            },
            {
                'plant_id': '2',
                'plant_data': {'plant_name': 'Vinca'},
                'containers': [{'container_size': 'small', 'container_material': 'ceramic'}],
                'location_data': {'location_name': 'Garden'}
            }
        ]
        
        response = format_query_response(results, 'summary', [])
        
        assert response['total_matches'] == 2
        assert 'summary' in response
        assert 'by_plant_type' in response['summary']
        assert 'by_container' in response['summary']
        assert 'by_location' in response['summary']
        assert 'sample_plants' in response
        
        # Check aggregations
        assert response['summary']['by_plant_type']['Vinca'] == 2
        assert 'small plastic' in response['summary']['by_container']
        assert 'small ceramic' in response['summary']['by_container']
    
    def test_format_detailed(self):
        """Test detailed response format"""
        results = [
            {
                'plant_id': '1',
                'plant_data': {'plant_name': 'Vinca'},
                'location_data': {'location_name': 'Patio'},
                'containers': [{'container_type': 'pot'}]
            }
        ]
        
        response = format_query_response(results, 'detailed', ['plants', 'locations', 'containers'])
        
        assert 'plants' in response
        assert response['response_format'] == 'detailed'
        assert len(response['plants']) == 1
        
        plant_record = response['plants'][0]
        assert 'plant_data' in plant_record
        assert 'location_data' in plant_record
        assert 'containers' in plant_record


class TestIntegration:
    """Integration tests for component interaction"""
    
    def test_full_query_flow_mock(self):
        """Test the full query flow with mocked data"""
        
        # Mock query that should parse successfully
        query_data = {
            "filters": {
                "plants": {
                    "Plant Name": {"$regex": "vinca", "$options": "i"}
                },
                "containers": {
                    "container_size": {"$eq": "small"}
                }
            },
            "response_format": "summary",
            "limit": 10
        }
        
        # Test parsing
        parsed_query = parse_advanced_query(query_data)
        assert parsed_query['is_valid'] is True
        assert len(parsed_query['filters']) == 2
        
        # Test that we can extract filter conditions
        plant_filters = parsed_query['filters']['plants']
        assert len(plant_filters) == 1
        assert plant_filters[0]['operator'] == '$regex'
        assert plant_filters[0]['value'] == 'vinca'
        
        container_filters = parsed_query['filters']['containers']
        assert len(container_filters) == 1
        assert container_filters[0]['operator'] == '$eq'
        assert container_filters[0]['value'] == 'small'


def run_component_tests():
    """Run all component tests"""
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_component_tests()
