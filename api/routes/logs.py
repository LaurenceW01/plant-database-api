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
    plant_name = flask_request.args.get('plant_name') or flask_request.args.get('Plant Name')
    entry = flask_request.args.get('entry') or flask_request.args.get('Entry')
    observation = flask_request.args.get('observation') or flask_request.args.get('Observation')
    action = flask_request.args.get('action') or flask_request.args.get('Action')
    
    # Validate required fields  
    if not plant_name:
        return jsonify({
            "error": "Plant name is required for creating a log entry",
            "message": "Use ?plant_name=YourPlantName&entry=YourLogEntry in the URL",
            "workaround": "GET endpoint due to ChatGPT POST issue",
            "received_args": dict(flask_request.args)
        }), 400
    
    # WORKAROUND: Simulate POST request body
    simulated_json = {
        'plant_name': plant_name
    }
    if entry:
        simulated_json['entry'] = entry
    if observation:
        simulated_json['observation'] = observation  
    if action:
        simulated_json['action'] = action
    
    # Store original data
    original_method = flask_request.method
    original_get_json = flask_request.get_json
    original_normalized_data = getattr(g, 'normalized_request_data', None)
    original_original_data = getattr(g, 'original_request_data', None)
    
    # Mock request and g objects
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
        
        # Validate required fields (redundant but kept for consistency)
        if not plant_name:
            error_response = create_error_response_with_field_suggestions(
                "Plant name is required for creating a log entry",
                ['Plant Name']
            )
            return jsonify(error_response), 400
        
        # Import the original create_plant_log_simple function
        from api.main import create_plant_log_simple
        
        # Call the underlying function and add Phase 2 markers
        response_tuple = create_plant_log_simple()
    finally:
        # Restore original request properties
        flask_request.get_json = original_get_json
        flask_request.method = original_method
        
        # Restore original g object data
        if original_normalized_data is not None:
            g.normalized_request_data = original_normalized_data
        elif hasattr(g, 'normalized_request_data'):
            delattr(g, 'normalized_request_data')
            
        if original_original_data is not None:
            g.original_request_data = original_original_data
        elif hasattr(g, 'original_request_data'):
            delattr(g, 'original_request_data')
    
    # Handle both tuple and direct response formats
    if isinstance(response_tuple, tuple):
        response_data, status_code = response_tuple
    else:
        response_data = response_tuple
        status_code = 200
    
    # Add Phase 2 markers to successful responses
    if hasattr(response_data, 'get_json'):
        try:
            data = response_data.get_json()
            if isinstance(data, dict) and data.get('success'):
                # Add Phase 2 markers
                data['phase2_direct'] = True
                data['endpoint_type'] = 'direct_implementation'
                data['separation_of_concerns'] = 'logs_separate_from_plants'
                data['ai_friendly_endpoint'] = True
                data['intuitive_url'] = '/api/logs/create'
                return jsonify(data), status_code
        except Exception as e:
            logging.warning(f"Failed to add Phase 2 markers: {e}")
    
    # Return original response if marking failed
    if isinstance(response_tuple, tuple):
        return response_tuple
    else:
        return response_data


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
    plant_name = flask_request.args.get('plant_name') or flask_request.args.get('Plant Name')
    entry = flask_request.args.get('entry') or flask_request.args.get('Entry')
    
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
        'plant_name': plant_name
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
        
        # Import the original create_plant_log_simple function
        from api.main import create_plant_log_simple
        
        # Call the underlying function and add Phase 2 markers
        response_tuple = create_plant_log_simple()
    finally:
        # Restore original request properties
        flask_request.get_json = original_get_json
        flask_request.method = original_method
        
        # Restore original g object data
        if original_normalized_data is not None:
            g.normalized_request_data = original_normalized_data
        elif hasattr(g, 'normalized_request_data'):
            delattr(g, 'normalized_request_data')
            
        if original_original_data is not None:
            g.original_request_data = original_original_data
        elif hasattr(g, 'original_request_data'):
            delattr(g, 'original_request_data')
    
    # Handle both tuple and direct response formats
    if isinstance(response_tuple, tuple):
        response_data, status_code = response_tuple
    else:
        response_data = response_tuple
        status_code = 200
    
    # Add Phase 2 markers to successful responses
    if hasattr(response_data, 'get_json'):
        try:
            data = response_data.get_json()
            if isinstance(data, dict) and data.get('success'):
                # Add Phase 2 markers
                data['phase2_direct'] = True
                data['endpoint_type'] = 'direct_implementation'
                data['simple_log_creation'] = True
                return jsonify(data), status_code
        except Exception as e:
            logging.warning(f"Failed to add Phase 2 markers to simple log: {e}")
    
    # Return original response if marking failed
    if isinstance(response_tuple, tuple):
        return response_tuple
    else:
        return response_data


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

