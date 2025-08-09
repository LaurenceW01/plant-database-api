"""
Core middleware for Plant Database API

Handles field normalization, authentication, and request preprocessing.
"""

from flask import g, request
import logging

print("🚨 MIDDLEWARE MODULE IMPORTED!")  # Debug: Check if module is imported at all


def setup_middleware(app):
    """
    Setup all middleware for the Flask application.
    This replaces the middleware setup that was in register_routes().
    """
    
    print("🔧 SETTING UP MIDDLEWARE...")  # Debug print
    logging.info("🔧 Setting up middleware...")
    
    # ========================================
    # FIELD NORMALIZATION MIDDLEWARE
    # ========================================
    # Register centralized field normalization middleware
    try:
        from utils.field_normalization_middleware import normalize_request_middleware
        print("✅ IMPORTED NORMALIZATION MIDDLEWARE")  # Debug print
        
        @app.before_request
        def apply_field_normalization():
            """Apply field normalization to all incoming requests"""
            print(f"🔄 MIDDLEWARE CALLED: {request.method} {request.path}")  # Debug print
            if request.is_json:
                print(f"📝 Original JSON: {request.get_json()}")  # Debug print
            normalize_request_middleware()
            if hasattr(g, 'normalized_request_data'):
                print(f"✅ Normalized data: {g.normalized_request_data}")  # Debug print
            else:
                print(f"❌ No normalized data in g")  # Debug print
        
        print("✅ FIELD NORMALIZATION MIDDLEWARE REGISTERED")  # Debug print
        logging.info("✅ Field normalization middleware registered")
        
    except Exception as e:
        print(f"❌ MIDDLEWARE SETUP ERROR: {e}")  # Debug print
        logging.error(f"❌ Middleware setup error: {e}")
        raise


def require_api_key(func):
    """
    Decorator to require API key for protected endpoints.
    Moved from main.py for better organization.
    """
    from functools import wraps
    from flask import request, jsonify
    import os
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Skip API key check if in testing mode
        if os.getenv('TESTING', 'false').lower() == 'true':
            return func(*args, **kwargs)
        
        api_key = request.headers.get('x-api-key')
        expected_api_key = os.getenv('API_KEY')
        
        if not expected_api_key:
            # If no API key is configured, allow the request (development mode)
            return func(*args, **kwargs)
        
        if not api_key or api_key != expected_api_key:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        
        return func(*args, **kwargs)
    return decorated_function
