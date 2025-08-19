"""
Container Operations Module

Core CRUD operations for Container data management from Google Sheets.
Handles container retrieval, updates, additions, and removals for plant maintenance operations.

Author: Plant Database API
Created: v4.0.0 - Plant Maintenance Feature Implementation
"""

import logging
import time
from typing import List, Dict, Optional, Tuple, Any
from config.config import SPREADSHEET_ID
from utils.sheets_client import sheets_client, check_rate_limit

# Set up logging for this module
logger = logging.getLogger(__name__)

# Sheet range for accessing Containers data
CONTAINERS_RANGE = 'Containers!A:F'  # Container ID through Container Material

# Container data caching to minimize API calls
_container_cache = {
    'data': [],
    'max_id': 0,
    'last_updated': 0,
    'cache_duration': 300  # 5 minutes cache duration
}

def get_all_containers() -> List[Dict]:
    """
    Fetch all containers from the Containers sheet with caching to minimize API calls.
    
    Returns:
        List[Dict]: List of container dictionaries with normalized field names
    """
    global _container_cache
    
    current_time = time.time()
    
    # Check if cache is still valid
    if (_container_cache['data'] and 
        _container_cache['last_updated'] and 
        current_time - _container_cache['last_updated'] < _container_cache['cache_duration']):
        logger.debug(f"Returning cached container data with {len(_container_cache['data'])} containers")
        return _container_cache['data'].copy()
    
    try:
        logger.info("Cache expired, fetching fresh container data from database")
        check_rate_limit()
        
        # Get data from Containers sheet
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=CONTAINERS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Need header + at least one data row
            logger.warning("No container data found in sheet")
            _container_cache['data'] = []
            _container_cache['max_id'] = 0
            _container_cache['last_updated'] = current_time
            return []
        
        # First row contains headers
        headers = values[0]
        containers = []
        max_id = 0
        
        # Process each data row (skip header row)
        for row in values[1:]:
            if len(row) >= 4:  # Ensure we have minimum required columns (Container ID, Plant Name, Location ID, Container Size)
                container = {}
                for i, header in enumerate(headers):
                    # Normalize field names to lowercase_underscore format per field normalization standards
                    normalized_field = header.lower().replace(' ', '_').replace('-', '_')
                    if i < len(row):
                        container[normalized_field] = row[i].strip() if row[i] else ""
                    else:
                        container[normalized_field] = ""
                
                # Only add containers with valid container_id
                container_id_str = container.get('container_id', '').strip()
                if container_id_str:
                    containers.append(container)
                    
                    # Track maximum ID for next ID generation
                    try:
                        container_id = int(container_id_str)
                        max_id = max(max_id, container_id)
                    except ValueError:
                        continue  # Skip non-numeric IDs
        
        # Update cache
        _container_cache['data'] = containers
        _container_cache['max_id'] = max_id
        _container_cache['last_updated'] = current_time
        
        logger.info(f"Updated container cache with {len(containers)} containers, max ID: {max_id}")
        return containers.copy()
        
    except Exception as e:
        logger.error(f"Error getting all containers: {e}")
        # Return cached data if available, otherwise empty list
        if _container_cache['data']:
            logger.info("Returning cached container data due to database error")
            return _container_cache['data'].copy()
        return []

def get_containers_for_plant(plant_name: str) -> List[Dict]:
    """
    Find all containers for a specific plant name.
    Since containers table stores plant_id, we need to convert plant_name to plant_id first.
    
    Args:
        plant_name (str): Name of the plant to find containers for
        
    Returns:
        List[Dict]: List of container dictionaries for the specified plant
    """
    try:
        # First, get the plant_id from the plant_name
        from utils.plant_database_operations import find_plant_by_id_or_name
        
        plant_row, plant_data = find_plant_by_id_or_name(plant_name.strip())
        if not plant_row or not plant_data:
            logger.info(f"Plant '{plant_name}' not found in system")
            return []
        
        plant_id = str(plant_data[0])  # Convert to string for comparison
        
        # Now search containers by plant_id
        all_containers = get_all_containers()
        plant_containers = []
        
        for container in all_containers:
            container_plant_id = str(container.get('plant_id', '')).strip()
            if container_plant_id == plant_id:
                plant_containers.append(container)
        
        logger.info(f"Found {len(plant_containers)} containers for plant '{plant_name}' (ID: {plant_id})")
        return plant_containers
        
    except Exception as e:
        logger.error(f"Error getting containers for plant '{plant_name}': {e}")
        return []

def get_container_by_plant_and_location(plant_name: str, location_name: str) -> Optional[Dict]:
    """
    Find a specific container by plant name and location name.
    Used for ambiguity resolution when plant exists in multiple locations.
    
    Args:
        plant_name (str): Name of the plant
        location_name (str): Name of the location
        
    Returns:
        Optional[Dict]: Container dictionary if found, None otherwise
    """
    try:
        # Import here to avoid circular imports
        from .locations_database_operations import get_all_locations
        
        # Get all locations to find location_id for the given location_name
        all_locations = get_all_locations()
        location_id = None
        
        # Normalize location name for comparison
        normalized_location_name = location_name.strip().lower()
        
        for location in all_locations:
            location_name_field = location.get('location_name', '').strip().lower()
            if location_name_field == normalized_location_name:
                location_id = location.get('location_id', '')
                break
        
        if not location_id:
            logger.warning(f"Location '{location_name}' not found")
            return None
        
        # Get containers for the plant
        plant_containers = get_containers_for_plant(plant_name)
        
        # Find container in the specific location
        for container in plant_containers:
            if container.get('location_id', '').strip() == str(location_id):
                logger.info(f"Found container for plant '{plant_name}' in location '{location_name}'")
                return container
        
        logger.info(f"No container found for plant '{plant_name}' in location '{location_name}'")
        return None
        
    except Exception as e:
        logger.error(f"Error getting container for plant '{plant_name}' in location '{location_name}': {e}")
        return None

def get_container_by_id(container_id: str) -> Optional[Dict]:
    """
    Get a specific container by its container ID.
    
    Args:
        container_id (str): ID of the container to retrieve
        
    Returns:
        Optional[Dict]: Container dictionary if found, None otherwise
    """
    try:
        all_containers = get_all_containers()
        
        for container in all_containers:
            if container.get('container_id', '').strip() == str(container_id).strip():
                logger.info(f"Found container with ID '{container_id}'")
                return container
        
        logger.warning(f"Container with ID '{container_id}' not found")
        return None
        
    except Exception as e:
        logger.error(f"Error getting container by ID '{container_id}': {e}")
        return None

def update_container(container_id: str, updates: Dict[str, str]) -> Dict[str, Any]:
    """
    Update container details with partial updates allowed.
    Only updates the specified fields, leaving others unchanged.
    
    Args:
        container_id (str): ID of the container to update
        updates (Dict[str, str]): Dictionary of field names and new values to update
        
    Returns:
        Dict[str, Any]: Result dictionary with success status and update details
    """
    try:
        check_rate_limit()
        
        # Get all containers to find the row to update
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=CONTAINERS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return {
                'success': False,
                'error': 'No container data found in sheet'
            }
        
        headers = values[0]
        container_row_index = None
        
        # Find the container row by container_id
        for row_idx, row in enumerate(values[1:], start=2):  # Start from row 2 (1-indexed, skip header)
            if len(row) > 0 and str(row[0]).strip() == str(container_id).strip():
                container_row_index = row_idx
                break
        
        if container_row_index is None:
            return {
                'success': False,
                'error': f'Container with ID {container_id} not found'
            }
        
        # Get current row data
        current_row = values[container_row_index - 1]  # Convert back to 0-indexed for values array
        
        # Update only the specified fields
        updated_fields = []
        for field_name, new_value in updates.items():
            # Normalize field name to match headers
            normalized_field = field_name.lower().replace('_', ' ').title().replace(' ', ' ')
            
            # Find matching header (case-insensitive)
            header_index = None
            for i, header in enumerate(headers):
                if header.lower().replace(' ', '_').replace('-', '_') == field_name.lower():
                    header_index = i
                    break
            
            if header_index is not None:
                # Extend row if necessary
                while len(current_row) <= header_index:
                    current_row.append('')
                
                # Update the field
                old_value = current_row[header_index]
                current_row[header_index] = str(new_value).strip()
                updated_fields.append({
                    'field': headers[header_index],
                    'old_value': old_value,
                    'new_value': new_value
                })
            else:
                logger.warning(f"Field '{field_name}' not found in container headers")
        
        if not updated_fields:
            return {
                'success': False,
                'error': 'No valid fields to update'
            }
        
        # Update the row in Google Sheets
        range_to_update = f'Containers!A{container_row_index}:F{container_row_index}'
        check_rate_limit()
        sheets_client.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_update,
            valueInputOption='USER_ENTERED',
            body={'values': [current_row]}
        ).execute()
        
        logger.info(f"Successfully updated container {container_id} with {len(updated_fields)} field changes")
        
        # Invalidate cache after successful update
        invalidate_container_cache()
        
        return {
            'success': True,
            'message': f'Container {container_id} updated successfully',
            'updated_fields': updated_fields,
            'container_id': container_id
        }
        
    except Exception as e:
        logger.error(f"Error updating container {container_id}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def add_container(plant_name: str, location_id: str, container_details: Dict[str, str]) -> Dict[str, Any]:
    """
    Add a new container record for a plant in a specific location.
    
    Args:
        plant_name (str): Name of the plant
        location_id (str): ID of the location
        container_details (Dict[str, str]): Container size, type, material details
        
    Returns:
        Dict[str, Any]: Result dictionary with success status and new container details
    """
    try:
        check_rate_limit()
        
        # Get plant_id from plant_name (required for container record)
        from utils.plant_database_operations import find_plant_by_id_or_name
        plant_row, plant_data = find_plant_by_id_or_name(plant_name.strip())
        
        if not plant_row or not plant_data:
            return {
                'success': False,
                'error': f'Plant "{plant_name}" not found in system. Cannot create container without valid plant_id.'
            }
        
        plant_id = plant_data[0]  # First element should be the plant ID
        logger.info(f"Found plant_id {plant_id} for plant '{plant_name}'")
        
        # Get next available container ID
        container_id = _get_next_container_id()
        
        # Get current headers to ensure proper column mapping
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Containers!1:1'
        ).execute()
        
        headers = result.get('values', [[]])[0] if result.get('values') else []
        if not headers:
            return {
                'success': False,
                'error': 'Could not retrieve container sheet headers'
            }
        
        # Build new container row with all required fields
        new_row = [''] * len(headers)
        
        # Set required fields (including mandatory plant_id)
        field_mapping = {
            'container_id': str(container_id),
            'plant_id': str(plant_id),  # Mandatory plant_id field
            'plant_name': plant_name.strip(),  # Optional plant_name for readability
            'location_id': str(location_id).strip(),
            'container_size': container_details.get('container_size', '').strip(),
            'container_type': container_details.get('container_type', '').strip(),
            'container_material': container_details.get('container_material', '').strip()
        }
        
        # Map fields to columns based on headers
        for field_name, value in field_mapping.items():
            for i, header in enumerate(headers):
                normalized_header = header.lower().replace(' ', '_').replace('-', '_')
                if normalized_header == field_name:
                    new_row[i] = value
                    break
        
        # Add the new container row
        check_rate_limit()
        sheets_client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=CONTAINERS_RANGE,
            valueInputOption='USER_ENTERED',
            body={'values': [new_row]}
        ).execute()
        
        logger.info(f"Successfully added new container {container_id} for plant '{plant_name}' in location {location_id}")
        
        # Invalidate cache after successful addition
        invalidate_container_cache()
        
        return {
            'success': True,
            'message': f'Container {container_id} added successfully',
            'container_id': container_id,
            'plant_id': plant_id,
            'plant_name': plant_name,
            'location_id': location_id,
            'container_details': container_details
        }
        
    except Exception as e:
        logger.error(f"Error adding container for plant '{plant_name}': {e}")
        return {
            'success': False,
            'error': str(e)
        }

def remove_container(container_id: str) -> Dict[str, Any]:
    """
    Remove a container record by deleting the entire row from the sheet.
    This properly removes the row rather than just clearing cells.
    
    Args:
        container_id (str): ID of the container to remove
        
    Returns:
        Dict[str, Any]: Result dictionary with success status and removal details
    """
    try:
        check_rate_limit()
        
        # Get all containers to find the row to remove
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=CONTAINERS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return {
                'success': False,
                'error': 'No container data found in sheet'
            }
        
        container_row_index = None
        container_data = None
        
        # Find the container row by container_id
        for row_idx, row in enumerate(values[1:], start=2):  # Start from row 2 (1-indexed, skip header)
            if len(row) > 0 and str(row[0]).strip() == str(container_id).strip():
                container_row_index = row_idx
                container_data = row.copy()
                break
        
        if container_row_index is None:
            return {
                'success': False,
                'error': f'Container with ID {container_id} not found'
            }
        
        # Get the sheet ID for the Containers sheet
        sheet_metadata = sheets_client.get(spreadsheetId=SPREADSHEET_ID).execute()
        containers_sheet_id = None
        
        for sheet in sheet_metadata.get('sheets', []):
            if sheet['properties']['title'] == 'Containers':
                containers_sheet_id = sheet['properties']['sheetId']
                break
        
        if containers_sheet_id is None:
            return {
                'success': False,
                'error': 'Could not find Containers sheet ID'
            }
        
        # Delete the entire row using batchUpdate
        # Note: row_index is 0-based for batchUpdate, but we found it as 1-based
        delete_row_index = container_row_index - 1  # Convert to 0-based
        
        batch_update_request = {
            'requests': [
                {
                    'deleteDimension': {
                        'range': {
                            'sheetId': containers_sheet_id,
                            'dimension': 'ROWS',
                            'startIndex': delete_row_index,
                            'endIndex': delete_row_index + 1
                        }
                    }
                }
            ]
        }
        
        check_rate_limit()
        sheets_client.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=batch_update_request
        ).execute()
        
        logger.info(f"Successfully deleted row {container_row_index} for container {container_id}")
        
        # Invalidate cache after successful removal
        invalidate_container_cache()
        
        return {
            'success': True,
            'message': f'Container {container_id} removed successfully (row deleted)',
            'container_id': container_id,
            'removed_data': container_data,
            'deleted_row': container_row_index
        }
        
    except Exception as e:
        logger.error(f"Error removing container {container_id}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_plant_locations_from_containers(plant_name: str) -> List[str]:
    """
    Get all location names where a plant exists based on container records.
    Used for updating the plant spreadsheet location column.
    
    Args:
        plant_name (str): Name of the plant
        
    Returns:
        List[str]: List of location names where the plant exists
    """
    try:
        # Import here to avoid circular imports
        from .locations_database_operations import get_all_locations
        
        # Get all containers for the plant
        plant_containers = get_containers_for_plant(plant_name)
        
        if not plant_containers:
            logger.info(f"No containers found for plant '{plant_name}'")
            return []
        
        # Get all locations to map location_id to location_name
        all_locations = get_all_locations()
        location_map = {str(loc.get('location_id', '')): loc.get('location_name', '') 
                       for loc in all_locations}
        
        # Extract unique location names from containers
        location_names = []
        for container in plant_containers:
            location_id = container.get('location_id', '').strip()
            if location_id and location_id in location_map:
                location_name = location_map[location_id].strip()
                if location_name and location_name not in location_names:
                    location_names.append(location_name)
        
        logger.info(f"Plant '{plant_name}' exists in {len(location_names)} locations: {location_names}")
        return location_names
        
    except Exception as e:
        logger.error(f"Error getting plant locations from containers for '{plant_name}': {e}")
        return []

def _get_next_container_id() -> Optional[str]:
    """
    Get the next available container ID using cached max_id to minimize API calls.
    Ensures we get maximum ID + 1 for proper ID generation.
    
    Returns:
        Optional[str]: Next available container ID as string, None if error
    """
    global _container_cache
    
    try:
        # Force cache refresh to get latest max_id
        get_all_containers()
        
        # Get next ID from cached max_id
        next_id = _container_cache['max_id'] + 1
        
        # Update cached max_id for subsequent calls
        _container_cache['max_id'] = next_id
        
        logger.info(f"Generated next container ID: {next_id} (from cached max_id)")
        return str(next_id)
        
    except Exception as e:
        logger.error(f"Error getting next container ID: {e}")
        return None

def invalidate_container_cache():
    """
    Invalidate the container cache to force a fresh fetch on next request.
    
    This should be called when containers are added, updated, or removed from the database.
    """
    global _container_cache
    _container_cache['last_updated'] = 0
    logger.info("Container cache invalidated")
