"""
Plant Logging Routes - Consolidated CRUD Operations

Handles all plant log-related operations through a single unified endpoint
supporting Create, Read, Update, and Search functionality.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging

# Create the logs blueprint
logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')


# ========================================
# CONSOLIDATED LOGS ENDPOINT
# ========================================
# Replaces /create, /create-simple, and /search endpoints
# Supports Create, Read, Update, and Search operations
@logs_bp.route('', methods=['GET'])  # Single consolidated endpoint  
def logs_handler():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    
    Consolidated logging endpoint supporting all CRUD operations through GET parameters.
    This replaces the separate /create, /create-simple, and /search endpoints.
    
    Operations:
    - CREATE: GET /api/logs?action=create&plant_name=...&other_fields=...
    - READ/GET: GET /api/logs?log_id=LOG-123 (specific log entry)
    - UPDATE: GET /api/logs?action=update&log_id=LOG-123&field1=value1&field2=value2 [NEW FEATURE]
    - SEARCH: GET /api/logs?plant_name=...&query=...&other_filters=... (default operation)
    
    TODO: Revert to proper REST methods (POST for create/update, GET for read/search) when ChatGPT POST issue is resolved.
    """
    from flask import request as flask_request, jsonify, g
    from utils.plant_log_operations import (
        create_log_entry, get_log_entry_by_id, search_log_entries, update_log_entry
    )
    from utils.upload_token_manager import generate_upload_url
    from models.field_config import generate_log_id
    from datetime import datetime
    
    try:
        # Determine operation type
        action = flask_request.args.get('action', '').lower()
        log_id = flask_request.args.get('log_id')
        
        # OPERATION 1: UPDATE LOG ENTRY
        if action == 'update':
            if not log_id:
                return jsonify({
                    "success": False,
                    "error": "log_id is required for update operation",
                    "example": "/api/logs?action=update&log_id=LOG-123&diagnosis=New diagnosis&user_notes=Updated notes",
                    "workaround": "GET endpoint due to ChatGPT PUT issue"
                }), 400
            
            # Extract all possible update fields
            update_fields = {}
            excluded_params = {'action', 'log_id'}  # Don't include these in updates
            
            for param, value in flask_request.args.items():
                if param not in excluded_params and value:
                    update_fields[param] = value
            
            logging.info(f"CONSOLIDATED UPDATE DEBUG: Extracted update_fields: {update_fields}")
            
            if not update_fields:
                return jsonify({
                    "success": False,
                    "error": "No fields provided for update",
                    "available_fields": "plant_name, diagnosis, treatment_recommendation, symptoms_observed, user_notes, log_title, location, etc.",
                    "workaround": "GET endpoint due to ChatGPT PUT issue"
                }), 400
            
            # Perform update
            result = update_log_entry(log_id, **update_fields)
            
            if result.get('success'):
                # Generate upload token for photo upload after update
                from utils.upload_token_manager import generate_upload_token, generate_upload_url
                
                # Get the plant name from the updated log entry or update fields
                plant_name = update_fields.get('plant_name')
                if not plant_name:
                    # If plant_name wasn't updated, get it from the existing log entry
                    log_result = get_log_entry_by_id(log_id)
                    if log_result.get('success'):
                        plant_name = log_result.get('log_entry', {}).get('plant_name', 'Unknown Plant')
                    else:
                        plant_name = 'Unknown Plant'
                
                # Generate upload token for log photo updates
                upload_token = generate_upload_token(
                    plant_name=plant_name,
                    token_type='log_upload',
                    log_id=log_id,
                    expiration_hours=24
                )
                upload_url = generate_upload_url(upload_token)
                
                return jsonify({
                    "success": True,
                    "message": f"Log entry {log_id} updated successfully",
                    "log_id": log_id,
                    "updated_fields": result.get('updated_fields', []),
                    "upload_url": upload_url,
                    "upload_token": upload_token,
                    "upload_instructions": "Use this URL to upload a photo for this updated log entry (24-hour expiration)",
                    "operation": "update",
                    "consolidated_endpoint": True,
                    "workaround": "GET converted from PUT"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error', 'Failed to update log entry'),
                    "operation": "update",
                    "workaround": "GET converted from PUT"
                }), 400
        
        # OPERATION 2: GET SPECIFIC LOG ENTRY
        elif log_id and action != 'create':
            result = get_log_entry_by_id(log_id)
            
            if result.get('success'):
                return jsonify({
                    "success": True,
                    "log_entry": result.get('log_entry'),
                    "operation": "get",
                    "consolidated_endpoint": True,
                    "workaround": "GET method (normal for read operations)"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error', f'Log entry {log_id} not found'),
                    "operation": "get",
                    "workaround": "GET method (normal for read operations)"
                }), 404
        
        # OPERATION 3: CREATE LOG ENTRY
        elif action == 'create':
            # WORKAROUND: Convert GET query params to POST body format
            # Extract all parameters from query string that could be log fields
            simulated_json = {}
            excluded_params = {'action'}  # Don't include action in the simulated body
            
            for key in flask_request.args.keys():
                if key not in excluded_params:
                    value = flask_request.args.get(key)
                    if value:  # Only include non-empty values
                        simulated_json[key] = value
            
            # Validate required fields  
            if 'plant_name' not in simulated_json:
                return jsonify({
                    "success": False,
                    "error": "plant_name is required for creating a log entry",
                    "message": "Use query parameters like ?action=create&plant_name=YourPlant&diagnosis=...",
                    "workaround": "GET endpoint due to ChatGPT POST issue",
                    "received_args": dict(flask_request.args)
                }), 400
    
            # WORKAROUND: Simulate POST request body by storing in both request and g objects
            # This allows the existing log creation logic to work without modification
            
            # Store original data and mock request/g objects
            original_method = flask_request.method
            original_get_json = flask_request.get_json
            original_normalized_data = getattr(g, 'normalized_request_data', None)
            original_original_data = getattr(g, 'original_request_data', None)
            
            # Mock the request.get_json() to return our simulated data
            flask_request.get_json = lambda: simulated_json
            flask_request.method = 'POST'  # Temporarily set to POST for compatibility
            
            # Set g object data for field normalization middleware
            g.normalized_request_data = simulated_json.copy()
            g.original_request_data = simulated_json.copy()
            
            try:
                # Extract creation fields with legacy support
                plant_name = simulated_json.get('plant_name')
                
                fields = {
                    'plant_name': plant_name,
                    'log_title': simulated_json.get('log_title', ''),
                    'diagnosis': simulated_json.get('diagnosis', ''),
                    'treatment': simulated_json.get('treatment_recommendation') or simulated_json.get('treatment', ''),
                    'symptoms': simulated_json.get('symptoms_observed') or simulated_json.get('symptoms', ''),
                    'user_notes': simulated_json.get('user_notes', ''),
                    'location': simulated_json.get('location', ''),
                    'photo_url': simulated_json.get('photo_url', ''),
                    'raw_photo_url': simulated_json.get('raw_photo_url', ''),
                    'confidence_score': float(simulated_json.get('confidence_score', 0.0)),
                    'analysis_type': simulated_json.get('analysis_type', 'general_care'),
                    'follow_up_required': simulated_json.get('follow_up_required', '').lower() in ['true', '1', 'yes'],
                    'follow_up_date': simulated_json.get('follow_up_date', '')
                }
                
                # Create log entry
                result = create_log_entry(**fields)
                
                if result.get('success'):
                    response_data = {
                        "success": True,
                        "message": f"Created log entry for {plant_name}",
                        "log_id": result.get('log_id'),
                        "log_date": result.get('log_data', {}).get('log_date'),
                        "plant_id": result.get('plant_id'),
                        "upload_url": result.get('upload_url'),
                        "upload_token": result.get('upload_token'),
                        "operation": "create",
                        "consolidated_endpoint": True,
                        "workaround": "GET converted from POST"
                    }
                    return jsonify(response_data), 201
                else:
                    response_data = {
                        "success": False,
                        "error": result.get('error', 'Failed to create log entry'),
                        "suggestions": result.get('suggestions', []),
                        "create_new_option": result.get('create_new_option', False),
                        "operation": "create",
                        "workaround": "GET converted from POST"
                    }
                    return jsonify(response_data), 400
                    
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
        
        # OPERATION 4: SEARCH LOG ENTRIES (default operation)
        else:
            # Extract search parameters
            plant_name = flask_request.args.get('plant_name', '').strip()
            search_query = flask_request.args.get('query', '').strip() or flask_request.args.get('search', '').strip()
            symptoms = flask_request.args.get('symptoms', '').strip()
            limit = int(flask_request.args.get('limit', 20))
            
            # Perform search
            result = search_log_entries(
                plant_name=plant_name if plant_name else None,
                query=search_query,
                symptoms=symptoms,
                limit=limit
            )
            
            if result.get('success'):
                return jsonify({
                    "success": True,
                    "search_results": result.get('search_results', []),
                    "total_results": result.get('total_results', 0),
                    "query": search_query,
                    "plant_name": plant_name,
                    "operation": "search",
                    "consolidated_endpoint": True,
                    "workaround": "GET method (normal for read operations)"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error', 'Failed to search log entries'),
                    "operation": "search",
                    "workaround": "GET method (normal for read operations)"
                }), 500
        
    except Exception as e:
        logging.error(f"Error in consolidated logs endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e),
            "consolidated_endpoint": True,
            "workaround": "GET endpoint due to ChatGPT compatibility"
        }), 500
    

# ========================================
# LEGACY ENDPOINTS - DEPRECATED
# ========================================
# These endpoints are maintained for backward compatibility
# and redirect to the consolidated endpoint

@logs_bp.route('/search', methods=['GET'])
def search_logs():
    """
    DEPRECATED: Use GET /api/logs instead.
    Redirects to consolidated endpoint for backward compatibility.
    """
    # Redirect to consolidated endpoint with same parameters
    from flask import redirect, request
    query_string = request.query_string.decode('utf-8')
    return redirect(f"/api/logs?{query_string}", code=301)


@logs_bp.route('/create', methods=['GET'])
def create_log():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    DEPRECATED: Use GET /api/logs?action=create instead.
    Redirects to consolidated endpoint for backward compatibility.
    TODO: Remove when ChatGPT POST requests work again and consolidation is complete.
    """
    from flask import redirect, request
    query_string = request.query_string.decode('utf-8')
    return redirect(f"/api/logs?action=create&{query_string}", code=301)


@logs_bp.route('/create-simple', methods=['GET'])
def create_simple_log():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    DEPRECATED: Use GET /api/logs?action=create instead.
    Redirects to consolidated endpoint for backward compatibility.
    TODO: Remove when ChatGPT POST requests work again and consolidation is complete.
    """
    from flask import redirect, request
    query_string = request.query_string.decode('utf-8')
    return redirect(f"/api/logs?action=create&{query_string}", code=301)



