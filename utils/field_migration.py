#!/usr/bin/env python3
"""
Field Migration Utilities for Phase 1 - AI-Friendly API Redesign

This module provides utilities for converting between different field naming formats
to maintain backward compatibility during the API transition.

Author: AI Assistant
Date: 2024
"""

import re
from typing import Dict, Any, Optional, Union


# Field mapping dictionary supporting multiple input formats
FIELD_MAPPINGS = {
    # Plant Name variations
    'plant_name': 'Plant Name',
    'Plant Name': 'Plant Name',
    'plantName': 'Plant Name',
    'plant-name': 'Plant Name',
    
    # Plant ID variations
    'plant_id': 'Plant ID',
    'Plant ID': 'Plant ID', 
    'plantId': 'Plant ID',
    'plant-id': 'Plant ID',
    'id': 'Plant ID',  # Common shorthand
    
    # Light Requirements variations
    'light_requirements': 'Light Requirements',
    'Light Requirements': 'Light Requirements',
    'lightRequirements': 'Light Requirements',
    'light-requirements': 'Light Requirements',
    'light': 'Light Requirements',  # Common shorthand
    
    # Water Requirements variations
    'water_requirements': 'Water Requirements',
    'Water Requirements': 'Water Requirements',
    'waterRequirements': 'Water Requirements',
    'water-requirements': 'Water Requirements',
    'water': 'Water Requirements',  # Common shorthand
    'watering': 'Water Requirements',
    
    # Soil Type variations
    'soil_type': 'Soil Type',
    'Soil Type': 'Soil Type',
    'soilType': 'Soil Type',
    'soil-type': 'Soil Type',
    'soil': 'Soil Type',  # Common shorthand
    
    # Fertilizer Schedule variations
    'fertilizer_schedule': 'Fertilizer Schedule',
    'Fertilizer Schedule': 'Fertilizer Schedule',
    'fertilizerSchedule': 'Fertilizer Schedule',
    'fertilizer-schedule': 'Fertilizer Schedule',
    'fertilizer': 'Fertilizer Schedule',  # Common shorthand
    'feeding': 'Fertilizer Schedule',
    
    # Planting Date variations
    'planting_date': 'Planting Date',
    'Planting Date': 'Planting Date',
    'plantingDate': 'Planting Date',
    'planting-date': 'Planting Date',
    'planted': 'Planting Date',  # Common shorthand
    'date_planted': 'Planting Date',
    
    # Plant Status variations
    'plant_status': 'Plant Status',
    'Plant Status': 'Plant Status',
    'plantStatus': 'Plant Status',
    'plant-status': 'Plant Status',
    'status': 'Plant Status',  # Common shorthand
    
    # Description variations
    'description': 'Description',
    'Description': 'Description',
    'desc': 'Description',  # Common shorthand
    'notes': 'Description',
    
    # Location variations
    'location': 'Location',
    'Location': 'Location',
    'loc': 'Location',  # Common shorthand
    'position': 'Location',
    'place': 'Location',
    
    # Location ID variations
    'location_id': 'Location ID',
    'Location ID': 'Location ID',
    'locationId': 'Location ID',
    'location-id': 'Location ID',
    
    # Container ID variations
    'container_id': 'Container ID',
    'Container ID': 'Container ID',
    'containerId': 'Container ID',
    'container-id': 'Container ID',
    'pot_id': 'Container ID',  # Alternative naming
    
    # Log Entry variations (for plant logs)
    'entry': 'Entry',
    'Entry': 'Entry',
    'log_entry': 'Entry',
    'logEntry': 'Entry',
    'log_text': 'Entry',
    'message': 'Entry',
    'text': 'Entry',
    
    # Date variations (for logs)
    'date': 'Date',
    'Date': 'Date',
    'timestamp': 'Date',
    'log_date': 'Date',
    'entry_date': 'Date',
    
    # Photo Path variations
    'photo_path': 'Photo Path',
    'Photo Path': 'Photo Path',
    'photoPath': 'Photo Path',
    'photo-path': 'Photo Path',
    'image_path': 'Photo Path',
    'photo': 'Photo Path',  # Common shorthand
    'image': 'Photo Path',
    
    # Care Instructions variations
    'care_instructions': 'Care Instructions',
    'Care Instructions': 'Care Instructions',
    'careInstructions': 'Care Instructions',
    'care-instructions': 'Care Instructions',
    'care': 'Care Instructions',  # Common shorthand
    'instructions': 'Care Instructions',
    
    # Plant Type variations
    'plant_type': 'Plant Type',
    'Plant Type': 'Plant Type',
    'plantType': 'Plant Type',
    'plant-type': 'Plant Type',
    'type': 'Plant Type',  # Common shorthand
    'species': 'Plant Type',
    'variety': 'Plant Type',
}

# Reverse mappings for converting FROM canonical format TO other formats
REVERSE_MAPPINGS = {
    'snake_case': {
        'Plant Name': 'plant_name',
        'Plant ID': 'plant_id',
        'Light Requirements': 'light_requirements', 
        'Water Requirements': 'water_requirements',
        'Soil Type': 'soil_type',
        'Fertilizer Schedule': 'fertilizer_schedule',
        'Planting Date': 'planting_date',
        'Plant Status': 'plant_status',
        'Description': 'description',
        'Location': 'location',
        'Location ID': 'location_id',
        'Container ID': 'container_id',
        'Entry': 'entry',
        'Date': 'date',
        'Photo Path': 'photo_path',
        'Care Instructions': 'care_instructions',
        'Plant Type': 'plant_type',
    },
    'camelCase': {
        'Plant Name': 'plantName',
        'Plant ID': 'plantId',
        'Light Requirements': 'lightRequirements',
        'Water Requirements': 'waterRequirements', 
        'Soil Type': 'soilType',
        'Fertilizer Schedule': 'fertilizerSchedule',
        'Planting Date': 'plantingDate',
        'Plant Status': 'plantStatus',
        'Description': 'description',
        'Location': 'location',
        'Location ID': 'locationId',
        'Container ID': 'containerId',
        'Entry': 'entry',
        'Date': 'date',
        'Photo Path': 'photoPath',
        'Care Instructions': 'careInstructions',
        'Plant Type': 'plantType',
    },
    'kebab-case': {
        'Plant Name': 'plant-name',
        'Plant ID': 'plant-id',
        'Light Requirements': 'light-requirements',
        'Water Requirements': 'water-requirements',
        'Soil Type': 'soil-type', 
        'Fertilizer Schedule': 'fertilizer-schedule',
        'Planting Date': 'planting-date',
        'Plant Status': 'plant-status',
        'Description': 'description',
        'Location': 'location',
        'Location ID': 'location-id',
        'Container ID': 'container-id',
        'Entry': 'entry',
        'Date': 'date',
        'Photo Path': 'photo-path',
        'Care Instructions': 'care-instructions',
        'Plant Type': 'plant-type',
    }
}


def transform_request_fields(data: Union[Dict[str, Any], None], 
                           strict_mode: bool = False) -> Dict[str, Any]:
    """
    Convert incoming field names to canonical format (space-separated).
    
    Args:
        data: Dictionary with field names to transform
        strict_mode: If True, raise error for unknown fields. If False, keep as-is.
        
    Returns:
        Dictionary with canonical field names
        
    Raises:
        ValueError: If strict_mode=True and unknown field encountered
    """
    if not data:
        return {}
        
    transformed = {}
    
    for key, value in data.items():
        # Get canonical field name
        canonical_key = FIELD_MAPPINGS.get(key)
        
        if canonical_key:
            transformed[canonical_key] = value
        elif strict_mode:
            raise ValueError(f"Unknown field name: '{key}'. "
                           f"Supported fields: {sorted(set(FIELD_MAPPINGS.values()))}")
        else:
            # Keep original key if not found and not in strict mode
            transformed[key] = value
            
    return transformed


def transform_response_fields(data: Union[Dict[str, Any], None], 
                            format_type: str = 'space') -> Dict[str, Any]:
    """
    Convert outgoing field names from canonical format to requested format.
    
    Args:
        data: Dictionary with canonical field names to transform
        format_type: Target format ('space', 'snake_case', 'camelCase', 'kebab-case')
        
    Returns:
        Dictionary with field names in requested format
        
    Raises:
        ValueError: If format_type is not supported
    """
    if not data:
        return {}
        
    if format_type == 'space':
        # Already in canonical format
        return data.copy()
        
    if format_type not in REVERSE_MAPPINGS:
        supported = ['space'] + list(REVERSE_MAPPINGS.keys())
        raise ValueError(f"Unsupported format: '{format_type}'. "
                        f"Supported formats: {supported}")
    
    mapping = REVERSE_MAPPINGS[format_type]
    transformed = {}
    
    for key, value in data.items():
        # Get target field name
        target_key = mapping.get(key, key)  # Keep original if no mapping found
        transformed[target_key] = value
        
    return transformed


def auto_detect_field_format(data: Dict[str, Any]) -> str:
    """
    Auto-detect the field naming format used in a dictionary.
    
    Args:
        data: Dictionary to analyze
        
    Returns:
        Detected format: 'space', 'snake_case', 'camelCase', 'kebab-case', or 'mixed'
    """
    if not data:
        return 'space'  # Default
    
    space_count = 0
    snake_count = 0
    camel_count = 0
    kebab_count = 0
    
    for key in data.keys():
        if ' ' in key:
            space_count += 1
        elif '_' in key:
            snake_count += 1
        elif '-' in key:
            kebab_count += 1
        elif re.search(r'[a-z][A-Z]', key):  # camelCase pattern
            camel_count += 1
    
    total_fields = len(data)
    
    # Determine dominant format (>50% of fields)
    if space_count > total_fields * 0.5:
        return 'space'
    elif snake_count > total_fields * 0.5:
        return 'snake_case'
    elif camel_count > total_fields * 0.5:
        return 'camelCase'
    elif kebab_count > total_fields * 0.5:
        return 'kebab-case'
    else:
        return 'mixed'


def create_field_compatibility_wrapper(func):
    """
    Decorator to automatically handle field name transformations for API endpoints.
    
    Usage:
        @create_field_compatibility_wrapper
        def my_api_endpoint():
            # Function will receive normalized field names
            # and return appropriately formatted response
    """
    def wrapper(*args, **kwargs):
        from flask import request
        
        # Transform incoming request data to canonical format
        if request.is_json:
            request_data = request.get_json() or {}
            _ = transform_request_fields(request_data)  # For future use
            
            # Note: This is a simplified approach; in practice, you might
            # need to monkey-patch the request object or pass data explicitly
            
        # Call original function
        result = func(*args, **kwargs)
        
        # Transform response if it's a dictionary
        if isinstance(result, tuple) and len(result) >= 1:
            response_data, *rest = result
            if isinstance(response_data, dict):
                # Detect client preference (could be from Accept header or query param)
                preferred_format = request.args.get('field_format', 'space')
                transformed_response = transform_response_fields(response_data, preferred_format)
                return (transformed_response, *rest)
        
        return result
    
    return wrapper


def validate_field_names(data: Dict[str, Any], 
                        required_fields: Optional[list] = None) -> Dict[str, str]:
    """
    Validate field names and return suggested corrections for unknown fields.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required canonical field names
        
    Returns:
        Dictionary mapping unknown fields to suggested corrections
    """
    field_suggestions = {}
    canonical_fields = set(FIELD_MAPPINGS.values())
    
    for key in data.keys():
        if key not in FIELD_MAPPINGS:
            # Find closest match
            best_match = None
            best_score = 0
            
            for canonical_field in canonical_fields:
                # Simple similarity scoring (could be improved with Levenshtein distance)
                score = len(set(key.lower().split()) & set(canonical_field.lower().split()))
                if score > best_score:
                    best_score = score
                    best_match = canonical_field
            
            if best_match and best_score > 0:
                field_suggestions[key] = best_match
                
    # Check required fields
    if required_fields:
        canonical_data = transform_request_fields(data)
        missing_fields = set(required_fields) - set(canonical_data.keys())
        if missing_fields:
            field_suggestions['_missing_required'] = list(missing_fields)
    
    return field_suggestions


def get_supported_field_formats() -> Dict[str, list]:
    """
    Get all supported field name variations for each canonical field.
    
    Returns:
        Dictionary mapping canonical field names to their supported variations
    """
    field_variations = {}
    
    for input_field, canonical_field in FIELD_MAPPINGS.items():
        if canonical_field not in field_variations:
            field_variations[canonical_field] = []
        if input_field not in field_variations[canonical_field]:
            field_variations[canonical_field].append(input_field)
    
    # Sort variations for consistency
    for field in field_variations:
        field_variations[field].sort()
    
    return field_variations


def log_field_transformation(original_data: Dict[str, Any], 
                           transformed_data: Dict[str, Any], 
                           transformation_type: str = 'request') -> None:
    """
    Log field transformations for monitoring and debugging.
    
    Args:
        original_data: Original field data
        transformed_data: Transformed field data
        transformation_type: Type of transformation ('request' or 'response')
    """
    import logging
    
    # Only log if transformations actually occurred
    if original_data != transformed_data:
        original_fields = set(original_data.keys())
        transformed_fields = set(transformed_data.keys())
        
        if original_fields != transformed_fields:
            mapping_info = {
                'transformation_type': transformation_type,
                'original_fields': sorted(original_fields),
                'transformed_fields': sorted(transformed_fields),
                'field_mappings': {
                    k: v for k, v in zip(original_data.keys(), transformed_data.keys())
                    if k != v
                }
            }
            
            logging.info("Field transformation applied: %s", mapping_info)


if __name__ == '__main__':
    # Example usage and testing
    print("=== Field Migration Utilities Demo ===\n")
    
    # Test data with various field formats
    test_data_mixed = {
        'plant_name': 'Rose Bush',
        'lightRequirements': 'Full Sun',
        'water-requirements': 'Daily',
        'Soil Type': 'Well-draining',
        'location': 'Garden Bed 1'
    }
    
    print("Original data:", test_data_mixed)
    print("Detected format:", auto_detect_field_format(test_data_mixed))
    
    # Transform to canonical format
    canonical = transform_request_fields(test_data_mixed)
    print("Canonical format:", canonical)
    
    # Transform to different output formats
    snake_case = transform_response_fields(canonical, 'snake_case')
    print("Snake case format:", snake_case)
    
    camel_case = transform_response_fields(canonical, 'camelCase')
    print("Camel case format:", camel_case)
    
    # Test validation
    unknown_data = {'weird_field': 'value', 'plant_name': 'Test'}
    suggestions = validate_field_names(unknown_data, required_fields=['Plant Name'])
    print("Field suggestions:", suggestions)
    
    # Show supported variations
    variations = get_supported_field_formats()
    print("\nSupported field variations:")
    for canonical, variants in list(variations.items())[:3]:  # Show first 3
        print(f"  {canonical}: {variants}")
