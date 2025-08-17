"""
Plant Logging Routes

Handles all plant log-related endpoints including log creation,
search functionality, and plant-specific logging.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging

# Create the logs blueprint
logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET']
@logs_bp.route('/create', methods=['GET'])  # WORKAROUND: was POST
def create_log():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    
    Original: Phase 2 direct implementation: Create plant log entry with AI-friendly endpoint name.
    """
    from flask import request as flask_request, jsonify, g
    
    # WORKAROUND: Extract parameters from query string
    # Extract all possible log fields using correct field names
    log_id = flask_request.args.get('log_id')
    plant_name = flask_request.args.get('plant_name')
    plant_id = flask_request.args.get('plant_id')
    location = flask_request.args.get('location')
    log_date = flask_request.args.get('log_date')
    log_title = flask_request.args.get('log_title')
    photo_url = flask_request.args.get('photo_url')
    raw_photo_url = flask_request.args.get('raw_photo_url')
    diagnosis = flask_request.args.get('diagnosis')
    treatment_recommendation = flask_request.args.get('treatment_recommendation')
    symptoms_observed = flask_request.args.get('symptoms_observed')
    user_notes = flask_request.args.get('user_notes')
    confidence_score = flask_request.args.get('confidence_score')
    analysis_type = flask_request.args.get('analysis_type')
    follow_up_required = flask_request.args.get('follow_up_required')
    follow_up_date = flask_request.args.get('follow_up_date')
    
    # Also support legacy field names for backward compatibility
    symptoms = flask_request.args.get('symptoms')  # legacy name
    treatment = flask_request.args.get('treatment')  # legacy name
    
    # Auto-generate required fields if not provided
    if not log_id:
        from models.field_config import generate_log_id
        log_id = generate_log_id()
    
    if not log_date:
        from datetime import datetime
        log_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Validate required fields  
    if not plant_name:
        return jsonify({
            "error": "Plant name is required for creating a log entry",
            "message": "Use ?plant_name=YourPlantName&log_title=YourTitle&symptoms=YourSymptoms&treatment=YourTreatment in the URL",
            "workaround": "GET endpoint due to ChatGPT POST issue",
            "received_args": dict(flask_request.args)
        }), 400
    
    try:
        # Use the proper create_log_entry function which includes plant validation and photo upload
        from utils.plant_log_operations import create_log_entry
        from utils.upload_token_manager import generate_upload_url
        
        # Create log entry using the comprehensive function
        result = create_log_entry(
            plant_name=plant_name,
            photo_url=photo_url or "",
            raw_photo_url=raw_photo_url or "",
            diagnosis=diagnosis or "",
            treatment=treatment_recommendation or (treatment or ""),  # Support legacy field name
            symptoms=symptoms_observed or (symptoms or ""),  # Support legacy field name  
            user_notes=user_notes or "",
            confidence_score=float(confidence_score) if confidence_score else 0.0,
            analysis_type=analysis_type or "general_care",
            follow_up_required=follow_up_required and follow_up_required.lower() in ['true', '1', 'yes'],
            follow_up_date=follow_up_date or "",
            log_title=log_title or "",
            location=location or ""
        )
        
        if result.get('success'):
            response_tuple = (jsonify({
                "success": True,
                "message": f"Created log entry for {plant_name}",
                "log_id": result.get('log_id'),
                "log_date": result.get('log_data', {}).get('log_date'),
                "plant_id": result.get('plant_id'),
                "upload_url": result.get('upload_url'),
                "upload_token": result.get('upload_token'),
                "phase2_direct": True,
                "endpoint_type": "comprehensive_implementation"
            }), 200)
        else:
            response_tuple = (jsonify({
                "success": False,
                "error": result.get('error', 'Failed to create log entry'),
                "suggestions": result.get('suggestions', []),
                "create_new_option": result.get('create_new_option', False),
                "phase2_direct": True,
                "endpoint_type": "comprehensive_implementation"
            }), 400)
        
    except Exception as e:
        logging.error(f"Error creating log entry: {e}")
        response_tuple = (jsonify({
            "success": False,
            "error": "Failed to create log entry",
            "details": str(e),
            "phase2_direct": True,
            "endpoint_type": "direct_implementation"
        }), 500)
    
    # Return the response
    return response_tuple


@logs_bp.route('/search', methods=['GET'])
def search_logs():
    """
    Phase 2 direct implementation: Search across all plant logs with separation from plant endpoints.
    Provides semantic alignment: searchPlantLogs operationId → /api/logs/search URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    Implements proper separation of concerns (logs separate from plants).
    """
    try:
        # Import the original search function
        from api.main import search_plant_logs
        
        # Direct implementation using existing search logic
        response = search_plant_logs()
        
        # Mark as Phase 2 direct implementation in response
        if hasattr(response, 'get_json'):
            try:
                data = response.get_json()
                if isinstance(data, dict):
                    data['phase2_direct'] = True
                    data['endpoint_type'] = 'direct_implementation'
                    data['separation_of_concerns'] = 'logs_separate_from_plants'
                    return jsonify(data), response.status_code
            except:
                pass
        
        return response
        
    except Exception as e:
        logging.error(f"Error in Phase 2 search_logs: {e}")
        return jsonify({
            'error': str(e),
            'phase2_direct': True,
            'separation_of_concerns': 'logs_separate_from_plants'
        }), 500


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET']
@logs_bp.route('/create-simple', methods=['GET'])  # WORKAROUND: was POST
def create_simple_log():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    
    Original: Phase 2 direct implementation: Create simple plant log entry.
    """
    from flask import request as flask_request, jsonify, g
    
    # WORKAROUND: Extract parameters from query string
    log_id = flask_request.args.get('log_id')
    plant_name = flask_request.args.get('plant_name')
    entry = (flask_request.args.get('entry') or 
             flask_request.args.get('user_notes'))
    log_date = flask_request.args.get('log_date')
    
    # Auto-generate required fields if not provided
    if not log_id:
        from models.field_config import generate_log_id
        log_id = generate_log_id()
    
    if not log_date:
        from datetime import datetime
        log_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Validate required fields  
    if not plant_name:
        return jsonify({
            "error": "Plant name is required for creating a simple log entry",
            "message": "Use ?plant_name=YourPlantName&entry=YourLogEntry in the URL",
            "workaround": "GET endpoint due to ChatGPT POST issue",
            "received_args": dict(flask_request.args)
        }), 400
    
    # WORKAROUND: Simulate POST request body
    simulated_json = {
        'plant_name': plant_name,
        'log_id': log_id,
        'log_date': log_date
    }
    if entry:
        simulated_json['entry'] = entry
    
    # Store original data and mock request/g objects
    original_method = flask_request.method
    original_get_json = flask_request.get_json
    original_normalized_data = getattr(g, 'normalized_request_data', None)
    original_original_data = getattr(g, 'original_request_data', None)
    
    flask_request.get_json = lambda: simulated_json
    flask_request.method = 'POST'
    g.normalized_request_data = simulated_json.copy()
    g.original_request_data = simulated_json.copy()
    
    try:
        # Apply field normalization middleware (already handled by @app.before_request)
        from utils.field_normalization_middleware import (
            get_plant_name, get_normalized_field, create_error_response_with_field_suggestions,
            validate_required_fields
        )
        
        # Get normalized field values
        plant_name = get_plant_name()
        
        # Validate required fields  
        if not plant_name:
            error_response = create_error_response_with_field_suggestions(
                "Plant name is required for creating a simple log entry",
                ['Plant Name']
            )
            return jsonify(error_response), 400
        
        # Use the proper create_log_entry function for simple logs too
        from utils.plant_log_operations import create_log_entry
        
        # Create simple log entry using the comprehensive function
        result = create_log_entry(
            plant_name=plant_name,
            user_notes=entry or "",
            analysis_type="general_care",
            log_title="Simple Log Entry"
        )
        
        if result.get('success'):
            response_tuple = (jsonify({
                "success": True,
                "message": f"Created simple log entry for {plant_name}",
                "log_id": result.get('log_id'),
                "log_date": result.get('log_data', {}).get('log_date'),
                "plant_id": result.get('plant_id'),
                "entry": entry,
                "upload_url": result.get('upload_url'),
                "upload_token": result.get('upload_token'),
                "phase2_direct": True,
                "endpoint_type": "comprehensive_implementation",
                "simple_log_creation": True
            }), 200)
        else:
            response_tuple = (jsonify({
                "success": False,
                "error": result.get('error', 'Failed to create simple log entry'),
                "suggestions": result.get('suggestions', []),
                "create_new_option": result.get('create_new_option', False),
                "phase2_direct": True,
                "endpoint_type": "comprehensive_implementation"
            }), 400)
        
    except Exception as e:
        logging.error(f"Error creating simple log entry: {e}")
        response_tuple = (jsonify({
            "success": False,
            "error": "Failed to create simple log entry",
            "details": str(e),
            "phase2_direct": True,
            "endpoint_type": "direct_implementation"
        }), 500)
    
    # Return the response
    return response_tuple


@logs_bp.route('/create-for-plant/<plant_name>', methods=['POST'])
def create_log_for_plant(plant_name):
    """
    Phase 2 direct implementation: Create log for specific plant with separation from plant endpoints.
    Provides semantic alignment: createLogForPlant operationId → /api/logs/create-for-plant/{name} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    Implements proper separation of concerns (logs separate from plants).
    """
    # For now, return a helpful error message pointing to the correct endpoint structure
    # This maintains the Phase 2 pattern while guiding users to use the standard log creation
    return jsonify({
        "error": "Please use /api/logs/create with 'Plant Name' in the request body", 
        "suggested_endpoint": "/api/logs/create",
        "plant_name_provided": plant_name,
        "phase2_direct": True,
        "endpoint_type": "direct_implementation",
        "separation_of_concerns": "logs_separate_from_plants",
        "example_request": {
            "Plant Name": plant_name,
            "Entry": "Your log entry text here",
            "Diagnosis": "(optional)",
            "Treatment": "(optional)"
        }
    }), 400



