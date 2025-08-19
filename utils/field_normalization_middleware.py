#!/usr/bin/env python3
"""
Centralized Field Normalization Middleware for Phase 1 - AI-Friendly API Redesign

This module provides Flask decorators and middleware to automatically normalize
field names across all API endpoints without modifying individual functions.

Author: AI Assistant
Date: 2024
"""

from functools import wraps
from flask import request, g
import logging
from typing import Dict, Any, Optional


def normalize_request_middleware():
    """
    Flask before_request middleware to automatically normalize field names
    for all incoming requests with JSON data.
    
    This runs before every request and stores normalized data in Flask's g object.
    """
    print(f"normalize_request_middleware() START for {request.method} {request.path}")  # Debug print
    
    # Use silent=True to handle ChatGPT requests with Content-Type: application/json but no body
    if request.is_json and request.get_json(silent=True):
        print(f"Request has JSON data, proceeding with normalization...")  # Debug print
        from utils.compatibility_helpers import normalize_request_fields
        
        try:
            print(f"Getting JSON data...")  # Debug print
            original_data = request.get_json(silent=True)
            print(f"Got JSON data: {len(original_data)} fields")  # Debug print
            
            # DEBUG: Log the raw request data size and keys
            logging.info(f"RAW REQUEST DEBUG: Content-Length: {request.content_length}")
            logging.info(f"RAW REQUEST DEBUG: Content-Type: {request.content_type}")
            logging.info(f"RAW REQUEST DEBUG: request.get_json() returned {len(original_data)} fields: {list(original_data.keys())}")
            
            print(f"About to call normalize_request_fields()...")  # Debug print
            normalized_data = normalize_request_fields(original_data)
            print(f"normalize_request_fields() completed successfully")  # Debug print
            
            # Store both original and normalized data in Flask's g object
            g.original_request_data = original_data
            g.normalized_request_data = normalized_data
            
            # Log field transformations if they occurred
            if original_data != normalized_data:
                transformed_fields = {
                    k: v for k, v in zip(original_data.keys(), normalized_data.keys())
                    if k != v
                }
                if transformed_fields:
                    logging.info(f"MIDDLEWARE: Field normalization applied: {transformed_fields}")
                else:
                    logging.info(f"MIDDLEWARE: No field transformations needed")
            else:
                logging.info(f"MIDDLEWARE: No field normalization applied")
                    
        except Exception as e:
            print(f"EXCEPTION in field normalization: {e}")  # Debug print
            logging.warning(f"Field normalization failed: {e}")
            # Store original data as fallback
            g.original_request_data = request.get_json(silent=True)
            g.normalized_request_data = request.get_json(silent=True)
    else:
        print(f"No JSON data in request, skipping normalization")  # Debug print
    
    print(f"normalize_request_middleware() END for {request.method} {request.path}")  # Debug print


def get_normalized_field(field_name: str, default: Any = None) -> Any:
    """
    Get a field value from normalized request data with fallback to original data.
    
    Args:
        field_name: The field name to retrieve (supports multiple formats)
        default: Default value if field not found
        
    Returns:
        Field value from normalized data, original data, or default
    """
    # Try normalized data first
    if hasattr(g, 'normalized_request_data') and g.normalized_request_data:
        normalized_value = g.normalized_request_data.get(field_name)
        if normalized_value is not None:
            return normalized_value
    
    # Fallback to original data
    if hasattr(g, 'original_request_data') and g.original_request_data:
        original_value = g.original_request_data.get(field_name)
        if original_value is not None:
            return original_value
    
    # Try direct request access as final fallback
    if request.is_json:
        request_data = request.get_json() or {}
        direct_value = request_data.get(field_name)
        if direct_value is not None:
            return direct_value
    
    return default


def get_plant_name_field() -> Optional[str]:
    """
    Get plant name from request data using multiple possible field names.
    
    Returns:
        Plant name string or None if not found
    """
    # Try canonical underscore name first (new normalization target)
    plant_name = get_normalized_field('plant_name')
    if plant_name:
        return plant_name.strip()
    
    # Try other variations as fallback
    for field_name in ['plant_name', 'Plant Name', 'plantName', 'name', 'plant-name']:
        value = get_normalized_field(field_name)
        if value:
            return value.strip()
    
    return None


def with_field_normalization(func):
    """
    Decorator to ensure field normalization is applied to an endpoint.
    
    This decorator:
    1. Ensures normalized data is available via get_normalized_field()
    2. Provides helper methods for common field patterns
    3. Maintains backward compatibility
    
    Usage:
        @app.route('/api/plants', methods=['POST'])
        @with_field_normalization
        def add_plant():
            plant_name = get_plant_name_field()
            location = get_normalized_field('Location', '')
            # ... rest of function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ensure normalization has been applied
        if not hasattr(g, 'normalized_request_data'):
            normalize_request_middleware()
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper


class FieldNormalizationConfig:
    """Configuration for field normalization behavior"""
    
    # Field mappings for common patterns
    COMMON_FIELD_MAPPINGS = {
        'plant_name': 'plant_name',
        'plantName': 'plant_name', 
        'name': 'plant_name',
        'plant-name': 'plant_name',
        
        'location': 'location',
        'loc': 'location',
        'position': 'location',
        
        'entry': 'user_notes',
        'log_entry': 'user_notes',
        'logEntry': 'user_notes',
        'message': 'user_notes',
        'text': 'user_notes',
        
        'diagnosis': 'diagnosis',
        'treatment': 'treatment',
        'symptoms': 'symptoms',
        
        'light_requirements': 'light_requirements',
        'lightRequirements': 'light_requirements',
        'light': 'light_requirements',
        
        'water_requirements': 'watering_needs',
        'waterRequirements': 'watering_needs', 
        'water': 'watering_needs',
        'watering': 'watering_needs',
    }
    
    # Required fields for different endpoint types
    REQUIRED_FIELDS = {
        'add_plant': ['plant_name'],
        'create_log': ['plant_name'],
        'analyze_plant': ['plant_name'],
    }


def validate_required_fields(endpoint_type: str) -> Dict[str, Any]:
    """
    Validate that required fields are present for a specific endpoint type.
    
    Args:
        endpoint_type: Type of endpoint ('add_plant', 'create_log', etc.)
        
    Returns:
        Dictionary with validation results
    """
    required_fields = FieldNormalizationConfig.REQUIRED_FIELDS.get(endpoint_type, [])
    missing_fields = []
    
    for field in required_fields:
        value = get_normalized_field(field)
        if not value or (isinstance(value, str) and not value.strip()):
            missing_fields.append(field)
    
    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': missing_fields,
        'error_message': f"Missing required fields: {', '.join(missing_fields)}" if missing_fields else None
    }


def create_error_response_with_field_suggestions(error_message: str, missing_fields: list = None) -> Dict[str, Any]:
    """
    Create a helpful error response with field name suggestions.
    
    Args:
        error_message: Base error message
        missing_fields: List of missing field names
        
    Returns:
        Error response dictionary with suggestions
    """
    response = {
        'success': False,
        'error': error_message
    }
    
    if missing_fields:
        suggestions = {}
        for field in missing_fields:
            if field == 'plant_name':
                suggestions[field] = ["plant_name", "Plant Name", "plantName", "name"]
            elif field == 'user_notes':
                suggestions[field] = ["user_notes", "Entry", "entry", "log_entry", "message", "text"]
            elif field == 'location':
                suggestions[field] = ["location", "Location", "loc", "position"]
        
        if suggestions:
            response['field_suggestions'] = suggestions
            response['help'] = "Use any of the suggested field name formats above"
    
    return response


# Convenient field getters for common patterns
def get_field_with_fallbacks(canonical_name: str, *fallback_names) -> Optional[str]:
    """
    Get a field value trying canonical name first, then fallbacks.
    
    Args:
        canonical_name: The canonical field name (e.g., 'plant_name')
        *fallback_names: Alternative field names to try
        
    Returns:
        Field value or None
    """
    # Try canonical name first
    value = get_normalized_field(canonical_name)
    if value:
        return value.strip() if isinstance(value, str) else value
    
    # Try fallback names
    for fallback in fallback_names:
        value = get_normalized_field(fallback)
        if value:
            return value.strip() if isinstance(value, str) else value
    
    return None


# Pre-defined field getters for common use cases
def get_plant_name() -> Optional[str]:
    """Get plant name using all possible field variations"""
    return get_field_with_fallbacks('plant_name', 'Plant Name', 'plantName', 'name', 'plant-name')


def get_location() -> Optional[str]:
    """Get location using all possible field variations"""
    return get_field_with_fallbacks('location', 'Location', 'loc', 'position', 'place')


def get_entry() -> Optional[str]:
    """Get log entry using all possible field variations"""
    return get_field_with_fallbacks('user_notes', 'Entry', 'entry', 'log_entry', 'logEntry', 'message', 'text')


def get_diagnosis() -> Optional[str]:
    """Get diagnosis using all possible field variations"""
    return get_field_with_fallbacks('diagnosis', 'Diagnosis')


def get_treatment() -> Optional[str]:
    """Get treatment using all possible field variations"""
    return get_field_with_fallbacks('treatment', 'Treatment')


def get_symptoms() -> Optional[str]:
    """Get symptoms using all possible field variations"""
    return get_field_with_fallbacks('symptoms', 'Symptoms')


if __name__ == '__main__':
    # Example usage for testing
    print("=== Field Normalization Middleware ===")
    print("Use @with_field_normalization decorator on Flask routes")
    print("Access normalized fields with get_plant_name(), get_location(), etc.")
    print("Add normalize_request_middleware() to Flask app.before_request")
