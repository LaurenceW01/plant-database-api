#!/usr/bin/env python3
"""
Compatibility Helpers for Phase 1 - AI-Friendly API Redesign

Simple utilities for maintaining backward compatibility during API transition.
These helpers can be easily integrated into existing endpoints.

Author: AI Assistant  
Date: 2024
"""

from typing import Dict, Any, Optional
from flask import request
import logging


def normalize_request_fields(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simple field normalization for common ChatGPT field variations.
    
    Args:
        data: Request data dictionary (can be None)
        
    Returns:
        Dictionary with normalized field names
    """
    if not data:
        return {}
    
    # Simple mapping for most common variations - mapping TO canonical underscore format
    field_map = {
        # Plant name variations
        'Plant Name': 'plant_name',
        'plantName': 'plant_name', 
        'name': 'plant_name',
        
        # Plant ID variations
        'Plant ID': 'plant_id',
        'plantId': 'plant_id',
        'id': 'plant_id',
        
        # Light variations
        'Light Requirements': 'light_requirements',
        'lightRequirements': 'light_requirements',
        'light': 'light_requirements',
        
        # Water variations  
        'Water Requirements': 'watering_needs',
        'Watering Needs': 'watering_needs',
        'waterRequirements': 'watering_needs',
        'water': 'watering_needs',
        'watering': 'watering_needs',
        
        # Soil variations
        'Soil Preferences': 'soil_preferences',
        'soilPreferences': 'soil_preferences',
        'soil': 'soil_preferences',
        
        # Location variations
        'Location ID': 'location_id',
        'locationId': 'location_id',
        'Location': 'location',
        
        # Container variations
        'Container ID': 'container_id',
        'containerId': 'container_id',
        
        # Log entry variations
        'Entry': 'user_notes',
        'entry': 'user_notes',
        'log_entry': 'user_notes',
        'logEntry': 'user_notes',
        'message': 'user_notes',
        'text': 'user_notes',
        'User Notes': 'user_notes',
        'user_notes': 'user_notes',
        
        # Date variations
        'Date': 'date',
        'timestamp': 'date',
        'log_date': 'date',
        
        # Description variations
        'Description': 'description',
        'desc': 'description',
        'notes': 'description',
        
        # Care notes
        'Care Notes': 'care_notes',
        'careNotes': 'care_notes',
    }
    
    normalized = {}
    for key, value in data.items():
        # Use mapped name if available, otherwise keep original
        normalized_key = field_map.get(key, key)
        normalized[normalized_key] = value
        
        # Log if transformation occurred
        if normalized_key != key:
            logging.debug(f"Field normalized: '{key}' -> '{normalized_key}'")
    
    return normalized


def ensure_required_fields(data: Dict[str, Any], 
                         required: list, 
                         endpoint_name: str = "unknown") -> Dict[str, str]:
    """
    Check for required fields and return helpful error messages.
    
    Args:
        data: Request data to validate
        required: List of required field names (canonical format)
        endpoint_name: Name of endpoint for error context
        
    Returns:
        Dictionary of validation errors (empty if all required fields present)
    """
    errors = {}
    missing_fields = []
    
    for field in required:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        errors['missing_fields'] = missing_fields
        errors['message'] = (f"Missing required fields for {endpoint_name}: "
                           f"{', '.join(missing_fields)}")
        
        # Provide helpful suggestions for common mistakes
        suggestions = []
        for missing in missing_fields:
            if missing == 'plant_name':
                suggestions.append("Try: 'Plant Name', 'plant_name', 'plantName', or 'name'")
            elif missing == 'user_notes':
                suggestions.append("Try: 'Entry', 'entry', 'User Notes', 'message', or 'text'")
            elif missing == 'location_id':
                suggestions.append("Try: 'Location ID', 'location_id', or 'locationId'")
        
        if suggestions:
            errors['field_suggestions'] = suggestions
    
    return errors


def handle_request_with_field_normalization(required_fields: Optional[list] = None):
    """
    Decorator to automatically normalize request fields for endpoints.
    
    Args:
        required_fields: List of required field names (canonical format)
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import jsonify
            
            # Get and normalize request data
            request_data = request.get_json() or {}
            normalized_data = normalize_request_fields(request_data)
            
            # Validate required fields if specified
            if required_fields:
                validation_errors = ensure_required_fields(
                    normalized_data, 
                    required_fields, 
                    func.__name__
                )
                if validation_errors:
                    return jsonify({
                        'success': False,
                        'error': validation_errors['message'],
                        'details': validation_errors
                    }), 400
            
            # Replace the original function's ability to access request data
            # by adding normalized_data as a keyword argument
            return func(*args, normalized_data=normalized_data, **kwargs)
            
        return wrapper
    return decorator


def add_compatibility_info_to_response(response_data: Dict[str, Any], 
                                     original_endpoint: str,
                                     redirect_from: Optional[str] = None) -> Dict[str, Any]:
    """
    Add compatibility information to API responses for monitoring.
    
    Args:
        response_data: Original response data
        original_endpoint: The actual endpoint that processed the request
        redirect_from: The endpoint that redirected to this one (if any)
        
    Returns:
        Response data with added compatibility metadata
    """
    # Only add compatibility info in testing mode or if explicitly requested
    if request.args.get('include_debug_info') == 'true' or \
       request.environ.get('TESTING'):
        
        compat_info = {
            'processed_by': original_endpoint,
            'api_version': 'phase1_compatibility',
        }
        
        if redirect_from:
            compat_info['redirected_from'] = redirect_from
            compat_info['redirect_note'] = (
                f"This request was automatically redirected from {redirect_from} "
                f"to {original_endpoint} for compatibility."
            )
        
        # Add compatibility info without overwriting existing data
        response_data['_compatibility_info'] = compat_info
    
    return response_data


def log_endpoint_usage(original_endpoint: str, 
                      accessed_via: Optional[str] = None,
                      request_fields: Optional[Dict[str, Any]] = None):
    """
    Log endpoint usage for monitoring redirect patterns.
    
    Args:
        original_endpoint: The actual endpoint that handled the request
        accessed_via: The URL path that was actually requested 
        request_fields: Normalized request fields for analysis
    """
    usage_info = {
        'endpoint': original_endpoint,
        'accessed_via': accessed_via or original_endpoint,
        'is_redirect': accessed_via != original_endpoint,
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'field_count': len(request_fields) if request_fields else 0
    }
    
    # Log with different levels based on whether it's a redirect
    if usage_info['is_redirect']:
        logging.info(f"API Redirect: {accessed_via} -> {original_endpoint}")
        logging.debug(f"Redirect details: {usage_info}")
    else:
        logging.debug(f"Direct API access: {usage_info}")


def create_redirect_response_with_logging(target_function,
                                       redirect_from: str,
                                       original_endpoint: str):
    """
    Create a redirect response with proper logging and compatibility info.
    
    Args:
        target_function: The function to call for the actual work
        redirect_from: The redirected endpoint path
        original_endpoint: The canonical endpoint path
        
    Returns:
        Response from target_function with added compatibility metadata
    """
    # Log the redirect
    log_endpoint_usage(original_endpoint, redirect_from)
    
    # Call the target function
    response = target_function()
    
    # Add compatibility info if response is JSON
    if isinstance(response, tuple) and len(response) >= 1:
        response_data, *rest = response
        if isinstance(response_data, dict):
            enhanced_response = add_compatibility_info_to_response(
                response_data, 
                original_endpoint, 
                redirect_from
            )
            return (enhanced_response, *rest)
    
    return response


def get_field_mapping_stats() -> Dict[str, Any]:
    """
    Get statistics about field name mappings for monitoring.
    
    Returns:
        Dictionary with mapping statistics
    """
    from .field_migration import FIELD_MAPPINGS
    
    canonical_fields = set(FIELD_MAPPINGS.values())
    total_mappings = len(FIELD_MAPPINGS)
    
    # Count variations per canonical field
    field_counts = {}
    for input_field, canonical_field in FIELD_MAPPINGS.items():
        field_counts[canonical_field] = field_counts.get(canonical_field, 0) + 1
    
    return {
        'total_field_mappings': total_mappings,
        'canonical_fields_count': len(canonical_fields),
        'avg_variations_per_field': total_mappings / len(canonical_fields),
        'max_variations': max(field_counts.values()),
        'most_varied_field': max(field_counts.keys(), key=lambda k: field_counts[k])
    }


# Convenience functions for common endpoint patterns
def handle_plant_request_fields(request_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle field normalization specifically for plant-related requests."""
    normalized = normalize_request_fields(request_data)
    
    # Ensure Plant Name is present for plant operations
    if not normalized.get('Plant Name') and any(key in normalized for key in ['id', 'plant_id', 'plantId']):
        # If we have an ID but no name, we might be doing a lookup
        pass  # Let the endpoint handle ID-based lookups
    
    return normalized


def handle_log_request_fields(request_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle field normalization specifically for log-related requests."""
    normalized = normalize_request_fields(request_data)
    
    # Ensure we have either Plant Name or Plant ID for log operations
    has_plant_identifier = any(normalized.get(field) for field in ['Plant Name', 'Plant ID'])
    
    if not has_plant_identifier:
        # Check if plant identifier is in a different format
        for key in normalized.keys():
            if 'plant' in key.lower() and normalized[key]:
                # Found a plant-related field, assume it's an identifier
                if 'id' in key.lower():
                    normalized['Plant ID'] = normalized[key]
                else:
                    normalized['Plant Name'] = normalized[key]
                break
    
    return normalized


if __name__ == '__main__':
    # Simple test of the compatibility helpers
    print("=== Compatibility Helpers Demo ===\n")
    
    # Test field normalization
    test_data = {
        'plant_name': 'Rose',
        'lightRequirements': 'Full Sun',
        'water': 'Daily'
    }
    
    print("Original:", test_data)
    normalized = normalize_request_fields(test_data)
    print("Normalized:", normalized)
    
    # Test validation
    errors = ensure_required_fields(normalized, ['Plant Name', 'Entry'], 'test_endpoint')
    print("Validation errors:", errors)
    
    # Test stats
    from utils.field_migration import FIELD_MAPPINGS
    if FIELD_MAPPINGS:  # Only if the import worked
        stats = get_field_mapping_stats()
        print("Field mapping stats:", stats)
