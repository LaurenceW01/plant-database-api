import logging
from typing import List, Dict
from models.field_config import get_canonical_field_name

logger = logging.getLogger(__name__)

def search_plants(query: str) -> List[Dict]:
    """
    Search plants by name or other criteria.
    
    Args:
        query (str): Search query
        
    Returns:
        List[Dict]: List of matching plant dictionaries
    """
    try:
        from .plant_database_operations import get_all_plants
        
        # Get all plants
        all_plants = get_all_plants()
        
        if not query.strip():
            return all_plants
        
        query_lower = query.lower().strip()
        matching_plants = []
        
        for plant in all_plants:
            # Search in plant name
            plant_name = plant.get(get_canonical_field_name('plant_name'), '').lower()
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
