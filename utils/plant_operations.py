import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional, Tuple, Union, Any
from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
from utils.sheets_client import check_rate_limit, get_next_id
from models.field_config import get_canonical_field_name, get_all_field_names, is_valid_field
import re
import time

logger = logging.getLogger(__name__)

def get_houston_timestamp() -> str:
    """
    Get current timestamp in Houston Central Time format.
    
    Returns:
        str: Formatted timestamp string (YYYY-MM-DD HH:MM:SS)
    """
    # Houston, Texas is in Central Time (US/Central)
    central = ZoneInfo('US/Central')
    return datetime.now(central).strftime('%Y-%m-%d %H:%M:%S')

def get_all_plants() -> List[Dict]:
    """Get all plants from the Google Sheet"""
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        header = values[0] if values else []
        plants = []
        
        # Use field_config to get canonical field names
        plant_name_field = get_canonical_field_name('Plant Name')
        location_field = get_canonical_field_name('Location')
        
        name_idx = header.index(plant_name_field) if plant_name_field in header else 1
        location_idx = header.index(location_field) if location_field in header else 3
        
        for row in values[1:]:
            if len(row) > max(name_idx, location_idx):
                raw_locations = row[location_idx].split(',')
                locations = [loc.strip().lower() for loc in raw_locations if loc.strip()]
                plants.append({
                    'name': row[name_idx],
                    'location': row[location_idx],
                    'locations': locations,
                    'frost_tolerance': row[5] if len(row) > 5 else '',
                    'watering_needs': row[6] if len(row) > 6 else ''
                })
        
        logger.info(f"Retrieved {len(plants)} plants from sheet")
        return plants
        
    except Exception as e:
        logger.error(f"Error getting plants: {e}")
        return []

def _normalize_plant_name(name: Optional[str]) -> str:
    """
    Normalize plant name for basic matching (handle plurals, common variations).
    
    Args:
        name (str): Plant name to normalize
    
    Returns:
        str: Normalized plant name
    """
    if not name:
        return ""
    
    name = name.lower().strip()
    
    # Common plural to singular mappings
    plural_to_singular = {
        'roses': 'rose',
        'tomatoes': 'tomato',
        'basils': 'basil',
        'lettuces': 'lettuce',
        'herbs': 'herb',
        'vegetables': 'vegetable',
        'fruits': 'fruit',
        'flowers': 'flower',
        'shrubs': 'shrub',
        'trees': 'tree',
        'vines': 'vine',
        'grasses': 'grass',
        'ferns': 'fern',
        'cacti': 'cactus',
        'cactuses': 'cactus',
        'succulents': 'succulent',
        'annuals': 'annual',
        'perennials': 'perennial',
        'bulbs': 'bulb',
        'seeds': 'seed',
        'seedlings': 'seedling',
        'cuttings': 'cutting',
        'plants': 'plant'
    }
    
    # Check if the name is a known plural
    if name in plural_to_singular:
        return plural_to_singular[name]
    
    # Handle common plural patterns
    if name.endswith('s'):
        # Remove 's' and check if it's a valid singular form
        singular = name[:-1]
        # Add back common endings that might have been removed
        if singular.endswith('ie'):  # tomatoes -> tomato
            return singular
        elif singular.endswith('e'):  # roses -> rose
            return singular
        elif len(singular) > 2:  # general case
            return singular
    
    return name

def _plant_names_match(search_name: str, plant_name: str) -> bool:
    """
    Check if a search name matches a plant name using simple normalization.
    
    This function is now simplified since the AI handles intelligent matching.
    It only does basic normalization (plurals, case) and exact matching.
    
    Args:
        search_name (str): The name being searched for (from AI analysis)
        plant_name (str): The plant name in the database
    
    Returns:
        bool: True if names match after normalization
    """
    search_normalized = _normalize_plant_name(search_name)
    plant_normalized = _normalize_plant_name(plant_name)
    
    # Simple exact match after normalization
    return search_normalized == plant_normalized

def get_plant_data(plant_names=None) -> List[Dict]:
    """Get data for specified plants or all plants"""
    try:
        check_rate_limit()
        # Get regular values first
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        plants_data = []
        
        # Get formulas for Photo URL column to handle IMAGE formulas properly
        photo_url_field = get_canonical_field_name('Photo URL')
        photo_url_col_idx = None
        if photo_url_field in headers:
            photo_url_col_idx = headers.index(photo_url_field)
        
        # Fetch formulas for the Photo URL column if it exists
        photo_formulas = {}
        if photo_url_col_idx is not None:
            try:
                col_letter = chr(65 + photo_url_col_idx)  # Convert index to column letter (A, B, C, ...)
                formula_range = f"Plants!{col_letter}2:{col_letter}"  # Start from row 2 (skip header)
                formula_result = sheets_client.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=formula_range,
                    valueRenderOption='FORMULA'  # Always get formulas for Photo URL column
                ).execute()
                
                formula_values = formula_result.get('values', [])
                for i, formula_row in enumerate(formula_values):
                    if formula_row:  # If row has content
                        row_num = i + 2  # Add 2 because we started from row 2
                        photo_formulas[row_num] = formula_row[0]
            except Exception as e:
                logger.error(f"Could not fetch Photo URL formulas: {e}")
        
        # Update the plant list cache timestamp when we successfully fetch data
        global _plant_list_cache
        if not plant_names:  # Only update for full data requests
            current_time = time.time()
            _plant_list_cache['last_updated'] = current_time
        
        for i, row in enumerate(values[1:], start=2):  # Start from row 2
            row_data = row + [''] * (len(headers) - len(row))
            plant_dict = dict(zip(headers, row_data))
            
            # Replace Photo URL field with actual formula if available
            if photo_url_field and photo_url_col_idx is not None and i in photo_formulas:
                plant_dict[photo_url_field] = photo_formulas[i]
            
            # Filter by plant names if specified
            if plant_names:
                plant_name = plant_dict.get(get_canonical_field_name('Plant Name'))
                if not plant_name or plant_name not in plant_names:
                    continue
            
            plants_data.append(plant_dict)
        
        return plants_data
        
    except Exception as e:
        logger.error(f"Error getting plant data: {e}")
        return []

def find_plant_by_id_or_name(identifier: str) -> Tuple[Optional[int], Optional[List]]:
    """Find a plant by ID or name"""
    try:
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        header = values[0] if values else []
        
        # Use field_config to get canonical field name
        plant_name_field = get_canonical_field_name('Plant Name')
        name_idx = header.index(plant_name_field) if plant_name_field in header else 1
        
        try:
            plant_id = str(int(identifier))
            for i, row in enumerate(values[1:], start=1):
                if row and row[0] == plant_id:
                    return i, row
        except ValueError:
            search_name = identifier.lower()
            
            # First try exact match
            for i, row in enumerate(values[1:], start=1):
                if row and len(row) > name_idx and row[name_idx].lower() == search_name:
                    return i, row
            
            # If no exact match, try partial matching
            # Split the search name into words and look for plants that contain all words
            search_words = search_name.split()
            best_match = None
            best_score = 0
            
            for i, row in enumerate(values[1:], start=1):
                if row and len(row) > name_idx and row[name_idx]:
                    plant_name = row[name_idx].lower()
                    plant_words = plant_name.split()
                    
                    # Count how many search words are found in the plant name
                    matches = sum(1 for word in search_words if any(word in plant_word for plant_word in plant_words))
                    score = matches / len(search_words) if search_words else 0
                    
                    if score > best_score and score >= 0.5:  # At least 50% of words must match
                        best_score = score
                        best_match = (i, row)
            
            if best_match:
                return best_match
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error finding plant: {e}")
        return None, None

def update_plant_legacy(plant_data: Dict) -> bool:
    """Update or add a plant in the Google Sheet (legacy function)"""
    try:
        check_rate_limit()
        logger.info("Starting plant update process")
        logger.info(f"Plant data received: {plant_data}")
        
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        header = values[0] if values else []
        
        # Use field_config to get canonical field names
        plant_name_field = get_canonical_field_name('Plant Name')
        plant_name = plant_data.get(plant_name_field)
        plant_row = None
        
        if plant_name:
            for i, row in enumerate(values[1:], start=1):
                if len(row) > 1 and row[1].lower() == plant_name.lower():
                    plant_row = i
                    break
        
        # Handle photo URLs - store both the IMAGE formula and raw URL
        photo_url_field = get_canonical_field_name('Photo URL')
        photo_url = plant_data.get(photo_url_field, '')
        photo_formula = f'=IMAGE("{photo_url}")' if photo_url else ''
        raw_photo_url = photo_url  # Store the raw URL directly
        
        # Use Houston Central Time for consistent timestamps
        timestamp = get_houston_timestamp()
        
        # Build new row using field_config to get all field names
        field_names = get_all_field_names()
        new_row = []
        
        for field_name in field_names:
            if field_name == get_canonical_field_name('ID'):
                new_row.append(str(len(values) if plant_row is None else values[plant_row][0]))
            elif field_name == photo_url_field:
                new_row.append(photo_formula)  # Photo URL as image formula
            elif field_name == get_canonical_field_name('Raw Photo URL'):
                new_row.append(raw_photo_url)  # Raw Photo URL stored directly
            elif field_name == get_canonical_field_name('Last Updated'):
                new_row.append(timestamp)
            else:
                new_row.append(plant_data.get(field_name, ''))
        
        try:
            if plant_row is not None:
                range_name = f'Plants!A{plant_row + 1}:Q{plant_row + 1}'
                result = sheets_client.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body={'values': [new_row]}
                ).execute()
            else:
                result = sheets_client.values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range='Plants!A1:Q',
                    valueInputOption='USER_ENTERED',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [new_row]}
                ).execute()
            
            # Phase 2: Invalidate cache after plant update
            invalidate_plant_list_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Sheet API error: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Error updating plant: {e}")
        return False

def update_plant(plant_id: Union[int, str], update_data: Dict) -> Dict[str, Union[bool, str]]:
    """
    Update a plant in the database by ID.
    
    Args:
        plant_id (Union[int, str]): ID of the plant to update
        update_data (Dict): Dictionary of field names and new values
        
    Returns:
        Dict[str, Union[bool, str]]: Result with success status and message
    """
    try:
        plant_id = str(plant_id)
        
        # Find the plant row
        plant_row, plant_data = find_plant_by_id_or_name(plant_id)
        if not plant_row:
            return {"success": False, "error": "Plant not found"}
        
        # Update each field
        for field_name, new_value in update_data.items():
            # Validate field name using field_config
            if not is_valid_field(field_name):
                logger.warning(f"Invalid field name: {field_name}")
                continue
            
            success = update_plant_field(plant_row, field_name, str(new_value))
            if not success:
                return {"success": False, "error": f"Failed to update field {field_name}"}
        
        # Invalidate cache
        invalidate_plant_list_cache()
        
        plant_name = plant_data[0][1] if plant_data and len(plant_data[0]) > 1 else "Unknown"
        logger.info(f"Successfully updated plant: {plant_name}")
        return {"success": True, "message": f"Updated {plant_name}"}
        
    except Exception as e:
        logger.error(f"Error updating plant {plant_id}: {e}")
        return {"success": False, "error": str(e)}

def update_plant_field(plant_row: int, field_name: str, new_value: str) -> bool:
    """Update a specific field for a plant"""
    try:
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        header = result.get('values', [])[0]
        
        # Use field_config to validate and get canonical field name
        canonical_field_name = get_canonical_field_name(field_name)
        if not canonical_field_name:
            logger.error(f"Field {field_name} not found in field configuration")
            return False
        
        try:
            col_idx = header.index(canonical_field_name)
        except ValueError:
            logger.error(f"Field {canonical_field_name} not found in sheet")
            return False
            
        if canonical_field_name == get_canonical_field_name('Photo URL'):
            # Check if the value is already an IMAGE formula
            if new_value.startswith('=IMAGE("'):
                formatted_value = new_value  # Already formatted, use as is
                raw_url_match = re.search(r'=IMAGE\("([^"]+)"\)', new_value)
                raw_url = raw_url_match.group(1) if raw_url_match else new_value
            else:
                # Not a formula, wrap it
                formatted_value = f'=IMAGE("{new_value}")' if new_value else ''
                raw_url = new_value
            
            # Update Photo URL column with IMAGE formula
            range_name = f'Plants!{chr(65 + col_idx)}{plant_row + 1}'
            logger.info(f"Updating {canonical_field_name} at {range_name}")
            sheets_client.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body={'values': [[formatted_value]]}
            ).execute()
            
            # Update Raw Photo URL column with raw URL
            try:
                raw_photo_url_field = get_canonical_field_name('Raw Photo URL')
                raw_url_col_idx = header.index(raw_photo_url_field)
                raw_range_name = f'Plants!{chr(65 + raw_url_col_idx)}{plant_row + 1}'
                logger.info(f"Updating Raw Photo URL at {raw_range_name}")
                sheets_client.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=raw_range_name,
                    valueInputOption='RAW',
                    body={'values': [[raw_url]]}
                ).execute()
            except ValueError:
                logger.error("Raw Photo URL column not found")
                return False
        else:
            formatted_value = new_value
            range_name = f'Plants!{chr(65 + col_idx)}{plant_row + 1}'
            logger.info(f"Updating {canonical_field_name} at {range_name}")
            sheets_client.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body={'values': [[formatted_value]]}
            ).execute()
        
        # Phase 2: Invalidate cache after field update
        invalidate_plant_list_cache()
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating plant field: {e}")
        return False

def upload_and_link_plant_photo(file, plant_id: str, plant_name: str) -> Dict[str, Any]:
    """
    Upload a photo to storage and link it to the plant record in the database.
    
    Args:
        file: The uploaded file object
        plant_id (str): ID of the plant to update
        plant_name (str): Name of the plant for storage organization
        
    Returns:
        Dict containing success status, photo URLs, and update results
    """
    try:
        from .storage_client import upload_plant_photo
        
        # Upload photo to Google Cloud Storage
        upload_result = upload_plant_photo(file, plant_name)
        
        # Update plant record with photo URLs
        photo_url = upload_result.get('photo_url', '')
        raw_photo_url = upload_result.get('raw_photo_url', '')
        
        update_data = {
            'Photo URL': f'=IMAGE("{photo_url}")' if photo_url else '',
            'Raw Photo URL': raw_photo_url
        }
        
        db_update_result = update_plant(plant_id, update_data)
        
        return {
            'success': True,
            'message': 'Photo uploaded and linked to plant record',
            'upload_result': upload_result,
            'database_update': db_update_result,
            'photo_url': photo_url,
            'raw_photo_url': raw_photo_url
        }
        
    except Exception as e:
        logger.error(f"Error in upload_and_link_plant_photo: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def migrate_photo_urls():
    """
    Migrates photo URLs from the Photo URL column (which may contain IMAGE formulas)
    to the Raw Photo URL column.
    
    Returns a status message indicating the number of URLs migrated and any errors.
    """
    try:
        # Get all values from the sheet
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return "No data found in sheet"
            
        # Find the column indices
        headers = values[0]
        try:
            photo_url_col = headers.index('Photo URL')
            raw_photo_url_col = headers.index('Raw Photo URL')
        except ValueError:
            return "Required columns 'Photo URL' and/or 'Raw Photo URL' not found"
            
        # Process each row
        updates = []
        migrated_count = 0
        error_count = 0
        
        for row_idx, row in enumerate(values[1:], start=2):  # Start from 2 to account for 1-based indexing and header row
            try:
                # Skip if row doesn't have enough columns
                if len(row) <= max(photo_url_col, raw_photo_url_col):
                    continue
                    
                photo_url = row[photo_url_col] if photo_url_col < len(row) else ''
                
                # Skip if no photo URL or if raw URL already exists
                if not photo_url or (raw_photo_url_col < len(row) and row[raw_photo_url_col]):
                    continue
                    
                # Extract URL from IMAGE formula if present
                url = None
                if photo_url.startswith('=IMAGE("'):
                    match = re.search(r'=IMAGE\("([^"]+)"\)', photo_url)
                    if match:
                        url = match.group(1)
                else:
                    # If not a formula, use the URL directly
                    url = photo_url if photo_url.startswith('http') else None
                    
                if url:
                    # Prepare the update
                    cell_range = f"{RANGE_NAME.split('!')[0]}!{chr(65 + raw_photo_url_col)}{row_idx}"
                    updates.append({
                        'range': cell_range,
                        'values': [[url]]
                    })
                    migrated_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"Error processing row {row_idx}: {str(e)}")
                
        # Apply all updates in a single batch
        if updates:
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            sheets_client.values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()
            
        return f"Migration complete. {migrated_count} URLs migrated. {error_count} errors encountered."
        
    except Exception as e:
        return f"Migration failed: {str(e)}"

# ========================================
# API ENDPOINT OPERATIONS (moved from main.py)
# ========================================

def add_plant_api():
    """Core plant addition logic for API endpoints"""
    try:
        from flask import request, jsonify
        from .upload_token_manager import generate_upload_token
        from .field_normalization_middleware import get_normalized_field, get_plant_name
        
        # Get plant data using field normalization and convert to canonical format
        plant_name = get_plant_name()
        
        plant_data = {
            'Plant Name': plant_name,
            'Description': get_normalized_field('Description', ''),
            'Light Requirements': get_normalized_field('Light Requirements', ''),
            'Watering Needs': get_normalized_field('Watering Needs', ''),
            'Soil Preferences': get_normalized_field('Soil Preferences', ''),
            'Location': get_normalized_field('Location', ''),
            'Care Notes': get_normalized_field('Care Notes', '')
        }
        
        # Validate required fields
        if not plant_data['Plant Name']:
            return jsonify({'error': 'Plant name is required'}), 400
        
        # Add plant to database
        result = add_plant_with_fields(plant_data)
        
        if result.get('success'):
            # Generate upload token for photo
            upload_token = generate_upload_token(
                plant_id=result.get('plant_id', result.get('id')),
                plant_name=plant_data['Plant Name'],
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
        import logging
        logging.error(f"Error adding plant: {e}")
        return jsonify({'error': str(e)}), 500

def update_plant_api(id_or_name):
    """Core plant update logic for API endpoints"""
    try:
        from flask import request, jsonify
        from .field_normalization_middleware import get_normalized_field
        
        # Build update data from normalized fields
        update_data = {}
        
        # Map common field variations to canonical names
        field_mappings = {
            'Description': get_normalized_field('Description'),
            'Light Requirements': get_normalized_field('Light Requirements'), 
            'Watering Needs': get_normalized_field('Watering Needs'),
            'Soil Preferences': get_normalized_field('Soil Preferences'),
            'Location': get_normalized_field('Location'),
            'Care Notes': get_normalized_field('Care Notes')
        }
        
        # Only include fields that have values
        for canonical_name, value in field_mappings.items():
            if value:
                update_data[canonical_name] = value
        
        if not update_data:
            return jsonify({'error': 'No valid fields provided for update'}), 400
        
        # Update the plant
        result = update_plant(id_or_name, update_data)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import logging
        logging.error(f"Error updating plant: {e}")
        return jsonify({'error': str(e)}), 500

def list_or_search_plants_api():
    """Core plant listing/search logic for API endpoints"""
    try:
        from flask import request, jsonify
        
        search_query = request.args.get('q', '').strip()
        limit = request.args.get('limit', type=int)
        
        if search_query:
            # Search for plants by name
            plants = search_plants(search_query)
            if plants is not None:
                result_plants = plants[:limit] if limit else plants
                return jsonify({
                    'count': len(result_plants),
                    'plants': result_plants
                }), 200
            else:
                return jsonify({'error': 'Search failed'}), 500
        else:
            # Return all plants
            plants = get_all_plants()
            if plants is not None:
                result_plants = plants[:limit] if limit else plants
                return jsonify({
                    'count': len(result_plants),
                    'plants': result_plants
                }), 200
            else:
                return jsonify({'error': 'Failed to retrieve plants'}), 500
                
    except Exception as e:
        import logging
        logging.error(f"Error listing/searching plants: {e}")
        return jsonify({'error': str(e)}), 500

def get_plant_details_api(id_or_name):
    """Core plant details retrieval logic for API endpoints"""
    try:
        from flask import jsonify
        
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
        import logging
        logging.error(f"Error getting plant details: {e}")
        return jsonify({'error': str(e)}), 500

def upload_photo_to_plant_api(token):
    """Core photo upload logic for plants"""
    try:
        from flask import request, jsonify
        from .upload_token_manager import validate_upload_token, mark_token_used
        
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
            import logging
            logging.warning("No plant_id in token - photo uploaded but not linked to plant record")
        
        # Mark token as used
        mark_token_used(token, request.remote_addr or '')
        
        return jsonify({
            'success': True,
            'message': 'Photo uploaded successfully',
            **result
        }), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error uploading photo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def add_test_photo_url():
    """
    Adds a test photo URL to the first plant to verify the migration process.
    """
    from sheets_client import sheets_client, SPREADSHEET_ID
    
    try:
        # Add a test IMAGE formula to the Photo URL column of the first plant
        test_url = "https://example.com/test-hibiscus.jpg"
        image_formula = f'=IMAGE("{test_url}")'
        
        # Update the Photo URL column for the first plant (row 2, since row 1 is header)
        range_name = 'Plants!N2'  # Assuming Photo URL is column N
        sheets_client.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body={'values': [[image_formula]]}
        ).execute()
        
        return "Test photo URL added successfully"
        
    except Exception as e:
        return f"Failed to add test photo URL: {str(e)}"

# Public API functions for web.py compatibility
def get_plants() -> List[Dict]:
    """
    Get all plants from the database (alias for get_all_plants).
    
    Returns:
        List[Dict]: List of plant dictionaries
    """
    return get_all_plants()

def add_plant(plant_name: str, description: str = "", location: str = "", photo_url: str = "") -> Dict[str, Union[bool, str]]:
    """
    Add a new plant to the database.
    
    Args:
        plant_name (str): Name of the plant
        description (str): Plant description
        location (str): Plant location
        photo_url (str): URL to plant photo
        
    Returns:
        Dict[str, Union[bool, str]]: Result with success status and message
    """
    try:
        # Get next available ID
        next_id = get_next_id()
        if not next_id:
            return {"success": False, "error": "Could not generate plant ID"}
        
        # Prepare plant data using field_config
        # Wrap the photo_url in =IMAGE() for the 'Photo URL' field
        photo_formula = f'=IMAGE("{photo_url}")' if photo_url else ''
        raw_photo_url = photo_url  # Store the raw URL directly
        plant_data = {
            get_canonical_field_name('ID'): next_id,
            get_canonical_field_name('Plant Name'): plant_name,
            get_canonical_field_name('Description'): description,
            get_canonical_field_name('Location'): location,
            get_canonical_field_name('Photo URL'): photo_formula,
            get_canonical_field_name('Raw Photo URL'): raw_photo_url,
            get_canonical_field_name('Last Updated'): get_houston_timestamp()
        }
        
        # Add empty values for all other fields
        all_fields = get_all_field_names()
        for field in all_fields:
            if field not in plant_data:
                plant_data[field] = ""
        
        # Convert to list format for Google Sheets
        headers = get_all_field_names()
        row_data = [plant_data.get(field, "") for field in headers]
        
        # Add to sheet
        check_rate_limit()
        sheets_client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',  # Changed from 'RAW' to 'USER_ENTERED'
            body={'values': [row_data]}
        ).execute()
        
        # Invalidate cache
        invalidate_plant_list_cache()
        
        logger.info(f"Successfully added plant: {plant_name}")
        return {"success": True, "message": f"Added {plant_name} to garden"}
        
    except Exception as e:
        logger.error(f"Error adding plant {plant_name}: {e}")
        return {"success": False, "error": str(e)}

def _generate_ai_care_information(plant_name: str, location: str = "") -> Dict[str, str]:
    """
    Generate comprehensive AI care information for a plant.
    
    Args:
        plant_name (str): Name of the plant to generate care for
        location (str): Location where the plant will be grown
        
    Returns:
        Dict[str, str]: Dictionary with care field names as keys and AI-generated content as values
    """
    logger.info(f"Starting AI care generation for {plant_name} at location: '{location}'")
    
    try:
        from config.config import openai_client
        import time
        logger.info("OpenAI client imported successfully")
        
        # Check if OpenAI client is available
        if not openai_client:
            logger.error("OpenAI client is None - OpenAI API key may be missing")
            return {
                'Description': f"A {plant_name} plant suitable for Houston gardening.",
                'Care Notes': f"Care guide for {plant_name}: Please research specific care requirements for this plant based on Houston's climate and growing conditions.",
                'Watering Needs': "Water when soil feels dry to touch",
                'Light Requirements': "Provide appropriate light conditions for plant type"
            }
        
        # Create location context
        location_context = f" in {location}" if location else ""
        location_advice = f"Focus on practical advice for the specified location: {location}. " if location else ""
        
        # Create detailed plant care guide prompt for OpenAI
        prompt = (
            f"Create a detailed plant care guide for {plant_name} in Houston, TX{location_context}. "
            "Include care requirements, growing conditions, and maintenance tips. "
            f"{location_advice}"
            "Provide comprehensive information suitable for a home gardener.\n\n"
            "IMPORTANT: Use EXACTLY the section format shown below with double asterisks and colons:\n"
            "**Description:**\n"
            "**Light:**\n"
            "**Soil:**\n"
            "**Soil pH Type:**\n"
            "**Soil pH Range:**\n"
            "**Watering:**\n"
            "**Temperature:**\n"
            "**Pruning:**\n"
            "**Mulching:**\n"
            "**Fertilizing:**\n"
            "**Winter Care:**\n"
            "**Spacing:**\n"
            "**Care Notes:**"
        )
        
        logger.info(f"Calling OpenAI API for {plant_name}")
        start_time = time.time()
        
        # Get plant care information from OpenAI using GPT-4
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert gardener and plant database manager specializing in Houston, Texas climate. "
                               "Answer as a knowledgeable, friendly assistant. Important: Do not use markdown headers (###). "
                               "For soil pH information: Soil pH Type must be one of: high alkalinity, medium alkalinity, "
                               "slightly alkaline, neutral, slightly acidic, medium acidity, high acidity. "
                               "Soil pH Range must be in format like '5.5 - 6.5' with numerical ranges only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )
        
        ai_time = time.time() - start_time
        logger.info(f"OpenAI API call completed in {ai_time:.2f} seconds for {plant_name}")
        
        ai_response = response.choices[0].message.content or ""
        logger.info(f"Generated AI care response for {plant_name} (length: {len(ai_response)} chars): {ai_response[:150]}...")
        
        # Parse the care guide response to extract structured data for database storage
        care_details = _parse_care_guide(ai_response)
        
        logger.info(f"Successfully generated AI care information for {plant_name}: {len(care_details)} fields parsed")
        return care_details
        
    except ImportError as e:
        logger.error(f"Import error for OpenAI client: {e}")
        return {
            'Description': f"A {plant_name} plant suitable for Houston gardening.",
            'Care Notes': f"Care guide for {plant_name}: Please research specific care requirements for this plant based on Houston's climate and growing conditions.",
            'Watering Needs': "Water when soil feels dry to touch",
            'Light Requirements': "Provide appropriate light conditions for plant type"
        }
    except AttributeError as e:
        logger.error(f"OpenAI client attribute error - API key may be invalid: {e}")
        return {
            'Description': f"A {plant_name} plant suitable for Houston gardening.",
            'Care Notes': f"Care guide for {plant_name}: AI care generation failed due to configuration error. Please research specific care requirements.",
            'Watering Needs': "Water when soil feels dry to touch", 
            'Light Requirements': "Provide appropriate light conditions for plant type"
        }
    except Exception as e:
        logger.error(f"Unexpected error generating AI care information for {plant_name}: {type(e).__name__}: {e}")
        # Return fallback care information if AI generation fails
        return {
            'Description': f"A {plant_name} plant suitable for Houston gardening.",
            'Care Notes': f"Care guide for {plant_name}: Please research specific care requirements for this plant based on Houston's climate and growing conditions.",
            'Watering Needs': "Water when soil feels dry to touch",
            'Light Requirements': "Provide appropriate light conditions for plant type"
        }

def _parse_care_guide(response: str) -> Dict[str, str]:
    """
    Parse the care guide response from OpenAI into a structured dictionary.
    Handles **Section:** headers and maps short names to full field names.
    
    Args:
        response (str): AI response text with section headers
        
    Returns:
        Dict[str, str]: Dictionary mapping field names to care content
    """
    # Mapping from possible section names to spreadsheet field names
    section_map = {
        'Description': 'Description',
        'Light': 'Light Requirements', 
        'Soil': 'Soil Preferences',
        'Soil pH Type': 'Soil pH Type',
        'Soil pH Range': 'Soil pH Range',
        'Watering': 'Watering Needs',
        'Temperature': 'Frost Tolerance',
        'Pruning': 'Pruning Instructions',
        'Mulching': 'Mulching Needs',
        'Fertilizing': 'Fertilizing Schedule',
        'Winter Care': 'Winterizing Instructions',
        'Spacing': 'Spacing Requirements',
        'Care Notes': 'Care Notes'
    }

    care_details = {}
    lines = response.split('\n')
    current_section = None
    current_content = []

    def save_section(section, content):
        """Save the current section content to care_details"""
        if section and content:
            # Extract section name from **Section:** format
            section_name = section.strip('*').strip().rstrip(':').strip()
            field_name = section_map.get(section_name)
            if field_name:
                content_text = '\n'.join(content).strip()
                if content_text:  # Only add non-empty content
                    care_details[field_name] = content_text

    for line in lines:
        line = line.strip()
        # Check if this is a section header (starts and ends with **)
        if line.startswith('**') and line.endswith('**'):
            # Save previous section
            save_section(current_section, current_content)
            # Start new section
            current_section = line
            current_content = []
        elif current_section and line:
            # Add content to current section
            current_content.append(line)
    
    # Save the last section
    save_section(current_section, current_content)
    
    # If no structured content was found, add the full response as care notes
    if not care_details:
        care_details['Care Notes'] = response.strip()
    
    logger.info(f"Parsed care guide into {len(care_details)} fields: {list(care_details.keys())}")
    return care_details

def add_plant_with_fields(plant_data_dict: Dict[str, str]) -> Dict[str, Union[bool, str]]:
    """
    Add a new plant to the database with comprehensive field support.
    
    Args:
        plant_data_dict (Dict[str, str]): Dictionary containing plant field data
        
    Returns:
        Dict[str, Union[bool, str]]: Result with success status, message, and plant ID
    """
    try:
        # Validate that Plant Name is provided
        plant_name_field = get_canonical_field_name('Plant Name')
        plant_name = plant_data_dict.get(plant_name_field) if plant_name_field else None
        if not plant_name:
            return {"success": False, "error": "'Plant Name' is required"}
        
        # Get next available ID
        next_id = get_next_id()
        if not next_id:
            return {"success": False, "error": "Could not generate plant ID"}
        
        # Prepare plant data using field_config
        plant_data = {
            get_canonical_field_name('ID'): next_id,
            get_canonical_field_name('Last Updated'): get_houston_timestamp()
        }
        
        # Process all provided fields
        for field_name, field_value in plant_data_dict.items():
            canonical_field = get_canonical_field_name(field_name)
            if canonical_field:
                if canonical_field == get_canonical_field_name('Photo URL'):
                    # Handle photo URL specially - store both IMAGE formula and raw URL
                    photo_formula = f'=IMAGE("{field_value}")' if field_value else ''
                    plant_data[canonical_field] = photo_formula
                    plant_data[get_canonical_field_name('Raw Photo URL')] = field_value
                else:
                    plant_data[canonical_field] = field_value
        
        # Check if we need to generate AI care information (minimal data provided)
        care_fields_to_check = [
            'Description', 'Light Requirements', 'Watering Needs', 'Soil Preferences',
            'Pruning Instructions', 'Fertilizing Schedule', 'Care Notes'
        ]
        
        provided_care_fields = sum(1 for field in care_fields_to_check 
                                 if get_canonical_field_name(field) in plant_data and 
                                 plant_data[get_canonical_field_name(field)].strip())
        
        # If minimal care information provided (less than 3 care fields), generate AI care
        if provided_care_fields < 3:
            logger.info(f"Generating AI care information for {plant_name} (only {provided_care_fields} care fields provided)")
            try:
                ai_care_data = _generate_ai_care_information(plant_name, plant_data.get(get_canonical_field_name('Location'), ''))
                
                # Merge AI-generated care data with existing data (don't overwrite user-provided fields)
                fields_added = 0
                for field_name, ai_value in ai_care_data.items():
                    canonical_field = get_canonical_field_name(field_name)
                    if canonical_field and (canonical_field not in plant_data or not plant_data[canonical_field].strip()):
                        plant_data[canonical_field] = ai_value
                        fields_added += 1
                
                logger.info(f"AI care generation successful: added {fields_added} care fields for {plant_name}")
                
            except Exception as e:
                logger.error(f"AI care generation failed for {plant_name}, continuing with minimal data: {e}")
                # Continue with whatever data we have - don't fail the entire operation
        
        # Add empty values for all fields not provided
        all_fields = get_all_field_names()
        for field in all_fields:
            if field not in plant_data:
                plant_data[field] = ""
        
        # Convert to list format for Google Sheets
        headers = get_all_field_names()
        row_data = [plant_data.get(field, "") for field in headers]
        
        # Add to sheet
        check_rate_limit()
        sheets_client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body={'values': [row_data]}
        ).execute()
        
        # Invalidate cache
        invalidate_plant_list_cache()
        
        logger.info(f"Successfully added plant with comprehensive fields: {plant_name}")
        return {
            "success": True,
            "message": f"Added {plant_name} to garden",
            "plant_id": next_id
        }
        
    except Exception as e:
        logger.error(f"Error adding plant with fields: {e}")
        return {"success": False, "error": str(e)}

def search_plants(query: str) -> List[Dict]:
    """
    Search plants by name or other criteria.
    
    Args:
        query (str): Search query
        
    Returns:
        List[Dict]: List of matching plant dictionaries
    """
    try:
        # Get all plants
        all_plants = get_plant_data()
        
        if not query.strip():
            return all_plants
        
        query_lower = query.lower().strip()
        matching_plants = []
        
        for plant in all_plants:
            # Search in plant name
            plant_name = plant.get(get_canonical_field_name('Plant Name'), '').lower()
            if query_lower in plant_name:
                matching_plants.append(plant)
                continue
            
            # Search in description
            description = plant.get(get_canonical_field_name('Description'), '').lower()
            if query_lower in description:
                matching_plants.append(plant)
                continue
            
            # Search in location
            location = plant.get(get_canonical_field_name('Location'), '').lower()
            if query_lower in location:
                matching_plants.append(plant)
                continue
        
        logger.info(f"Search for '{query}' found {len(matching_plants)} plants")
        return matching_plants
        
    except Exception as e:
        logger.error(f"Error searching plants for '{query}': {e}")
        return []

# Phase 2: Plant List Caching System
_plant_list_cache = {
    'names': [],
    'last_updated': 0,
    'cache_duration': 300  # 5 minutes cache duration
}

def get_plant_names_from_database() -> List[str]:
    """
    Get a list of all plant names from the database.
    
    This function uses caching to improve performance and reduce API calls.
    The cache is invalidated when plants are added or updated.
    
    Returns:
        List[str]: List of plant names currently in the database
    """
    # Import here to avoid circular imports
    from plant_operations import _plant_list_cache
    
    current_time = time.time()
    cache_duration = 300  # 5 minutes
    
    # Check if cache is still valid
    if (_plant_list_cache['names'] and 
        _plant_list_cache['last_updated'] and 
        current_time - _plant_list_cache['last_updated'] < cache_duration):
        logger.info(f"Returning cached plant list with {len(_plant_list_cache['names'])} plants")
        return _plant_list_cache['names'].copy()
    
    try:
        logger.info("Cache expired, fetching fresh plant list from database")
        check_rate_limit()
        
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) <= 1:
            logger.warning("No plants found in database or only header row present")
            _plant_list_cache['names'] = []
            _plant_list_cache['last_updated'] = current_time
            return []
        
        headers = values[0]
        # Use field_config to get canonical field name
        plant_name_field = get_canonical_field_name('Plant Name')
        name_idx = headers.index(plant_name_field) if plant_name_field in headers else 1
        
        # Extract plant names from all rows except header
        plant_names = []
        for row in values[1:]:
            if len(row) > name_idx and row[name_idx]:
                plant_name = row[name_idx].strip()
                if plant_name:  # Only add non-empty names
                    plant_names.append(plant_name)
        
        # Update cache
        _plant_list_cache['names'] = plant_names
        _plant_list_cache['last_updated'] = current_time
        
        logger.info(f"Updated plant list cache with {len(plant_names)} plants")
        return plant_names.copy()
        
    except Exception as e:
        logger.error(f"Error fetching plant names from database: {e}")
        # Return cached data if available, otherwise empty list
        if _plant_list_cache['names']:
            logger.info("Returning cached plant list due to database error")
            return _plant_list_cache['names'].copy()
        return []

def invalidate_plant_list_cache():
    """
    Invalidate the plant list cache to force a fresh fetch on next request.
    
    This should be called when plants are added, updated, or removed from the database.
    """
    global _plant_list_cache
    _plant_list_cache['last_updated'] = 0
    logger.info("Plant list cache invalidated")

def get_plant_list_cache_info() -> Dict:
    """
    Get information about the current plant list cache status.
    
    Returns:
        Dict: Cache information including count, last updated, and cache duration
    """
    global _plant_list_cache
    current_time = time.time()
    age = current_time - _plant_list_cache['last_updated']
    is_valid = age < _plant_list_cache['cache_duration']
    
    return {
        'plant_count': len(_plant_list_cache['names']),
        'last_updated': _plant_list_cache['last_updated'],
        'cache_age_seconds': age,
        'is_valid': is_valid,
        'cache_duration_seconds': _plant_list_cache['cache_duration']
    } 

def get_location_names_from_database() -> List[str]:
    """
    Get a list of unique location names from the database.
    
    This function extracts all unique location values from the database
    to support location-based queries like "what plants are in the arboretum".
    
    Returns:
        List[str]: List of unique location names from the database
    """
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        # Use field_config to get canonical field name
        location_field = get_canonical_field_name('Location')
        location_idx = headers.index(location_field) if location_field in headers else 3
        
        # Extract all location values
        locations = set()
        for row in values[1:]:
            if len(row) > location_idx and row[location_idx]:
                # Split by comma and clean up each location
                location_parts = row[location_idx].split(',')
                for part in location_parts:
                    location = part.strip()
                    if location:  # Only add non-empty locations
                        locations.add(location)
        
        location_list = sorted(list(locations))
        logger.info(f"Retrieved {len(location_list)} unique locations from database")
        return location_list
        
    except Exception as e:
        logger.error(f"Error getting location names from database: {e}")
        return []

def get_plants_by_location(location_names: List[str]) -> List[Dict]:
    """
    Get plants that are located in any of the specified locations (exact match only).
    Args:
        location_names (List[str]): List of location names to search for
    Returns:
        List[Dict]: List of plant data dictionaries for plants in the specified locations
    """
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        if not values:
            return []
        headers = values[0]
        location_idx = headers.index('Location') if 'Location' in headers else 3
        matching_plants = []
        location_names_lower = [loc.lower().strip() for loc in location_names]
        for row in values[1:]:
            if len(row) > location_idx and row[location_idx]:
                plant_locations = [loc.strip().lower() for loc in row[location_idx].split(',') if loc.strip()]
                if any(loc in location_names_lower for loc in plant_locations):
                    row_data = row + [''] * (len(headers) - len(row))
                    plant_dict = dict(zip(headers, row_data))
                    matching_plants.append(plant_dict)
        logger.info(f"Found {len(matching_plants)} plants in locations: {location_names}")
        return matching_plants
    except Exception as e:
        logger.error(f"Error getting plants by location: {e}")
        return []

def enhanced_plant_matching(plant_identification: str) -> Dict:
    """
    Enhanced plant matching with fuzzy logic and confidence scoring.
    Matches ChatGPT's plant identification against the user's plant database.
    
    Args:
        plant_identification (str): Plant name identified by ChatGPT
        
    Returns:
        Dict: Matching result with confidence score and database info
    """
    try:
        logger.info(f"Enhanced plant matching for: {plant_identification}")
        
        # Get all plants from the database
        all_plants = get_plant_data()
        
        if not all_plants:
            return {
                'found_in_database': False,
                'confidence': 'low',
                'matched_plant_name': None,
                'database_info': 'No plants found in database',
                'alternatives': []
            }
        
        # Extract plant names for matching
        plant_name_field = get_canonical_field_name('Plant Name')
        plant_names = [plant.get(plant_name_field, '') for plant in all_plants if plant.get(plant_name_field)]
        
        # Find the best match using enhanced fuzzy matching
        best_match = find_best_plant_match(plant_identification, plant_names)
        
        if best_match['found']:
            # Get the matched plant's full data
            matched_plant_data = next(
                (plant for plant in all_plants if plant.get(plant_name_field) == best_match['plant_name']),
                None
            )
            
            return {
                'found_in_database': True,
                'plant_name': best_match['plant_name'],
                'matched_plant_name': best_match['plant_name'], 
                'confidence': best_match['confidence'],
                'match_score': best_match['score'],
                'database_info': f"Exact match found in your plant database",
                'plant_data': matched_plant_data,
                'alternatives': best_match.get('alternatives', [])
            }
        else:
            # No match found - provide suggestions for similar plants
            return {
                'found_in_database': False,
                'plant_name': plant_identification,
                'matched_plant_name': None,
                'confidence': 'low',
                'match_score': 0.0,
                'database_info': f"'{plant_identification}' not found in your plant database",
                'suggestions': best_match.get('alternatives', []),
                'alternatives': best_match.get('alternatives', [])
            }
    
    except Exception as e:
        logger.error(f"Error in enhanced plant matching: {e}")
        return {
            'found_in_database': False,
            'confidence': 'low',
            'matched_plant_name': None,
            'database_info': f'Error during plant matching: {str(e)}',
            'error': str(e)
        }

def find_best_plant_match(search_name: str, plant_names: List[str]) -> Dict:
    """
    Find the best matching plant using fuzzy string matching algorithms.
    
    Args:
        search_name (str): Plant name to search for
        plant_names (List[str]): List of plant names in the database
        
    Returns:
        Dict: Best match result with confidence scoring
    """
    try:
        import difflib
        from collections import defaultdict
        
        search_normalized = _normalize_plant_name(search_name)
        
        # Track all potential matches with scores
        matches = []
        
        for plant_name in plant_names:
            if not plant_name:
                continue
                
            plant_normalized = _normalize_plant_name(plant_name)
            
            # Method 1: Exact match (highest confidence)
            if search_normalized == plant_normalized:
                matches.append({
                    'plant_name': plant_name,
                    'score': 1.0,
                    'method': 'exact'
                })
                continue
            
            # Method 2: Substring match
            if search_normalized in plant_normalized or plant_normalized in search_normalized:
                # Calculate substring match score
                overlap = max(len(search_normalized), len(plant_normalized))
                min_len = min(len(search_normalized), len(plant_normalized))
                score = min_len / overlap if overlap > 0 else 0
                matches.append({
                    'plant_name': plant_name,
                    'score': score * 0.9,  # Slightly lower than exact match
                    'method': 'substring'
                })
                continue
            
            # Method 3: Word-by-word matching
            search_words = set(search_normalized.split())
            plant_words = set(plant_normalized.split())
            
            if search_words and plant_words:
                # Intersection over union
                intersection = len(search_words.intersection(plant_words))
                union = len(search_words.union(plant_words))
                word_score = intersection / union if union > 0 else 0
                
                if word_score > 0.4:  # At least 40% word overlap
                    matches.append({
                        'plant_name': plant_name,
                        'score': word_score * 0.8,
                        'method': 'word_overlap'
                    })
            
            # Method 4: Fuzzy string matching using difflib
            ratio = difflib.SequenceMatcher(None, search_normalized, plant_normalized).ratio()
            if ratio > 0.6:  # At least 60% similarity
                matches.append({
                    'plant_name': plant_name,
                    'score': ratio * 0.7,
                    'method': 'fuzzy'
                })
        
        # Sort matches by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Determine confidence level based on best match score
        if matches:
            best_score = matches[0]['score']
            if best_score >= 0.9:
                confidence = 'high'
            elif best_score >= 0.7:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            # Get top alternatives (excluding the best match)
            alternatives = [
                {
                    'plant_name': match['plant_name'],
                    'score': match['score'],
                    'method': match['method']
                }
                for match in matches[1:4]  # Top 3 alternatives
                if match['score'] > 0.5
            ]
            
            return {
                'found': best_score >= 0.6,  # Minimum threshold for a match
                'plant_name': matches[0]['plant_name'],
                'score': best_score,
                'confidence': confidence,
                'method': matches[0]['method'],
                'alternatives': alternatives
            }
        else:
            # No matches found, but provide some suggestions based on partial word matches
            suggestions = []
            search_words = search_normalized.split()
            
            for plant_name in plant_names[:10]:  # Check first 10 plants for suggestions
                plant_normalized = _normalize_plant_name(plant_name)
                plant_words = plant_normalized.split()
                
                # Check if any search words appear in plant name
                if any(word in plant_normalized for word in search_words):
                    suggestions.append({
                        'plant_name': plant_name,
                        'score': 0.3,  # Low score for suggestions
                        'method': 'suggestion'
                    })
            
            return {
                'found': False,
                'plant_name': None,
                'score': 0.0,
                'confidence': 'none',
                'alternatives': suggestions[:3]  # Top 3 suggestions
            }
    
    except Exception as e:
        logger.error(f"Error in find_best_plant_match: {e}")
        return {
            'found': False,
            'plant_name': None,
            'score': 0.0,
            'confidence': 'error',
            'error': str(e)
        } 