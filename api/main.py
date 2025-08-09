# Import the Flask class from the flask package
from flask import Flask, jsonify, request, url_for, render_template  # Import request to access query parameters, url_for for links
import sys
sys.path.append('..')  # Add parent directory to sys.path to allow imports from utils and models
from utils.plant_operations import get_plant_data, search_plants  # Import plant data functions
from models.field_config import get_canonical_field_name, get_all_field_names  # Import field name utility
from flask_cors import CORS  # Import CORS for cross-origin support
import os  # For environment variable access
from functools import wraps  # For creating decorators
from dotenv import load_dotenv  # For loading .env files
from flask_limiter import Limiter  # Import Limiter for rate limiting
from flask_limiter.util import get_remote_address  # Utility to get client IP for rate limiting
import logging  # Import logging module for audit logging
from utils.upload_token_manager import get_token_info  # Import token manager functions

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
API_KEY = os.environ.get('GARDENLLM_API_KEY')

# Define a decorator to require the API key for protected endpoints
def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the API key from the request headers
        key = request.headers.get('x-api-key')
        # If the key is missing or incorrect, return 401 Unauthorized
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        # Otherwise, proceed with the request
        return func(*args, **kwargs)
    return wrapper

# Field name mapping for ChatGPT compatibility (underscore to space format)
def map_underscore_fields_to_canonical(data):
    """
    Convert underscore field names from ChatGPT to canonical field names.
    Maps fields like 'plant_name' or 'Plant___Name' to 'Plant Name' for API compatibility.
    Handles both single underscores and triple underscores from ChatGPT's OpenAPI parser.
    """
    field_mapping = {
        'plant_name': 'Plant Name',
        'plant___name': 'Plant Name',
        'description': 'Description',
        'location': 'Location',
        'light_requirements': 'Light Requirements',
        'light___requirements': 'Light Requirements',
        'frost_tolerance': 'Frost Tolerance',
        'frost___tolerance': 'Frost Tolerance',
        'watering_needs': 'Watering Needs',
        'watering___needs': 'Watering Needs',
        'soil_preferences': 'Soil Preferences',
        'soil___preferences': 'Soil Preferences',
        # Fix for pH field mapping - add missing Soil pH Type mappings
        'soil_ph_type': 'Soil pH Type',
        'soil___ph___type': 'Soil pH Type',
        # Fix for pH field mapping - add missing Soil pH Range mappings  
        'soil_ph_range': 'Soil pH Range',
        'soil___ph___range': 'Soil pH Range',
        'pruning_instructions': 'Pruning Instructions',
        'pruning___instructions': 'Pruning Instructions',
        'mulching_needs': 'Mulching Needs',
        'mulching___needs': 'Mulching Needs',
        'fertilizing_schedule': 'Fertilizing Schedule',
        'fertilizing___schedule': 'Fertilizing Schedule',
        'winterizing_instructions': 'Winterizing Instructions',
        'winterizing___instructions': 'Winterizing Instructions',
        'spacing_requirements': 'Spacing Requirements',
        'spacing___requirements': 'Spacing Requirements',
        'care_notes': 'Care Notes',
        'care___notes': 'Care Notes',
        'photo_url': 'Photo URL',
        'photo___url': 'Photo URL',
        'raw_photo_url': 'Raw Photo URL',
        'raw___photo___url': 'Raw Photo URL',
        'last_updated': 'Last Updated',
        'last___updated': 'Last Updated',
        'id': 'ID'
    }
    
    # Convert underscore fields to canonical names
    canonical_data = {}
    for key, value in data.items():
        canonical_key = field_mapping.get(key.lower(), key)  # Use mapping or original key
        canonical_data[canonical_key] = value
    
    return canonical_data

# Define the add_plant and update_plant view functions (without decorators)
def add_plant():
    """
    Add a new plant to the database.
    Expects a JSON payload with required plant fields.
    Accepts both underscore format (from ChatGPT) and space format field names.
    Returns a success message or error details.
    """
    from utils.plant_operations import add_plant_with_fields
    from models.field_config import get_canonical_field_name, is_valid_field
    from utils.upload_token_manager import generate_upload_token, generate_upload_url
    
    # Log comprehensive debug information about what ChatGPT is sending
    debug_info = {
        "method": request.method,
        "url": request.url,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'Not provided'),
        "content_type": request.content_type,
        "content_length": request.content_length,
        "x_api_key_present": request.headers.get('x-api-key') is not None,
        "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
        "json_data": request.get_json() if request.is_json else None,
        "all_headers": dict(request.headers)
    }
    
    # Log comprehensive debug info to server console
    logging.info(f"ADD_PLANT_DEBUG | {debug_info}")
    
    data = request.get_json()
    # Log the write operation for auditability
    logging.info(
        f"ADD_PLANT | IP: {get_remote_address()} | Endpoint: /api/plants | Payload: {data}"
    )
    if data is None:
        return jsonify({"error": "Missing JSON payload."}), 400
    
    # Phase 1: Use centralized field normalization (Clean Implementation)
    from utils.field_normalization_middleware import (
        get_plant_name, create_error_response_with_field_suggestions
    )
    from flask import g
    
    # Get normalized data from middleware (already processed by before_request)
    normalized_data = getattr(g, 'normalized_request_data', data)
    
    # Fallback to existing underscore conversion for backward compatibility
    canonical_data = map_underscore_fields_to_canonical(normalized_data)
    
    # Validate all fields in the payload
    invalid_fields = [k for k in canonical_data.keys() if not is_valid_field(k)]
    if invalid_fields:
        return jsonify({"error": f"Invalid field(s): {', '.join(invalid_fields)}"}), 400
    
    # Use centralized plant name extraction
    plant_name = get_plant_name()
    if not plant_name:
        error_response = create_error_response_with_field_suggestions(
            "Plant Name is required", 
            ['Plant Name']
        )
        return jsonify(error_response), 400
    
    # Log the request for debugging
    logging.info(f"Adding plant: {plant_name} with {len(canonical_data)} fields")
    
    # Use the comprehensive add_plant_with_fields function that handles all fields
    try:
        result = add_plant_with_fields(canonical_data)
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            logging.error(f"Failed to add plant {plant_name}: {error_msg}")
            return jsonify({"error": error_msg}), 400
    except Exception as e:
        error_msg = f"Exception while adding plant {plant_name}: {type(e).__name__}: {e}"
        logging.error(error_msg)
        return jsonify({"error": f"Server error while adding plant: {str(e)}"}), 500
    
    # Generate upload token for photo upload
    plant_id = result.get('plant_id')
    if not plant_id:
        logging.warning(f"No plant ID returned for {plant_name}, upload token may not work correctly")
    
    try:
        upload_token = generate_upload_token(
            plant_name=plant_name,
            token_type='plant_upload',
            plant_id=str(plant_id) if plant_id else None,
            operation='add'
        )
        upload_url = generate_upload_url(upload_token)
        logging.info(f"Successfully generated upload token for {plant_name} (ID: {plant_id})")
        
    except Exception as e:
        logging.error(f"Failed to generate upload token for {plant_name}: {e}")
        # Continue without upload URL if token generation fails
        upload_url = ""
        upload_token = ""
    
    # Return success response with upload URL
    response_data = {
        "message": result.get('message', 'Plant added successfully'),
        "plant_id": plant_id
    }
    
    if upload_url:
        response_data.update({
            "upload_url": upload_url,
            "upload_instructions": f"To add a photo of your plant, visit: {upload_url}"
        })
    else:
        response_data["upload_instructions"] = "Photo upload temporarily unavailable"
    
    success_msg = f"Successfully added plant {plant_name} (ID: {plant_id})"
    logging.info(success_msg)
    return jsonify(response_data), 201

def update_plant(id_or_name):
    """
    Update an existing plant by its ID or name.
    Expects a JSON payload with fields to update.
    Accepts both underscore format (from ChatGPT) and space format field names.
    Returns a success message or error details.
    """
    from utils.plant_operations import update_plant as update_plant_func
    from models.field_config import is_valid_field
    from utils.upload_token_manager import generate_upload_token, generate_upload_url
    
    # Log comprehensive debug information about what ChatGPT is sending
    debug_info = {
        "method": request.method,
        "url": request.url,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'Not provided'),
        "content_type": request.content_type,
        "content_length": request.content_length,
        "x_api_key_present": request.headers.get('x-api-key') is not None,
        "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
        "json_data": request.get_json() if request.is_json else None,
        "plant_identifier": id_or_name,
        "all_headers": dict(request.headers)
    }
    
    # Log comprehensive debug info to server console
    logging.info(f"UPDATE_PLANT_DEBUG | {debug_info}")
    
    data = request.get_json()
    # Log the write operation for auditability
    logging.info(
        f"UPDATE_PLANT | IP: {get_remote_address()} | Endpoint: /api/plants/{id_or_name} | Payload: {data}"
    )
    if data is None:
        return jsonify({"error": "Missing JSON payload."}), 400
    
    # Convert underscore field names to canonical format for ChatGPT compatibility
    canonical_data = map_underscore_fields_to_canonical(data)
    
    # Validate all fields in the payload
    invalid_fields = [k for k in canonical_data.keys() if not is_valid_field(k)]
    if invalid_fields:
        return jsonify({"error": f"Invalid field(s): {', '.join(invalid_fields)}"}), 400
    update_fields = {k: v for k, v in canonical_data.items() if is_valid_field(k)}
    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400
    result = update_plant_func(id_or_name, update_fields)
    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Unknown error')}), 400
        
    # Generate upload token for photo upload
    upload_token = generate_upload_token(
        plant_name=result.get('plant_name', id_or_name),
        token_type='plant_upload',
        plant_id=str(id_or_name),
        operation='update'
    )
    upload_url = generate_upload_url(upload_token)
    
    # Return success response with upload URL
    return jsonify({
        "message": result.get('message', 'Plant updated successfully'),
        "upload_url": upload_url,
        "upload_instructions": f"To update your plant's photo, visit: {upload_url}"
    }), 200

def test_logging():
    """Test endpoint to verify logging works on server console"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🧪 LOG TEST: This is an INFO message - should appear on Render console")
    logger.warning("🧪 LOG TEST: This is a WARNING message - should appear on Render console") 
    logger.error("🧪 LOG TEST: This is an ERROR message - should appear on Render console")
    
    return jsonify({
        "success": True,
        "message": "Logging test completed - check Render.com console for log messages",
        "timestamp": "Check logs for messages with '🧪 LOG TEST' prefix"
    })

# Function to register all routes (GET, POST, PUT) after config is set
def register_routes(app, limiter, require_api_key):
    """
    Register all API routes after app config is set. Rate limiting is only applied if not in testing mode.
    """
    
    # ========================================
    # PHASE 1: FIELD NORMALIZATION MIDDLEWARE
    # ========================================
    # Register centralized field normalization middleware
    from utils.field_normalization_middleware import normalize_request_middleware
    
    @app.before_request
    def apply_field_normalization():
        """Apply field normalization to all incoming requests"""
        normalize_request_middleware()
    
    # Health check route
    @app.route('/', methods=['GET'])
    def health_check():
        """
        Health check endpoint.
        Returns a simple JSON response to confirm the API is running.
        """
        return jsonify({"status": "ok", "message": "Plant Database API is running."}), 200

    # ========================================
    # PHASE 1: CHATGPT HALLUCINATION REDIRECTS (SAFETY NET)
    # ========================================
    # These endpoints handle common ChatGPT hallucinations by redirecting to correct endpoints
    
    # Redirect for ChatGPT's incorrect /add endpoint (safety net)
    @app.route('/api/plants/add', methods=['POST'])
    def add_plant_redirect():
        """Redirect ChatGPT's incorrect /api/plants/add to correct /api/plants"""
        return add_plant()
    
    # Plant Management Redirects
    @app.route('/api/plants/search', methods=['GET'])
    def search_plants_redirect():
        """Redirect ChatGPT's /api/plants/search to correct /api/plants"""
        return list_or_search_plants()
    
    @app.route('/api/plants/get/<id_or_name>', methods=['GET'])
    def get_plant_redirect(id_or_name):
        """Redirect ChatGPT's /api/plants/get/{id} to correct /api/plants/{id}"""
        return get_plant_by_id_or_name(id_or_name)
    
    @app.route('/api/plants/update/<id_or_name>', methods=['PUT'])
    def update_plant_redirect(id_or_name):
        """Redirect ChatGPT's /api/plants/update/{id} to correct /api/plants/{id}"""
        return update_plant(id_or_name)
    
    @app.route('/api/plants/remove/<id_or_name>', methods=['DELETE'])
    def remove_plant_redirect(id_or_name):
        """Redirect ChatGPT's /api/plants/remove/{id} to correct delete endpoint"""
        # Note: DELETE functionality needs to be implemented
        return jsonify({"error": "Delete functionality not yet implemented", "redirect_attempted": True}), 501
    
    # Logging Redirects  
    @app.route('/api/logs/create', methods=['POST'])
    def create_log_redirect():
        """Redirect ChatGPT's /api/logs/create to correct /api/plants/log"""
        return create_plant_log()
    
    @app.route('/api/logs/create-simple', methods=['POST'])
    def create_log_simple_redirect():
        """Redirect ChatGPT's /api/logs/create-simple to correct /api/plants/log/simple"""
        return create_plant_log_simple()
    
    @app.route('/api/logs/search', methods=['GET'])
    def search_logs_redirect():
        """Redirect ChatGPT's /api/logs/search to correct /api/plants/log/search"""
        return search_plant_logs()
    
    @app.route('/api/logs/create-for-plant/<plant_name>', methods=['POST'])
    def create_log_for_plant_redirect(plant_name):
        """Redirect ChatGPT's /api/logs/create-for-plant/{name} to plant-specific log endpoint"""
        # Modify request to include plant name and redirect to standard log creation
        from flask import request
        request_data = request.get_json() or {}
        request_data['Plant Name'] = plant_name
        
        # We need to modify the request context, but this is complex
        # For now, return a helpful error message
        return jsonify({
            "error": "Please use /api/plants/log with 'Plant Name' in the request body", 
            "suggested_endpoint": "/api/plants/log",
            "plant_name_provided": plant_name,
            "redirect_attempted": True
        }), 400
    
    # Analysis Redirects
    @app.route('/api/plants/diagnose', methods=['POST'])
    def diagnose_plant_redirect():
        """Redirect ChatGPT's /api/plants/diagnose to correct /api/analyze-plant"""
        return analyze_plant()
    
    @app.route('/api/plants/enhance-analysis', methods=['POST'])
    def enhance_analysis_redirect():
        """Redirect ChatGPT's /api/plants/enhance-analysis to correct /api/enhance-analysis"""
        return enhance_analysis()
    
    # Location Context Redirects
    @app.route('/api/locations/get-context/<location_id>', methods=['GET'])
    def get_location_context_redirect(location_id):
        """Redirect ChatGPT's /api/locations/get-context/{id} to existing location endpoint"""
        # Map to existing location care profile endpoint
        return get_location_care_profile(location_id)
    
    @app.route('/api/plants/get-context/<plant_id>', methods=['GET'])
    def get_plant_context_redirect(plant_id):
        """Redirect ChatGPT's /api/plants/get-context/{id} to correct /api/plants/{id}/context"""
        return get_plant_context(plant_id)
    
    @app.route('/api/garden/get-metadata', methods=['GET'])
    def get_garden_metadata_redirect():
        """Redirect ChatGPT's /api/garden/get-metadata to correct /api/garden/metadata/enhanced"""
        return get_enhanced_metadata()
    
    @app.route('/api/garden/optimize-care', methods=['GET'])
    def optimize_care_redirect():
        """Redirect ChatGPT's /api/garden/optimize-care to correct /api/garden/care-optimization"""
        return get_care_optimization()
    
    # Photo Upload Redirects
    @app.route('/api/photos/upload-for-plant/<token>', methods=['POST'])
    def upload_photo_for_plant_redirect(token):
        """Redirect ChatGPT's /api/photos/upload-for-plant/{token} to correct /upload/plant/{token}"""
        return upload_photo_to_plant(token)
    
    @app.route('/api/photos/upload-for-log/<token>', methods=['POST'])
    def upload_photo_for_log_redirect(token):
        """Redirect ChatGPT's /api/photos/upload-for-log/{token} to correct /upload/log/{token}"""
        return upload_photo_to_log(token)

    # Test logging endpoint (temporary for debugging)
    @app.route('/test-logging', methods=['GET'])
    def test_logging_endpoint():
        return test_logging()

    # Privacy policy route
    @app.route('/privacy', methods=['GET'])
    def privacy_policy():
        """
        Privacy policy endpoint.
        Returns the privacy policy as HTML for ChatGPT Actions compliance.
        """
        try:
            with open('privacy_policy.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        except FileNotFoundError:
            return jsonify({"error": "Privacy policy not found"}), 404

    # List/search plants route
    @app.route('/api/plants', methods=['GET'])
    def list_or_search_plants():
        """
        List all plants or search for plants by query string.
        Optional query parameters:
        - 'q': search by name, description, or location
        - 'limit': maximum number of plants to return (default: 20 for ChatGPT compatibility)
        - 'offset': number of plants to skip (default: 0)
        Returns a JSON list of plant records.
        """
        query = request.args.get('q', default='', type=str)
        limit = request.args.get('limit', default=20, type=int)  # Default limit for ChatGPT
        offset = request.args.get('offset', default=0, type=int)
        
        if query:
            plants = search_plants(query)
        else:
            plants = get_plant_data()
        
        # Apply pagination
        total_plants = len(plants)
        paginated_plants = plants[offset:offset + limit] if limit > 0 else plants
        
        # Calculate pagination info for ChatGPT guidance
        has_more = (offset + limit) < total_plants
        next_offset = offset + limit if has_more else None
        remaining_plants = max(0, total_plants - (offset + limit))
        
        # Return paginated results with metadata and ChatGPT guidance
        response = {
            "plants": paginated_plants,
            "total": total_plants,
            "count": len(paginated_plants),
            "offset": offset,
            "limit": limit,
            "has_more": has_more,
            "remaining": remaining_plants
        }
        
        # Add helpful guidance for ChatGPT when there are more plants
        if has_more:
            response["pagination_info"] = {
                "message": f"Showing {len(paginated_plants)} of {total_plants} plants. {remaining_plants} more plants available.",
                "next_page_instruction": f"To get the next {min(limit, remaining_plants)} plants, use: GET /api/plants?offset={next_offset}&limit={limit}",
                "get_all_instruction": "To get ALL remaining plants at once, use: GET /api/plants/all"
            }
        
        return jsonify(response), 200

    # Get all plants without pagination (ChatGPT-friendly endpoint)
    @app.route('/api/plants/all', methods=['GET'])
    def get_all_plants():
        """
        Get ALL plants without pagination limits.
        This endpoint is designed for ChatGPT to easily access the complete plant database.
        Optional query parameters:
        - 'q': search by name, description, or location
        Warning: This endpoint may return large amounts of data. Use with caution.
        """
        query = request.args.get('q', default='', type=str)
        
        if query:
            plants = search_plants(query)
        else:
            plants = get_plant_data()
        
        # Return all results without pagination
        response = {
            "plants": plants,
            "total": len(plants),
            "count": len(plants),
            "warning": "This endpoint returns ALL plants. For large databases, consider using paginated /api/plants endpoint.",
            "pagination_alternative": "Use GET /api/plants?limit=20&offset=0 for paginated results"
        }
        return jsonify(response), 200

    # Get plant by ID or name route
    @app.route('/api/plants/<id_or_name>', methods=['GET'])
    def get_plant_by_id_or_name(id_or_name):
        """
        Retrieve a single plant by its ID or name.
        Returns a JSON object for the plant, or a 404 error if not found.
        """
        from utils.plant_operations import find_plant_by_id_or_name
        from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
        from models.field_config import get_canonical_field_name
        
        plant_row, plant_data = find_plant_by_id_or_name(id_or_name)
        if not plant_row or not plant_data:
            return jsonify({"error": f"Plant with ID or name '{id_or_name}' not found."}), 404
        
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        headers = result.get('values', [[]])[0]
        plant_dict = dict(zip(headers, plant_data))
        
        # Get Photo URL formula if the field exists
        photo_url_field = get_canonical_field_name('Photo URL')
        if photo_url_field and photo_url_field in headers:
            try:
                photo_url_col_idx = headers.index(photo_url_field)
                col_letter = chr(65 + photo_url_col_idx)  # Convert index to column letter
                actual_row_num = plant_row + 1  # plant_row is 0-based, sheets are 1-based
                formula_range = f"Plants!{col_letter}{actual_row_num}"
                
                formula_result = sheets_client.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=formula_range,
                    valueRenderOption='FORMULA'
                ).execute()
                
                formula_values = formula_result.get('values', [])
                if formula_values and formula_values[0]:
                    plant_dict[photo_url_field] = formula_values[0][0]
            except Exception as e:
                print(f"Warning: Could not fetch Photo URL formula: {e}")
        
        return jsonify({"plant": plant_dict}), 200

    # Register POST/PUT routes with or without rate limiting
    if not app.config.get('TESTING', False):
        app.add_url_rule(
            '/api/plants',
            view_func=limiter.limit('10 per minute')(require_api_key(add_plant)),
            methods=['POST']
        )
        app.add_url_rule(
            '/api/plants/<id_or_name>',
            view_func=limiter.limit('10 per minute')(require_api_key(update_plant)),
            methods=['PUT']
        )
    else:
        app.add_url_rule(
            '/api/plants',
            view_func=require_api_key(add_plant),
            methods=['POST']
        )
        app.add_url_rule(
            '/api/plants/<id_or_name>',
            view_func=require_api_key(update_plant),
            methods=['PUT']
        )

    # Phase 1 Locations & Containers Integration Endpoints
    
    # Get plant location context - combines container and location data for specific plant
    @app.route('/api/plants/<plant_id>/location-context', methods=['GET'])
    def get_plant_location_context(plant_id):
        """
        Get comprehensive location and container context for a specific plant.
        Returns all containers for the plant with their location details and care recommendations.
        """
        from utils.locations_operations import get_plant_location_context
        
        try:
            contexts = get_plant_location_context(plant_id)
            
            if not contexts:
                return jsonify({
                    "error": f"No location context found for plant {plant_id}",
                    "plant_id": plant_id,
                    "message": "This plant may not have any containers assigned to locations"
                }), 404
            
            return jsonify({
                "plant_id": plant_id,
                "contexts": contexts,
                "total_contexts": len(contexts),
                "message": f"Found {len(contexts)} location context(s) for plant {plant_id}"
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting plant location context for {plant_id}: {e}")
            return jsonify({
                "error": "Internal server error getting plant location context",
                "plant_id": plant_id
            }), 500
    
    # Get location care profile - comprehensive care analysis for specific location
    @app.route('/api/locations/<location_id>/care-profile', methods=['GET'])
    def get_location_care_profile(location_id):
        """
        Get comprehensive care profile for a specific location.
        Returns sun exposure analysis, watering strategy, and general recommendations.
        """
        from utils.care_intelligence import generate_care_profile_for_location
        
        try:
            care_profile = generate_care_profile_for_location(location_id)
            
            if not care_profile:
                return jsonify({
                    "error": f"Location not found: {location_id}",
                    "location_id": location_id,
                    "message": "Please check that the location ID exists"
                }), 404
            
            return jsonify({
                "location_id": location_id,
                "care_profile": care_profile,
                "message": f"Care profile generated for location {care_profile.get('location_info', {}).get('location_name', location_id)}"
            }), 200
            
        except Exception as e:
            logging.error(f"Error generating care profile for location {location_id}: {e}")
            return jsonify({
                "error": "Internal server error generating location care profile",
                "location_id": location_id
            }), 500
    
    # Get container care requirements - specific care needs for individual container
    @app.route('/api/garden/containers/<container_id>/care-requirements', methods=['GET'])
    def get_container_care_requirements(container_id):
        """
        Get specific care requirements for a container.
        Returns container details, location context, and integrated care recommendations.
        """
        from utils.care_intelligence import generate_container_care_requirements
        
        try:
            requirements = generate_container_care_requirements(container_id)
            
            if not requirements:
                return jsonify({
                    "error": f"Container not found: {container_id}",
                    "container_id": container_id,
                    "message": "Please check that the container ID exists"
                }), 404
            
            return jsonify({
                "container_id": container_id,
                "care_requirements": requirements,
                "message": f"Care requirements generated for container {container_id}"
            }), 200
            
        except Exception as e:
            logging.error(f"Error generating care requirements for container {container_id}: {e}")
            return jsonify({
                "error": "Internal server error generating container care requirements",
                "container_id": container_id
            }), 500
    
    # Locations data endpoints for GPT integration
    
    # Get all locations with metadata
    @app.route('/api/locations/all', methods=['GET'])
    def get_all_locations():
        """
        Get all locations with complete metadata.
        Returns list of all locations with sun exposure and microclimate data.
        """
        from utils.locations_operations import get_all_locations
        
        try:
            locations = get_all_locations()
            
            return jsonify({
                "locations": locations,
                "total": len(locations),
                "message": f"Retrieved {len(locations)} locations"
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting all locations: {e}")
            return jsonify({
                "error": "Internal server error getting locations"
            }), 500
    
    # Get all containers with metadata
    @app.route('/api/containers/all', methods=['GET'])
    def get_all_containers():
        """
        Get all containers with complete metadata.
        Returns list of all containers with plant, location, and specification data.
        """
        from utils.locations_operations import get_all_containers
        
        try:
            containers = get_all_containers()
            
            return jsonify({
                "containers": containers,
                "total": len(containers),
                "message": f"Retrieved {len(containers)} containers"
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting all containers: {e}")
            return jsonify({
                "error": "Internal server error getting containers"
            }), 500

    # =============================================================================
    # PHASE 2: ADVANCED METADATA AGGREGATION ENDPOINTS
    # =============================================================================
    
    # Enhanced location analysis endpoint - comprehensive location analysis with container context
    @app.route('/api/garden/location-analysis/<location_id>', methods=['GET'])
    def get_location_analysis(location_id):
        """
        Returns comprehensive location analysis with container context.
        
        This endpoint implements the Phase 2 location analysis functionality described
        in the Locations & Containers Integration Strategy. It provides:
        - Location profile with aggregated container statistics
        - Care recommendations based on location and container combination
        - Optimization suggestions for the location
        - Cross-reference intelligence analysis
        """
        from utils.locations_operations import get_location_profile, generate_location_recommendations
        
        try:
            # Get comprehensive location profile
            location_profile = get_location_profile(location_id)
            
            if not location_profile:
                return jsonify({
                    "error": f"Location not found: {location_id}",
                    "location_id": location_id,
                    "message": "Please check that the location ID exists"
                }), 404
            
            # Generate comprehensive recommendations
            recommendations = generate_location_recommendations(location_id)
            
            return jsonify({
                "location_id": location_id,
                "location_profile": location_profile,
                "care_recommendations": recommendations,
                "optimization_suggestions": location_profile.get('optimization_opportunities', []),
                "message": f"Comprehensive analysis generated for location {location_profile['location_data']['location_name']}"
            }), 200
            
        except Exception as e:
            logging.error(f"Error generating location analysis for {location_id}: {e}")
            return jsonify({
                "error": "Internal server error generating location analysis",
                "location_id": location_id
            }), 500
    
    # Enhanced plant context endpoint - full environmental and container context for specific plants
    @app.route('/api/plants/<plant_id>/context', methods=['GET'])
    def get_plant_context(plant_id):
        """
        Returns full contextual analysis for specific plant.
        
        This endpoint provides comprehensive environmental and container context
        by analyzing all containers for a plant and their respective locations.
        Includes care plans and optimization tips for each context.
        """
        from utils.locations_operations import (
            get_containers_by_plant_id, 
            get_location_by_id, 
            generate_location_recommendations
        )
        from utils.care_intelligence import generate_container_care_requirements
        from utils.plant_operations import find_plant_by_id_or_name
        
        try:
            # Get plant information including name
            plant_row, plant_data = find_plant_by_id_or_name(plant_id)
            plant_name = "Unknown Plant"
            if plant_data and len(plant_data) > 1:
                plant_name = plant_data[1]  # Plant Name is typically in column 2 (index 1)
            
            # Get all containers for this plant
            containers = get_containers_by_plant_id(plant_id)
            
            if not containers:
                return jsonify({
                    "error": f"No containers found for plant {plant_id}",
                    "plant_id": plant_id,
                    "plant_name": plant_name,
                    "message": "This plant may not have any containers assigned"
                }), 404
            
            contexts = []
            
            # For each container, build comprehensive context
            for container in containers:
                location = get_location_by_id(container['location_id'])
                
                if location:
                    # Generate contextual care plan
                    care_requirements = generate_container_care_requirements(container['container_id'])
                    location_recommendations = generate_location_recommendations(container['location_id'])
                    
                    context = {
                        "container": container,
                        "location": location,
                        "care_plan": care_requirements,
                        "location_intelligence": location_recommendations,
                        "optimization_tips": _suggest_container_improvements_helper(container, location)
                    }
                    contexts.append(context)
            
            return jsonify({
                "plant_id": plant_id,
                "plant_name": plant_name,
                "contexts": contexts,
                "total_contexts": len(contexts),
                "message": f"Generated {len(contexts)} comprehensive context(s) for plant {plant_id} ({plant_name})"
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting plant context for {plant_id}: {e}")
            return jsonify({
                "error": "Internal server error getting plant context",
                "plant_id": plant_id
            }), 500
    
    # Enhanced garden metadata endpoint - comprehensive garden metadata with location + container intelligence
    @app.route('/api/garden/metadata/enhanced', methods=['GET'])
    def get_enhanced_metadata():
        """
        Returns comprehensive garden metadata with location + container intelligence.
        
        This endpoint implements the Phase 2 enhanced metadata aggregation, providing:
        - Garden overview with comprehensive statistics
        - Location distribution analysis
        - Container intelligence insights
        - Care complexity assessment
        - Optimization opportunities across the garden
        """
        from utils.locations_operations import get_garden_metadata_enhanced
        
        try:
            enhanced_metadata = get_garden_metadata_enhanced()
            
            if not enhanced_metadata:
                return jsonify({
                    "error": "Unable to generate enhanced metadata",
                    "message": "No location or container data available"
                }), 404
            
            return jsonify({
                "enhanced_metadata": enhanced_metadata,
                "api_version": "Phase 2 - Advanced Metadata Aggregation",
                "message": "Enhanced garden metadata generated successfully"
            }), 200
            
        except Exception as e:
            logging.error(f"Error generating enhanced metadata: {e}")
            return jsonify({
                "error": "Internal server error generating enhanced metadata"
            }), 500
    
    # Location profiles endpoint - get all location profiles with aggregated data
    @app.route('/api/garden/location-profiles', methods=['GET'])
    def get_all_location_profiles():
        """
        Get comprehensive profiles for all locations with aggregated container statistics.
        
        This endpoint returns location profiles that combine location data with
        container statistics, implementing the Phase 2 location profiles view.
        """
        from utils.locations_operations import get_all_location_profiles
        
        try:
            location_profiles = get_all_location_profiles()
            
            return jsonify({
                "location_profiles": location_profiles,
                "total_profiles": len(location_profiles),
                "message": f"Generated {len(location_profiles)} location profiles"
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting location profiles: {e}")
            return jsonify({
                "error": "Internal server error getting location profiles"
            }), 500
    
    # Care optimization endpoint - get location and container-based care optimization suggestions
    @app.route('/api/garden/care-optimization', methods=['GET'])
    def get_care_optimization():
        """
        Get location and container-based care optimization suggestions.
        
        This endpoint provides proactive care recommendations and efficiency
        improvements based on cross-analysis of locations and containers.
        """
        from utils.locations_operations import get_garden_metadata_enhanced, get_all_location_profiles
        
        try:
            # Get enhanced metadata which includes optimization opportunities
            enhanced_metadata = get_garden_metadata_enhanced()
            location_profiles = get_all_location_profiles()
            
            if not enhanced_metadata:
                return jsonify({
                    "error": "Unable to generate care optimization",
                    "message": "No data available for optimization analysis"
                }), 404
            
            # Extract optimization-focused data
            optimization_data = {
                "garden_wide_opportunities": enhanced_metadata.get('optimization_opportunities', []),
                "care_complexity_summary": enhanced_metadata.get('care_complexity_analysis', {}),
                "high_priority_locations": [],
                "container_upgrade_recommendations": [],
                "efficiency_improvements": []
            }
            
            # Analyze each location for specific optimization opportunities
            for profile in location_profiles:
                location_id = profile.get('location_id')
                
                # Get detailed recommendations for this location
                recommendations = generate_location_recommendations(location_id)
                
                if recommendations:
                    # Check for high priority care needs
                    complexity = recommendations.get('care_complexity_assessment', {})
                    if complexity.get('complexity_level') == 'high':
                        optimization_data['high_priority_locations'].append({
                            'location_id': location_id,
                            'location_name': profile.get('location_name'),
                            'complexity_factors': complexity.get('complexity_factors', []),
                            'recommended_frequency': complexity.get('recommended_monitoring_frequency')
                        })
                    
                    # Extract container upgrade recommendations
                    container_compat = recommendations.get('location_analysis', {}).get('container_compatibility', {})
                    concerning_combinations = container_compat.get('concerning_combinations', [])
                    
                    for combination in concerning_combinations:
                        if combination.get('risk_level') == 'high':
                            optimization_data['container_upgrade_recommendations'].append({
                                'location_name': profile.get('location_name'),
                                'container_id': combination.get('container_id'),
                                'issue': combination.get('issue'),
                                'impact': combination.get('impact')
                            })
            
            # Add efficiency improvements from garden-wide analysis
            care_complexity = enhanced_metadata.get('care_complexity_analysis', {})
            daily_care_locations = care_complexity.get('daily_care_locations', [])
            
            if len(daily_care_locations) > 0:
                optimization_data['efficiency_improvements'].append({
                    'type': 'daily_care_routing',
                    'description': f"{len(daily_care_locations)} locations require daily care",
                    'recommendation': f"Create efficient care routes for: {', '.join(daily_care_locations[:3])}{'...' if len(daily_care_locations) > 3 else ''}",
                    'priority': 'high' if len(daily_care_locations) > 3 else 'medium'
                })
            
            return jsonify({
                "optimization_analysis": optimization_data,
                "total_opportunities": len(optimization_data['garden_wide_opportunities']),
                "high_priority_locations": len(optimization_data['high_priority_locations']),
                "message": "Care optimization analysis completed"
            }), 200
            
        except Exception as e:
            logging.error(f"Error generating care optimization: {e}")
            return jsonify({
                "error": "Internal server error generating care optimization"
            }), 500

def _suggest_container_improvements_helper(container, location):
    """
    Helper function to suggest container improvements based on location analysis.
    
    Args:
        container: Container information dictionary
        location: Location information dictionary
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    # Analyze material vs sun exposure
    material = container.get('container_material', '').lower()
    afternoon_sun = location.get('afternoon_sun_hours', 0)
    total_sun = location.get('total_sun_hours', 0)
    
    if material == 'plastic' and afternoon_sun > 3:
        suggestions.append({
            'type': 'material_upgrade',
            'priority': 'medium',
            'current_issue': 'Plastic container in high afternoon sun',
            'recommendation': 'Consider upgrading to ceramic or terracotta container',
            'benefit': 'Better temperature regulation and root protection'
        })
    
    # Analyze size vs sun exposure
    size = container.get('container_size', '').lower()
    if size == 'small' and total_sun > 7:
        suggestions.append({
            'type': 'size_upgrade',
            'priority': 'medium',
            'current_issue': 'Small container in high sun location',
            'recommendation': 'Consider upgrading to medium or large container',
            'benefit': 'Better water retention and reduced watering frequency'
        })
    
    # Microclimate optimization
    microclimate = location.get('microclimate_conditions', '').lower()
    if 'north' in microclimate and material != 'ceramic':
        suggestions.append({
            'type': 'microclimate_optimization',
            'priority': 'low',
            'current_issue': 'Not optimizing cool microclimate benefits',
            'recommendation': 'This location is perfect for heat-sensitive plants',
            'benefit': 'Take advantage of cooler conditions for specialized plants'
        })
    
    return suggestions

# New enhance-analysis endpoint for ChatGPT Vision + API Consultation
def enhance_analysis():
    """
    Enhanced analysis endpoint that accepts ChatGPT's image analysis text and enhances it
    with database knowledge, personalized care instructions, and historical correlation.
    This endpoint does NOT force log creation - it's for consultation only.
    """
    try:
        # Log comprehensive debug information about what ChatGPT is sending
        debug_info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "x_api_key_present": request.headers.get('x-api-key') is not None,
            "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
            "json_data": request.get_json() if request.is_json else None,
            "all_headers": dict(request.headers)
        }
        
        # Log comprehensive debug info to server console
        logging.info(f"ENHANCE_ANALYSIS_DEBUG | {debug_info}")
        
        # Validate JSON request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing JSON payload'
            }), 400
        
        # Extract required fields
        gpt_analysis = data.get('gpt_analysis', '').strip()
        plant_identification = data.get('plant_identification', '').strip()
        
        # Extract optional fields
        user_question = data.get('user_question', '').strip()
        location = data.get('location', '').strip()
        analysis_type = data.get('analysis_type', 'health_assessment').strip()
        
        # Validate required fields
        if not gpt_analysis or not plant_identification:
            return jsonify({
                'success': False,
                'error': 'Both gpt_analysis and plant_identification are required'
            }), 400
        
        # Import required modules for enhanced analysis
        from utils.plant_operations import enhanced_plant_matching
        
        # Step 1: Enhanced plant matching against user's database
        plant_match_result = enhanced_plant_matching(plant_identification)
        
        # Step 2: Get personalized care instructions
        care_enhancement = generate_personalized_care_instructions(
            plant_identification=plant_identification,
            location=location,
            analysis_type=analysis_type,
            gpt_analysis=gpt_analysis
        )
        
        # Step 3: Diagnosis enhancement using AI + database knowledge
        diagnosis_enhancement = enhance_diagnosis_with_database_knowledge(
            gpt_analysis=gpt_analysis,
            plant_identification=plant_identification,
            plant_match_result=plant_match_result,
            user_question=user_question
        )
        
        # Step 4: Get historical context if plant is in database
        database_context = {}
        if plant_match_result.get('found_in_database'):
            database_context = get_database_context_for_plant(
                plant_match_result['matched_plant_name'],
                plant_identification
            )
        
        # Step 5: Generate suggested actions
        suggested_actions = generate_suggested_actions(
            diagnosis_enhancement=diagnosis_enhancement,
            care_enhancement=care_enhancement,
            analysis_type=analysis_type
        )
        
        # Step 6: Determine if logging is recommended
        logging_offer = generate_logging_recommendation(
            plant_match_result=plant_match_result,
            diagnosis_enhancement=diagnosis_enhancement,
            gpt_analysis=gpt_analysis,
            plant_identification=plant_identification
        )
        
        # Build comprehensive response
        response_data = {
            'success': True,
            'enhanced_analysis': {
                'plant_match': plant_match_result,
                'care_enhancement': care_enhancement,
                'diagnosis_enhancement': diagnosis_enhancement,
                'database_context': database_context
            },
            'suggested_actions': suggested_actions,
            'logging_offer': logging_offer
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        # Comprehensive error handling
        error_msg = str(e)
        logging.error(f"Error in enhance-analysis endpoint: {e}")
        
        return jsonify({
            'success': False,
            'error': f'Server error during enhanced analysis: {error_msg}',
            'enhanced_analysis': {
                'plant_match': {'found_in_database': False, 'error': 'Analysis failed'},
                'care_enhancement': {'error': 'Could not generate care instructions'},
                'diagnosis_enhancement': {'error': 'Could not enhance diagnosis'}
            }
        }), 500

# Helper functions for enhanced analysis
def generate_personalized_care_instructions(plant_identification: str, location: str, analysis_type: str, gpt_analysis: str) -> dict:
    """
    Generate personalized care instructions based on location and plant type.
    Integrates with weather data and location-specific advice.
    """
    try:
        # Get location-specific advice based on Houston climate if location provided
        location_advice = ""
        if location and "houston" in location.lower():
            location_advice = "For Houston's humid subtropical climate with hot summers and mild winters: "
        
        # Generate seasonal advice based on current month
        from datetime import datetime
        current_month = datetime.now().month
        seasonal_advice = get_seasonal_advice_for_month(current_month, plant_identification)
        
        # Build care enhancement response
        care_enhancement = {
            "specific_care_instructions": f"{location_advice}Based on your {plant_identification}, focus on proper drainage and air circulation to prevent fungal issues common in humid climates.",
            "common_issues": f"{plant_identification} commonly experiences humidity-related fungal problems, spider mites in hot weather, and may need extra protection during occasional Houston freezes.",
            "seasonal_advice": seasonal_advice,
            "watering_recommendations": "Water deeply but less frequently to encourage deep root growth. Check soil moisture before watering.",
            "location_specific": location_advice != ""
        }
        
        return care_enhancement
        
    except Exception as e:
        logging.error(f"Error generating personalized care instructions: {e}")
        return {
            "specific_care_instructions": "Unable to generate personalized advice at this time.",
            "common_issues": "Check for common plant health issues like overwatering, pests, or light problems.",
            "seasonal_advice": "Adjust care based on current season and weather conditions.",
            "error": str(e)
        }

def enhance_diagnosis_with_database_knowledge(gpt_analysis: str, plant_identification: str, plant_match_result: dict, user_question: str) -> dict:
    """
    Enhance ChatGPT's diagnosis with database knowledge and historical patterns.
    """
    try:
        # Extract key symptoms from GPT analysis
        symptoms = extract_symptoms_from_analysis(gpt_analysis)
        
        # Determine urgency level based on symptoms
        urgency_level = determine_urgency_level(symptoms, gpt_analysis)
        
        # Generate treatment recommendations
        treatment_recommendations = generate_treatment_recommendations(symptoms, plant_identification, gpt_analysis)
        
        # Build diagnosis enhancement
        diagnosis_enhancement = {
            "likely_causes": symptoms.get('likely_causes', []),
            "treatment_recommendations": treatment_recommendations,
            "urgency_level": urgency_level,
            "confidence_assessment": plant_match_result.get('confidence', 'medium'),
            "symptoms_identified": symptoms.get('symptoms_list', [])
        }
        
        return diagnosis_enhancement
        
    except Exception as e:
        logging.error(f"Error enhancing diagnosis: {e}")
        return {
            "likely_causes": ["Unable to determine specific causes"],
            "treatment_recommendations": "Monitor plant closely and consider consulting local garden center.",
            "urgency_level": "monitor",
            "error": str(e)
        }

def get_database_context_for_plant(matched_plant_name: str, original_identification: str) -> dict:
    """
    Get historical context and previous issues for a plant from the database.
    """
    try:
        from utils.plant_log_operations import get_plant_log_entries
        
        # Get recent log entries for this plant
        log_result = get_plant_log_entries(matched_plant_name, limit=5, offset=0)
        
        context = {
            "your_plant_history": f"Found {matched_plant_name} in your database",
            "previous_issues": [],
            "plant_count": 1,
            "last_logged": "No recent logs"
        }
        
        if log_result.get('success') and log_result.get('log_entries'):
            log_entries = log_result['log_entries']
            context["last_logged"] = log_entries[0].get('Date', 'Unknown') if log_entries else "No recent logs"
            
            # Extract previous issues from log entries
            previous_issues = []
            for entry in log_entries[:3]:  # Last 3 entries
                diagnosis = entry.get('Diagnosis', '')
                symptoms = entry.get('Symptoms', '')
                if diagnosis or symptoms:
                    previous_issues.append(f"{entry.get('Date', 'Unknown date')}: {diagnosis or symptoms}")
            
            context["previous_issues"] = previous_issues[:2]  # Limit to 2 most recent
        
        return context
        
    except Exception as e:
        logging.error(f"Error getting database context: {e}")
        return {
            "your_plant_history": f"Plant identified as {original_identification}",
            "error": str(e)
        }

def generate_suggested_actions(diagnosis_enhancement: dict, care_enhancement: dict, analysis_type: str) -> dict:
    """
    Generate specific action recommendations based on the enhanced analysis.
    """
    try:
        urgency = diagnosis_enhancement.get('urgency_level', 'monitor')
        
        suggested_actions = {
            "immediate_care": [],
            "monitoring": [],
            "follow_up": []
        }
        
        # Immediate care based on urgency
        if urgency == "urgent":
            suggested_actions["immediate_care"] = [
                "Address identified issues immediately",
                "Remove any damaged plant material",
                "Isolate from other plants if disease suspected"
            ]
        elif urgency == "moderate":
            suggested_actions["immediate_care"] = [
                "Begin recommended treatment within 24-48 hours",
                "Monitor for symptom progression"
            ]
        else:
            suggested_actions["immediate_care"] = [
                "Continue regular care routine",
                "Make gradual adjustments as recommended"
            ]
        
        # Monitoring recommendations
        suggested_actions["monitoring"] = [
            "Check plant daily for changes",
            "Document any new symptoms",
            "Monitor watering and light conditions"
        ]
        
        # Follow-up timing
        if urgency == "urgent":
            suggested_actions["follow_up"] = "Re-evaluate in 2-3 days"
        elif urgency == "moderate":
            suggested_actions["follow_up"] = "Re-evaluate in 1 week"
        else:
            suggested_actions["follow_up"] = "Re-evaluate in 2-3 weeks"
        
        return suggested_actions
        
    except Exception as e:
        logging.error(f"Error generating suggested actions: {e}")
        return {
            "immediate_care": ["Monitor plant carefully"],
            "monitoring": ["Check daily for changes"],
            "follow_up": "Re-evaluate in 1 week"
        }

def generate_logging_recommendation(plant_match_result: dict, diagnosis_enhancement: dict, gpt_analysis: str, plant_identification: str) -> dict:
    """
    Determine if logging is recommended and prepare pre-filled data.
    """
    try:
        # Determine if logging is recommended
        recommended = False
        reason = ""
        
        urgency = diagnosis_enhancement.get('urgency_level', 'monitor')
        found_in_db = plant_match_result.get('found_in_database', False)
        
        if urgency in ['urgent', 'moderate']:
            recommended = True
            reason = "Track treatment progress for health issues"
        elif found_in_db:
            recommended = True
            reason = "Update plant history in your database"
        else:
            reason = "Optional - helps track plant health over time"
        
        # Extract symptoms and diagnosis for pre-filled data
        symptoms = extract_symptoms_from_analysis(gpt_analysis)
        
        logging_offer = {
            "recommended": recommended,
            "reason": reason,
            "pre_filled_data": {
                "plant_name": plant_match_result.get('matched_plant_name', plant_identification),
                "symptoms": ", ".join(symptoms.get('symptoms_list', [])),
                "diagnosis": gpt_analysis[:200] + "..." if len(gpt_analysis) > 200 else gpt_analysis,
                "treatment": diagnosis_enhancement.get('treatment_recommendations', ''),
                "analysis_type": "health_assessment",
                "confidence_score": 0.8
            }
        }
        
        return logging_offer
        
    except Exception as e:
        logging.error(f"Error generating logging recommendation: {e}")
        return {
            "recommended": False,
            "reason": "Unable to generate recommendation",
            "error": str(e)
        }

# Utility functions for enhanced analysis
def get_seasonal_advice_for_month(month: int, plant_name: str) -> str:
    """Generate seasonal advice based on current month and plant type."""
    # Houston seasonal advice mapping
    if month in [12, 1, 2]:  # Winter
        return f"Winter care for {plant_name}: Protect from occasional freezes, reduce watering, avoid fertilizing."
    elif month in [3, 4, 5]:  # Spring
        return f"Spring care for {plant_name}: Great time for planting and fertilizing, increase watering as temperatures rise."
    elif month in [6, 7, 8]:  # Summer
        return f"Summer care for {plant_name}: Provide afternoon shade, water deeply and frequently, watch for heat stress."
    else:  # Fall (9, 10, 11)
        return f"Fall care for {plant_name}: Reduce fertilizing, prepare for winter, good time for root development."

def extract_symptoms_from_analysis(gpt_analysis: str) -> dict:
    """Extract symptoms and likely causes from GPT analysis text."""
    symptoms_list = []
    likely_causes = []
    
    # Common symptom keywords to look for
    symptom_keywords = {
        'yellowing': 'yellowing leaves',
        'browning': 'browning/brown spots',
        'wilting': 'wilting',
        'dropping': 'leaf drop',
        'spots': 'spotted leaves',
        'curling': 'leaf curling',
        'stunted': 'stunted growth'
    }
    
    # Common cause keywords
    cause_keywords = {
        'overwater': 'overwatering',
        'underwater': 'underwatering',
        'fungal': 'fungal infection',
        'pest': 'pest infestation',
        'nutrient': 'nutrient deficiency',
        'light': 'lighting issues'
    }
    
    analysis_lower = gpt_analysis.lower()
    
    # Extract symptoms
    for keyword, description in symptom_keywords.items():
        if keyword in analysis_lower:
            symptoms_list.append(description)
    
    # Extract likely causes
    for keyword, description in cause_keywords.items():
        if keyword in analysis_lower:
            likely_causes.append(description)
    
    return {
        'symptoms_list': symptoms_list[:3],  # Limit to top 3
        'likely_causes': likely_causes[:3]   # Limit to top 3
    }

def determine_urgency_level(symptoms: dict, gpt_analysis: str) -> str:
    """Determine urgency level based on symptoms and analysis."""
    analysis_lower = gpt_analysis.lower()
    
    # Urgent indicators
    urgent_indicators = ['dying', 'severe', 'spreading', 'rapidly', 'emergency', 'immediate']
    if any(indicator in analysis_lower for indicator in urgent_indicators):
        return 'urgent'
    
    # Moderate indicators
    moderate_indicators = ['browning', 'yellowing', 'wilting', 'spots', 'pest', 'fungal']
    if any(indicator in analysis_lower for indicator in moderate_indicators):
        return 'moderate'
    
    return 'monitor'

def generate_treatment_recommendations(symptoms: dict, plant_name: str, gpt_analysis: str) -> str:
    """Generate specific treatment recommendations based on symptoms."""
    recommendations = []
    
    symptoms_list = symptoms.get('symptoms_list', [])
    likely_causes = symptoms.get('likely_causes', [])
    
    # Treatment based on likely causes
    if 'overwatering' in likely_causes:
        recommendations.append("Reduce watering frequency and improve drainage")
    if 'underwatering' in likely_causes:
        recommendations.append("Increase watering frequency and check soil moisture regularly")
    if 'fungal infection' in likely_causes:
        recommendations.append("Apply fungicide and improve air circulation")
    if 'pest infestation' in likely_causes:
        recommendations.append("Treat with appropriate pest control measures")
    if 'nutrient deficiency' in likely_causes:
        recommendations.append("Apply balanced fertilizer according to plant needs")
    
    # If no specific causes identified, provide general advice
    if not recommendations:
        recommendations.append("Monitor plant closely and adjust care routine as needed")
        recommendations.append("Ensure proper watering, lighting, and drainage")
    
    return ". ".join(recommendations) + "."

def extract_plant_name_from_analysis(gpt_analysis: str) -> str:
    """
    Extract plant name from ChatGPT's analysis text.
    Looks for common patterns like "This appears to be a [plant name]" or "PLANT IDENTIFICATION: [plant name]"
    """
    analysis_lower = gpt_analysis.lower()
    
    # Pattern 1: Look for structured identification
    if "**plant identification:**" in analysis_lower:
        lines = gpt_analysis.split('\n')
        for line in lines:
            if "**plant identification:**" in line.lower():
                plant_name = line.split(":**", 1)[1].strip() if ":**" in line else ""
                # Clean up the plant name (remove brackets, extra text)
                if plant_name:
                    return plant_name.split('(')[0].split('[')[0].strip()
    
    # Pattern 2: Look for "appears to be" or "looks like" patterns
    patterns = [
        r"appears to be (?:a|an)\s+([^,.]+)",
        r"looks like (?:a|an)\s+([^,.]+)", 
        r"this is (?:a|an)\s+([^,.]+)",
        r"identified as (?:a|an)\s+([^,.]+)",
        r"species.*?([A-Z][a-z]+\s+[a-z]+)"  # Scientific name pattern
    ]
    
    import re
    for pattern in patterns:
        match = re.search(pattern, analysis_lower)
        if match:
            plant_name = match.group(1).strip()
            # Clean up and return first reasonable plant name
            if len(plant_name) > 2 and len(plant_name) < 50:
                return plant_name.title()
    
    # Pattern 3: Look for plant names at the beginning of sentences
    sentences = gpt_analysis.split('.')
    for sentence in sentences[:3]:  # Check first 3 sentences
        sentence = sentence.strip()
        # Look for capitalized words that might be plant names
        words = sentence.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3:
                # Check if next word is also capitalized (might be scientific name)
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    return f"{word} {words[i + 1]}"
                elif word.lower() in ['rose', 'tomato', 'basil', 'mint', 'sage', 'rosemary', 'lavender', 'hibiscus']:
                    return word
    
    return ""  # Return empty if no plant name found

# Enhanced analyze-plant endpoint with log integration
def analyze_plant():
    """
    Enhanced image analysis endpoint that integrates with plant logging.
    Uploads images to Google Cloud Storage and creates log entries automatically.
    """
    try:
        # Log comprehensive debug information about what ChatGPT is sending
        debug_info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "x_api_key_present": request.headers.get('x-api-key') is not None,
            "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
            "form_data_keys": list(request.form.keys()) if request.form else [],
            "files_present": list(request.files.keys()) if request.files else [],
            "json_data": request.get_json() if request.is_json else None,
            "all_headers": dict(request.headers)
        }
        
        # Add file details if present
        if request.files:
            debug_info["file_details"] = {}
            for file_key, file_obj in request.files.items():
                debug_info["file_details"][file_key] = {
                    "filename": file_obj.filename,
                    "content_type": file_obj.content_type,
                    "size": len(file_obj.read()) if file_obj else 0
                }
                if file_obj:
                    file_obj.seek(0)  # Reset file pointer after reading size
        
        # Log comprehensive debug info to server console
        logging.info(f"ANALYZE_PLANT_DEBUG | {debug_info}")
        
        # Handle both JSON and form-data requests
        if request.content_type and 'application/json' in request.content_type:
            # JSON request - TEXT ONLY (ChatGPT cannot send actual photos via JSON)
            json_data = request.get_json() or {}
            plant_name = json_data.get('plant_name', '').strip()
            user_notes = json_data.get('user_notes', '').strip()
            analysis_type = json_data.get('analysis_type', 'general_care').strip()
            location = json_data.get('location', '').strip()
            
            # New field: gpt_analysis for enhanced ChatGPT integration
            gpt_analysis = json_data.get('gpt_analysis', '').strip()
            
            # JSON mode is TEXT ONLY - no photo processing
            # Note: ChatGPT may send invalid file references like 'file-ABC123' which we ignore
            has_photo_data = False
            has_file = False
            image_data_b64 = None
            
            # Log warning if ChatGPT tries to send photo references
            if json_data.get('photo_data') or json_data.get('image_data') or json_data.get('file'):
                logging.warning(f"ChatGPT sent invalid photo reference in JSON request: {json_data.get('photo_data') or json_data.get('image_data') or json_data.get('file')} - ignoring and proceeding with text-only advice")
        else:
            # Form-data request (direct photo upload)
            plant_name = request.form.get('plant_name', '').strip()
            user_notes = request.form.get('user_notes', '').strip()
            analysis_type = request.form.get('analysis_type', 'general_care').strip()
            location = request.form.get('location', '').strip()
            # Check if image file is present
            has_file = 'file' in request.files and request.files['file'].filename != ''
            has_photo_data = has_file
        
        # If no photo data provided, require plant_name for general advice UNLESS user_notes suggest image analysis
        if not has_photo_data and not plant_name and not user_notes:
            return jsonify({
                'success': False, 
                'error': 'Either photo data, plant_name, or user_notes describing the plant is required.'
            }), 400
        
        # Special case: If user_notes mention visual symptoms but no plant_name, this is likely an image analysis request
        # where ChatGPT analyzed the image but didn't forward the actual file
        if not has_photo_data and not plant_name and user_notes:
            # Check if user_notes contain visual descriptors suggesting image analysis
            visual_keywords = ['leaves', 'turning', 'browning', 'yellowing', 'spotted', 'wilting', 'flowers', 'growth', 'color', 'patches']
            has_visual_description = any(keyword in user_notes.lower() for keyword in visual_keywords)
            
            if has_visual_description:
                # This appears to be an image analysis request where ChatGPT processed the image
                # but only sent the text description. Set a generic plant name for logging.
                plant_name = "Unknown Plant (Image Analysis)"
                logging.info(f"Detected image analysis request from ChatGPT with visual description: {user_notes[:100]}...")
        
        # Import required modules
        from utils.storage_client import upload_plant_photo, is_storage_available
        from utils.plant_log_operations import create_log_entry, validate_plant_for_log
        from config.config import openai_client
        import base64
        
        # Initialize variables
        upload_result = None
        analysis_text = ""
        image_base64 = None
        
        if has_photo_data:
            # PHOTO ANALYSIS PATH: Analyze image (with or without storage)
            
            if has_file:
                # DIRECT FILE UPLOAD (multipart/form-data)
                file = request.files['file']
                
                # Check if storage is available for photo upload
                if not is_storage_available():
                    return jsonify({
                        'success': False, 
                        'error': 'Image storage not available. Check Google Cloud Storage configuration.'
                    }), 500
                
                # Validate and upload image file
                try:
                    upload_result = upload_plant_photo(file, plant_name)
                except ValueError as e:
                    return jsonify({'success': False, 'error': str(e)}), 400
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Failed to upload image: {str(e)}'}), 500
                
                # Reset file pointer for OpenAI analysis
                file.seek(0)
                image_data = file.read()
                
                # Convert image to base64 for OpenAI Vision API
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
            else:
                # JSON requests don't support photo processing
                # This branch should never execute since has_photo_data is always False for JSON
                logging.error("Unexpected code path: JSON request trying to process photo data")
                pass
            
            # Only proceed with OpenAI analysis if we have valid image data
            if image_base64:
                # Prepare prompt for image analysis
                prompt = f"""Analyze this plant image and provide a comprehensive assessment. IMPORTANT: Start your response with the plant identification.

Please structure your response as follows:
**PLANT IDENTIFICATION:** [Species/common name]
**HEALTH ASSESSMENT:** [Current condition and any issues]
**TREATMENT RECOMMENDATIONS:** [Specific actions needed]
**GENERAL CARE:** [Ongoing care advice]

Analysis details:
- User provided name: {plant_name if plant_name else 'Not specified - please identify from image'}
- User notes: {user_notes if user_notes else 'None provided'}
- Analysis type: {analysis_type}

Be specific about the plant species/variety so it can be properly logged."""
                
                # Call OpenAI Vision API
                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4o",  # Updated from deprecated gpt-4-vision-preview
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=500
                    )
                    
                    analysis_text = response.choices[0].message.content
                    
                except Exception as e:
                    # If OpenAI analysis fails, provide fallback
                    analysis_text = f"Image analysis failed: {str(e)}"
                    logging.error(f"OpenAI Vision API error: {e}")
            else:
                analysis_text = "No valid image data provided for analysis"
        
        else:
            # TEXT-ONLY ADVICE PATH: Provide general plant advice without photo
            
            # Check if we have gpt_analysis (enhanced mode with ChatGPT vision analysis)
            if gpt_analysis:
                # Enhanced mode: Use the provided ChatGPT analysis and enhance it
                logging.info("Enhanced mode: Using provided GPT analysis for text-only advice")
                
                # Use the enhanced analysis functions similar to enhance-analysis endpoint
                from utils.plant_operations import enhanced_plant_matching
                
                # Extract plant identification from gpt_analysis if plant_name is not provided
                if not plant_name:
                    # Try to extract plant name from the analysis
                    plant_name = extract_plant_name_from_analysis(gpt_analysis) or "Unknown Plant"
                
                # Get enhanced plant matching
                plant_match_result = enhanced_plant_matching(plant_name)
                
                # Generate enhanced care instructions
                care_enhancement = generate_personalized_care_instructions(
                    plant_identification=plant_name,
                    location=location,
                    analysis_type=analysis_type,
                    gpt_analysis=gpt_analysis
                )
                
                # Enhance diagnosis with database knowledge
                diagnosis_enhancement = enhance_diagnosis_with_database_knowledge(
                    gpt_analysis=gpt_analysis,
                    plant_identification=plant_name,
                    plant_match_result=plant_match_result,
                    user_question=user_notes
                )
                
                # Combine the analysis with enhanced information
                analysis_text = f"""Enhanced Analysis for {plant_name}:

ORIGINAL ANALYSIS:
{gpt_analysis}

ENHANCED CARE RECOMMENDATIONS:
{care_enhancement.get('specific_care_instructions', '')}

SEASONAL ADVICE:
{care_enhancement.get('seasonal_advice', '')}

TREATMENT RECOMMENDATIONS:
{diagnosis_enhancement.get('treatment_recommendations', '')}

DATABASE MATCH:
{plant_match_result.get('database_info', 'Plant not found in your database')}"""
                
            else:
                # Standard mode: Generate general plant advice
                prompt = f"""Provide comprehensive plant care advice for the following:

Plant: {plant_name}
User Questions/Notes: {user_notes if user_notes else 'General care advice needed'}
Analysis Type: {analysis_type}

Please provide detailed advice covering:
1. Watering requirements and schedule
2. Light and location preferences
3. Soil and fertilization needs
4. Common problems and prevention
5. Seasonal care tips
6. Any specific concerns mentioned in user notes

Format your response clearly and practically for plant care."""
                
                # Call OpenAI text completion API
                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=500
                    )
                    
                    analysis_text = response.choices[0].message.content
                    
                except Exception as e:
                    analysis_text = f"Unable to provide plant advice: {str(e)}"
                    logging.error(f"OpenAI text API error: {e}")
        
        # Parse analysis into structured components
        # Ensure analysis_text is a string
        if not analysis_text:
            analysis_text = "No analysis available"
        
        # Extract plant identification from AI response for automatic logging
        extracted_plant_name = plant_name  # Use provided name as fallback
        diagnosis = analysis_text
        treatment = ""
        symptoms = user_notes or ""
        confidence_score = 0.8  # Default confidence
        
        # Parse structured AI response to extract plant name and sections
        if analysis_text and "**PLANT IDENTIFICATION:**" in analysis_text:
            try:
                lines = analysis_text.split('\n')
                current_section = ""
                diagnosis_lines = []
                treatment_lines = []
                
                for line in lines:
                    line = line.strip()
                    if "**PLANT IDENTIFICATION:**" in line:
                        # Extract plant name from identification line
                        plant_id_text = line.replace("**PLANT IDENTIFICATION:**", "").strip()
                        if plant_id_text and not extracted_plant_name:
                            # Clean up the plant name (remove brackets, extra text)
                            extracted_plant_name = plant_id_text.split('(')[0].split('[')[0].strip()
                        current_section = "identification"
                    elif "**HEALTH ASSESSMENT:**" in line:
                        current_section = "health"
                    elif "**TREATMENT RECOMMENDATIONS:**" in line:
                        current_section = "treatment"
                    elif "**GENERAL CARE:**" in line:
                        current_section = "care"
                    elif line and line.startswith("**"):
                        current_section = "other"
                    elif line:
                        if current_section in ["health", "identification"]:
                            diagnosis_lines.append(line)
                        elif current_section in ["treatment", "care"]:
                            treatment_lines.append(line)
                
                # Rebuild diagnosis and treatment from parsed sections
                if diagnosis_lines:
                    diagnosis = '\n'.join(diagnosis_lines).strip()
                if treatment_lines:
                    treatment = '\n'.join(treatment_lines).strip()
                    
            except Exception as e:
                logging.warning(f"Failed to parse structured AI response: {e}")
                # Fall back to original logic
                pass
        
        # Fallback parsing for unstructured responses
        if not treatment and analysis_text and ("recommend" in analysis_text.lower() or "treatment" in analysis_text.lower()):
            lines = analysis_text.split('\n')
            diagnosis_lines = []
            treatment_lines = []
            in_treatment_section = False
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['recommend', 'treatment', 'care', 'action']):
                    in_treatment_section = True
                    treatment_lines.append(line)
                elif in_treatment_section and line.strip():
                    treatment_lines.append(line)
                elif not in_treatment_section and line.strip():
                    diagnosis_lines.append(line)
            
            if treatment_lines:
                diagnosis = '\n'.join(diagnosis_lines).strip()
                treatment = '\n'.join(treatment_lines).strip()
        
        # Create log entry if plant was identified
        log_entry_result = None
        if extracted_plant_name and has_photo_data:
            # Create log entry with or without photo storage
            photo_url = upload_result['photo_url'] if upload_result else ""
            raw_photo_url = upload_result['raw_photo_url'] if upload_result else ""
            
            log_entry_result = create_log_entry(
                plant_name=extracted_plant_name,
                photo_url=photo_url,
                raw_photo_url=raw_photo_url,
                diagnosis=diagnosis,
                treatment=treatment,
                symptoms=symptoms,
                user_notes=user_notes,
                confidence_score=confidence_score,
                analysis_type=analysis_type,
                follow_up_required=False,
                follow_up_date="",
                location=location
            )
        
        # Prepare response
        response_data = {
            'success': True,
            'analysis': {
                'diagnosis': diagnosis,
                'treatment': treatment if treatment else diagnosis,
                'confidence': confidence_score,
                'analysis_type': analysis_type,
                'advice_type': 'photo_analysis' if has_photo_data else 'text_advice_only'
            }
        }
        
        # Include identified plant name if extracted from photo
        if extracted_plant_name and extracted_plant_name != plant_name:
            response_data['analysis']['identified_plant'] = extracted_plant_name
        
        # Clear messaging about what actually happened
        if has_file:
            response_data['analysis']['photo_processed'] = True
            response_data['analysis']['photo_stored'] = True
            response_data['analysis']['note'] = "Photo was analyzed and uploaded to storage"
        elif has_photo_data:
            response_data['analysis']['photo_processed'] = True
            response_data['analysis']['photo_stored'] = False
            response_data['analysis']['note'] = "Photo was analyzed but not stored (ChatGPT mode)"
        else:
            response_data['analysis']['photo_processed'] = False
            response_data['analysis']['photo_stored'] = False
            response_data['analysis']['note'] = "Text-only advice provided - no photo was analyzed"
        
        # Add image upload info only if file was uploaded
        if has_file and upload_result:
            response_data['image_upload'] = {
                'photo_url': upload_result['raw_photo_url'],
                'filename': upload_result['filename'],
                'upload_time': upload_result['upload_time']
            }
        
        # Add log entry info if created, or explain why no log was created
        if log_entry_result and log_entry_result.get('success'):
            log_message = "Log entry successfully created in your plant database"
            if has_file:
                log_message += " (with photo)"
            else:
                log_message += " (text-based, no photo stored)"
                
            response_data['log_entry'] = {
                'log_id': log_entry_result['log_id'],
                'plant_name': log_entry_result['plant_name'],
                'created': True,
                'message': log_message
            }
        elif extracted_plant_name and has_photo_data:
            # Plant was identified from photo but log creation failed (likely not in database)
            plant_validation = validate_plant_for_log(extracted_plant_name)
            response_data['suggestions'] = {
                'plant_not_found': True,
                'identified_plant': extracted_plant_name,
                'similar_plants': plant_validation.get('suggestions', []),
                'create_new_plant': plant_validation.get('create_new_option', False),
                'message': f"I identified this as '{extracted_plant_name}' but it's not in your plant database. You can add it or link to a similar plant."
            }
            response_data['log_entry'] = {
                'created': False,
                'message': f"No log entry created - '{extracted_plant_name}' not found in plant database"
            }
        else:
            # No photo data or no plant identified
            response_data['log_entry'] = {
                'created': False,
                'message': "No log entry created - text advice only (no photo analysis performed)"
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        # Comprehensive error handling to prevent "Error talking to connector"
        error_msg = str(e)
        logging.error(f"Error in analyze-plant endpoint: {e}")
        
        # Return a user-friendly error response
        return jsonify({
            'success': False, 
            'error': f'Server error during analysis: {error_msg}',
            'advice_type': 'error',
            'analysis': {
                'diagnosis': 'Unable to complete analysis due to server error',
                'treatment': 'Please try again or contact support if the problem persists',
                'confidence': 0.0,
                'analysis_type': analysis_type if 'analysis_type' in locals() else 'unknown'
            }
        }), 500

def register_image_analysis_route(app, limiter, require_api_key):
    """Register the image analysis route with appropriate rate limiting and API key protection"""
    if not app.config.get('TESTING', False):
        app.add_url_rule(
            '/api/analyze-plant',
            view_func=limiter.limit('5 per minute')(require_api_key(analyze_plant)),  # Added API key requirement
            methods=['POST']
        )
        # Register new enhance-analysis endpoint
        app.add_url_rule(
            '/api/enhance-analysis',
            view_func=limiter.limit('10 per minute')(require_api_key(enhance_analysis)),
            methods=['POST']
        )
    else:
        app.add_url_rule(
            '/api/analyze-plant',
            view_func=require_api_key(analyze_plant),  # Added API key requirement for testing too
            methods=['POST']
        )
        # Register new enhance-analysis endpoint for testing
        app.add_url_rule(
            '/api/enhance-analysis',
            view_func=require_api_key(enhance_analysis),
            methods=['POST']
        )

# Plant Log endpoints
def create_plant_log():
    """
    Create a new plant log entry.
    Expects multipart/form-data with file upload and log details.
    """
    try:
        from utils.plant_log_operations import create_log_entry
        from utils.storage_client import upload_plant_photo, is_storage_available
        
        # Log comprehensive debug information about what ChatGPT is sending
        debug_info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "x_api_key_present": request.headers.get('x-api-key') is not None,
            "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
            "form_data_keys": list(request.form.keys()) if request.form else [],
            "form_data_values": {k: v[:100] + "..." if len(str(v)) > 100 else v for k, v in request.form.items()} if request.form else {},
            "files_present": list(request.files.keys()) if request.files else [],
            "all_headers": dict(request.headers)
        }
        
        # Add file details if present
        if request.files:
            debug_info["file_details"] = {}
            for file_key, file_obj in request.files.items():
                debug_info["file_details"][file_key] = {
                    "filename": file_obj.filename,
                    "content_type": file_obj.content_type,
                    "size": len(file_obj.read()) if file_obj else 0
                }
                if file_obj:
                    file_obj.seek(0)  # Reset file pointer after reading size
        
        # Log comprehensive debug info to server console
        logging.info(f"CREATE_PLANT_LOG_DEBUG | {debug_info}")
        
        # Get form data
        plant_name = request.form.get('plant_name', '').strip()
        user_notes = request.form.get('user_notes', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        treatment = request.form.get('treatment', '').strip()
        symptoms = request.form.get('symptoms', '').strip()
        analysis_type = request.form.get('analysis_type', 'health_assessment').strip()
        confidence_score = float(request.form.get('confidence_score', 0.8))
        follow_up_required = request.form.get('follow_up_required', 'false').lower() == 'true'
        follow_up_date = request.form.get('follow_up_date', '').strip()
        log_title = request.form.get('log_title', '').strip()
        location = request.form.get('location', '').strip()
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'plant_name is required'}), 400
        
        photo_url = ""
        raw_photo_url = ""
        
        # Handle optional file upload
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            if is_storage_available():
                try:
                    upload_result = upload_plant_photo(file, plant_name)
                    photo_url = upload_result['photo_url']
                    raw_photo_url = upload_result['raw_photo_url']
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Failed to upload image: {str(e)}'}), 500
            else:
                return jsonify({'success': False, 'error': 'Image storage not available'}), 500
        
        # Create log entry
        result = create_log_entry(
            plant_name=plant_name,
            photo_url="",  # No photo in JSON mode
            raw_photo_url="",
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes,
            confidence_score=confidence_score,
            analysis_type=analysis_type,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date,
            location=location,
            log_title=log_title
        )
        
        if result['success']:
            # Generate upload token and URL for adding photos later
            from utils.upload_token_manager import generate_upload_token
            
            upload_token = generate_upload_token(
                log_id=result['log_id'],
                plant_name=plant_name,
                token_type='log_upload',
                expiration_hours=24
            )
            
            # Force HTTPS protocol to avoid reverse proxy issues 
            upload_url = f"https://{request.host}/upload/log/{upload_token}"
            
            # Detect if user mentioned photos in their input
            photo_keywords = ['photo', 'picture', 'image', 'pic', 'camera', 'take', 'show', 'visual', 'upload']
            text_to_check = f"{user_notes} {diagnosis} {treatment} {symptoms}".lower()
            photo_mentioned = any(keyword in text_to_check for keyword in photo_keywords)
            
            # Customize response based on whether photos were mentioned
            if photo_mentioned:
                upload_instructions = f"🔥 PHOTO UPLOAD READY: Since you mentioned photos, use this link to upload them: {upload_url}"
                message = f"Log entry created successfully with photo upload ready"
            else:
                upload_instructions = f"To add a photo to this log entry, visit: {upload_url}"
                message = f"Log entry created successfully"
            
            # Enhance the response with upload information
            enhanced_result = result.copy()
            enhanced_result['upload_url'] = upload_url
            enhanced_result['upload_instructions'] = upload_instructions
            enhanced_result['message'] = message
            enhanced_result['photo_mentioned'] = photo_mentioned
            
            return jsonify(enhanced_result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error creating plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_plant_log_simple():
    """
    Create a new plant log entry using JSON (ChatGPT-friendly).
    No file upload - focuses on text-based logging.
    """
    try:
        from utils.plant_log_operations import create_log_entry
        
        # Log comprehensive debug information about what ChatGPT is sending
        debug_info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "x_api_key_present": request.headers.get('x-api-key') is not None,
            "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
            "json_data": request.get_json() if request.is_json else None,
            "all_headers": dict(request.headers)
        }
        
        # Log comprehensive debug info to server console
        logging.info(f"CREATE_PLANT_LOG_SIMPLE_DEBUG | {debug_info}")
        
        data = request.get_json()
        if data is None:
            return jsonify({'success': False, 'error': 'Missing JSON payload'}), 400
        
        # Use centralized field normalization (Phase 1 - Clean Implementation)
        from utils.field_normalization_middleware import (
            get_plant_name, get_location, get_entry, get_diagnosis, 
            get_treatment, get_symptoms, get_normalized_field,
            validate_required_fields, create_error_response_with_field_suggestions
        )
        
        # Get fields using centralized helper functions
        plant_name = get_plant_name()
        user_notes = get_normalized_field('User Notes') or get_normalized_field('user_notes', '')
        diagnosis = get_diagnosis() or ''
        treatment = get_treatment() or ''
        symptoms = get_symptoms() or ''
        analysis_type = get_normalized_field('Analysis Type') or get_normalized_field('analysis_type', 'health_assessment')
        confidence_score = float(get_normalized_field('confidence_score', 0.8))
        follow_up_required = get_normalized_field('follow_up_required', False)
        follow_up_date = get_normalized_field('Follow-up Date') or get_normalized_field('follow_up_date', '')
        log_title = get_normalized_field('Log Title') or get_normalized_field('log_title', '')
        location = get_location() or ''
        
        # Validate required fields using centralized validation
        if not plant_name:
            error_response = create_error_response_with_field_suggestions(
                "Plant name is required", 
                ['Plant Name']
            )
            return jsonify(error_response), 400
        
        # Create log entry without file upload
        result = create_log_entry(
            plant_name=plant_name,
            photo_url="",  # No photo for simple JSON endpoint
            raw_photo_url="",
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes,
            confidence_score=confidence_score,
            analysis_type=analysis_type,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date,
            log_title=log_title,
            location=location
        )
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error creating simple plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_plant_log_history(plant_name):
    """Get log history for a specific plant in journal format"""
    try:
        from utils.plant_log_operations import get_plant_log_entries, format_log_entries_as_journal
        
        # Get query parameters
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        format_type = request.args.get('format', default='standard', type=str)
        
        # Get log entries
        result = get_plant_log_entries(plant_name, limit, offset)
        
        if not result.get('success'):
            return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 400
        
        # Format as journal if requested
        if format_type == 'journal':
            journal_entries = format_log_entries_as_journal(result['log_entries'])
            result['journal_entries'] = journal_entries
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error getting plant log history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_log_entry_details(log_id):
    """Get details of a specific log entry"""
    try:
        from utils.plant_log_operations import get_log_entry_by_id, format_log_entries_as_journal
        
        format_type = request.args.get('format', default='standard', type=str)
        
        result = get_log_entry_by_id(log_id)
        
        if not result.get('success'):
            return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 400
        
        # Format as journal if requested
        if format_type == 'journal':
            journal_entries = format_log_entries_as_journal([result['log_entry']])
            if journal_entries:
                result['journal_entry'] = journal_entries[0]
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error getting log entry: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def search_plant_logs():
    """Search plant log entries with various filters"""
    try:
        from utils.plant_log_operations import search_log_entries, format_log_entries_as_journal
        
        # Get query parameters
        plant_name = request.args.get('plant_name', default='', type=str)
        query = request.args.get('q', default='', type=str)
        symptoms = request.args.get('symptoms', default='', type=str)
        date_from = request.args.get('date_from', default='', type=str)
        date_to = request.args.get('date_to', default='', type=str)
        limit = request.args.get('limit', default=20, type=int)
        format_type = request.args.get('format', default='standard', type=str)
        
        # Search log entries
        result = search_log_entries(
            plant_name=plant_name,
            query=query,
            symptoms=symptoms,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Format as journal if requested
        if format_type == 'journal':
            journal_entries = format_log_entries_as_journal(result['search_results'])
            result['journal_entries'] = journal_entries
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error searching plant logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def upload_photo_to_log(token):
    """
    Upload a photo to an existing log entry using a secure upload token.
    This endpoint supports the two-step photo upload workflow where users 
    first create a log entry, then upload photos using the provided token.
    Also updates the plant's photo in the main database if it doesn't have one.
    """
    try:
        # Add debugging to identify where the 500 error occurs
        logging.info(f"UPLOAD_DEBUG: Starting upload_photo_to_log function")
        
        from utils.upload_token_manager import validate_upload_token, mark_token_used
        logging.info(f"UPLOAD_DEBUG: Imported upload_token_manager")
        
        from utils.storage_client import upload_plant_photo, is_storage_available
        logging.info(f"UPLOAD_DEBUG: Imported storage_client")
        
        from utils.plant_log_operations import update_log_entry_photo
        from utils.plant_operations import find_plant_by_id_or_name, update_plant
        logging.info(f"UPLOAD_DEBUG: Imported plant_log_operations and plant_operations")
        
        # Token is passed as function parameter from Flask route
        logging.info(f"UPLOAD_DEBUG: Received token parameter: {token[:20] if token else 'None'}...")
        
        if not token:
            logging.error(f"UPLOAD_DEBUG: No token provided")
            return jsonify({
                'success': False, 
                'error': 'Upload token is required'
            }), 400
        
        # Validate upload token
        logging.info(f"UPLOAD_DEBUG: Validating token...")
        is_valid, token_data, error_message = validate_upload_token(token)
        logging.info(f"UPLOAD_DEBUG: Token validation result: valid={is_valid}, data={token_data}")
        
        if not is_valid or not token_data:
            logging.error(f"UPLOAD_DEBUG: Token validation failed: {error_message}")
            return jsonify({
                'success': False,
                'error': f'Invalid upload token: {error_message}'
            }), 401
        
        # Check if photo file is provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No photo file provided. Please select a photo to upload.'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No photo file selected. Please choose a file.'
            }), 400
        
        # Validate storage availability
        if not is_storage_available():
            return jsonify({
                'success': False,
                'error': 'Photo storage is currently unavailable. Please try again later.'
            }), 500
        
        # Extract log information from token
        log_id = token_data.get('log_id', '')
        plant_name = token_data.get('plant_name', '')
        
        # Upload photo to storage
        try:
            upload_result = upload_plant_photo(file, plant_name)
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'Failed to upload photo: {str(e)}'
            }), 500
        
        # Update log entry with photo URLs
        update_result = update_log_entry_photo(
            log_id, 
            upload_result['photo_url'], 
            upload_result['raw_photo_url']
        )
        
        if not update_result.get('success'):
            # Photo uploaded but log update failed - log warning but continue
            logging.warning(f"Photo uploaded but log update failed for {log_id}: {update_result.get('error')}")
        
        # Check if plant exists and needs photo update
        plant_row, plant_data = find_plant_by_id_or_name(plant_name)
        plant_update_result = {'success': False, 'message': 'Plant photo update not needed'}
        
        if plant_data:
            # Get the Photo URL field index
            headers = get_all_field_names()
            photo_url_field = get_canonical_field_name('Photo URL')
            photo_url_idx = headers.index(photo_url_field) if photo_url_field in headers else None
            
            # Check if plant has no photo
            if photo_url_idx is not None and (
                len(plant_data) <= photo_url_idx or 
                not plant_data[photo_url_idx] or 
                plant_data[photo_url_idx].strip() == ''
            ):
                # Update plant's photo
                plant_update_result = update_plant(plant_data[0], {
                    'Photo URL': upload_result['photo_url'],
                    'Raw Photo URL': upload_result['raw_photo_url']
                })
                if plant_update_result.get('success'):
                    logging.info(f"Updated plant {plant_name} with new photo from log entry")
                else:
                    logging.warning(f"Failed to update plant photo: {plant_update_result.get('error')}")
        
        # Mark token as used to prevent reuse
        user_ip = request.remote_addr or "unknown"
        mark_token_used(token, user_ip)
        
        # Return success response
        return jsonify({
            'success': True,
            'message': f'Photo uploaded successfully to {plant_name} log entry',
            'log_id': log_id,
            'plant_name': plant_name,
            'photo_upload': {
                'photo_url': upload_result['raw_photo_url'],
                'filename': upload_result['filename'],
                'upload_time': upload_result['upload_time'],
                'file_size': upload_result.get('file_size', 'unknown')
            },
            'log_update': {
                'updated': update_result.get('success', False),
                'message': update_result.get('message', 'Log entry updated with photo')
            },
            'plant_update': {
                'updated': plant_update_result.get('success', False),
                'message': plant_update_result.get('message', 'Plant photo not updated')
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error in upload_photo_to_log endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during photo upload'
        }), 500

def get_upload_token_info(token):
    """
    Get information about an upload token.
    Used by the upload page to display plant information.
    """
    try:
        from utils.upload_token_manager import validate_upload_token
        
        # Validate the token
        is_valid, token_data, error_message = validate_upload_token(token)
        
        if not is_valid or not token_data:
            return jsonify({
                'success': False,
                'error': error_message or 'Invalid upload token'
            }), 401
        
        # Return token information
        return jsonify({
            'success': True,
            'plant_name': token_data.get('plant_name', ''),
            'plant_id': token_data.get('plant_id', ''),
            'operation': token_data.get('operation', ''),
            'token_type': token_data.get('token_type', '')
        })
        
    except Exception as e:
        logging.error(f"Error getting token info: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

def serve_log_upload_page(token):
    """
    Serve the upload page for log entries.
    """
    try:
        # Verify token is valid and not expired
        token_info = get_token_info(token)
        if not token_info or not isinstance(token_info, dict):
            return jsonify({'error': 'Invalid or expired upload token'}), 401
        
        # Verify this is a log upload token
        if token_info.get('token_type') != 'log_upload':
            return jsonify({'error': 'This token is not for log photo uploads'}), 400
        
        # Get plant name and log ID for display
        plant_name = token_info.get('plant_name', 'Unknown Plant')
        log_id = token_info.get('log_id', 'Unknown Log')
        
        # Render the upload page template
        return render_template(
            'upload.html',
            token=token,
            plant_name=plant_name,
            log_id=log_id,
            upload_type='log',
            token_info_url=url_for('get_upload_token_info', token=token),
            upload_url=url_for('upload_photo_to_log', token=token)
        )
    except Exception as e:
        logging.error(f"Error serving log upload page: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def serve_plant_upload_page(token):
    """
    Serve the upload page for plant photos.
    """
    try:
        # Verify token is valid and not expired
        token_info = get_token_info(token)
        if not token_info or not isinstance(token_info, dict):
            return jsonify({'error': 'Invalid or expired upload token'}), 401
        
        # Verify this is a plant upload token
        if token_info.get('token_type') != 'plant_upload':
            return jsonify({'error': 'This token is not for plant photo uploads'}), 400
        
        # Get plant name and operation type for display
        plant_name = token_info.get('plant_name', 'Unknown Plant')
        operation = token_info.get('operation', 'update')
        
        # Render the upload page template
        return render_template(
            'upload.html',
            token=token,
            plant_name=plant_name,
            operation=operation,
            upload_type='plant',
            token_info_url=url_for('get_upload_token_info', token=token),
            upload_url=url_for('upload_photo_to_plant', token=token)
        )
    except Exception as e:
        logging.error(f"Error serving plant upload page: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def upload_photo_to_plant(token):
    """
    Upload a photo to a plant using a secure upload token.
    This endpoint supports the two-step photo upload workflow where users 
    first create/update a plant, then upload photos using the provided token.
    """
    try:
        # Add debugging to identify where errors occur
        logging.info(f"UPLOAD_DEBUG: Starting upload_photo_to_plant function")
        
        from utils.upload_token_manager import validate_upload_token, mark_token_used
        logging.info(f"UPLOAD_DEBUG: Imported upload_token_manager")
        
        from utils.storage_client import upload_plant_photo, is_storage_available
        logging.info(f"UPLOAD_DEBUG: Imported storage_client")
        
        from utils.plant_operations import update_plant
        logging.info(f"UPLOAD_DEBUG: Imported plant_operations")
        
        # Token is passed as function parameter from Flask route
        logging.info(f"UPLOAD_DEBUG: Received token parameter: {token[:20] if token else 'None'}...")
        
        if not token:
            logging.error(f"UPLOAD_DEBUG: No token provided")
            return jsonify({
                'success': False, 
                'error': 'Upload token is required'
            }), 400
        
        # Validate upload token
        logging.info(f"UPLOAD_DEBUG: Validating token...")
        is_valid, token_data, error_message = validate_upload_token(token)
        logging.info(f"UPLOAD_DEBUG: Token validation result: valid={is_valid}, data={token_data}")
        
        if not is_valid or not token_data:
            logging.error(f"UPLOAD_DEBUG: Token validation failed: {error_message}")
            return jsonify({
                'success': False,
                'error': f'Invalid upload token: {error_message}'
            }), 401
            
        # Verify this is a plant upload token
        if token_data.get('token_type') != 'plant_upload':
            return jsonify({
                'success': False,
                'error': 'Invalid token type. This token is not for plant photo uploads.'
            }), 400
        
        # Check if photo file is provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No photo file provided. Please select a photo to upload.'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No photo file selected. Please choose a file.'
            }), 400
        
        # Validate storage availability
        if not is_storage_available():
            return jsonify({
                'success': False,
                'error': 'Photo storage is currently unavailable. Please try again later.'
            }), 500
        
        # Extract plant information from token
        plant_id = token_data.get('plant_id', '')
        plant_name = token_data.get('plant_name', '')
        
        # Upload photo to storage
        try:
            upload_result = upload_plant_photo(file, plant_name)
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'Failed to upload photo: {str(e)}'
            }), 500
        
        # Update plant record with photo URLs - use raw URL since add_plant_with_fields will wrap it
        update_data = {
            'Photo URL': upload_result['raw_photo_url'],  # Use raw URL, not wrapped one
            'Raw Photo URL': upload_result['raw_photo_url']
        }
        
        # Always use update_plant since the plant already exists
        update_result = update_plant(plant_id, update_data)
        
        if not update_result.get('success'):
            # Photo uploaded but plant update failed - log warning but continue
            logging.warning(f"Photo uploaded but plant update failed for {plant_id}: {update_result.get('error')}")
        
        # Mark token as used to prevent reuse
        user_ip = request.remote_addr or "unknown"
        mark_token_used(token, user_ip)
        
        # Return success response
        return jsonify({
            'success': True,
            'message': f'Photo uploaded successfully to plant: {plant_name}',
            'plant_id': plant_id,
            'plant_name': plant_name,
            'photo_upload': {
                'photo_url': upload_result['raw_photo_url'],
                'filename': upload_result['filename'],
                'upload_time': upload_result['upload_time'],
                'file_size': upload_result.get('file_size', 'unknown')
            },
            'plant_update': {
                'updated': update_result.get('success', False),
                'message': update_result.get('message', 'Plant record updated with photo')
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error in upload_photo_to_plant endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during photo upload'
        }), 500

def register_plant_log_routes(app, limiter, require_api_key):
    """Register plant log API routes"""
    if not app.config.get('TESTING', False):
        # POST /api/plants/log - Create log entry with file upload (requires API key)
        app.add_url_rule(
            '/api/plants/log',
            view_func=limiter.limit('10 per minute')(require_api_key(create_plant_log)),
            methods=['POST']
        )
        
        # POST /api/plants/log/simple - Create log entry with JSON (ChatGPT-friendly)
        app.add_url_rule(
            '/api/plants/log/simple',
            view_func=limiter.limit('10 per minute')(require_api_key(create_plant_log_simple)),
            methods=['POST']
        )
        
        # POST /upload/log/{token} - Upload photo to existing log entry (no API key needed, token is auth)
        app.add_url_rule(
            '/upload/log/<token>',
            view_func=limiter.limit('20 per minute')(upload_photo_to_log),
            methods=['POST']
        )
        
        # GET /upload/log/{token} - Serve upload page for specific token (no API key needed, token is auth)
        app.add_url_rule(
            '/upload/log/<token>',
            view_func=limiter.limit('60 per minute')(serve_log_upload_page),
            methods=['GET']
        )
        
        # GET routes (no API key required for reading)
        app.add_url_rule(
            '/api/plants/<plant_name>/log',
            view_func=limiter.limit('30 per minute')(get_plant_log_history),
            methods=['GET']
        )
        
        app.add_url_rule(
            '/api/plants/log/<log_id>',
            view_func=limiter.limit('30 per minute')(get_log_entry_details),
            methods=['GET']
        )
        
        app.add_url_rule(
            '/api/plants/log/search',
            view_func=limiter.limit('30 per minute')(search_plant_logs),
            methods=['GET']
        )
    else:
        # Testing mode - no rate limits
        app.add_url_rule('/api/plants/log', view_func=require_api_key(create_plant_log), methods=['POST'])
        app.add_url_rule('/api/plants/log/simple', view_func=require_api_key(create_plant_log_simple), methods=['POST'])
        app.add_url_rule('/upload/log/<token>', view_func=upload_photo_to_log, methods=['POST'])
        app.add_url_rule('/upload/log/<token>', view_func=serve_log_upload_page, methods=['GET'])
        app.add_url_rule('/api/plants/<plant_name>/log', view_func=get_plant_log_history, methods=['GET'])
        app.add_url_rule('/api/plants/log/<log_id>', view_func=get_log_entry_details, methods=['GET'])
        app.add_url_rule('/api/plants/log/search', view_func=search_plant_logs, methods=['GET'])

def register_plant_routes(app, limiter, require_api_key):
    """Register plant API routes"""
    if not app.config.get('TESTING', False):
        # POST /upload/plant/{token} - Upload photo to plant (no API key needed, token is auth)
        app.add_url_rule(
            '/upload/plant/<token>',
            view_func=limiter.limit('20 per minute')(upload_photo_to_plant),
            methods=['POST']
        )
        
        # GET /upload/plant/{token} - Serve upload page for plant photo (no API key needed, token is auth)
        app.add_url_rule(
            '/upload/plant/<token>',
            view_func=limiter.limit('60 per minute')(serve_plant_upload_page),
            methods=['GET']
        )
        
        # GET /api/upload/info/{token} - Get token info for upload page
        app.add_url_rule(
            '/api/upload/info/<token>',
            view_func=limiter.limit('60 per minute')(get_upload_token_info),
            methods=['GET']
        )
    else:
        # Testing mode - no rate limits
        app.add_url_rule('/upload/plant/<token>', view_func=upload_photo_to_plant, methods=['POST'])
        app.add_url_rule('/upload/plant/<token>', view_func=serve_plant_upload_page, methods=['GET'])
        app.add_url_rule('/api/upload/info/<token>', view_func=get_upload_token_info, methods=['GET'])

def create_app(testing=False):
    """
    Create and configure the Flask app. If testing=True, disables rate limiting.
    """
    app = Flask(__name__, template_folder='../templates')  # Configure template folder
    CORS(app)
    # Set config flags
    app.config['TESTING'] = testing
    app.config['RATELIMIT_ENABLED'] = not testing
    # Set up Flask-Limiter with production-ready storage
    if not testing:
        # Try to use Redis for production rate limiting storage
        redis_url = os.environ.get('REDIS_URL')
        if redis_url:
            # Production: Use Redis for persistent, scalable rate limiting
            try:
                limiter = Limiter(
                    key_func=get_remote_address,
                    app=app,
                    default_limits=[],
                    storage_uri=redis_url,
                    on_breach=lambda limit: logging.warning(f"Rate limit exceeded: {limit}")
                )
                logging.info("Rate limiting configured with Redis storage")
            except Exception as e:
                logging.warning(f"Redis connection failed, falling back to in-memory storage: {e}")
                limiter = Limiter(
                    key_func=get_remote_address,
                    app=app,
                    default_limits=[]
                )
        else:
            # Fallback: Use in-memory storage with warning
            limiter = Limiter(
                key_func=get_remote_address,
                app=app,
                default_limits=[]
            )
            logging.warning("REDIS_URL not set. Using in-memory rate limiting. Set REDIS_URL for production.")
    else:
        # Testing: Use simple in-memory storage without warnings
        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            default_limits=[]
        )
    # Set up additional logging for auditability
    logger = logging.getLogger()
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    # Register all routes after config is set
    register_routes(app, limiter, require_api_key)
    # Register image analysis route
    register_image_analysis_route(app, limiter, require_api_key)
    # Register plant log routes
    register_plant_log_routes(app, limiter, require_api_key)
    # Register plant routes
    register_plant_routes(app, limiter, require_api_key)
    # Register weather routes
    from api.weather_service import register_weather_routes
    register_weather_routes(app, limiter)
    
    return app



# Only run the app if this file is executed directly (not imported)
if __name__ == '__main__':
    import os
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 