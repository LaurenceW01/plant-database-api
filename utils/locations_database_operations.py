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
        
        if not values:
            logger.warning("No location data found")
            return []
        
        # First row contains headers
        headers = values[0]
        locations = []
        
        # Process each location row
        for row in values[1:]:
            # Pad row with empty strings if needed
            padded_row = row + [''] * (len(headers) - len(row))
            
            # Create location dictionary
            location = {}
            for i, header in enumerate(headers):
                location[header] = padded_row[i] if i < len(padded_row) else ''
            
            # Only add locations with valid ID
            if location.get('Location ID', '').strip():
                locations.append(location)
        
        logger.info(f"Retrieved {len(locations)} locations from database")
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
            if location.get('Location ID', '').strip() == location_id.strip():
                logger.debug(f"Found location: {location_id}")
                return location
        
        logger.warning(f"Location not found: {location_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting location by ID {location_id}: {e}")
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
        
        if not values:
            logger.warning("No container data found")
            return []
        
        # First row contains headers
        headers = values[0]
        containers = []
        
        # Process each container row
        for row in values[1:]:
            # Pad row with empty strings if needed
            padded_row = row + [''] * (len(headers) - len(row))
            
            # Create container dictionary
            container = {}
            for i, header in enumerate(headers):
                container[header] = padded_row[i] if i < len(padded_row) else ''
            
            # Only add containers with valid ID
            if container.get('Container ID', '').strip():
                containers.append(container)
        
        logger.info(f"Retrieved {len(containers)} containers from database")
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
            if container.get('Location ID', '').strip() == location_id.strip()
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
            if container.get('Plant ID', '').strip() == plant_id.strip()
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
            if container.get('Container ID', '').strip() == container_id.strip():
                logger.debug(f"Found container: {container_id}")
                return container
        
        logger.warning(f"Container not found: {container_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting container by ID {container_id}: {e}")
        return None
