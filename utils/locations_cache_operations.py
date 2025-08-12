"""
Locations Cache Operations Module

Cache management for Locations and Containers data to prevent excessive API calls.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import Dict
import logging
import time

# Set up logging for this module
logger = logging.getLogger(__name__)

# Simple caching to prevent excessive API calls
_locations_cache = None
_containers_cache = None
_plants_cache = None
_cache_timestamp = 0
CACHE_DURATION = 300  # 5 minutes cache

def _is_cache_valid() -> bool:
    """Check if cache is still valid"""
    global _cache_timestamp
    return (time.time() - _cache_timestamp) < CACHE_DURATION

def _update_cache_timestamp():
    """Update cache timestamp"""
    global _cache_timestamp
    _cache_timestamp = time.time()

def _get_cached_plants() -> Dict[str, str]:
    """
    Get cached plant data (ID -> name mapping) to avoid rate limiting.
    
    Returns:
        Dict[str, str]: Mapping of plant_id to plant_name
    """
    global _plants_cache
    
    # Return cached data if valid
    if _plants_cache is not None and _is_cache_valid():
        logger.debug("Returning cached plants data")
        return _plants_cache
    
    try:
        # Import here to avoid circular imports
        from utils.plant_operations import get_plant_data
        
        # Get all plant data
        plants = get_plant_data()
        
        # Create ID -> name mapping
        plant_mapping = {}
        for plant in plants:
            if isinstance(plant, dict) and 'ID' in plant and 'Plant Name' in plant:
                plant_mapping[plant['ID']] = plant['Plant Name']
        
        # Cache the results
        _plants_cache = plant_mapping
        _update_cache_timestamp()
        
        logger.info(f"Cached {len(plant_mapping)} plant names")
        return plant_mapping
        
    except Exception as e:
        logger.error(f"Error getting cached plants: {e}")
        return {}
