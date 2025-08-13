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
    houston_tz = ZoneInfo("US/Central")
    now = datetime.now(houston_tz)
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_all_plants() -> List[Dict]:
    """Get all plants from the database with field configuration"""
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])

        if not values:
            logger.info("No plant data found")
            return []

        header = values[0]
        plants = []
        
        for row in values[1:]:
            plant = {}
            for i, field in enumerate(header):
                if i < len(row):
                    plant[field] = row[i]
                else:
                    plant[field] = ""
            if plant:  # Only add non-empty plants
                plants.append(plant)
        
        logger.info(f"Retrieved {len(plants)} plants from database")
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
    Check if two plant names match, handling common variations.
    
    Args:
        search_name: The name being searched for
        plant_name: The name from the database
    
    Returns:
        bool: True if names match
    """
    search_normalized = _normalize_plant_name(search_name)
    plant_normalized = _normalize_plant_name(plant_name)
    
    # Exact match
    if search_normalized == plant_normalized:
        return True
    
    # Check if one is contained in the other
    if search_normalized in plant_normalized or plant_normalized in search_normalized:
        return True
    
    return False

def get_plant_data(plant_names=None) -> List[Dict]:
    """
    Get plant data from Google Sheets, optionally filtered by plant names.
    Uses field_config for consistent field mapping.
    
    Args:
        plant_names (List[str], optional): List of plant names to filter by
        
    Returns:
        List[Dict]: List of plant dictionaries with canonical field names
    """
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])

        if not values:
            logger.info("No plant data found")
            return []

        header = values[0]
        plants = []
        
        for row in values[1:]:
            plant = {}
            for i, field in enumerate(header):
                if i < len(row):
                    plant[field] = row[i]
                else:
                    plant[field] = ""
            
            # Filter by plant names if provided
            if plant_names:
                plant_name_field = get_canonical_field_name('Plant Name')
                current_plant_name = plant.get(plant_name_field, '')
                
                # Check if current plant matches any of the requested names
                matches = any(_plant_names_match(requested_name, current_plant_name) 
                            for requested_name in plant_names)
                
                if matches and plant:
                    plants.append(plant)
            elif plant:  # No filter, add all non-empty plants
                plants.append(plant)
        
        logger.info(f"Retrieved {len(plants)} plants from database")
        return plants

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
                    return i, row  # Return actual row number (1-based from data rows), not ID
        except ValueError:
            search_name = identifier.lower().strip()
            
            # First try exact match (case-insensitive)
            for i, row in enumerate(values[1:], start=1):
                if row and len(row) > name_idx and row[name_idx].lower().strip() == search_name:
                    plant_id_from_sheet = row[0] if row else str(i)  # Plant ID for logging
                    logger.info(f"Exact match found: '{identifier}' -> sheet_id={plant_id_from_sheet}, row {i}, plant_name='{row[name_idx]}'")
                    return i, row  # Return row number, not ID
            
            # If no exact match, try partial matching with stricter criteria
            search_words = search_name.split()
            best_match = None
            best_score = 0
            
            for i, row in enumerate(values[1:], start=1):
                if row and len(row) > name_idx and row[name_idx]:
                    plant_name = row[name_idx].lower().strip()
                    
                    # For single word searches like "vinca", require exact word match
                    if len(search_words) == 1:
                        plant_words = plant_name.split()
                        if search_name in plant_words:  # Exact word match
                            score = 1.0
                            if score > best_score:
                                best_score = score
                                plant_id_from_sheet = int(row[0]) if row and row[0] else i
                                best_match = (i, row)  # Return row number, not ID
                                logger.info(f"Single word match: '{identifier}' -> sheet_id={plant_id_from_sheet}, row {i}, plant_name='{row[name_idx]}'")
                    else:
                        # Multi-word matching logic (existing)
                        plant_words = plant_name.split()
                        matches = sum(1 for word in search_words if any(word in plant_word for plant_word in plant_words))
                        score = matches / len(search_words) if search_words else 0
                        
                        if score > best_score and score >= 0.8:  # Increased threshold for multi-word
                            best_score = score
                            plant_id_from_sheet = int(row[0]) if row and row[0] else i
                            best_match = (i, row)  # Return row number, not ID
                            logger.info(f"Multi-word match: '{identifier}' -> sheet_id={plant_id_from_sheet}, row {i}, plant_name='{row[name_idx]}', score={score}")
            
            if best_match:
                return best_match
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error finding plant: {e}")
        return None, None



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
        from utils.plant_cache_operations import invalidate_plant_list_cache
        invalidate_plant_list_cache()
        
        plant_name = plant_data[1] if plant_data and len(plant_data) > 1 else "Unknown"
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
            # Handle photo URL specially - store as IMAGE formula and update Raw Photo URL
            if new_value and not new_value.startswith('=IMAGE("'):
                photo_formula = f'=IMAGE("{new_value}")' if new_value else ''
            else:
                photo_formula = new_value  # Already wrapped or empty
            range_name = f'Plants!{chr(65 + col_idx)}{plant_row + 1}'
            logger.info(f"Updating Photo URL at {range_name}")
            sheets_client.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body={'values': [[photo_formula]]}
            ).execute()
            
            # Also update Raw Photo URL column
            raw_photo_url_field = get_canonical_field_name('Raw Photo URL')
            try:
                raw_col_idx = header.index(raw_photo_url_field)
                raw_range_name = f'Plants!{chr(65 + raw_col_idx)}{plant_row + 1}'
                logger.info(f"Updating Raw Photo URL at {raw_range_name}")
                sheets_client.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=raw_range_name,
                    valueInputOption='USER_ENTERED',
                    body={'values': [[new_value]]}
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
        from utils.plant_cache_operations import invalidate_plant_list_cache
        invalidate_plant_list_cache()
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating plant field: {e}")
        return False

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
        # Wrap the photo_url in =IMAGE() for the 'Photo URL' field (if not already wrapped)
        if photo_url and not photo_url.startswith('=IMAGE("'):
            photo_formula = f'=IMAGE("{photo_url}")' if photo_url else ''
            raw_photo_url = photo_url  # Store the raw URL directly
        else:
            photo_formula = photo_url  # Already wrapped or empty
            # Extract raw URL from IMAGE formula if needed
            if photo_url and photo_url.startswith('=IMAGE("') and photo_url.endswith('")'):
                raw_photo_url = photo_url[8:-2]  # Remove =IMAGE(" and ")
            else:
                raw_photo_url = photo_url
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
            valueInputOption='USER_ENTERED',
            body={'values': [row_data]}
        ).execute()
        
        # Invalidate cache
        from utils.plant_cache_operations import invalidate_plant_list_cache
        invalidate_plant_list_cache()
        
        logger.info(f"Successfully added plant: {plant_name}")
        return {
            "success": True,
            "message": f"Added {plant_name} to garden",
            "plant_id": next_id
        }
        
    except Exception as e:
        logger.error(f"Error adding plant: {e}")
        return {"success": False, "error": str(e)}


