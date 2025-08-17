"""
Locations Intelligence Operations Module

Advanced analysis and intelligence functions for location and container data.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import List, Dict, Optional
import logging

# Set up logging for this module
logger = logging.getLogger(__name__)

def get_plant_location_context(plant_id: str) -> List[Dict]:
    """
    Get comprehensive location and container context for a specific plant.
    
    OPTIMIZED: Fetches all locations once to avoid rate limit issues.
    
    Args:
        plant_id (str): The plant ID to get context for
        
    Returns:
        List[Dict]: List of context dictionaries, each containing:
            - container: Dict (container information)
            - location: Dict (location information) 
            - context: Dict (combined analysis for care recommendations)
    """
    try:
        from .locations_database_operations import get_containers_by_plant_id, get_all_locations
        
        # Get all containers for this plant
        plant_containers = get_containers_by_plant_id(plant_id)
        
        if not plant_containers:
            logger.warning(f"No containers found for plant {plant_id}")
            return []
        
        # OPTIMIZATION: Fetch all locations once instead of calling get_location_by_id for each container
        all_locations = get_all_locations()
        locations_dict = {loc.get('location_id', ''): loc for loc in all_locations}
        
        contexts = []
        
        # For each container, get location details and create context
        for container in plant_containers:
            location_id = container.get('location_id', '')
            location = locations_dict.get(location_id)
            
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
                logger.warning(f"Location {location_id} not found for container {container['container_id']}")
        
        logger.info(f"Generated {len(contexts)} location contexts for plant {plant_id} (optimized - 1 API call)")
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

def get_location_profile(location_id: str) -> Optional[Dict]:
    """
    Get comprehensive location profile combining location data with container statistics.
    
    This function implements the Phase 2 location profile intelligence by aggregating
    location data with container distribution and usage statistics.
    
    Args:
        location_id (str): The location ID to get profile for
        
    Returns:
        Optional[Dict]: Enhanced location profile with aggregated metadata or None if not found
    """
    try:
        from .locations_database_operations import get_location_by_id, get_containers_by_location_id
        
        # Get base location data
        location = get_location_by_id(location_id)
        if not location:
            logger.warning(f"Location {location_id} not found for profile generation")
            return None
        
        # Get all containers at this location
        containers = get_containers_by_location_id(location_id)
        
        # Generate aggregated statistics
        profile = {
            'location_data': location,
            'container_statistics': _calculate_container_statistics(containers),
            'care_intelligence': _generate_location_care_intelligence(location, containers),
            'optimization_opportunities': _identify_location_optimization_opportunities(location, containers),
            'plant_distribution': _analyze_plant_distribution(containers)
        }
        
        logger.info(f"Generated location profile for location {location_id}")
        return profile
        
    except Exception as e:
        logger.error(f"Error generating location profile for {location_id}: {e}")
        return None

def _calculate_container_statistics(containers: List[Dict]) -> Dict:
    """
    Calculate comprehensive container statistics for a location.
    
    Args:
        containers (List[Dict]): List of containers at the location
        
    Returns:
        Dict: Container statistics including counts, types, materials, and sizes
    """
    if not containers:
        return {
            'total_containers': 0,
            'unique_plants': 0,
            'container_types': {},
            'container_sizes': {},
            'container_materials': {},
            'type_breakdown': [],
            'size_breakdown': [],
            'material_breakdown': []
        }
    
    # Count unique plants
    unique_plants = len(set(container.get('plant_id', '') for container in containers if container.get('plant_id', '')))
    
    # Aggregate container types
    type_counts = {}
    size_counts = {}
    material_counts = {}
    
    for container in containers:
        # Count types
        container_type = container.get('container_type', 'Unknown')
        type_counts[container_type] = type_counts.get(container_type, 0) + 1
        
        # Count sizes
        container_size = container.get('container_size', 'Unknown')
        size_counts[container_size] = size_counts.get(container_size, 0) + 1
        
        # Count materials
        container_material = container.get('container_material', 'Unknown')
        material_counts[container_material] = material_counts.get(container_material, 0) + 1
    
    # Create breakdown lists
    type_breakdown = [{'type': k, 'count': v, 'percentage': round(v/len(containers)*100, 1)} 
                     for k, v in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)]
    
    size_breakdown = [{'size': k, 'count': v, 'percentage': round(v/len(containers)*100, 1)} 
                     for k, v in sorted(size_counts.items(), key=lambda x: x[1], reverse=True)]
    
    material_breakdown = [{'material': k, 'count': v, 'percentage': round(v/len(containers)*100, 1)} 
                         for k, v in sorted(material_counts.items(), key=lambda x: x[1], reverse=True)]
    
    return {
        'total_containers': len(containers),
        'unique_plants': unique_plants,
        'container_types': type_counts,
        'container_sizes': size_counts,
        'container_materials': material_counts,
        'type_breakdown': type_breakdown,
        'size_breakdown': size_breakdown,
        'material_breakdown': material_breakdown
    }

def _generate_location_care_intelligence(location: Dict, containers: List[Dict]) -> Dict:
    """
    Generate care intelligence based on location and container analysis.
    
    Args:
        location (Dict): Location information
        containers (List[Dict]): List of containers at the location
        
    Returns:
        Dict: Care intelligence recommendations and insights
    """
    if not containers:
        return {
            'watering_strategy': 'No containers at this location',
            'sun_exposure_notes': 'Location has no active containers',
            'care_complexity_summary': 'No care requirements',
            'seasonal_considerations': []
        }
    
    total_sun_hours = float(location.get('total_sun_hours', '0') or '0')
    afternoon_sun_hours = float(location.get('afternoon_sun_hours', '0') or '0')
    
    # Watering strategy based on containers and sun exposure
    plastic_containers = sum(1 for c in containers if c.get('container_material', '').lower() == 'plastic')
    small_containers = sum(1 for c in containers if c.get('container_size', '').lower() == 'small')
    
    watering_notes = []
    if plastic_containers > 0 and afternoon_sun_hours > 2:
        watering_notes.append(f'{plastic_containers} plastic containers need morning watering')
    if small_containers > 0:
        watering_notes.append(f'{small_containers} small containers need frequent monitoring')
    
    # Sun exposure analysis
    if total_sun_hours > 7:
        sun_strategy = 'High sun location - monitor for heat stress'
    elif total_sun_hours > 4:
        sun_strategy = 'Moderate sun location - good for most plants'
    else:
        sun_strategy = 'Lower sun location - suitable for shade-tolerant plants'
    
    # Overall complexity
    high_complexity = sum(1 for c in containers if _assess_care_complexity(c, location) == 'high')
    
    return {
        'watering_strategy': '; '.join(watering_notes) if watering_notes else 'Standard watering based on individual plant needs',
        'sun_exposure_notes': sun_strategy,
        'care_complexity_summary': f'{high_complexity} high-complexity setups out of {len(containers)} total',
        'seasonal_considerations': _get_seasonal_considerations(location, containers)
    }

def _get_seasonal_considerations(location: Dict, containers: List[Dict]) -> List[str]:
    """
    Get seasonal care considerations for a location.
    
    Args:
        location (Dict): Location information
        containers (List[Dict]): List of containers at the location
        
    Returns:
        List[str]: Seasonal care considerations
    """
    considerations = []
    
    afternoon_sun_hours = float(location.get('afternoon_sun_hours', '0') or '0')
    
    # Summer considerations
    if afternoon_sun_hours > 3:
        considerations.append('Summer: Provide afternoon shade for sensitive plants')
    
    # Container material considerations
    plastic_count = sum(1 for c in containers if c.get('container_material', '').lower() == 'plastic')
    if plastic_count > 0:
        considerations.append(f'Summer: Monitor {plastic_count} plastic containers for overheating')
    
    # Winter considerations
    if location.get('microclimate_conditions', '').lower().find('exposed') != -1:
        considerations.append('Winter: Protect containers from freezing winds')
    
    return considerations

def _identify_location_optimization_opportunities(location: Dict, containers: List[Dict]) -> List[Dict]:
    """
    Identify optimization opportunities for a location.
    
    Args:
        location (Dict): Location information
        containers (List[Dict]): List of containers at the location
        
    Returns:
        List[Dict]: List of optimization opportunities
    """
    opportunities = []
    
    if not containers:
        return opportunities
    
    # Container material optimization
    plastic_in_high_sun = [c for c in containers 
                          if c.get('container_material', '').lower() == 'plastic' 
                          and float(location.get('afternoon_sun_hours', '0') or '0') > 3]
    
    if plastic_in_high_sun:
        opportunities.append({
            'type': 'container_material',
            'priority': 'medium',
            'description': f'Consider upgrading {len(plastic_in_high_sun)} plastic containers to ceramic or terracotta',
            'benefit': 'Better root temperature control in afternoon sun'
        })
    
    # Small container optimization
    small_containers = [c for c in containers if c.get('container_size', '').lower() == 'small']
    if len(small_containers) > 3:
        opportunities.append({
            'type': 'container_size',
            'priority': 'low',
            'description': f'Consider consolidating some of {len(small_containers)} small containers',
            'benefit': 'Reduced watering frequency and better plant growth'
        })
    
    return opportunities

def _analyze_plant_distribution(containers: List[Dict]) -> Dict:
    """
    Analyze plant distribution across containers.
    
    Args:
        containers (List[Dict]): List of containers
        
    Returns:
        Dict: Plant distribution analysis
    """
    if not containers:
        return {
            'plant_names': [],
            'unique_count': 0,
            'container_utilization': 'No containers'
        }
    
    from .locations_cache_operations import _get_cached_plants
    
    # Get plant names
    plant_mapping = _get_cached_plants()
    
    plant_ids = [c.get('plant_id', '') for c in containers if c.get('plant_id', '')]
    unique_plant_ids = list(set(plant_ids))
    
    plant_names = []
    for plant_id in unique_plant_ids:
        plant_name = plant_mapping.get(plant_id, f'Plant ID {plant_id}')
        plant_names.append(plant_name)
    
    return {
        'plant_names': sorted(plant_names),
        'unique_count': len(unique_plant_ids),
        'container_utilization': f'{len(containers)} containers housing {len(unique_plant_ids)} unique plants'
    }
