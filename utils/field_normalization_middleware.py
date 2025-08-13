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
    if request.is_json and request.get_json():
        from utils.compatibility_helpers import normalize_request_fields
        
        try:
            original_data = request.get_json()
            normalized_data = normalize_request_fields(original_data)
            
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
                    logging.info(f"🔄 MIDDLEWARE: Field normalization applied: {transformed_fields}")
                else:
                    logging.info(f"🔄 MIDDLEWARE: No field transformations needed")
            else:
                logging.info(f"🔄 MIDDLEWARE: No field normalization applied")
                    
        except Exception as e:
            logging.warning(f"Field normalization failed: {e}")
            # Store original data as fallback
            g.original_request_data = request.get_json()
            g.normalized_request_data = request.get_json()


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
    for field_name in ['Plant Name', 'plantName', 'name', 'plant-name']:
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
        'plant_name': 'Plant Name',
        'plantName': 'Plant Name', 
        'name': 'Plant Name',
        'plant-name': 'Plant Name',
        
        'location': 'Location',
        'loc': 'Location',
        'position': 'Location',
        
        'entry': 'Entry',
        'log_entry': 'Entry',
        'logEntry': 'Entry',
        'message': 'Entry',
        'text': 'Entry',
        
        'diagnosis': 'Diagnosis',
        'treatment': 'Treatment',
        'symptoms': 'Symptoms',
        
        'light_requirements': 'Light Requirements',
        'lightRequirements': 'Light Requirements',
        'light': 'Light Requirements',
        
        'water_requirements': 'Water Requirements',
        'waterRequirements': 'Water Requirements', 
        'water': 'Water Requirements',
        'watering': 'Water Requirements',
    }
    
    # Required fields for different endpoint types
    REQUIRED_FIELDS = {
        'add_plant': ['Plant Name'],
        'create_log': ['Plant Name'],
        'analyze_plant': ['plant_name'],  # Uses original format for now
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
            if field == 'Plant Name':
                suggestions[field] = ["Plant Name", "plant_name", "plantName", "name"]
            elif field == 'Entry':
                suggestions[field] = ["Entry", "entry", "log_entry", "message", "text"]
            elif field == 'Location':
                suggestions[field] = ["Location", "location", "loc", "position"]
        
        if suggestions:
            response['field_suggestions'] = suggestions
            response['help'] = "Use any of the suggested field name formats above"
    
    return response


# Convenient field getters for common patterns
def get_field_with_fallbacks(canonical_name: str, *fallback_names) -> Optional[str]:
    """
    Get a field value trying canonical name first, then fallbacks.
    
    Args:
        canonical_name: The canonical field name (e.g., 'Plant Name')
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
