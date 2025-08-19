"""
Plant Maintenance Routes

Handles plant maintenance operations including moving plants between locations,
updating container details, and managing plant placement using natural language commands.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging

# Create the plant maintenance blueprint
plant_maintenance_bp = Blueprint('plant_maintenance', __name__, url_prefix='/api/plants')

# Set up logging for this module
logger = logging.getLogger(__name__)


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET']
@plant_maintenance_bp.route('/maintenance', methods=['GET'])  # WORKAROUND: was POST
@require_api_key
def plant_maintenance():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    
    Plant Maintenance Endpoint - Move plants between locations and update container details.
    
    This endpoint allows users to:
    - Move plants between locations
    - Add plants to new locations
    - Remove plants from specific locations
    - Update container details (size, type, material) with partial updates allowed
    
    Query Parameters:
        plant_name (required): Exact plant name from AI
        destination_location (optional): New location name (null/empty for removal or container only change)
        source_location (optional): Current location (for ambiguity resolution or container change)
        container_size (optional): New container size
        container_type (optional): New container type  
        container_material (optional): New container material
        
    Returns:
        JSON response with success status, operation details, or error information
    """
    try:
        from flask import request as flask_request
        from utils.plant_maintenance_operations import process_plant_maintenance
        
        logger.info("Plant maintenance endpoint called")
        logger.info(f"Query parameters: {dict(flask_request.args)}")
        
        # WORKAROUND: Extract parameters from query string
        plant_name = flask_request.args.get('plant_name')
        destination_location = flask_request.args.get('destination_location')
        source_location = flask_request.args.get('source_location')
        container_size = flask_request.args.get('container_size')
        container_type = flask_request.args.get('container_type')
        container_material = flask_request.args.get('container_material')
        
        # Validate required parameters
        if not plant_name:
            logger.warning("Plant maintenance called without plant_name parameter")
            return jsonify({
                "success": False,
                "error": "Plant name is required for maintenance operations",
                "message": "Use ?plant_name=YourPlantName in the URL",
                "workaround": "GET endpoint due to ChatGPT POST issue",
                "received_args": dict(flask_request.args)
            }), 400
        
        # Validate that at least one operation is specified
        has_location_operation = bool(destination_location or source_location)
        has_container_operation = any([container_size, container_type, container_material])
        
        if not has_location_operation and not has_container_operation:
            logger.warning(f"Plant maintenance called for '{plant_name}' without any operations specified")
            return jsonify({
                "success": False,
                "error": "At least one operation must be specified",
                "message": "Specify destination_location/source_location for moves or container attributes for updates",
                "available_operations": [
                    "Move plant: ?destination_location=NewLocation&source_location=OldLocation",
                    "Add location: ?destination_location=NewLocation", 
                    "Remove from location: ?source_location=OldLocation",
                    "Update container: ?container_size=Large&container_type=Pot&container_material=Ceramic"
                ],
                "received_args": dict(flask_request.args)
            }), 400
        
        # Log the operation details
        logger.info(f"Processing maintenance for plant '{plant_name}':")
        logger.info(f"  - Destination location: {destination_location}")
        logger.info(f"  - Source location: {source_location}")
        logger.info(f"  - Container updates: size={container_size}, type={container_type}, material={container_material}")
        
        # Process the plant maintenance operation
        result = process_plant_maintenance(
            plant_name=plant_name.strip(),
            destination_location=destination_location.strip() if destination_location else None,
            source_location=source_location.strip() if source_location else None,
            container_size=container_size.strip() if container_size else None,
            container_type=container_type.strip() if container_type else None,
            container_material=container_material.strip() if container_material else None
        )
        
        # Log the result
        if result.get('success', False):
            logger.info(f"Plant maintenance successful for '{plant_name}': {result.get('message', 'Operation completed')}")
        else:
            logger.warning(f"Plant maintenance failed for '{plant_name}': {result.get('error', 'Unknown error')}")
        
        # Return appropriate HTTP status code based on result
        if result.get('success', False):
            # Check if this is an ambiguity error (which should return 422 for user action required)
            return jsonify(result), 200
        else:
            # Check for specific error types to return appropriate status codes
            error_message = result.get('error', '').lower()
            
            if 'not found' in error_message:
                return jsonify(result), 404
            elif 'multiple locations found' in error_message or 'ambiguity' in error_message:
                return jsonify(result), 422  # Unprocessable Entity - user needs to provide more info
            elif 'required' in error_message or 'validation' in error_message:
                return jsonify(result), 400  # Bad Request
            else:
                return jsonify(result), 500  # Internal Server Error
        
    except Exception as e:
        logger.error(f"Unexpected error in plant maintenance endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred while processing the maintenance request",
            "details": str(e) if logger.level <= logging.DEBUG else "Enable debug logging for details"
        }), 500


# Additional utility endpoint for debugging and testing
@plant_maintenance_bp.route('/maintenance/info', methods=['GET'])
@require_api_key
def maintenance_info():
    """
    Get information about the plant maintenance endpoint capabilities.
    Useful for debugging and understanding available operations.
    """
    try:
        return jsonify({
            "success": True,
            "endpoint": "/api/plants/maintenance",
            "method": "GET",
            "description": "Plant maintenance operations endpoint",
            "capabilities": {
                "move_plants": "Transfer plants between locations",
                "add_locations": "Add new location for existing plant",
                "remove_plants": "Remove plant from specific location", 
                "update_containers": "Change container size, type, material (partial updates allowed)"
            },
            "parameters": {
                "required": {
                    "plant_name": "Exact plant name from AI"
                },
                "optional": {
                    "destination_location": "New location name (null/empty for removal or container only change)",
                    "source_location": "Current location (for ambiguity resolution or container change)",
                    "container_size": "New container size",
                    "container_type": "New container type",
                    "container_material": "New container material"
                }
            },
            "example_operations": {
                "move_plant": "/api/plants/maintenance?plant_name=Tropical Hibiscus&source_location=Patio&destination_location=Pool Path&container_size=Large",
                "add_location": "/api/plants/maintenance?plant_name=Tropical Hibiscus&destination_location=Garden Bed",
                "remove_plant": "/api/plants/maintenance?plant_name=Tropical Hibiscus&source_location=Patio",
                "update_container": "/api/plants/maintenance?plant_name=Tropical Hibiscus&container_size=Large&container_type=Ceramic"
            },
            "response_formats": {
                "success": {
                    "success": True,
                    "message": "Plant moved successfully",
                    "data": {
                        "plant_name": "Tropical Hibiscus",
                        "old_locations": ["Patio"],
                        "new_locations": ["Pool Path"],
                        "container_updates": {"size": "Large"}
                    }
                },
                "ambiguity_error": {
                    "success": False,
                    "error": "Multiple locations found",
                    "options": {
                        "locations": ["Front Patio", "Back Patio", "Side Patio"],
                        "message": "Please specify which patio location"
                    }
                }
            },
            "workaround_note": "Currently using GET method due to ChatGPT POST limitation"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in maintenance info endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve maintenance info",
            "details": str(e)
        }), 500
