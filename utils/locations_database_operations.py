"""
Locations Database Operations Module

Core CRUD operations for Locations and Containers data access.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import List, Dict, Optional
import logging
from config.config import SPREADSHEET_ID
from utils.sheets_client import sheets_client, check_rate_limit

# Set up logging for this module
logger = logging.getLogger(__name__)

# Sheet ranges for accessing Locations and Containers data
LOCATIONS_RANGE = 'Locations!A:G'  # Location ID through Microclimate Conditions
CONTAINERS_RANGE = 'Containers!A:F'  # Container ID through Container Material

def get_all_locations() -> List[Dict]:
    """
    Fetch all locations from the Locations sheet.
    
    Returns:
        List[Dict]: List of location dictionaries with all location data
    """
    try:
        check_rate_limit()
        
        # Get data from Locations sheet
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=LOCATIONS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Need header + at least one data row
            logger.warning("No location data found in sheet")
            return []
        
        # headers = values[0]  # First row contains headers (unused in current implementation)
        locations = []
        
        # Process each data row (skip header row)
        for row in values[1:]:
            if len(row) >= 6:  # Ensure we have all required columns
                try:
                    # Parse sun exposure hours as integers, default to 0 if invalid
                    morning_hours = int(row[2]) if len(row) > 2 and row[2].isdigit() else 0
                    afternoon_hours = int(row[3]) if len(row) > 3 and row[3].isdigit() else 0
                    evening_hours = int(row[4]) if len(row) > 4 and row[4].isdigit() else 0
                    
                    location = {
                        'location_id': row[0],  # Location ID
                        'location_name': row[1],  # Location name
                        'morning_sun_hours': morning_hours,  # Morning sun exposure
                        'afternoon_sun_hours': afternoon_hours,  # Afternoon sun exposure
                        'evening_sun_hours': evening_hours,  # Evening sun exposure
                        'shade_pattern': row[5] if len(row) > 5 else '',  # Shade pattern description
                        'microclimate_conditions': row[6] if len(row) > 6 else '',  # Microclimate details
                        'total_sun_hours': morning_hours + afternoon_hours + evening_hours  # Calculated total
                    }
                    locations.append(location)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing location row {row}: {e}")
                    continue
        
        logger.info(f"Retrieved {len(locations)} locations from sheet")
        return locations
        
    except Exception as e:
        logger.error(f"Error getting all locations: {e}")
        return []

def get_location_by_id(location_id: str) -> Optional[Dict]:
    """
    Get a specific location by its ID.
    
    Args:
        location_id (str): The location ID to search for
        
    Returns:
        Optional[Dict]: Location data dictionary if found, None otherwise
    """
    try:
        all_locations = get_all_locations()
        
        for location in all_locations:
            if location.get('location_id', '').strip() == location_id.strip():
                logger.debug(f"Found location: {location_id}")
                return location
        
        logger.warning(f"Location not found: {location_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting location by ID {location_id}: {e}")
        return None

def find_location_by_id_or_name(identifier: str) -> Optional[Dict]:
    """
    Find a location by ID or name, similar to find_plant_by_id_or_name.
    
    Args:
        identifier (str): Location ID or location name to search for
        
    Returns:
        Optional[Dict]: Location data dictionary if found, None otherwise
    """
    try:
        all_locations = get_all_locations()
        
        # First try to find by ID (exact match)
        for location in all_locations:
            if location.get('location_id', '').strip() == identifier.strip():
                logger.debug(f"Found location by ID: {identifier}")
                return location
        
        # If not found by ID, try to find by name (case-insensitive)
        identifier_lower = identifier.lower().strip()
        for location in all_locations:
            location_name = location.get('location_name', '').lower().strip()
            if location_name == identifier_lower:
                logger.debug(f"Found location by name: {identifier}")
                return location
        
        # If still not found, try partial matching on name
        for location in all_locations:
            location_name = location.get('location_name', '').lower().strip()
            if identifier_lower in location_name:
                logger.debug(f"Found location by partial name match: {identifier}")
                return location
        
        logger.warning(f"Location not found by ID or name: {identifier}")
        return None
        
    except Exception as e:
        logger.error(f"Error finding location by ID or name {identifier}: {e}")
        return None

def get_all_containers() -> List[Dict]:
    """
    Fetch all containers from the Containers sheet.
    
    Returns:
        List[Dict]: List of container dictionaries with all container data
    """
    try:
        check_rate_limit()
        
        # Get data from Containers sheet
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=CONTAINERS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Need header + at least one data row
            logger.warning("No container data found in sheet")
            return []
        
        # headers = values[0]  # First row contains headers (unused in current implementation)
        containers = []
        
        # Process each data row (skip header row)
        for row in values[1:]:
            if len(row) >= 6:  # Ensure we have all required columns
                container = {
                    'container_id': row[0],  # Container ID
                    'plant_id': row[1],  # Plant ID this container holds
                    'location_id': row[2],  # Location where container is placed
                    'container_type': row[3],  # Type of container (pot, planter, etc.)
                    'container_size': row[4],  # Size designation (small, medium, large)
                    'container_material': row[5]  # Material (plastic, ceramic, etc.)
                }
                containers.append(container)
        
        logger.info(f"Retrieved {len(containers)} containers from sheet")
        return containers
        
    except Exception as e:
        logger.error(f"Error getting all containers: {e}")
        return []

def get_containers_by_location_id(location_id: str) -> List[Dict]:
    """
    Get all containers for a specific location.
    
    Args:
        location_id (str): The location ID to search for
        
    Returns:
        List[Dict]: List of container dictionaries for the specified location
    """
    try:
        all_containers = get_all_containers()
        
        # Filter containers by location ID
        location_containers = [
            container for container in all_containers
            if container.get('location_id', '').strip() == location_id.strip()
        ]
        
        logger.debug(f"Found {len(location_containers)} containers for location {location_id}")
        return location_containers
        
    except Exception as e:
        logger.error(f"Error getting containers for location {location_id}: {e}")
        return []

def get_containers_by_plant_id(plant_id: str) -> List[Dict]:
    """
    Get all containers that contain a specific plant.
    
    Args:
        plant_id (str): The plant ID to search for
        
    Returns:
        List[Dict]: List of container dictionaries containing the specified plant
    """
    try:
        all_containers = get_all_containers()
        
        # Filter containers by plant ID
        plant_containers = [
            container for container in all_containers
            if container.get('plant_id', '').strip() == plant_id.strip()
        ]
        
        logger.debug(f"Found {len(plant_containers)} containers for plant {plant_id}")
        return plant_containers
        
    except Exception as e:
        logger.error(f"Error getting containers for plant {plant_id}: {e}")
        return []

def get_container_by_id(container_id: str) -> Optional[Dict]:
    """
    Get a specific container by its ID.
    
    Args:
        container_id (str): The container ID to search for
        
    Returns:
        Optional[Dict]: Container data dictionary if found, None otherwise
    """
    try:
        all_containers = get_all_containers()
        
        for container in all_containers:
            if container.get('container_id', '').strip() == container_id.strip():
                logger.debug(f"Found container: {container_id}")
                return container
        
        logger.warning(f"Container not found: {container_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting container by ID {container_id}: {e}")
        return None
