"""
Locations and Containers Operations Module

This module provides data access and intelligence functions for the Locations and Containers sheets,
enabling location-specific care recommendations and container-aware plant management.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import List, Dict, Optional
import logging
import time
from config.config import SPREADSHEET_ID
from utils.sheets_client import sheets_client, check_rate_limit

# Set up logging for this module
logger = logging.getLogger(__name__)

# Simple caching to prevent excessive API calls
_locations_cache = None
_containers_cache = None
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

# Sheet ranges for accessing Locations and Containers data
LOCATIONS_RANGE = 'Locations!A:G'  # Location ID through Microclimate Conditions
CONTAINERS_RANGE = 'Containers!A:F'  # Container ID through Container Material

def get_all_locations() -> List[Dict]:
    """
    Get all locations from the Locations sheet with complete metadata.
    Uses caching to reduce API calls.
    
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
    global _locations_cache
    
    # Return cached data if valid
    if _locations_cache is not None and _is_cache_valid():
        logger.debug("Returning cached locations data")
        return _locations_cache
    
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
        
        # Cache the results
        _locations_cache = locations
        _update_cache_timestamp()
        
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
    Uses caching to reduce API calls.
    
    Returns:
        List[Dict]: List of container dictionaries with keys:
            - container_id: str
            - plant_id: str
            - location_id: str
            - container_type: str
            - container_size: str
            - container_material: str
    """
    global _containers_cache
    
    # Return cached data if valid
    if _containers_cache is not None and _is_cache_valid():
        logger.debug("Returning cached containers data")
        return _containers_cache
    
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
        
        # Cache the results
        _containers_cache = containers
        _update_cache_timestamp()
        
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

# =============================================================================
# PHASE 2: ADVANCED METADATA AGGREGATION
# =============================================================================

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
    unique_plants = len(set(container['plant_id'] for container in containers))
    
    # Aggregate container types
    type_counts = {}
    size_counts = {}
    material_counts = {}
    
    for container in containers:
        # Count container types
        container_type = container.get('container_type', 'Unknown')
        type_counts[container_type] = type_counts.get(container_type, 0) + 1
        
        # Count container sizes
        container_size = container.get('container_size', 'Unknown')
        size_counts[container_size] = size_counts.get(container_size, 0) + 1
        
        # Count container materials
        container_material = container.get('container_material', 'Unknown')
        material_counts[container_material] = material_counts.get(container_material, 0) + 1
    
    return {
        'total_containers': len(containers),
        'unique_plants': unique_plants,
        'container_types': type_counts,
        'container_sizes': size_counts,
        'container_materials': material_counts,
        'type_breakdown': [f"{count} {type_name}" for type_name, count in type_counts.items()],
        'size_breakdown': [f"{count} {size}" for size, count in size_counts.items()],
        'material_breakdown': [f"{count} {material}" for material, count in material_counts.items()]
    }

def _generate_location_care_intelligence(location: Dict, containers: List[Dict]) -> Dict:
    """
    Generate intelligent care recommendations based on location and container combination.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Containers at this location
        
    Returns:
        Dict: Intelligent care recommendations and insights
    """
    intelligence = {
        'watering_strategy': {},
        'optimal_times': {},
        'material_considerations': [],
        'risk_assessments': []
    }
    
    # Analyze sun exposure patterns for watering recommendations
    total_sun = location.get('total_sun_hours', 0)
    morning_sun = location.get('morning_sun_hours', 0)
    afternoon_sun = location.get('afternoon_sun_hours', 0)
    evening_sun = location.get('evening_sun_hours', 0)
    
    # Determine optimal watering times based on sun pattern
    if evening_sun > afternoon_sun and evening_sun > morning_sun:
        intelligence['optimal_times']['primary'] = 'early_morning'
        intelligence['optimal_times']['reasoning'] = 'Evening sun dominant - water early to prepare plants for end-of-day heat stress'
    elif afternoon_sun > 3:
        intelligence['optimal_times']['primary'] = 'early_morning'
        intelligence['optimal_times']['reasoning'] = 'High afternoon sun - water early to prevent heat stress during peak sun'
    elif morning_sun > afternoon_sun and morning_sun > evening_sun:
        intelligence['optimal_times']['primary'] = 'late_evening'
        intelligence['optimal_times']['reasoning'] = 'Morning sun dominant - can water in evening after sun exposure'
    else:
        intelligence['optimal_times']['primary'] = 'early_morning'
        intelligence['optimal_times']['reasoning'] = 'General recommendation for consistent plant care'
    
    # Analyze container materials for heat considerations
    plastic_containers = [c for c in containers if c.get('container_material', '').lower() == 'plastic']
    if plastic_containers and afternoon_sun > 2:
        intelligence['material_considerations'].append({
            'concern': 'plastic_heat_retention',
            'containers_affected': len(plastic_containers),
            'recommendation': 'Monitor plastic containers closely during hot weather - they retain heat and may stress roots',
            'priority': 'high' if afternoon_sun > 4 else 'medium'
        })
    
    # Assess container size vs sun exposure risks
    small_containers = [c for c in containers if c.get('container_size', '').lower() == 'small']
    if small_containers and total_sun > 6:
        intelligence['risk_assessments'].append({
            'risk_type': 'small_container_high_sun',
            'containers_affected': len(small_containers),
            'description': 'Small containers in high sun locations dry out quickly',
            'mitigation': 'Check soil moisture daily, consider grouping for easier monitoring',
            'priority': 'high' if total_sun > 8 else 'medium'
        })
    
    # Watering frequency recommendations
    if total_sun > 8:
        frequency = 'daily_checks'
        frequency_note = 'Very high sun exposure requires daily monitoring'
    elif total_sun > 6:
        frequency = 'every_other_day'
        frequency_note = 'High sun exposure - check every 1-2 days'
    elif total_sun > 3:
        frequency = 'twice_weekly'
        frequency_note = 'Moderate sun - check 2-3 times per week'
    else:
        frequency = 'weekly'
        frequency_note = 'Low sun - weekly checks usually sufficient'
    
    intelligence['watering_strategy'] = {
        'frequency': frequency,
        'frequency_note': frequency_note,
        'total_containers': len(containers),
        'special_considerations': len(intelligence['material_considerations']) + len(intelligence['risk_assessments'])
    }
    
    return intelligence

def _identify_location_optimization_opportunities(location: Dict, containers: List[Dict]) -> List[Dict]:
    """
    Identify optimization opportunities for the location based on container distribution and conditions.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Containers at this location
        
    Returns:
        List[Dict]: List of optimization opportunities with priority and description
    """
    opportunities = []
    
    # Check for container material optimization
    plastic_containers = [c for c in containers if c.get('container_material', '').lower() == 'plastic']
    afternoon_sun = location.get('afternoon_sun_hours', 0)
    
    if plastic_containers and afternoon_sun > 3:
        opportunities.append({
            'type': 'container_material',
            'priority': 'medium',
            'description': f'{len(plastic_containers)} plastic containers in high afternoon sun',
            'recommendation': 'Consider upgrading to ceramic or terracotta containers for better temperature regulation',
            'containers_affected': len(plastic_containers)
        })
    
    # Check for container size optimization
    container_sizes = [c.get('container_size', '') for c in containers]
    small_count = sum(1 for size in container_sizes if size.lower() == 'small')
    total_sun = location.get('total_sun_hours', 0)
    
    if small_count > 2 and total_sun > 6:
        opportunities.append({
            'type': 'container_size',
            'priority': 'medium',
            'description': f'{small_count} small containers in high sun location',
            'recommendation': 'Consider upgrading to medium containers to reduce watering frequency',
            'containers_affected': small_count
        })
    
    # Check for grouping opportunities
    if len(containers) > 5:
        opportunities.append({
            'type': 'care_efficiency',
            'priority': 'low',
            'description': f'{len(containers)} containers at this location',
            'recommendation': 'Consider grouping containers by care requirements for efficient maintenance',
            'containers_affected': len(containers)
        })
    
    # Check for microclimate utilization
    microclimate = location.get('microclimate_conditions', '').lower()
    if 'north' in microclimate and len(containers) < 3:
        opportunities.append({
            'type': 'location_utilization',
            'priority': 'low',
            'description': 'North-facing microclimate underutilized',
            'recommendation': 'This cooler microclimate could support more shade-tolerant plants',
            'containers_affected': 0
        })
    
    return opportunities

def _analyze_plant_distribution(containers: List[Dict]) -> Dict:
    """
    Analyze plant distribution patterns at the location.
    Includes plant names for better GPT responses.
    
    Args:
        containers (List[Dict]): Containers at the location
        
    Returns:
        Dict: Plant distribution analysis with plant names
    """
    if not containers:
        return {
            'total_plants': 0,
            'unique_plants': 0,
            'plant_counts': {},
            'plant_details': {},
            'multiple_container_plants': [],
            'single_container_plants': []
        }
    
    # Import here to avoid circular imports
    from utils.plant_operations import find_plant_by_id_or_name
    
    # Count plants by ID and get their names
    plant_counts = {}
    plant_details = {}
    
    for container in containers:
        plant_id = container.get('plant_id', 'Unknown')
        plant_counts[plant_id] = plant_counts.get(plant_id, 0) + 1
        
        # Get plant name if we don't have it yet
        if plant_id not in plant_details and plant_id != 'Unknown':
            try:
                plant_row, plant_data = find_plant_by_id_or_name(plant_id)
                if plant_data and len(plant_data) > 1:
                    plant_name = plant_data[1]
                else:
                    plant_name = f"Plant ID {plant_id}"
                plant_details[plant_id] = {
                    'plant_name': plant_name,
                    'containers': []
                }
            except Exception as e:
                logger.warning(f"Could not get plant name for ID {plant_id}: {e}")
                plant_details[plant_id] = {
                    'plant_name': f"Plant ID {plant_id}",
                    'containers': []
                }
    
    # Add container information to plant details
    for container in containers:
        plant_id = container.get('plant_id', 'Unknown')
        if plant_id in plant_details:
            plant_details[plant_id]['containers'].append({
                'container_id': container.get('container_id'),
                'material': container.get('container_material'),
                'size': container.get('container_size'),
                'type': container.get('container_type')
            })
    
    # Categorize plants by container count
    multiple_container_plants = []
    single_container_plants = []
    
    for plant_id, count in plant_counts.items():
        plant_info = {
            'plant_id': plant_id,
            'plant_name': plant_details.get(plant_id, {}).get('plant_name', f"Plant ID {plant_id}"),
            'container_count': count
        }
        
        if count > 1:
            multiple_container_plants.append(plant_info)
        else:
            single_container_plants.append(plant_info)
    
    return {
        'total_plants': sum(plant_counts.values()),
        'unique_plants': len(plant_counts),
        'plant_counts': plant_counts,
        'plant_details': plant_details,
        'multiple_container_plants': multiple_container_plants,
        'single_container_plants': single_container_plants,
        'distribution_summary': f"{len(single_container_plants)} single-container plants, {len(multiple_container_plants)} multi-container plants"
    }

def generate_location_recommendations(location_id: str) -> Dict:
    """
    Generate comprehensive recommendations for a location using cross-reference intelligence.
    
    This function implements the Phase 2 cross-reference intelligence system by analyzing
    location and container data together to provide smart recommendations.
    
    Args:
        location_id (str): The location ID to generate recommendations for
        
    Returns:
        Dict: Comprehensive recommendations including watering strategy, plant placement, and optimization
    """
    try:
        # Get location profile with aggregated data
        location_profile = get_location_profile(location_id)
        if not location_profile:
            logger.warning(f"Could not generate recommendations - location profile not found for {location_id}")
            return {}
        
        location = location_profile['location_data']
        containers = get_containers_by_location_id(location_id)
        
        # Generate cross-reference recommendations
        recommendations = {
            'location_analysis': {
                'location_name': location.get('location_name', 'Unknown'),
                'sun_exposure_profile': _generate_sun_exposure_analysis(location),
                'microclimate_assessment': _assess_microclimate_benefits(location),
                'container_compatibility': _assess_container_location_compatibility(location, containers)
            },
            'watering_strategy': _calculate_optimal_watering_strategy(location, containers),
            'plant_placement': _generate_plant_placement_recommendations(location, containers),
            'optimization_recommendations': location_profile['optimization_opportunities'],
            'care_complexity_assessment': _assess_overall_care_complexity(location, containers)
        }
        
        logger.info(f"Generated comprehensive recommendations for location {location_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating location recommendations for {location_id}: {e}")
        return {}

def _generate_sun_exposure_analysis(location: Dict) -> Dict:
    """
    Generate detailed sun exposure analysis for the location.
    
    Args:
        location (Dict): Location data
        
    Returns:
        Dict: Detailed sun exposure analysis
    """
    morning = location.get('morning_sun_hours', 0)
    afternoon = location.get('afternoon_sun_hours', 0)
    evening = location.get('evening_sun_hours', 0)
    total = location.get('total_sun_hours', 0)
    pattern = location.get('shade_pattern', 'Unknown')
    
    # Determine peak intensity period
    peak_period = 'morning' if morning >= afternoon and morning >= evening else \
                 'afternoon' if afternoon >= evening else 'evening'
    
    # Classify sun intensity
    if total > 8:
        intensity_class = 'very_high'
        intensity_description = 'Very high sun exposure - requires careful water management'
    elif total > 6:
        intensity_class = 'high'
        intensity_description = 'High sun exposure - daily monitoring recommended'
    elif total > 3:
        intensity_class = 'moderate'
        intensity_description = 'Moderate sun exposure - regular monitoring needed'
    else:
        intensity_class = 'low'
        intensity_description = 'Low sun exposure - good for shade-tolerant plants'
    
    return {
        'hours_breakdown': {
            'morning': morning,
            'afternoon': afternoon,
            'evening': evening,
            'total': total
        },
        'pattern': pattern,
        'peak_intensity_period': peak_period,
        'intensity_classification': intensity_class,
        'intensity_description': intensity_description,
        'heat_stress_risk': 'high' if (afternoon > 3 or evening > 3) else 'low'
    }

def _assess_microclimate_benefits(location: Dict) -> Dict:
    """
    Assess microclimate benefits and characteristics.
    
    Args:
        location (Dict): Location data
        
    Returns:
        Dict: Microclimate assessment
    """
    microclimate = location.get('microclimate_conditions', '').lower()
    
    benefits = []
    considerations = []
    
    if 'north' in microclimate:
        benefits.append('Cooler temperatures, less heat stress')
        benefits.append('More consistent moisture levels')
        considerations.append('May need less frequent watering')
        considerations.append('Good for heat-sensitive plants')
    
    if 'facing' in microclimate:
        benefits.append('Directional exposure creates unique growing conditions')
        considerations.append('May have wind exposure to consider')
    
    if 'wall' in microclimate:
        benefits.append('Protected from wind and extreme weather')
        considerations.append('May retain heat from thermal mass')
    
    return {
        'microclimate_type': microclimate,
        'benefits': benefits,
        'care_considerations': considerations,
        'suitability': 'excellent' if 'north' in microclimate else 'good'
    }

def _assess_container_location_compatibility(location: Dict, containers: List[Dict]) -> Dict:
    """
    Assess how well containers are suited to their location.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Containers at location
        
    Returns:
        Dict: Container-location compatibility assessment
    """
    if not containers:
        return {
            'overall_compatibility': 'N/A',
            'compatible_containers': 0,
            'concerning_combinations': [],
            'recommendations': []
        }
    
    concerning_combinations = []
    recommendations = []
    afternoon_sun = location.get('afternoon_sun_hours', 0)
    total_sun = location.get('total_sun_hours', 0)
    
    # Check for problematic combinations
    for container in containers:
        material = container.get('container_material', '').lower()
        size = container.get('container_size', '').lower()
        
        # Plastic containers in high afternoon sun
        if material == 'plastic' and afternoon_sun > 3:
            concerning_combinations.append({
                'container_id': container.get('container_id'),
                'issue': 'Plastic container in high afternoon sun',
                'risk_level': 'medium',
                'impact': 'Root heating, increased water needs'
            })
        
        # Small containers in very high sun
        if size == 'small' and total_sun > 7:
            concerning_combinations.append({
                'container_id': container.get('container_id'),
                'issue': 'Small container in very high sun',
                'risk_level': 'high',
                'impact': 'Rapid moisture loss, frequent watering needed'
            })
    
    # Generate recommendations based on concerns
    if concerning_combinations:
        if any(combo['risk_level'] == 'high' for combo in concerning_combinations):
            recommendations.append('Consider relocating high-risk containers or upgrading container size/material')
        if any('plastic' in combo['issue'].lower() for combo in concerning_combinations):
            recommendations.append('Monitor plastic containers closely during hot weather')
        if any('small' in combo['issue'].lower() for combo in concerning_combinations):
            recommendations.append('Increase watering frequency for small containers')
    
    compatible_count = len(containers) - len(concerning_combinations)
    
    # Determine overall compatibility
    if not concerning_combinations:
        overall = 'excellent'
    elif len(concerning_combinations) < len(containers) / 2:
        overall = 'good'
    else:
        overall = 'needs_attention'
    
    return {
        'overall_compatibility': overall,
        'compatible_containers': compatible_count,
        'concerning_combinations': concerning_combinations,
        'recommendations': recommendations,
        'compatibility_percentage': round((compatible_count / len(containers)) * 100, 1)
    }

def _calculate_optimal_watering_strategy(location: Dict, containers: List[Dict]) -> Dict:
    """
    Calculate optimal watering strategy based on location and container factors.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Containers at location
        
    Returns:
        Dict: Optimal watering strategy recommendations
    """
    if not containers:
        return {
            'strategy': 'No containers at location',
            'timing': 'N/A',
            'frequency': 'N/A'
        }
    
    # Analyze location factors
    afternoon_sun = location.get('afternoon_sun_hours', 0)
    evening_sun = location.get('evening_sun_hours', 0)
    total_sun = location.get('total_sun_hours', 0)
    microclimate = location.get('microclimate_conditions', '').lower()
    
    # Determine optimal timing
    if evening_sun > 3:
        optimal_time = 'early_morning'
        timing_reason = 'High evening sun - water early to prepare plants for end-of-day heat'
    elif afternoon_sun > 3:
        optimal_time = 'early_morning'
        timing_reason = 'High afternoon sun - water early to prevent midday heat stress'
    elif 'north' in microclimate:
        optimal_time = 'morning_or_evening'
        timing_reason = 'North-facing cooler microclimate allows flexible timing'
    else:
        optimal_time = 'early_morning'
        timing_reason = 'General best practice for plant health'
    
    # Calculate frequency based on sun exposure and container factors
    base_frequency_days = 7  # Start with weekly
    
    # Adjust for sun exposure
    if total_sun > 8:
        base_frequency_days = 1  # Daily
    elif total_sun > 6:
        base_frequency_days = 2  # Every other day
    elif total_sun > 3:
        base_frequency_days = 3  # Every 3 days
    
    # Adjust for container factors
    small_containers = sum(1 for c in containers if c.get('container_size', '').lower() == 'small')
    plastic_containers = sum(1 for c in containers if c.get('container_material', '').lower() == 'plastic')
    
    # Small containers need more frequent watering
    if small_containers > len(containers) / 2:
        base_frequency_days = max(1, base_frequency_days - 1)
    
    # Plastic containers in high sun need more attention
    if plastic_containers > 0 and afternoon_sun > 2:
        base_frequency_days = max(1, base_frequency_days - 1)
    
    # North-facing locations can have less frequent watering
    if 'north' in microclimate:
        base_frequency_days = min(7, base_frequency_days + 1)
    
    # Convert to frequency description
    if base_frequency_days == 1:
        frequency_desc = 'Daily monitoring required'
    elif base_frequency_days == 2:
        frequency_desc = 'Every other day'
    elif base_frequency_days == 3:
        frequency_desc = 'Every 2-3 days'
    elif base_frequency_days <= 5:
        frequency_desc = 'Twice weekly'
    else:
        frequency_desc = 'Weekly'
    
    return {
        'optimal_timing': optimal_time,
        'timing_reason': timing_reason,
        'frequency': frequency_desc,
        'frequency_days': base_frequency_days,
        'total_containers': len(containers),
        'special_needs_containers': small_containers + plastic_containers,
        'microclimate_adjustment': 'Less frequent watering' if 'north' in microclimate else 'Standard frequency'
    }

def _generate_plant_placement_recommendations(location: Dict, containers: List[Dict]) -> Dict:
    """
    Generate plant placement recommendations for the location.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Current containers at location
        
    Returns:
        Dict: Plant placement recommendations
    """
    total_sun = location.get('total_sun_hours', 0)
    afternoon_sun = location.get('afternoon_sun_hours', 0)
    microclimate = location.get('microclimate_conditions', '').lower()
    
    # Determine suitable plant types
    if total_sun > 8:
        sun_category = 'full_sun'
        plant_types = ['Sun-loving perennials', 'Drought-tolerant plants', 'Mediterranean herbs']
        cautions = ['Avoid shade-loving plants', 'Ensure adequate water supply']
    elif total_sun > 6:
        sun_category = 'partial_sun'
        plant_types = ['Most vegetables', 'Many flowering plants', 'Fruit plants']
        cautions = ['Monitor for heat stress in very hot weather']
    elif total_sun > 3:
        sun_category = 'partial_shade'
        plant_types = ['Leafy greens', 'Herbs', 'Some flowering plants']
        cautions = ['Avoid full-sun plants']
    else:
        sun_category = 'shade'
        plant_types = ['Shade-tolerant plants', 'Ferns', 'Hostas', 'Some herbs']
        cautions = ['Avoid sun-loving plants', 'Watch for overwatering']
    
    # Container recommendations
    container_recommendations = []
    if afternoon_sun > 3:
        container_recommendations.append('Use ceramic or terracotta containers to prevent root heating')
        container_recommendations.append('Avoid small plastic containers')
    
    if total_sun > 6:
        container_recommendations.append('Medium to large containers recommended for water retention')
    
    if 'north' in microclimate:
        container_recommendations.append('This cool microclimate is excellent for heat-sensitive plants')
    
    return {
        'sun_category': sun_category,
        'suitable_plant_types': plant_types,
        'placement_cautions': cautions,
        'container_recommendations': container_recommendations,
        'current_utilization': f"{len(containers)} containers currently placed",
        'expansion_potential': 'High' if len(containers) < 5 else 'Consider grouping for efficiency'
    }

def _assess_overall_care_complexity(location: Dict, containers: List[Dict]) -> Dict:
    """
    Assess the overall care complexity for this location.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Containers at location
        
    Returns:
        Dict: Overall care complexity assessment
    """
    complexity_score = 0
    complexity_factors = []
    
    # Sun exposure complexity
    total_sun = location.get('total_sun_hours', 0)
    afternoon_sun = location.get('afternoon_sun_hours', 0)
    
    if total_sun > 8:
        complexity_score += 3
        complexity_factors.append('Very high sun exposure requires careful water management')
    elif total_sun > 6:
        complexity_score += 2
        complexity_factors.append('High sun exposure needs regular monitoring')
    elif total_sun < 2:
        complexity_score += 1
        complexity_factors.append('Low light conditions need specialized plant selection')
    
    # Container complexity
    if containers:
        container_materials = [c.get('container_material', '').lower() for c in containers]
        container_sizes = [c.get('container_size', '').lower() for c in containers]
        
        # Plastic containers in high sun
        plastic_count = sum(1 for material in container_materials if material == 'plastic')
        if plastic_count > 0 and afternoon_sun > 2:
            complexity_score += 2
            complexity_factors.append(f'{plastic_count} plastic containers in afternoon sun increase care needs')
        
        # Small containers
        small_count = sum(1 for size in container_sizes if size == 'small')
        if small_count > 0:
            complexity_score += 1
            complexity_factors.append(f'{small_count} small containers need frequent monitoring')
        
        # High container count
        if len(containers) > 8:
            complexity_score += 1
            complexity_factors.append(f'{len(containers)} containers require systematic care approach')
    
    # Determine complexity level
    if complexity_score >= 6:
        complexity_level = 'high'
        management_approach = 'Requires daily attention and systematic monitoring'
    elif complexity_score >= 3:
        complexity_level = 'medium'
        management_approach = 'Regular monitoring with some special considerations'
    else:
        complexity_level = 'low'
        management_approach = 'Straightforward care requirements'
    
    return {
        'complexity_level': complexity_level,
        'complexity_score': complexity_score,
        'complexity_factors': complexity_factors,
        'management_approach': management_approach,
        'container_count': len(containers),
        'recommended_monitoring_frequency': 'Daily' if complexity_level == 'high' else 'Every 2-3 days' if complexity_level == 'medium' else 'Weekly'
    }

def get_all_location_profiles() -> List[Dict]:
    """
    Get comprehensive profiles for all locations with aggregated container statistics.
    
    This function implements the Phase 2 location profiles view by creating
    virtual location profiles that combine location data with container statistics.
    Equivalent to the SQL view described in the strategy document.
    
    Returns:
        List[Dict]: List of location profiles with aggregated metadata
    """
    try:
        # Get all locations and containers
        all_locations = get_all_locations()
        all_containers = get_all_containers()
        
        if not all_locations:
            logger.warning("No locations found for profile generation")
            return []
        
        # Group containers by location
        containers_by_location = {}
        for container in all_containers:
            location_id = container.get('location_id', '')
            if location_id not in containers_by_location:
                containers_by_location[location_id] = []
            containers_by_location[location_id].append(container)
        
        # Generate profiles for each location
        location_profiles = []
        for location in all_locations:
            location_id = location.get('location_id', '')
            location_containers = containers_by_location.get(location_id, [])
            
            # Calculate aggregated statistics
            unique_plants = len(set(c['plant_id'] for c in location_containers))
            
            # Aggregate container types, sizes, and materials
            container_types = list(set(c.get('container_type', 'Unknown') for c in location_containers))
            container_sizes = list(set(c.get('container_size', 'Unknown') for c in location_containers))
            container_materials = list(set(c.get('container_material', 'Unknown') for c in location_containers))
            
            # Create profile combining location and container data
            profile = {
                'location_id': location_id,
                'location_name': location.get('location_name', 'Unknown'),
                'morning_sun_hours': location.get('morning_sun_hours', 0),
                'afternoon_sun_hours': location.get('afternoon_sun_hours', 0),
                'evening_sun_hours': location.get('evening_sun_hours', 0),
                'total_sun_hours': location.get('total_sun_hours', 0),
                'shade_pattern': location.get('shade_pattern', ''),
                'microclimate_conditions': location.get('microclimate_conditions', ''),
                'total_containers': len(location_containers),
                'unique_plants': unique_plants,
                'container_types': container_types,
                'container_sizes': container_sizes,
                'container_materials': container_materials,
                'containers_detail': location_containers
            }
            
            location_profiles.append(profile)
        
        logger.info(f"Generated {len(location_profiles)} location profiles")
        return location_profiles
        
    except Exception as e:
        logger.error(f"Error generating all location profiles: {e}")
        return []

def get_garden_metadata_enhanced() -> Dict:
    """
    Get comprehensive garden metadata with location and container intelligence.
    
    This function implements the enhanced garden metadata aggregation described
    in Phase 2, providing a complete overview of the garden's location and
    container distribution with intelligence insights.
    
    Returns:
        Dict: Comprehensive garden metadata with enhanced intelligence
    """
    try:
        # Get all data
        location_profiles = get_all_location_profiles()
        all_containers = get_all_containers()
        all_locations = get_all_locations()
        
        if not location_profiles:
            logger.warning("No location profiles available for enhanced metadata")
            return {}
        
        # Calculate garden overview statistics
        garden_overview = _calculate_garden_statistics(location_profiles, all_containers)
        
        # Analyze location distribution
        location_distribution = _analyze_location_usage(location_profiles)
        
        # Analyze container intelligence
        container_intelligence = _analyze_container_distribution(all_containers, all_locations)
        
        # Assess care complexity
        care_complexity = _assess_care_requirements(location_profiles)
        
        # Identify optimization opportunities
        optimization_opportunities = _identify_improvement_areas(location_profiles)
        
        metadata = {
            'garden_overview': garden_overview,
            'location_distribution': location_distribution,
            'container_intelligence': container_intelligence,
            'care_complexity_analysis': care_complexity,
            'optimization_opportunities': optimization_opportunities,
            'generated_at': f"Generated at: {__import__('datetime').datetime.now().isoformat()}",
            'total_locations': len(location_profiles),
            'total_containers': len(all_containers)
        }
        
        logger.info("Generated enhanced garden metadata successfully")
        return metadata
        
    except Exception as e:
        logger.error(f"Error generating enhanced garden metadata: {e}")
        return {}

def _calculate_garden_statistics(location_profiles: List[Dict], all_containers: List[Dict]) -> Dict:
    """
    Calculate comprehensive garden statistics.
    
    Args:
        location_profiles (List[Dict]): All location profiles
        all_containers (List[Dict]): All containers
        
    Returns:
        Dict: Garden overview statistics
    """
    if not location_profiles:
        return {
            'total_locations': 0,
            'total_containers': 0,
            'total_plants': 0,
            'utilization': 'No data available'
        }
    
    # Basic counts
    total_locations = len(location_profiles)
    total_containers = len(all_containers)
    
    # Count unique plants
    unique_plants = len(set(c['plant_id'] for c in all_containers))
    
    # Calculate utilization metrics
    locations_with_containers = sum(1 for profile in location_profiles if profile['total_containers'] > 0)
    utilization_percentage = round((locations_with_containers / total_locations) * 100, 1) if total_locations > 0 else 0
    
    # Average containers per location
    avg_containers_per_location = round(total_containers / total_locations, 1) if total_locations > 0 else 0
    
    # Sun exposure distribution
    sun_categories = {
        'very_high': sum(1 for p in location_profiles if p['total_sun_hours'] > 8),
        'high': sum(1 for p in location_profiles if 6 < p['total_sun_hours'] <= 8),
        'moderate': sum(1 for p in location_profiles if 3 < p['total_sun_hours'] <= 6),
        'low': sum(1 for p in location_profiles if p['total_sun_hours'] <= 3)
    }
    
    return {
        'total_locations': total_locations,
        'total_containers': total_containers,
        'unique_plants': unique_plants,
        'locations_with_containers': locations_with_containers,
        'location_utilization_percentage': utilization_percentage,
        'average_containers_per_location': avg_containers_per_location,
        'sun_exposure_distribution': sun_categories,
        'busiest_location': max(location_profiles, key=lambda x: x['total_containers'])['location_name'] if location_profiles else 'None'
    }

def _analyze_location_usage(location_profiles: List[Dict]) -> Dict:
    """
    Analyze location usage patterns.
    
    Args:
        location_profiles (List[Dict]): All location profiles
        
    Returns:
        Dict: Location usage analysis
    """
    if not location_profiles:
        return {'usage_analysis': 'No locations available'}
    
    # Categorize locations by container count
    empty_locations = [p for p in location_profiles if p['total_containers'] == 0]
    light_usage = [p for p in location_profiles if 1 <= p['total_containers'] <= 2]
    moderate_usage = [p for p in location_profiles if 3 <= p['total_containers'] <= 5]
    heavy_usage = [p for p in location_profiles if p['total_containers'] > 5]
    
    # Identify underutilized prime locations
    underutilized_prime = []
    for profile in location_profiles:
        if (profile['total_containers'] < 3 and 
            profile['total_sun_hours'] > 6 and 
            'north' not in profile['microclimate_conditions'].lower()):
            underutilized_prime.append(profile['location_name'])
    
    # Identify overutilized locations
    overutilized = []
    for profile in location_profiles:
        if profile['total_containers'] > 8:
            overutilized.append({
                'location_name': profile['location_name'],
                'container_count': profile['total_containers']
            })
    
    return {
        'empty_locations': [p['location_name'] for p in empty_locations],
        'light_usage_locations': [p['location_name'] for p in light_usage],
        'moderate_usage_locations': [p['location_name'] for p in moderate_usage],
        'heavy_usage_locations': [p['location_name'] for p in heavy_usage],
        'underutilized_prime_locations': underutilized_prime,
        'overutilized_locations': overutilized,
        'usage_distribution': {
            'empty': len(empty_locations),
            'light': len(light_usage),
            'moderate': len(moderate_usage),
            'heavy': len(heavy_usage)
        }
    }

def _analyze_container_distribution(all_containers: List[Dict], all_locations: List[Dict]) -> Dict:
    """
    Analyze container distribution patterns across the garden.
    
    Args:
        all_containers (List[Dict]): All containers
        all_locations (List[Dict]): All locations
        
    Returns:
        Dict: Container distribution analysis
    """
    if not all_containers:
        return {'distribution_analysis': 'No containers available'}
    
    # Analyze by material
    material_counts = {}
    for container in all_containers:
        material = container.get('container_material', 'Unknown')
        material_counts[material] = material_counts.get(material, 0) + 1
    
    # Analyze by size
    size_counts = {}
    for container in all_containers:
        size = container.get('container_size', 'Unknown')
        size_counts[size] = size_counts.get(size, 0) + 1
    
    # Analyze by type
    type_counts = {}
    for container in all_containers:
        container_type = container.get('container_type', 'Unknown')
        type_counts[container_type] = type_counts.get(container_type, 0) + 1
    
    # Risk analysis - plastic containers in high sun
    high_sun_locations = {loc['location_id']: loc for loc in all_locations if loc.get('afternoon_sun_hours', 0) > 3}
    plastic_high_sun_risk = 0
    for container in all_containers:
        if (container.get('container_material', '').lower() == 'plastic' and 
            container.get('location_id') in high_sun_locations):
            plastic_high_sun_risk += 1
    
    # Small containers in high sun
    small_high_sun_risk = 0
    for container in all_containers:
        location_id = container.get('location_id')
        if location_id in high_sun_locations:
            location = high_sun_locations[location_id]
            if (container.get('container_size', '').lower() == 'small' and 
                location.get('total_sun_hours', 0) > 7):
                small_high_sun_risk += 1
    
    return {
        'material_distribution': material_counts,
        'size_distribution': size_counts,
        'type_distribution': type_counts,
        'risk_assessments': {
            'plastic_containers_high_sun': plastic_high_sun_risk,
            'small_containers_high_sun': small_high_sun_risk
        },
        'total_containers': len(all_containers),
        'most_common_material': max(material_counts.items(), key=lambda x: x[1])[0] if material_counts else 'None',
        'most_common_size': max(size_counts.items(), key=lambda x: x[1])[0] if size_counts else 'None'
    }

def _assess_care_requirements(location_profiles: List[Dict]) -> Dict:
    """
    Assess overall garden care requirements complexity.
    
    Args:
        location_profiles (List[Dict]): All location profiles
        
    Returns:
        Dict: Care complexity assessment
    """
    if not location_profiles:
        return {'complexity_assessment': 'No locations available'}
    
    complexity_scores = []
    daily_care_locations = []
    weekly_care_locations = []
    
    for profile in location_profiles:
        # Get containers for this location
        containers = profile.get('containers_detail', [])
        
        # Build location dict for assessment
        location = {
            'total_sun_hours': profile.get('total_sun_hours', 0),
            'afternoon_sun_hours': profile.get('afternoon_sun_hours', 0),
            'microclimate_conditions': profile.get('microclimate_conditions', '')
        }
        
        # Assess complexity for this location
        complexity_assessment = _assess_overall_care_complexity(location, containers)
        complexity_scores.append(complexity_assessment['complexity_score'])
        
        # Categorize by care frequency
        if complexity_assessment['complexity_level'] == 'high':
            daily_care_locations.append(profile['location_name'])
        elif complexity_assessment['complexity_level'] == 'low':
            weekly_care_locations.append(profile['location_name'])
    
    # Calculate overall garden complexity
    avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
    
    if avg_complexity >= 4:
        overall_complexity = 'high'
        garden_approach = 'Requires systematic daily garden monitoring with specialized care protocols'
    elif avg_complexity >= 2:
        overall_complexity = 'medium'
        garden_approach = 'Regular monitoring with location-specific care adjustments'
    else:
        overall_complexity = 'low'
        garden_approach = 'Straightforward garden care with weekly monitoring'
    
    return {
        'overall_complexity': overall_complexity,
        'average_complexity_score': round(avg_complexity, 1),
        'garden_management_approach': garden_approach,
        'daily_care_locations': daily_care_locations,
        'weekly_care_locations': weekly_care_locations,
        'complexity_distribution': {
            'high': len(daily_care_locations),
            'low': len(weekly_care_locations),
            'medium': len(location_profiles) - len(daily_care_locations) - len(weekly_care_locations)
        }
    }

def _identify_improvement_areas(location_profiles: List[Dict]) -> List[Dict]:
    """
    Identify garden-wide improvement opportunities.
    
    Args:
        location_profiles (List[Dict]): All location profiles
        
    Returns:
        List[Dict]: Garden improvement opportunities
    """
    opportunities = []
    
    if not location_profiles:
        return opportunities
    
    # Identify underutilized locations
    empty_good_locations = []
    for profile in location_profiles:
        if (profile['total_containers'] == 0 and 
            profile['total_sun_hours'] > 4):
            empty_good_locations.append(profile['location_name'])
    
    if empty_good_locations:
        opportunities.append({
            'type': 'location_utilization',
            'priority': 'medium',
            'description': f"{len(empty_good_locations)} good locations are empty",
            'recommendation': f"Consider utilizing: {', '.join(empty_good_locations[:3])}{'...' if len(empty_good_locations) > 3 else ''}",
            'locations_affected': len(empty_good_locations)
        })
    
    # Identify container upgrade opportunities
    total_plastic_high_sun = 0
    for profile in location_profiles:
        if profile['afternoon_sun_hours'] > 3:
            plastic_containers = [c for c in profile.get('containers_detail', []) 
                                if c.get('container_material', '').lower() == 'plastic']
            total_plastic_high_sun += len(plastic_containers)
    
    if total_plastic_high_sun > 3:
        opportunities.append({
            'type': 'container_material_upgrade',
            'priority': 'medium',
            'description': f"{total_plastic_high_sun} plastic containers in high afternoon sun",
            'recommendation': "Consider upgrading to ceramic or terracotta containers for better heat management",
            'containers_affected': total_plastic_high_sun
        })
    
    # Identify care efficiency opportunities
    high_maintenance_locations = [p for p in location_profiles if p['total_containers'] > 6]
    if len(high_maintenance_locations) > 2:
        opportunities.append({
            'type': 'care_efficiency',
            'priority': 'low',
            'description': f"{len(high_maintenance_locations)} locations with many containers",
            'recommendation': "Consider grouping containers by care requirements for efficient maintenance routing",
            'locations_affected': len(high_maintenance_locations)
        })
    
    # Identify microclimate optimization
    north_facing_underused = []
    for profile in location_profiles:
        if ('north' in profile['microclimate_conditions'].lower() and 
            profile['total_containers'] < 2):
            north_facing_underused.append(profile['location_name'])
    
    if north_facing_underused:
        opportunities.append({
            'type': 'microclimate_optimization',
            'priority': 'low',
            'description': f"{len(north_facing_underused)} north-facing microclimates underutilized",
            'recommendation': "These cooler areas are perfect for heat-sensitive plants",
            'locations_affected': len(north_facing_underused)
        })
    
    return opportunities