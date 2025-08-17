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
        # Direct log creation implementation
        from utils.plant_log_operations import initialize_log_sheet
        from config.config import sheets_client, SPREADSHEET_ID, LOG_SHEET_NAME
        from models.field_config import get_all_log_field_names
        
        # Initialize log sheet if needed
        initialize_log_sheet()
        
        # Prepare log entry data
        headers = get_all_log_field_names()
        log_data = {
            'log_id': log_id,
            'plant_name': plant_name,
            'log_date': log_date
        }
        
        # Add all optional fields with correct field names
        if plant_id:
            log_data['plant_id'] = plant_id
        if location:
            log_data['location'] = location
        if log_title:
            log_data['log_title'] = log_title
        if photo_url:
            log_data['photo_url'] = photo_url
        if raw_photo_url:
            log_data['raw_photo_url'] = raw_photo_url
        if diagnosis:
            log_data['diagnosis'] = diagnosis
        if treatment_recommendation:
            log_data['treatment_recommendation'] = treatment_recommendation
        if symptoms_observed:
            log_data['symptoms_observed'] = symptoms_observed
        if user_notes:
            log_data['user_notes'] = user_notes
        if confidence_score:
            log_data['confidence_score'] = confidence_score
        if analysis_type:
            log_data['analysis_type'] = analysis_type
        if follow_up_required:
            log_data['follow-up_required'] = follow_up_required
        if follow_up_date:
            log_data['follow-up_date'] = follow_up_date
            
        # Support legacy field names for backward compatibility
        if symptoms and not symptoms_observed:
            log_data['symptoms_observed'] = symptoms
        if treatment and not treatment_recommendation:
            log_data['treatment_recommendation'] = treatment
            
        # MANDATORY: Add last_updated timestamp for all log entries
        from utils.plant_log_operations import get_houston_timestamp_iso
        log_data['last_updated'] = get_houston_timestamp_iso()
        
        # Fill missing fields with empty strings
        for field in headers:
            if field not in log_data:
                log_data[field] = ""
        
        # Convert to row format for sheets
        row_data = [log_data.get(field, "") for field in headers]
        
        # Append to log sheet
        result = sheets_client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{LOG_SHEET_NAME}!A:A',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [row_data]}
        ).execute()
        
        response_tuple = (jsonify({
            "success": True,
            "message": f"Created log entry for {plant_name}",
            "log_id": log_id,
            "log_date": log_date,
            "phase2_direct": True,
            "endpoint_type": "direct_implementation"
        }), 200)
        
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
        
        # Direct simple log creation implementation
        from utils.plant_log_operations import initialize_log_sheet
        from config.config import sheets_client, SPREADSHEET_ID, LOG_SHEET_NAME
        from models.field_config import get_all_log_field_names
        
        # Initialize log sheet if needed
        initialize_log_sheet()
        
        # Prepare simple log entry data
        headers = get_all_log_field_names()
        log_data = {
            'log_id': log_id,
            'plant_name': plant_name,
            'log_date': log_date
        }
        
        # Add the entry/user_notes to user_notes field
        if entry:
            log_data['user_notes'] = entry
            
        # MANDATORY: Add last_updated timestamp for all log entries
        from utils.plant_log_operations import get_houston_timestamp_iso
        log_data['last_updated'] = get_houston_timestamp_iso()
        
        # Fill missing fields with empty strings
        for field in headers:
            if field not in log_data:
                log_data[field] = ""
        
        # Convert to row format for sheets
        row_data = [log_data.get(field, "") for field in headers]
        
        # Append to log sheet
        result = sheets_client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{LOG_SHEET_NAME}!A:A',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [row_data]}
        ).execute()
        
        response_tuple = (jsonify({
            "success": True,
            "message": f"Created simple log entry for {plant_name}",
            "log_id": log_id,
            "log_date": log_date,
            "entry": entry,
            "phase2_direct": True,
            "endpoint_type": "direct_implementation",
                        "simple_log_creation": True
        }), 200)
        
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

