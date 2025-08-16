"""
Advanced Query Parser Module

MongoDB-style JSON query parser for complex plant database filtering.
Supports multi-table queries across plants, locations, and containers with
comprehensive operator support and field validation.

Author: Plant Database API
Created: Advanced Filtering System Implementation
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import re
from models.field_config import (
    get_canonical_field_name, 
    get_all_field_names,
    is_valid_field,
    FIELD_NAMES
)

# Set up logging for this module
logger = logging.getLogger(__name__)

# Define supported query operators with their functions
SUPPORTED_OPERATORS = {
    '$eq': 'equals',
    '$ne': 'not_equals', 
    '$in': 'in_array',
    '$nin': 'not_in_array',
    '$gt': 'greater_than',
    '$gte': 'greater_than_equal',
    '$lt': 'less_than',
    '$lte': 'less_than_equal',
    '$regex': 'regex_match',
    '$exists': 'field_exists',
    '$contains': 'substring_match'
}

# Define valid table names for multi-table queries
VALID_TABLES = ['plants', 'locations', 'containers']

# Define table field mappings for validation
TABLE_FIELD_MAPPINGS = {
    'plants': FIELD_NAMES,  # From field_config.py
    'locations': [
        'location_id', 'location_name', 'morning_sun_hours', 
        'afternoon_sun_hours', 'evening_sun_hours', 'total_sun_hours',
        'shade_pattern', 'microclimate_conditions'
    ],
    'containers': [
        'container_id', 'plant_id', 'location_id', 'container_type',
        'container_size', 'container_material'
    ]
}

class QueryParseError(Exception):
    """Custom exception for query parsing errors"""
    pass

class AdvancedQueryParser:
    """
    MongoDB-style query parser for advanced plant database filtering.
    
    Supports complex queries across plants, locations, and containers tables
    with comprehensive operator support and field validation.
    """
    
    def __init__(self):
        """Initialize the query parser with field mappings and operator definitions"""
        self.supported_operators = SUPPORTED_OPERATORS
        self.valid_tables = VALID_TABLES
        self.table_fields = TABLE_FIELD_MAPPINGS
        
    def parse_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate a complete query request.
        
        Args:
            query_data (Dict): Complete query request with filters, options, etc.
            
        Returns:
            Dict: Parsed and validated query structure
            
        Raises:
            QueryParseError: If query structure or filters are invalid
        """
        try:
            # Extract main components
            filters = query_data.get('filters', {})
            join_type = query_data.get('join', 'AND').upper()
            include_fields = query_data.get('include', ['plants', 'locations', 'containers'])
            response_format = query_data.get('response_format', 'summary')
            limit = query_data.get('limit', 50)
            sort_options = query_data.get('sort', [])
            
            # Validate join type
            if join_type not in ['AND', 'OR']:
                raise QueryParseError(f"Invalid join type: {join_type}. Must be 'AND' or 'OR'")
            
            # Validate response format
            valid_formats = ['summary', 'detailed', 'minimal', 'ids_only']
            if response_format not in valid_formats:
                raise QueryParseError(f"Invalid response_format: {response_format}. Must be one of: {valid_formats}")
            
            # Validate include fields
            for include_field in include_fields:
                if include_field not in ['plants', 'locations', 'containers', 'context']:
                    raise QueryParseError(f"Invalid include field: {include_field}")
            
            # Validate limit
            if not isinstance(limit, int) or limit < 1 or limit > 1000:
                raise QueryParseError("Limit must be an integer between 1 and 1000")
            
            # Parse and validate filters
            parsed_filters = self.parse_filters(filters)
            
            # Parse and validate sort options
            parsed_sort = self.parse_sort_options(sort_options)
            
            return {
                'filters': parsed_filters,
                'join_type': join_type,
                'include': include_fields,
                'response_format': response_format,
                'limit': limit,
                'sort': parsed_sort,
                'is_valid': True
            }
            
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            raise QueryParseError(f"Query parsing failed: {str(e)}")
    
    def parse_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate filter conditions for each table.
        
        Args:
            filters (Dict): Filter conditions organized by table
            
        Returns:
            Dict: Parsed and validated filters
            
        Raises:
            QueryParseError: If filters are invalid
        """
        parsed_filters = {}
        
        # Process filters for each table
        for table_name, table_filters in filters.items():
            if table_name not in self.valid_tables:
                raise QueryParseError(f"Invalid table name: {table_name}. Must be one of: {self.valid_tables}")
            
            # Parse individual field filters for this table
            parsed_table_filters = self.parse_table_filters(table_name, table_filters)
            parsed_filters[table_name] = parsed_table_filters
        
        return parsed_filters
    
    def parse_table_filters(self, table_name: str, table_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse filters for a specific table.
        
        Args:
            table_name (str): Name of the table being filtered
            table_filters (Dict): Filter conditions for this table
            
        Returns:
            List[Dict]: List of parsed filter conditions
            
        Raises:
            QueryParseError: If table filters are invalid
        """
        parsed_conditions = []
        
        for field_name, condition in table_filters.items():
            # Validate field name for this table
            valid_field = self.validate_field_for_table(table_name, field_name)
            
            # Parse the condition (can be a simple value or operator object)
            parsed_condition = self.parse_field_condition(table_name, valid_field, condition)
            parsed_conditions.append(parsed_condition)
        
        return parsed_conditions
    
    def validate_field_for_table(self, table_name: str, field_name: str) -> str:
        """
        Validate that a field name is valid for the specified table.
        
        Args:
            table_name (str): Name of the table
            field_name (str): Field name to validate
            
        Returns:
            str: Canonical field name
            
        Raises:
            QueryParseError: If field is not valid for the table
        """
        # For plants table, use existing field normalization
        if table_name == 'plants':
            canonical_field = get_canonical_field_name(field_name)
            if canonical_field is None:
                raise QueryParseError(f"Invalid field '{field_name}' for plants table")
            return canonical_field
        
        # For other tables, check against defined field lists
        table_fields = self.table_fields.get(table_name, [])
        
        # Normalize field name for comparison (handle common variations)
        normalized_field = field_name.lower().strip()
        normalized_table_fields = [f.lower() for f in table_fields]
        
        if normalized_field in normalized_table_fields:
            # Return the original case version
            for original_field in table_fields:
                if original_field.lower() == normalized_field:
                    return original_field
        
        # Also check for underscore variations
        underscore_field = normalized_field.replace(' ', '_').replace('-', '_')
        for original_field in table_fields:
            original_normalized = original_field.lower().replace(' ', '_').replace('-', '_')
            if original_normalized == underscore_field:
                return original_field
        
        raise QueryParseError(f"Invalid field '{field_name}' for {table_name} table. Valid fields: {table_fields}")
    
    def parse_field_condition(self, table_name: str, field_name: str, condition: Any) -> Dict[str, Any]:
        """
        Parse a condition for a specific field.
        
        Args:
            table_name (str): Name of the table
            field_name (str): Name of the field
            condition (Any): Condition value or operator object
            
        Returns:
            Dict: Parsed condition with operator and value
            
        Raises:
            QueryParseError: If condition is invalid
        """
        # If condition is a simple value, treat as equality
        if not isinstance(condition, dict):
            return {
                'table': table_name,
                'field': field_name,
                'operator': '$eq',
                'value': condition
            }
        
        # If condition is a dict, it should contain operators
        # Special case: Allow $regex with $options
        if len(condition) == 2 and '$regex' in condition and '$options' in condition:
            operator = '$regex'
            value = {
                'pattern': condition['$regex'],
                'options': condition['$options']
            }
        elif len(condition) != 1:
            raise QueryParseError(f"Field condition must contain exactly one operator, got: {list(condition.keys())}")
        else:
            operator, value = next(iter(condition.items()))
        
        # Validate operator
        if operator not in self.supported_operators:
            raise QueryParseError(f"Unsupported operator: {operator}. Supported operators: {list(self.supported_operators.keys())}")
        
        # Validate value for operator
        self.validate_operator_value(operator, value)
        
        return {
            'table': table_name,
            'field': field_name,
            'operator': operator,
            'value': value
        }
    
    def validate_operator_value(self, operator: str, value: Any) -> None:
        """
        Validate that a value is appropriate for the specified operator.
        
        Args:
            operator (str): Operator being used
            value (Any): Value to validate
            
        Raises:
            QueryParseError: If value is invalid for the operator
        """
        if operator in ['$in', '$nin']:
            if not isinstance(value, list):
                raise QueryParseError(f"Operator {operator} requires a list value, got: {type(value)}")
            if len(value) == 0:
                raise QueryParseError(f"Operator {operator} requires a non-empty list")
        
        elif operator in ['$gt', '$gte', '$lt', '$lte']:
            if not isinstance(value, (int, float)):
                try:
                    float(value)  # Try to convert to float
                except (ValueError, TypeError):
                    raise QueryParseError(f"Operator {operator} requires a numeric value, got: {type(value)}")
        
        elif operator == '$regex':
            if not isinstance(value, str):
                raise QueryParseError(f"Operator $regex requires a string value, got: {type(value)}")
            # Validate regex pattern
            try:
                re.compile(value)
            except re.error as e:
                raise QueryParseError(f"Invalid regex pattern: {value}. Error: {str(e)}")
        
        elif operator == '$exists':
            if not isinstance(value, bool):
                raise QueryParseError(f"Operator $exists requires a boolean value, got: {type(value)}")
    
    def parse_sort_options(self, sort_options: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Parse and validate sort options.
        
        Args:
            sort_options (List[Dict]): List of sort specifications
            
        Returns:
            List[Dict]: Validated sort options
            
        Raises:
            QueryParseError: If sort options are invalid
        """
        if not isinstance(sort_options, list):
            raise QueryParseError("Sort options must be a list")
        
        parsed_sort = []
        
        for sort_spec in sort_options:
            if not isinstance(sort_spec, dict):
                raise QueryParseError("Each sort specification must be a dictionary")
            
            if 'field' not in sort_spec:
                raise QueryParseError("Sort specification must include 'field'")
            
            field = sort_spec['field']
            direction = sort_spec.get('direction', 'asc').lower()
            
            if direction not in ['asc', 'desc']:
                raise QueryParseError(f"Sort direction must be 'asc' or 'desc', got: {direction}")
            
            # Note: Field validation would require knowing which table the field belongs to
            # For now, we'll validate fields during query execution
            
            parsed_sort.append({
                'field': field,
                'direction': direction
            })
        
        return parsed_sort

def parse_advanced_query(query_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to parse an advanced query.
    
    Args:
        query_data (Dict): Complete query request
        
    Returns:
        Dict: Parsed query structure
        
    Raises:
        QueryParseError: If query is invalid
    """
    parser = AdvancedQueryParser()
    return parser.parse_query(query_data)
