"""
Advanced Query Operations Module

Handles database filtering operations and field value comparisons
for the advanced query system.

Author: Plant Database API
Created: Advanced Filtering System Implementation
"""

from typing import Dict, List, Any, Optional
import logging
import re
from collections import defaultdict

# Import existing database operations (no modifications)
from utils.plant_database_operations import get_all_plants
from utils.locations_database_operations import get_all_locations, get_all_containers

logger = logging.getLogger(__name__)

def load_database_data() -> Dict[str, List[Dict]]:
    """
    Load all data from database using existing operations.
    
    Returns:
        Dict: All data organized by table name
    """
    try:
        plants_data = get_all_plants()
        locations_data = get_all_locations()
        containers_data = get_all_containers()
        
        logger.info(f"Loaded {len(plants_data)} plants, {len(locations_data)} locations, {len(containers_data)} containers")
        
        return {
            'plants': plants_data,
            'locations': locations_data,
            'containers': containers_data
        }
    except Exception as e:
        logger.error(f"Error loading database data: {e}")
        raise

def filter_table_data(table_data: List[Dict], filters: List[Dict], join_type: str) -> List[Dict]:
    """
    Filter data for a single table based on conditions.
    
    Args:
        table_data: Data for one table
        filters: Filter conditions for this table
        join_type: 'AND' or 'OR' for combining conditions
        
    Returns:
        List[Dict]: Filtered records
    """
    if not filters:
        return table_data
    
    filtered_records = []
    
    for record in table_data:
        if join_type == 'AND':
            if all(evaluate_condition(record, condition) for condition in filters):
                filtered_records.append(record)
        else:  # OR
            if any(evaluate_condition(record, condition) for condition in filters):
                filtered_records.append(record)
    
    return filtered_records

def evaluate_condition(record: Dict, condition: Dict) -> bool:
    """
    Evaluate a single filter condition against a record.
    
    Args:
        record: Database record to check
        condition: Filter condition
        
    Returns:
        bool: True if condition matches
    """
    field_name = condition['field']
    operator = condition['operator']
    expected_value = condition['value']
    
    actual_value = get_field_value(record, field_name)
    return apply_operator(actual_value, operator, expected_value)

def get_field_value(record: Dict, field_name: str) -> Any:
    """
    Get field value from record, handling different field name formats.
    
    Args:
        record: Database record
        field_name: Field name to retrieve
        
    Returns:
        Any: Field value or None if not found
    """
    # Try exact match first
    if field_name in record:
        return record[field_name]
    
    # Try lowercase underscore format
    underscore_field = field_name.lower().replace(' ', '_').replace('-', '_')
    if underscore_field in record:
        return record[underscore_field]
    
    # Try different case variations
    for key in record.keys():
        if key.lower().replace(' ', '_').replace('-', '_') == underscore_field:
            return record[key]
    
    return None

def apply_operator(actual_value: Any, operator: str, expected_value: Any) -> bool:
    """
    Apply a comparison operator to values.
    
    Args:
        actual_value: Value from database record
        operator: Comparison operator
        expected_value: Expected value from query
        
    Returns:
        bool: True if condition is satisfied
    """
    # Handle None/empty values
    if actual_value is None or actual_value == '':
        if operator == '$exists':
            return not expected_value
        return False
    
    actual_str = str(actual_value).strip()
    
    try:
        if operator == '$eq':
            return str(expected_value).strip().lower() == actual_str.lower()
        
        elif operator == '$ne':
            return str(expected_value).strip().lower() != actual_str.lower()
        
        elif operator == '$in':
            return any(str(val).strip().lower() == actual_str.lower() for val in expected_value)
        
        elif operator == '$nin':
            return not any(str(val).strip().lower() == actual_str.lower() for val in expected_value)
        
        elif operator in ['$gt', '$gte', '$lt', '$lte']:
            actual_num = float(actual_value)
            expected_num = float(expected_value)
            
            if operator == '$gt':
                return actual_num > expected_num
            elif operator == '$gte':
                return actual_num >= expected_num
            elif operator == '$lt':
                return actual_num < expected_num
            elif operator == '$lte':
                return actual_num <= expected_num
        
        elif operator == '$regex':
            pattern = expected_value
            flags = re.IGNORECASE  # Default case-insensitive
            
            if isinstance(expected_value, dict):
                # Support both formats: {"pattern": "x", "options": "i"} and {"$regex": "x", "$options": "i"} 
                pattern = expected_value.get('pattern', expected_value.get('$regex', expected_value))
                options = expected_value.get('options', expected_value.get('$options', ''))
                flags = re.IGNORECASE if options and 'i' in options.lower() else re.IGNORECASE
            
            # Handle case where pattern is still a dict (fallback)
            if isinstance(pattern, dict):
                pattern = str(pattern.get('$regex', pattern))
            
            return bool(re.search(str(pattern), actual_str, flags))
        
        elif operator == '$exists':
            has_value = actual_value is not None and actual_value != ''
            return has_value == expected_value
        
        elif operator == '$contains':
            return str(expected_value).strip().lower() in actual_str.lower()
        
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
            
    except (ValueError, TypeError) as e:
        logger.warning(f"Error applying operator {operator}: {e}")
        return False

def join_filtered_data(filtered_data: Dict[str, List[Dict]]) -> List[Dict]:
    """
    Join filtered data from multiple tables based on relationships.
    
    Args:
        filtered_data: Filtered data for each table
        
    Returns:
        List[Dict]: Joined records with related data
    """
    plants = filtered_data.get('plants', [])
    locations = filtered_data.get('locations', [])
    containers = filtered_data.get('containers', [])
    
    # Create lookup maps (ensure consistent string keys)
    locations_by_id = {str(loc.get('location_id', '')): loc for loc in locations}
    locations_by_name = {loc.get('location_name', '').strip().lower(): loc for loc in locations}
    containers_by_plant_id = defaultdict(list)
    
    # Group containers by plant_id (ensure consistent string keys)
    for container in containers:
        plant_id = container.get('plant_id', '')
        if plant_id:
            containers_by_plant_id[str(plant_id)].append(container)
    

    
    joined_results = []
    
    for plant in plants:
        plant_id = plant.get('id') or plant.get('ID') or plant.get('plant_id', '')
        plant_location = plant.get('location') or plant.get('Location', '')
        
        # Find related containers and location
        related_containers = containers_by_plant_id.get(str(plant_id), [])
        
        # Use containers table as authoritative source for plant locations
        related_location = None
        if related_containers:
            # Get location from first container (containers should all be in same location)
            container_location_id = related_containers[0].get('location_id', '')
            if container_location_id:
                related_location = locations_by_id.get(str(container_location_id))
            
            # Fallback: try location_name from container if location_id doesn't work
            if not related_location:
                container_location_name = related_containers[0].get('location_name', '').strip().lower()
                if container_location_name:
                    related_location = locations_by_name.get(container_location_name)
        
        # Create joined record
        joined_record = {
            'plant_data': plant,
            'containers': related_containers,
            'location_data': related_location,
            'plant_id': plant_id
        }
        
        # Include if we have required relationships or no filtering was done
        include_record = True
        
        if 'containers' in filtered_data and not related_containers:
            include_record = False
        
        if 'locations' in filtered_data and not related_location:
            include_record = False
        
        if include_record:
            joined_results.append(joined_record)
    
    return joined_results

def apply_sorting(results: List[Dict], sort_options: List[Dict]) -> List[Dict]:
    """
    Apply sorting to query results.
    
    Args:
        results: Query results to sort
        sort_options: Sort specifications
        
    Returns:
        List[Dict]: Sorted results
    """
    if not sort_options:
        return results
    
    try:
        for sort_spec in reversed(sort_options):
            field_name = sort_spec['field']
            direction = sort_spec['direction']
            reverse = (direction == 'desc')
            
            def get_sort_key(record):
                # Try plant data first, then location, then containers
                value = get_field_value(record.get('plant_data', {}), field_name)
                
                if value is None and record.get('location_data'):
                    value = get_field_value(record['location_data'], field_name)
                
                if value is None and record.get('containers'):
                    value = get_field_value(record['containers'][0], field_name)
                
                return str(value or '').lower()
            
            results.sort(key=get_sort_key, reverse=reverse)
        
        return results
        
    except Exception as e:
        logger.warning(f"Error applying sorting: {e}")
        return results
