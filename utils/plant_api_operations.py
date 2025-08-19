import logging
from typing import List, Dict, Optional, Tuple, Union, Any
from flask import request, jsonify, g

logger = logging.getLogger(__name__)

def add_plant_api():
    """Core plant addition logic for API endpoints"""
    try:
        from .upload_token_manager import generate_upload_token
        from .field_normalization_middleware import get_normalized_field, get_plant_name
        from .plant_photo_operations import add_plant_with_fields
        
        # Get plant data using field normalization and convert to canonical format
        plant_name = get_plant_name()
        
        plant_data = {
            'plant_name': plant_name,
            'description': get_normalized_field('description', ''),
            'light_requirements': get_normalized_field('light_requirements', ''),
            'watering_needs': get_normalized_field('watering_needs', ''),
            'soil_preferences': get_normalized_field('soil_preferences', ''),
            'frost_tolerance': get_normalized_field('frost_tolerance', ''),
            'pruning_instructions': get_normalized_field('pruning_instructions', ''),
            'fertilizing_schedule': get_normalized_field('fertilizing_schedule', ''),
            'location': get_normalized_field('location', ''),
            'care_notes': get_normalized_field('care_notes', '')
        }
        
        # Validate required fields
        if not plant_data['plant_name']:
            return jsonify({'error': 'Plant name is required'}), 400
        
        # Add plant to database
        result = add_plant_with_fields(plant_data)
        
        if result.get('success'):
            # Generate upload token for photo
            upload_token = generate_upload_token(
                plant_id=result.get('plant_id', result.get('id')),
                plant_name=plant_data['plant_name'],
                token_type='plant_upload',
                operation='add',
                expiration_hours=24
            )
            
            upload_url = f"https://{request.host}/api/photos/upload-for-plant/{upload_token}"
            
            return jsonify({
                **result,
                'upload_url': upload_url,
                'upload_instructions': f"To add a photo, visit: {upload_url}"
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error adding plant: {e}")
        return jsonify({'error': str(e)}), 500

def update_plant_api(id_or_name):
    """Core plant update logic for API endpoints"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from .field_normalization_middleware import get_normalized_field
        from .plant_database_operations import update_plant
        
        logger.info(f"🔧 UPDATE_PLANT_API called for plant: {id_or_name}")
        
        # Build update data from ALL normalized fields (not just hardcoded ones)
        update_data = {}
        
        # Get all normalized data from the request
        if hasattr(g, 'normalized_request_data') and g.normalized_request_data:
            normalized_data = g.normalized_request_data
            logger.info(f"📊 Processing {len(normalized_data)} normalized fields")
            
            # Map normalized field names back to canonical format using centralized config
            from models.field_config import FIELD_NAMES, LOG_FIELD_NAMES
            
            def underscore_to_canonical(underscore_name: str) -> str:
                """Convert underscore format back to canonical field name"""
                # Convert underscore to space and title case
                spaced = underscore_name.replace('_', ' ').title()
                
                # Check if this matches any canonical field name
                all_canonical_names = FIELD_NAMES + LOG_FIELD_NAMES
                for canonical in all_canonical_names:
                    if canonical.lower().replace(' ', '_').replace('-', '_') == underscore_name.lower():
                        return canonical
                
                # If no exact match, return the spaced version
                return spaced
            
            canonical_field_mappings = {}
            # Build mapping dynamically from centralized config
            for field_name in FIELD_NAMES + LOG_FIELD_NAMES:
                underscore_version = field_name.lower().replace(' ', '_').replace('-', '_')
                canonical_field_mappings[underscore_version] = field_name
            
            # Convert normalized fields back to canonical names for database update
            for normalized_field, value in normalized_data.items():
                # Skip 'id' field - it's for URL parameter, not for updating
                if normalized_field.lower() in ['id', 'plant_id']:
                    continue
                    
                # Map to canonical name if we know it, otherwise use as-is
                canonical_name = canonical_field_mappings.get(normalized_field, normalized_field)
                if value and str(value).strip():  # Only include non-empty values
                    update_data[canonical_name] = str(value).strip()
                    logger.info(f"   MAPPING: {normalized_field} -> {canonical_name}")
                else:
                    logger.debug(f"   SKIPPING empty field: {normalized_field}")
        
        # If no normalized data, try direct field access using centralized config
        if not update_data:
            logger.warning("WARNING: No normalized data found, trying direct field access")
            from models.field_config import FIELD_NAMES, get_aliases_for_field
            
            # Try all canonical field names and their aliases
            for canonical_name in FIELD_NAMES:
                # Get all known aliases for this field
                aliases = get_aliases_for_field(canonical_name)
                
                # Also try ChatGPT underscore variations
                chatgpt_variations = [
                    canonical_name.replace(' ', '___'),  # "Light Requirements" -> "Light___Requirements"
                    canonical_name.replace(' ', '_'),    # "Light Requirements" -> "Light_Requirements"
                    canonical_name.lower().replace(' ', '_'),  # "Light Requirements" -> "light_requirements"
                ]
                
                all_variations = [canonical_name] + aliases + chatgpt_variations
                
                for field_variation in all_variations:
                    value = get_normalized_field(field_variation)
                    if value and str(value).strip():
                        update_data[canonical_name] = str(value).strip()
                        break  # Found a value, move to next field
        
        if not update_data:
            logger.error("ERROR: No valid fields provided for update")
            return jsonify({'error': 'No valid fields provided for update'}), 400
        
        logger.info(f"Final update data: {list(update_data.keys())}")
        logger.info(f"Calling database update for plant {id_or_name}")
        
        # Update the plant
        result = update_plant(id_or_name, update_data)
        logger.info(f"Database update result: {result.get('success', False)}")
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error updating plant: {e}")
        return jsonify({'error': str(e)}), 500

def extract_plant_names_only(plants_data: List[Dict]) -> List[str]:
    """
    Extract only plant names from full plant data objects.
    
    Args:
        plants_data (List[Dict]): List of plant dictionaries with full data
        
    Returns:
        List[str]: List of plant names only, with duplicates removed and empty names filtered
    """
    from models.field_config import get_canonical_field_name
    
    # Get the canonical field name for 'Plant Name'
    name_field = get_canonical_field_name('plant_name')
    
    # Extract plant names and filter out empty ones
    plant_names = []
    for plant in plants_data:
        # Get plant name from the canonical field
        plant_name = plant.get(name_field, '').strip()
        if plant_name and plant_name not in plant_names:  # Remove duplicates and empty names
            plant_names.append(plant_name)
    
    # Sort names alphabetically for consistent output
    return sorted(plant_names)


def format_plants_response(plants_data: List[Dict], names_only: bool = False, search_query: str = None) -> Dict:
    """
    Format the plants response based on the names_only parameter.
    
    Args:
        plants_data (List[Dict]): List of plant dictionaries
        names_only (bool): If True, return only plant names
        search_query (str): Original search query for context
        
    Returns:
        Dict: Formatted response dictionary
    """
    if names_only:
        # Extract only plant names
        plant_names = extract_plant_names_only(plants_data)
        response = {
            'count': len(plant_names),
            'plants': plant_names,
            'names_only': True,
            'usage_note': 'Use these names with other plant endpoints for detailed information'
        }
        # Add search context if this was a search query
        if search_query:
            response['search_query'] = search_query
            response['note'] = f'Plant names matching "{search_query}"'
        else:
            response['note'] = 'All plant names in database'
    else:
        # Return full plant data (existing behavior)
        response = {
            'count': len(plants_data),
            'plants': plants_data
        }
        if search_query:
            response['search_query'] = search_query
    
    return response


def list_or_search_plants_api():
    """Core plant listing/search logic for API endpoints"""
    try:
        from .plant_search_operations import search_plants
        from .plant_database_operations import get_all_plants
        
        # Handle both query parameters and JSON body parameters (ChatGPT-friendly)
        search_query = request.args.get('q', '').strip()
        limit = request.args.get('limit', type=int)
        names_only = request.args.get('names_only', type=bool, default=False)
        
        # If not in query params, check JSON body
        if not search_query and request.is_json:
            json_data = request.get_json()
            if json_data:
                search_query = json_data.get('q', '').strip()
                if limit is None:
                    limit_value = json_data.get('limit')
                    if limit_value is not None:
                        try:
                            limit = int(limit_value)
                        except (ValueError, TypeError):
                            limit = None
                # Check for names_only parameter in JSON body
                if 'names_only' in json_data:
                    names_only = bool(json_data.get('names_only', False))
        
        # Log the request for debugging
        logger.info(f"🔍 Plant search request: query='{search_query}', limit={limit}, names_only={names_only}")
        
        if search_query:
            # Search for plants by name
            plants = search_plants(search_query)
            if plants is not None:
                result_plants = plants[:limit] if limit else plants
                response_data = format_plants_response(result_plants, names_only, search_query)
                return jsonify(response_data), 200
            else:
                return jsonify({'error': 'Search failed'}), 500
        else:
            # Return all plants
            plants = get_all_plants()
            if plants is not None:
                result_plants = plants[:limit] if limit else plants
                response_data = format_plants_response(result_plants, names_only)
                return jsonify(response_data), 200
            else:
                return jsonify({'error': 'Failed to retrieve plants'}), 500
                
    except Exception as e:
        logging.error(f"Error listing/searching plants: {e}")
        return jsonify({'error': str(e)}), 500

def get_plant_details_api(id_or_name):
    """Core plant details retrieval logic for API endpoints"""
    try:
        from .plant_cache_operations import get_plant_by_id_or_name
        
        plant = get_plant_by_id_or_name(id_or_name)
        
        if plant:
            return jsonify({
                'success': True,
                'plant': plant
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Plant not found: {id_or_name}'
            }), 404
            
    except Exception as e:
        logging.error(f"Error getting plant details: {e}")
        return jsonify({'error': str(e)}), 500

def upload_photo_to_plant_api(token):
    """Core photo upload logic for plants"""
    try:
        from .upload_token_manager import validate_upload_token, mark_token_used
        from .plant_photo_operations import upload_and_link_plant_photo
        
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
            result = upload_and_link_plant_photo(file, token_data['plant_id'], token_data['plant_name'])
        else:
            # Fallback to simple upload if no plant_id
            from .storage_client import upload_plant_photo
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

def get_plants() -> List[Dict]:
    """
    Legacy wrapper function for backward compatibility.
    Returns all plants from the database.
    """
    from .plant_database_operations import get_all_plants
    return get_all_plants()
