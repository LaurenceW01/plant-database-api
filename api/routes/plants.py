"""
Plant Management Routes

Handles all plant-related endpoints including CRUD operations,
search functionality, and plant context retrieval.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging

# Create the plants blueprint
plants_bp = Blueprint('plants', __name__, url_prefix='/api/plants')


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET'] 
# Changed: request.get_json() → request.args
@plants_bp.route('/add', methods=['GET'])  # WORKAROUND: was POST
def add_plant_new():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    
    Original: Phase 2 direct implementation: Add a new plant with action-based URL.
    Provides semantic alignment: addPlant operationId → /api/plants/add URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    # WORKAROUND: Convert GET query params to POST body format
    from flask import request as flask_request, g
    
    # Extract parameters from query string
    plant_name = flask_request.args.get('plant_name') or flask_request.args.get('Plant Name')
    location = flask_request.args.get('location')
    
    # Validate required fields  
    if not plant_name:
        return jsonify({
            "error": "Plant name is required for adding a plant",
            "message": "Use ?plant_name=YourPlantName in the URL",
            "workaround": "GET endpoint due to ChatGPT POST issue",
            "received_args": dict(flask_request.args)
        }), 400
    
    # WORKAROUND: Simulate POST request body by storing in both request and g objects
    # This allows the existing add_plant logic to work without modification
    simulated_json = {
        'plant_name': plant_name
    }
    if location:
        simulated_json['location'] = location
    
    # Temporarily override the request method and store JSON data
    original_method = flask_request.method
    original_get_json = flask_request.get_json
    
    # Store original g data if any
    original_normalized_data = getattr(g, 'normalized_request_data', None)
    original_original_data = getattr(g, 'original_request_data', None)
    
    # Mock the request.get_json() to return our simulated data
    flask_request.get_json = lambda: simulated_json
    flask_request.method = 'POST'  # Temporarily set to POST for compatibility
    
    # Set g object data for field normalization middleware
    g.normalized_request_data = simulated_json.copy()
    g.original_request_data = simulated_json.copy()
    
    try:
        # Import the core business logic function
        from api.main import add_plant
        
        # Direct implementation using existing add_plant logic with field normalization
        response = add_plant()
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
    
    # Mark as Phase 2 direct implementation in response
    if hasattr(response, 'get_json'):
        try:
            data = response.get_json()
            if isinstance(data, dict):
                data['phase2_direct'] = True
                data['endpoint_type'] = 'direct_implementation'
                return jsonify(data), response.status_code
        except:
            pass
    
    return response


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['GET', 'POST'] → methods=['GET'] (removed POST)
@plants_bp.route('/search', methods=['GET'])  # WORKAROUND: removed POST
def search_plants_new():
    """
    Phase 2 direct implementation: Search for plants with action-based URL.
    Provides semantic alignment: searchPlants operationId → /api/plants/search URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    # Import the original search function
    from api.main import list_or_search_plants
    
    # Direct implementation using existing search logic
    response = list_or_search_plants()
    
    # Mark as Phase 2 direct implementation in response
    if hasattr(response, 'get_json'):
        try:
            data = response.get_json()
            if isinstance(data, dict):
                data['phase2_direct'] = True
                data['endpoint_type'] = 'direct_implementation'
                return jsonify(data), response.status_code
        except:
            pass
    
    return response


@plants_bp.route('/get/<id_or_name>', methods=['GET'])
def get_plant_new(id_or_name):
    """
    Phase 2 direct implementation: Get plant details with action-based URL.
    Provides semantic alignment: getPlant operationId → /api/plants/get/{id} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    # Import the original get function
    from api.main import get_plant_details
    
    # Direct implementation using existing get logic
    response = get_plant_details(id_or_name)
    
    # Mark as Phase 2 direct implementation in response
    if hasattr(response, 'get_json'):
        try:
            data = response.get_json()
            if isinstance(data, dict):
                data['phase2_direct'] = True
                data['endpoint_type'] = 'direct_implementation'
                return jsonify(data), response.status_code
        except:
            pass
    
    return response


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT PUT requests work again
# Changed: methods=['PUT'] → methods=['GET']
@plants_bp.route('/update/<id_or_name>', methods=['GET'])  # WORKAROUND: was PUT
def update_plant_new(id_or_name):
    """
    CHATGPT WORKAROUND: Temporarily converted from PUT to GET due to ChatGPT platform issue.
    
    Phase 2 direct implementation: Update plant with action-based URL.
    Provides semantic alignment: updatePlant operationId → /api/plants/update/{id} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    # WORKAROUND: Convert GET query params to PUT body format
    from flask import request as flask_request, g
    
    # Extract all parameters from query string that could be plant fields
    simulated_json = {}
    for key in flask_request.args.keys():
        value = flask_request.args.get(key)
        if value:  # Only include non-empty values
            simulated_json[key] = value
    
    # Validate that we have at least some update data
    if not simulated_json:
        return jsonify({
            "error": "No update parameters provided",
            "message": "Use query parameters to specify fields to update (e.g., ?plant_name=NewName&location=NewLocation)",
            "workaround": "GET endpoint due to ChatGPT PUT issue",
            "received_args": dict(flask_request.args)
        }), 400
    
    # WORKAROUND: Simulate PUT request body by storing in both request and g objects
    # This allows the existing update_plant logic to work without modification
    
    # Store original data and mock request/g objects
    original_method = flask_request.method
    original_get_json = flask_request.get_json
    original_normalized_data = getattr(g, 'normalized_request_data', None)
    original_original_data = getattr(g, 'original_request_data', None)
    
    # Mock the request.get_json() to return our simulated data
    flask_request.get_json = lambda: simulated_json
    flask_request.method = 'PUT'  # Temporarily set to PUT for compatibility
    
    # Set g object data for field normalization middleware
    g.normalized_request_data = simulated_json.copy()
    g.original_request_data = simulated_json.copy()
    
    try:
        # Import the original update function
        from api.main import update_plant
        
        # Direct implementation using existing update logic
        response = update_plant(id_or_name)
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
    
    # Mark as Phase 2 direct implementation in response
    if hasattr(response, 'get_json'):
        try:
            data = response.get_json()
            if isinstance(data, dict):
                data['phase2_direct'] = True
                data['endpoint_type'] = 'direct_implementation'
                data['workaround'] = 'GET converted from PUT'
                return jsonify(data), response.status_code
        except:
            pass
    
    return response


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT PUT requests work again
# Changed: methods=['PUT'] → methods=['GET']
@plants_bp.route('/update', methods=['GET'])  # WORKAROUND: was PUT
def update_plant_flexible():
    """
    CHATGPT WORKAROUND: Temporarily converted from PUT to GET due to ChatGPT platform issue.
    
    Flexible update endpoint that accepts plant ID in query parameters.
    This provides ChatGPT-friendly alternative when ID is in request parameters instead of URL path.
    """
    import logging
    from utils.field_normalization_middleware import get_normalized_field
    from api.main import update_plant
    from flask import request as flask_request, g
    
    logger = logging.getLogger(__name__)
    
    # WORKAROUND: Convert GET query params to PUT body format
    # Extract all parameters from query string that could be plant fields
    simulated_json = {}
    for key in flask_request.args.keys():
        value = flask_request.args.get(key)
        if value:  # Only include non-empty values
            simulated_json[key] = value
    
    logger.info(f"🔄 UPDATE_PLANT_FLEXIBLE called with {len(simulated_json)} fields")
    logger.info(f"📝 Request parameters: {list(simulated_json.keys())}")
    
    # Validate that we have parameters
    if not simulated_json:
        return jsonify({
            "error": "No update parameters provided",
            "message": "Use query parameters to specify fields to update, including plant ID (e.g., ?id=123&plant_name=NewName)",
            "workaround": "GET endpoint due to ChatGPT PUT issue",
            "received_args": dict(flask_request.args)
        }), 400
    
    # WORKAROUND: Simulate PUT request body by storing in both request and g objects
    # This allows the existing update_plant logic to work without modification
    
    # Store original data and mock request/g objects
    original_method = flask_request.method
    original_get_json = flask_request.get_json
    original_normalized_data = getattr(g, 'normalized_request_data', None)
    original_original_data = getattr(g, 'original_request_data', None)
    
    # Mock the request.get_json() to return our simulated data
    flask_request.get_json = lambda: simulated_json
    flask_request.method = 'PUT'  # Temporarily set to PUT for compatibility
    
    # Set g object data for field normalization middleware
    g.normalized_request_data = simulated_json.copy()
    g.original_request_data = simulated_json.copy()
    
    try:
        # Get plant ID from simulated request body using field normalization
        plant_id = get_normalized_field('id') or get_normalized_field('plant_id')
        
        if not plant_id:
            logger.error("❌ No plant ID found in request parameters")
            return jsonify({
                'error': 'Plant ID is required in query parameters (use "id", "plant_id", or "Plant_ID" parameter)',
                'workaround': 'GET endpoint due to ChatGPT PUT issue',
                'received_args': dict(flask_request.args)
            }), 400
        
        logger.info(f"🎯 Plant ID identified: {plant_id}")
        
        # Call the same update logic but extract ID from simulated body
        response = update_plant(plant_id)
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
    
    # Mark as flexible endpoint in response
    if hasattr(response, 'get_json'):
        try:
            data = response.get_json()
            if isinstance(data, dict):
                data['endpoint_type'] = 'flexible_update'
                data['note'] = 'Used plant ID from query parameters'
                data['workaround'] = 'GET converted from PUT'
                return jsonify(data), response.status_code
        except:
            pass
    
    return response


@plants_bp.route('/remove/<id_or_name>', methods=['DELETE'])
def remove_plant_new(id_or_name):
    """
    Phase 2 direct implementation: Remove plant with action-based URL.
    Provides semantic alignment: removePlant operationId → /api/plants/remove/{id} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    # For now, return 501 Not Implemented (original behavior)
    return jsonify({
        "error": "Plant removal not implemented",
        "message": "Delete functionality is not available for safety reasons",
        "suggested_action": "Use update to mark as inactive instead",
        "phase2_direct": True,
        "endpoint_type": "direct_implementation"
    }), 501



# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again 
# Changed: methods=['GET', 'POST'] → methods=['GET'] (removed POST)
@plants_bp.route('/get-context/<plant_id>', methods=['GET'])  # WORKAROUND: removed POST
def get_plant_context_new(plant_id):
    """
    Phase 2 direct implementation: Get comprehensive plant context with location/container intelligence.
    Provides semantic alignment: getPlantContext operationId → /api/plants/get-context/{id} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    
    Supports both plant IDs (numeric) and plant names for ChatGPT compatibility.
    """
    try:
        from utils.locations_operations import get_plant_location_context
        from utils.plant_operations import find_plant_by_id_or_name
        
        # Convert plant name to ID if necessary (ChatGPT often sends plant names)
        actual_plant_id = plant_id
        if not plant_id.isdigit():
            # Try to find plant by name and get its ID
            plant_row, plant_data = find_plant_by_id_or_name(plant_id)
            if plant_row is not None and plant_data:
                actual_plant_id = str(plant_data[0])  # Use the actual Plant ID from sheet, not row number
                logging.info(f"Converted plant name '{plant_id}' to ID '{actual_plant_id}'")
            else:
                return jsonify({
                    "error": f"Plant '{plant_id}' not found in database",
                    "message": "Please check the plant name and try again",
                    "plant_id": plant_id,
                    "phase2_direct": True
                }), 404
        
        # Generate comprehensive context using numeric ID
        context_result = get_plant_location_context(actual_plant_id)
        
        if context_result:
            return jsonify({
                'contexts': context_result,
                'plant_id': actual_plant_id,
                'original_query': plant_id,
                'phase2_direct': True,
                'endpoint_type': 'direct_implementation'
            }), 200
        else:
            return jsonify({
                "error": f"No containers found for plant {plant_id}",
                "message": "This plant may not have any containers assigned in the locations database",
                "plant_id": actual_plant_id,
                "original_query": plant_id,
                "phase2_direct": True
            }), 404
            
    except Exception as e:
        logging.error(f"Error getting plant context for '{plant_id}': {e}")
        return jsonify({
            "error": "Failed to get plant context",
            "details": str(e),
            "plant_id": plant_id,
            "phase2_direct": True
        }), 500


@plants_bp.route('/get-all-fields/<id_or_name>', methods=['GET'])
def get_plant_all_fields(id_or_name):
    """
    NEW ENDPOINT: Get all plant fields from the plant spreadsheet for a given plant name or ID.
    
    This is a completely new endpoint that retrieves all available field data
    for a specific plant without modifying any existing functionality.
    
    Supports both plant IDs (numeric) and plant names for maximum compatibility.
    Returns all fields from the spreadsheet row for the specified plant.
    
    Args:
        id_or_name (str): Plant ID or plant name to retrieve all fields for
        
    Returns:
        JSON response containing all plant fields or error message
    """
    import logging
    
    try:
        # Use existing database operations without modification
        from utils.plant_database_operations import find_plant_by_id_or_name, get_all_plants
        from models.field_config import get_all_field_names
        
        logging.info(f"🔍 GET_PLANT_ALL_FIELDS called for: '{id_or_name}'")
        
        # Find the plant using existing function (no modification)
        plant_row, plant_data = find_plant_by_id_or_name(id_or_name)
        
        if plant_row is None or not plant_data:
            logging.error(f"❌ Plant not found: '{id_or_name}'")
            return jsonify({
                "success": False,
                "error": f"Plant '{id_or_name}' not found in database",
                "message": "Please check the plant name or ID and try again",
                "query": id_or_name,
                "endpoint_type": "get_all_fields"
            }), 404
        
        # Get all field names from field configuration (no modification)
        all_field_names = get_all_field_names()
        
        # Get full plant data to ensure we have all fields
        all_plants = get_all_plants()
        
        # Find the matching plant in the full dataset to get all fields
        target_plant = None
        plant_id = str(plant_data[0]) if plant_data else None
        
        for plant in all_plants:
            if plant.get('id', '') == plant_id:
                target_plant = plant
                break
        
        if target_plant is None:
            # Fallback: create plant object from row data and field names
            target_plant = {}
            header_result = []
            
            # Get header from sheets to map fields correctly
            from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
            try:
                result = sheets_client.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=RANGE_NAME
                ).execute()
                values = result.get('values', [])
                header_result = values[0] if values else []
            except Exception as header_error:
                logging.warning(f"Could not get header: {header_error}")
                header_result = all_field_names  # Fallback to field config
            
            # Map plant data to field names
            for i, field_name in enumerate(header_result):
                if i < len(plant_data):
                    target_plant[field_name] = plant_data[i]
                else:
                    target_plant[field_name] = ""
        
        # Ensure all configured fields are present
        for field_name in all_field_names:
            if field_name not in target_plant:
                target_plant[field_name] = ""
        
        # Count non-empty fields for response metadata
        non_empty_fields = sum(1 for value in target_plant.values() if value and str(value).strip())
        
        logging.info(f"✅ Retrieved all fields for plant: '{target_plant.get('plant_name', id_or_name)}'")
        logging.info(f"📊 Total fields: {len(target_plant)}, Non-empty: {non_empty_fields}")
        
        return jsonify({
            "success": True,
            "plant": target_plant,
            "metadata": {
                "query": id_or_name,
                "plant_id": plant_id,
                "plant_name": target_plant.get('plant_name', ''),
                "total_fields": len(target_plant),
                "non_empty_fields": non_empty_fields,
                "field_names": list(target_plant.keys())
            },
            "endpoint_type": "get_all_fields",
            "note": "All available plant fields from spreadsheet"
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting all plant fields for '{id_or_name}': {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve plant fields",
            "details": str(e),
            "query": id_or_name,
            "endpoint_type": "get_all_fields"
        }), 500


# Legacy route redirects for backward compatibility
@plants_bp.route('', methods=['GET'])
@plants_bp.route('/all', methods=['GET'])
def legacy_search_plants():
    """Legacy redirect to maintain backward compatibility"""
    return search_plants_new()


@plants_bp.route('/<id_or_name>', methods=['GET'])
def legacy_get_plant(id_or_name):
    """Legacy redirect to maintain backward compatibility"""
    return get_plant_new(id_or_name)


@plants_bp.route('/<plant_id>/location-context', methods=['GET'])
@plants_bp.route('/<plant_id>/context', methods=['GET'])
def legacy_get_plant_context(plant_id):
    """Legacy redirect to maintain backward compatibility"""
    return get_plant_context_new(plant_id)
