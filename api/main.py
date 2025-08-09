"""
Plant Database API - Main Application Entry Point (v2.3.0)

Modularized architecture with clean separation of concerns.
Routes are organized into blueprints by functional area.

Core business logic functions remain here for backward compatibility
while routes have been extracted to api/routes/ modules.
"""

import os
import logging
from functools import wraps
from flask import Flask, request, jsonify, render_template

# Import the app factory
from api.core.app_factory import create_app


# ========================================
# CORE BUSINESS LOGIC FUNCTIONS
# ========================================
# These functions are imported by the route modules

def require_api_key(func):
    """
    Decorator to require API key for protected endpoints.
    Used by route modules for authentication.
    """
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


def map_underscore_fields_to_canonical(data):
    """
    Map underscore field names to canonical format.
    Used for field normalization across the API.
    """
    # Import the field migration utility
    from utils.field_migration import transform_request_fields
    return transform_request_fields(data)


# ========================================
# CORE PLANT OPERATIONS
# ========================================
# These are the underlying business logic functions called by route modules

def add_plant():
    """Core plant addition logic called by the plants route module"""
    from utils.plant_operations import add_plant_api
    return add_plant_api()


def update_plant(id_or_name):
    """Core plant update logic called by the plants route module"""
    from utils.plant_operations import update_plant_api
    return update_plant_api(id_or_name)


def list_or_search_plants():
    """Core plant search logic called by the plants route module"""
    try:
        from utils.plant_operations import search_plants, get_all_plants
        
        # Get search parameters
        search_query = request.args.get('search', '').strip()
        location = request.args.get('location', '').strip()
        
        # Search plants
        if search_query:
            plants = search_plants(search_query)
            result = {'plants': plants, 'count': len(plants)}
        else:
            plants = get_all_plants()
            result = {'plants': plants, 'count': len(plants)}
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error searching plants: {e}")
        return jsonify({'error': str(e)}), 500


def get_plant_details(id_or_name):
    """Core plant details retrieval called by the plants route module"""
    try:
        from utils.plant_operations import find_plant_by_id_or_name
        
        # Find the plant
        plant_row, plant_list = find_plant_by_id_or_name(id_or_name)
        if plant_row is not None and plant_list:
            result = {'success': True, 'plant': plant_list[0] if plant_list else {}}
        else:
            result = {'success': False, 'error': 'Plant not found'}
         
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logging.error(f"Error getting plant details: {e}")
        return jsonify({'error': str(e)}), 500


# ========================================
# CORE LOG OPERATIONS
# ========================================

def create_plant_log():
    """Core plant log creation with multipart support (called by route modules)"""
    try:
        from utils.plant_log_operations import create_log_entry
        from utils.storage_client import upload_plant_photo, is_storage_available
        from utils.upload_token_manager import generate_upload_token
        
        # Get form data
        plant_name = request.form.get('plant_name', '').strip()
        user_notes = request.form.get('user_notes', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        treatment = request.form.get('treatment', '').strip()
        symptoms = request.form.get('symptoms', '').strip()
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'plant_name is required'}), 400
        
        # Handle file upload
        photo_url = ""
        raw_photo_url = ""
        
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            if is_storage_available():
                upload_result = upload_plant_photo(file, plant_name)
                photo_url = upload_result['photo_url']
                raw_photo_url = upload_result['raw_photo_url']
        
        # Create log entry
        result = create_log_entry(
            plant_name=plant_name,
            photo_url=photo_url,
            raw_photo_url=raw_photo_url,
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes
        )
        
        if result.get('success'):
            # Generate upload token
            upload_token = generate_upload_token(
                log_id=result['log_id'],
                plant_name=plant_name,
                token_type='log_upload',
                expiration_hours=24
            )
            
            upload_url = f"https://{request.host}/api/photos/upload-for-log/{upload_token}"
            
            return jsonify({
                **result,
                'upload_url': upload_url
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error creating plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def create_plant_log_simple():
    """Core simple log creation with JSON support (called by route modules)"""
    try:
        from utils.plant_log_operations import create_log_entry
        from utils.field_normalization_middleware import (
            get_plant_name, get_location, get_entry, get_diagnosis, 
            get_treatment, get_symptoms, get_normalized_field
        )
        from utils.upload_token_manager import generate_upload_token
        
        # Get normalized field values
        plant_name = get_plant_name()
        user_notes = get_normalized_field('User Notes') or get_normalized_field('user_notes', '')
        diagnosis = get_diagnosis() or ''
        treatment = get_treatment() or ''
        symptoms = get_symptoms() or ''
        location = get_location() or ''
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'Plant name is required'}), 400
        
        # Create log entry
        result = create_log_entry(
            plant_name=plant_name,
            photo_url="",
            raw_photo_url="",
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes,
            location=location
        )
        
        if result.get('success'):
            # Generate upload token
            upload_token = generate_upload_token(
                log_id=result['log_id'],
                plant_name=plant_name,
                token_type='log_upload',
                expiration_hours=24
            )
            
            upload_url = f"https://{request.host}/api/photos/upload-for-log/{upload_token}"
            
            return jsonify({
                **result,
                'upload_url': upload_url
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error creating simple plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def search_plant_logs():
    """Core log search logic called by route modules"""
    try:
        from utils.plant_log_operations import search_log_entries
        
        # Get search parameters
        plant_name = request.args.get('plant_name', '').strip()
        search_query = request.args.get('search', '').strip()
        
        result = search_log_entries(plant_name=plant_name, query=search_query)
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error searching logs: {e}")
        return jsonify({'error': str(e)}), 500


# ========================================
# CORE ANALYSIS OPERATIONS
# ========================================

def analyze_plant():
    """Core plant analysis logic called by analysis route module - OpenAI powered"""
    try:
        from utils.care_intelligence import analyze_plant_with_ai
        from utils.field_normalization_middleware import get_plant_name, get_normalized_field
        
        # Use field normalization to get data
        plant_name = get_plant_name() or ''
        user_notes = get_normalized_field('user_notes', '') or get_normalized_field('User Notes', '')
        analysis_type = get_normalized_field('analysis_type', 'general_care')
        location = get_normalized_field('location', '') or get_normalized_field('Location', '')
        
        # Perform AI analysis
        result = analyze_plant_with_ai(plant_name, user_notes, analysis_type, location)
        
        # Convert result to appropriate HTTP response
        if result.get('success'):
            return jsonify(result), 200
        else:
            status_code = 500 if 'AI analysis failed' in result.get('error', '') else 400
            return jsonify(result), status_code
        
    except Exception as e:
        logging.error(f"Error in analyze_plant: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def enhance_analysis():
    """Core analysis enhancement logic called by analysis route module"""
    try:
        from utils.care_intelligence import analyze_plant_with_ai
        from utils.field_normalization_middleware import get_normalized_field
        
        # Get data using field normalization
        gpt_analysis = get_normalized_field('gpt_analysis', '') or get_normalized_field('GPT Analysis', '')
        plant_identification = get_normalized_field('plant_identification', '') or get_normalized_field('Plant Identification', '')
        user_question = get_normalized_field('user_question', '') or get_normalized_field('User Question', '')
        location = get_normalized_field('location', '') or get_normalized_field('Location', '')
        analysis_type = get_normalized_field('analysis_type', 'health_assessment')
        
        # Fallback: if no normalized data, try direct JSON access
        if not any([gpt_analysis, plant_identification]):
            data = request.get_json() if request.is_json else {}
            gpt_analysis = data.get('gpt_analysis', '').strip()
            plant_identification = data.get('plant_identification', '').strip()
            user_question = data.get('user_question', '').strip()
            location = data.get('location', '').strip()
            analysis_type = data.get('analysis_type', 'health_assessment').strip()
        
        if not any([gpt_analysis, plant_identification]):
            return jsonify({
                'success': False,
                'error': 'Either gpt_analysis or plant_identification is required'
            }), 400
        
        # Use plant_identification as plant_name for AI analysis
        plant_name = plant_identification or ''
        user_notes = gpt_analysis or user_question or ''
        
        # Perform enhanced AI analysis with location context
        result = analyze_plant_with_ai(plant_name, user_notes, analysis_type, location)
        
        if result.get('success'):
            # Enhance the response with additional metadata for enhanced analysis
            enhanced_result = {
                'success': True,
                'enhanced_analysis': {
                    'plant_match': {
                        'found_in_database': False,  # Basic implementation
                        'original_identification': plant_identification,
                        'ai_refined_name': plant_name
                    },
                    'care_enhancement': result.get('analysis', {}),
                    'diagnosis_enhancement': {
                        'urgency_level': 'monitor',  # Basic implementation
                        'treatment_recommendations': 'Follow AI analysis recommendations'
                    },
                    'database_context': {
                        'note': 'Enhanced analysis with location intelligence integrated'
                    }
                },
                'suggested_actions': {
                    'immediate_care': ['Follow AI recommendations'],
                    'monitoring': ['Check plant regularly'],
                    'follow_up': 'Re-evaluate in 1 week'
                },
                'logging_offer': {
                    'recommended': True,
                    'reason': 'Enhanced analysis completed'
                }
            }
            return jsonify(enhanced_result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logging.error(f"Error enhancing analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========================================
# PHOTO UPLOAD OPERATIONS
# ========================================

def upload_photo_to_plant(token):
    """Core photo upload logic for plants"""
    try:
        from utils.upload_token_manager import validate_upload_token, mark_token_used
        from utils.storage_client import upload_plant_photo
        
        # Validate token
        is_valid, token_data, error_message = validate_upload_token(token)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message or 'Invalid or expired token'
            }), 401
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Upload photo and link to plant record
        if token_data.get('plant_id'):
            # Use the comprehensive upload and link function
            from utils.plant_operations import upload_and_link_plant_photo
            result = upload_and_link_plant_photo(file, token_data['plant_id'], token_data['plant_name'])
        else:
            # Fallback to simple upload if no plant_id
            from utils.storage_client import upload_plant_photo
            result = upload_plant_photo(file, token_data['plant_name'])
            logging.warning("No plant_id in token - photo uploaded but not linked to plant record")
        
        # Mark token as used
        mark_token_used(token, request.remote_addr or '')
        
        return jsonify({
            'success': True,
            'message': 'Photo uploaded successfully',
            **result
        }), 200
        
    except Exception as e:
        logging.error(f"Error uploading photo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def upload_photo_to_log(token):
    """Core photo upload logic for logs"""
    try:
        from utils.upload_token_manager import validate_upload_token, mark_token_used
        from utils.storage_client import upload_plant_photo
        
        # Validate token
        is_valid, token_data, error_message = validate_upload_token(token)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message or 'Invalid or expired token'
            }), 401
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Upload photo (use plant_photo function with appropriate identifier)
        # Handle both log upload tokens and plant upload tokens
        if token_data.get('token_type') == 'log_upload':
            identifier = f"log_{token_data['log_id']}"
        else:
            # For plant upload tokens, use plant info
            identifier = token_data.get('plant_name', 'unknown_plant')
        
        result = upload_plant_photo(file, identifier)
        
        # Mark token as used
        mark_token_used(token, request.remote_addr or '')
        
        return jsonify({
            'success': True,
            'message': 'Photo uploaded successfully',
            **result
        }), 200
        
    except Exception as e:
        logging.error(f"Error uploading log photo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========================================
# LEGACY ROUTE REGISTRATION
# ========================================
# These functions are imported by the app factory for backward compatibility

def register_image_analysis_route(app, limiter, require_api_key):
    """Register image analysis routes (legacy)"""
    pass  # Placeholder for any remaining image analysis routes


def register_plant_log_routes(app, limiter, require_api_key):
    """Register legacy plant log routes (legacy)"""
    pass  # Most routes moved to blueprints


def register_plant_routes(app, limiter, require_api_key):
    """Register legacy plant routes (legacy)"""
    pass  # Most routes moved to blueprints


# ========================================
# APPLICATION ENTRY POINT
# ========================================

def create_app_instance(testing=False):
    """Create Flask app instance using the modular architecture"""
    return create_app(testing=testing)


# For backward compatibility
app = create_app_instance()


# Only run the app if this file is executed directly (not imported)
# Upload page routes moved to api/routes/photos.py blueprint

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logging.info(f"🚀 Starting Plant Database API v2.3.0 (Modularized)")
    logging.info(f"🌐 Server will run on port {port}")
    logging.info(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

