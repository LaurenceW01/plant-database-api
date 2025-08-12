"""
Locations Recommendation Operations Module

Advanced recommendation and optimization functions for location and container management.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import List, Dict
import logging

# Set up logging for this module
logger = logging.getLogger(__name__)

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
        from .locations_intelligence_operations import get_location_profile
        from .locations_database_operations import get_containers_by_location_id
        
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
                'location_name': location.get('Location Name', 'Unknown'),
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
    morning = float(location.get('Morning Sun Hours', '0') or '0')
    afternoon = float(location.get('Afternoon Sun Hours', '0') or '0')
    evening = float(location.get('Evening Sun Hours', '0') or '0')
    total = float(location.get('Total Sun Hours', '0') or '0')
    pattern = location.get('Shade Pattern', 'Unknown')
    
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
    microclimate = location.get('Microclimate Conditions', '').lower()
    
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
    afternoon_sun = float(location.get('Afternoon Sun Hours', '0') or '0')
    total_sun = float(location.get('Total Sun Hours', '0') or '0')
    
    # Check for problematic combinations
    for container in containers:
        material = container.get('Container Material', '').lower()
        size = container.get('Container Size', '').lower()
        
        # Plastic containers in high afternoon sun
        if material == 'plastic' and afternoon_sun > 3:
            concerning_combinations.append({
                'container_id': container.get('Container ID'),
                'issue': 'Plastic container in high afternoon sun',
                'risk_level': 'medium',
                'impact': 'Root heating, increased water needs'
            })
        
        # Small containers in very high sun
        if size == 'small' and total_sun > 7:
            concerning_combinations.append({
                'container_id': container.get('Container ID'),
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
    afternoon_sun = float(location.get('Afternoon Sun Hours', '0') or '0')
    evening_sun = float(location.get('Evening Sun Hours', '0') or '0')
    total_sun = float(location.get('Total Sun Hours', '0') or '0')
    microclimate = location.get('Microclimate Conditions', '').lower()
    
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
    small_containers = sum(1 for c in containers if c.get('Container Size', '').lower() == 'small')
    plastic_containers = sum(1 for c in containers if c.get('Container Material', '').lower() == 'plastic')
    
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
    total_sun = float(location.get('Total Sun Hours', '0') or '0')
    afternoon_sun = float(location.get('Afternoon Sun Hours', '0') or '0')
    microclimate = location.get('Microclimate Conditions', '').lower()
    
    recommendations = []
    ideal_plants = []
    avoid_plants = []
    
    # Sun exposure recommendations
    if total_sun > 7:
        ideal_plants.extend(['Sun-loving vegetables', 'Mediterranean herbs', 'Drought-tolerant plants'])
        avoid_plants.extend(['Leafy greens (in summer)', 'Shade-loving plants'])
        recommendations.append('Excellent for full-sun plants but provide afternoon shade for sensitive varieties')
    elif total_sun > 4:
        ideal_plants.extend(['Most vegetables', 'Herbs', 'Flowering annuals'])
        recommendations.append('Versatile location suitable for most plant types')
    else:
        ideal_plants.extend(['Leafy greens', 'Shade-tolerant herbs', 'Hostas'])
        avoid_plants.extend(['Tomatoes', 'Peppers', 'Sun-loving flowering plants'])
        recommendations.append('Best for shade-tolerant plants and cool-season crops')
    
    # Microclimate-specific recommendations
    if 'north' in microclimate:
        ideal_plants.append('Cool-season vegetables')
        recommendations.append('Cooler microclimate extends growing season for cool-weather crops')
    
    # Container capacity assessment
    available_space = _estimate_available_space(containers)
    
    return {
        'sun_exposure_suitability': total_sun,
        'ideal_plant_types': ideal_plants,
        'plants_to_avoid': avoid_plants,
        'placement_recommendations': recommendations,
        'current_container_count': len(containers),
        'estimated_available_space': available_space,
        'microclimate_advantages': _get_microclimate_advantages(microclimate)
    }

def _estimate_available_space(containers: List[Dict]) -> str:
    """
    Estimate available space based on current container count.
    
    Args:
        containers (List[Dict]): Current containers
        
    Returns:
        str: Space availability estimate
    """
    container_count = len(containers)
    
    if container_count == 0:
        return 'High - No current containers, maximum flexibility'
    elif container_count <= 3:
        return 'High - Room for additional containers'
    elif container_count <= 6:
        return 'Medium - Some space for additional containers'
    elif container_count <= 10:
        return 'Low - Limited space for new containers'
    else:
        return 'Very Low - Location at capacity'

def _get_microclimate_advantages(microclimate: str) -> List[str]:
    """
    Get specific advantages of the microclimate.
    
    Args:
        microclimate (str): Microclimate description
        
    Returns:
        List[str]: List of microclimate advantages
    """
    advantages = []
    
    if 'north' in microclimate:
        advantages.extend([
            'Cooler temperatures reduce heat stress',
            'More consistent soil moisture',
            'Extended growing season for cool crops'
        ])
    
    if 'wall' in microclimate:
        advantages.extend([
            'Wind protection',
            'Thermal mass for temperature moderation'
        ])
    
    if 'facing' in microclimate:
        advantages.append('Directional exposure for specific plant needs')
    
    return advantages

def _assess_overall_care_complexity(location: Dict, containers: List[Dict]) -> Dict:
    """
    Assess overall care complexity for the location.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Containers at location
        
    Returns:
        Dict: Overall care complexity assessment
    """
    if not containers:
        return {
            'complexity_level': 'none',
            'complexity_score': 0,
            'primary_factors': [],
            'management_recommendations': ['No containers require care at this location']
        }
    
    from .locations_intelligence_operations import _assess_care_complexity
    
    complexity_counts = {'low': 0, 'medium': 0, 'high': 0}
    
    # Assess each container
    for container in containers:
        complexity = _assess_care_complexity(container, location)
        complexity_counts[complexity] += 1
    
    # Calculate overall complexity
    total = len(containers)
    high_percentage = (complexity_counts['high'] / total) * 100
    medium_percentage = (complexity_counts['medium'] / total) * 100
    
    if high_percentage > 50:
        overall_complexity = 'high'
        complexity_score = 8 + min(2, complexity_counts['high'] - total//2)
    elif high_percentage > 25 or medium_percentage > 50:
        overall_complexity = 'medium'
        complexity_score = 5 + min(2, complexity_counts['medium']//2)
    else:
        overall_complexity = 'low'
        complexity_score = 2 + complexity_counts['medium']//2
    
    # Generate management recommendations
    management_recommendations = []
    
    if complexity_counts['high'] > 0:
        management_recommendations.append(f'Monitor {complexity_counts["high"]} high-complexity containers daily')
    
    if complexity_counts['medium'] > 2:
        management_recommendations.append('Regular monitoring schedule recommended for multiple medium-complexity setups')
    
    total_sun = float(location.get('Total Sun Hours', '0') or '0')
    if total_sun > 7:
        management_recommendations.append('High sun exposure requires consistent watering schedule')
    
    return {
        'complexity_level': overall_complexity,
        'complexity_score': complexity_score,
        'complexity_breakdown': complexity_counts,
        'primary_factors': _identify_complexity_factors(location, containers),
        'management_recommendations': management_recommendations
    }

def _identify_complexity_factors(location: Dict, containers: List[Dict]) -> List[str]:
    """
    Identify primary factors contributing to care complexity.
    
    Args:
        location (Dict): Location data
        containers (List[Dict]): Containers at location
        
    Returns:
        List[str]: Primary complexity factors
    """
    factors = []
    
    total_sun = float(location.get('Total Sun Hours', '0') or '0')
    afternoon_sun = float(location.get('Afternoon Sun Hours', '0') or '0')
    
    if total_sun > 8:
        factors.append('Very high sun exposure')
    elif total_sun > 6:
        factors.append('High sun exposure')
    
    if afternoon_sun > 3:
        factors.append('High afternoon sun intensity')
    
    plastic_count = sum(1 for c in containers if c.get('Container Material', '').lower() == 'plastic')
    if plastic_count > 0:
        factors.append(f'{plastic_count} plastic containers requiring heat monitoring')
    
    small_count = sum(1 for c in containers if c.get('Container Size', '').lower() == 'small')
    if small_count > 2:
        factors.append(f'{small_count} small containers requiring frequent watering')
    
    if len(containers) > 8:
        factors.append('High container density requiring systematic management')
    
    return factors
