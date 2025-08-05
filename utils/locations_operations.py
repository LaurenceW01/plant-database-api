"""
Locations and Containers Operations Module

This module provides data access and intelligence functions for the Locations and Containers sheets,
enabling location-specific care recommendations and container-aware plant management.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import List, Dict, Optional, Any
import logging
from config.config import init_sheets_client, SPREADSHEET_ID
from utils.sheets_client import sheets_client, check_rate_limit

# Set up logging for this module
logger = logging.getLogger(__name__)

# Sheet ranges for accessing Locations and Containers data
LOCATIONS_RANGE = 'Locations!A:G'  # Location ID through Microclimate Conditions
CONTAINERS_RANGE = 'Containers!A:F'  # Container ID through Container Material

def get_all_locations() -> List[Dict]:
    """
    Get all locations from the Locations sheet with complete metadata.
    
    Returns:
        List[Dict]: List of location dictionaries with keys:
            - location_id: str
            - location_name: str  
            - morning_sun_hours: int
            - afternoon_sun_hours: int
            - evening_sun_hours: int
            - shade_pattern: str
            - microclimate_conditions: str
            - total_sun_hours: int (calculated)
    """
    try:
        check_rate_limit()  # Respect API rate limits
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=LOCATIONS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Need header + at least one data row
            logger.warning("No location data found in sheet")
            return []
        
        headers = values[0]  # First row contains headers
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
        logger.error(f"Error getting locations: {e}")
        return []

def get_location_by_id(location_id: str) -> Optional[Dict]:
    """
    Get a specific location by its ID.
    
    Args:
        location_id (str): The location ID to look up
        
    Returns:
        Optional[Dict]: Location dictionary if found, None otherwise
    """
    try:
        all_locations = get_all_locations()
        for location in all_locations:
            if location['location_id'] == str(location_id):
                return location
        
        logger.warning(f"Location not found for ID: {location_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting location by ID {location_id}: {e}")
        return None

def get_all_containers() -> List[Dict]:
    """
    Get all containers from the Containers sheet with complete metadata.
    
    Returns:
        List[Dict]: List of container dictionaries with keys:
            - container_id: str
            - plant_id: str
            - location_id: str
            - container_type: str
            - container_size: str
            - container_material: str
    """
    try:
        check_rate_limit()  # Respect API rate limits
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=CONTAINERS_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:  # Need header + at least one data row
            logger.warning("No container data found in sheet")
            return []
        
        headers = values[0]  # First row contains headers
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
        logger.error(f"Error getting containers: {e}")
        return []

def get_containers_by_location_id(location_id: str) -> List[Dict]:
    """
    Get all containers at a specific location.
    
    Args:
        location_id (str): The location ID to filter by
        
    Returns:
        List[Dict]: List of containers at the specified location
    """
    try:
        all_containers = get_all_containers()
        location_containers = [
            container for container in all_containers 
            if container['location_id'] == str(location_id)
        ]
        
        logger.info(f"Found {len(location_containers)} containers at location {location_id}")
        return location_containers
        
    except Exception as e:
        logger.error(f"Error getting containers for location {location_id}: {e}")
        return []

def get_containers_by_plant_id(plant_id: str) -> List[Dict]:
    """
    Get all containers for a specific plant.
    
    Args:
        plant_id (str): The plant ID to filter by
        
    Returns:
        List[Dict]: List of containers holding the specified plant
    """
    try:
        all_containers = get_all_containers()
        plant_containers = [
            container for container in all_containers 
            if container['plant_id'] == str(plant_id)
        ]
        
        logger.info(f"Found {len(plant_containers)} containers for plant {plant_id}")
        return plant_containers
        
    except Exception as e:
        logger.error(f"Error getting containers for plant {plant_id}: {e}")
        return []

def get_container_by_id(container_id: str) -> Optional[Dict]:
    """
    Get a specific container by its ID.
    
    Args:
        container_id (str): The container ID to look up
        
    Returns:
        Optional[Dict]: Container dictionary if found, None otherwise
    """
    try:
        all_containers = get_all_containers()
        for container in all_containers:
            if container['container_id'] == str(container_id):
                return container
        
        logger.warning(f"Container not found for ID: {container_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting container by ID {container_id}: {e}")
        return None

def get_plant_location_context(plant_id: str) -> List[Dict]:
    """
    Get comprehensive location and container context for a specific plant.
    
    This function provides the foundation for location-aware plant care recommendations
    by combining container and location data for a specific plant.
    
    Args:
        plant_id (str): The plant ID to get context for
        
    Returns:
        List[Dict]: List of context dictionaries, each containing:
            - container: Dict (container information)
            - location: Dict (location information) 
            - context: Dict (combined analysis for care recommendations)
    """
    try:
        # Get all containers for this plant
        plant_containers = get_containers_by_plant_id(plant_id)
        
        if not plant_containers:
            logger.warning(f"No containers found for plant {plant_id}")
            return []
        
        contexts = []
        
        # For each container, get location details and create context
        for container in plant_containers:
            location = get_location_by_id(container['location_id'])
            
            if location:
                # Create combined context for this plant-container-location combination
                context = {
                    'container': container,
                    'location': location,
                    'context': {
                        'placement_description': f"{container['container_type']} ({container['container_size']}, {container['container_material']}) in {location['location_name']}",
                        'sun_exposure_summary': f"{location['total_sun_hours']} total hours ({location['shade_pattern']})",
                        'care_complexity': _assess_care_complexity(container, location),
                        'priority_considerations': _get_priority_considerations(container, location)
                    }
                }
                contexts.append(context)
            else:
                logger.warning(f"Location {container['location_id']} not found for container {container['container_id']}")
        
        logger.info(f"Generated {len(contexts)} location contexts for plant {plant_id}")
        return contexts
        
    except Exception as e:
        logger.error(f"Error getting plant location context for plant {plant_id}: {e}")
        return []

def _assess_care_complexity(container: Dict, location: Dict) -> str:
    """
    Assess the care complexity based on container and location factors.
    
    Args:
        container (Dict): Container information
        location (Dict): Location information
        
    Returns:
        str: Care complexity level (low, medium, high)
    """
    complexity_factors = 0
    
    # Sun exposure complexity
    if location['total_sun_hours'] > 8:  # Very high sun
        complexity_factors += 2
    elif location['total_sun_hours'] > 6:  # High sun
        complexity_factors += 1
    
    # Container material considerations  
    if container['container_material'].lower() == 'plastic':
        if location['afternoon_sun_hours'] > 2:  # Plastic in afternoon sun
            complexity_factors += 1
    
    # Container size considerations
    if container['container_size'].lower() == 'small':
        complexity_factors += 1  # Small containers need more frequent attention
    
    # Microclimate complexity
    if 'facing' in location['microclimate_conditions'].lower():
        complexity_factors += 1  # Directional microclimates need special consideration
    
    # Determine overall complexity
    if complexity_factors >= 4:
        return 'high'
    elif complexity_factors >= 2:
        return 'medium'
    else:
        return 'low'

def _get_priority_considerations(container: Dict, location: Dict) -> List[str]:
    """
    Get priority care considerations based on container and location combination.
    
    Args:
        container (Dict): Container information  
        location (Dict): Location information
        
    Returns:
        List[str]: List of priority care considerations
    """
    considerations = []
    
    # Plastic container in high sun
    if (container['container_material'].lower() == 'plastic' and 
        location['afternoon_sun_hours'] > 2):
        considerations.append('Morning watering preferred to prevent root heating')
    
    # High sun exposure
    if location['total_sun_hours'] > 7:
        considerations.append('Daily watering checks during hot weather')
    
    # Small containers
    if container['container_size'].lower() == 'small':
        considerations.append('Frequent moisture monitoring due to small container size')
    
    # Evening sun locations
    if location['evening_sun_hours'] > 2:
        considerations.append('Water early morning to prepare for evening heat stress')
    
    # North facing locations
    if 'north' in location['microclimate_conditions'].lower():
        considerations.append('Cooler microclimate - adjust watering frequency accordingly')
    
    return considerations