"""
Streamlined locations_operations.py - now imports from split modules for backward compatibility
NO FUNCTIONALITY CHANGES - only reorganization and imports

This module provides data access and intelligence functions for the Locations and Containers sheets,
enabling location-specific care recommendations and container-aware plant management.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

# Import all functions from the split modules to maintain backward compatibility
from .locations_cache_operations import (
    _is_cache_valid,
    _update_cache_timestamp,
    _get_cached_plants
)

from .locations_database_operations import (
    get_all_locations,
    get_location_by_id,
    find_location_by_id_or_name,
    get_all_containers,
    get_containers_by_location_id,
    get_containers_by_plant_id,
    get_container_by_id
)

from .locations_intelligence_operations import (
    get_plant_location_context,
    _assess_care_complexity,
    _get_priority_considerations,
    get_location_profile,
    _calculate_container_statistics,
    _generate_location_care_intelligence,
    _get_seasonal_considerations,
    _identify_location_optimization_opportunities,
    _analyze_plant_distribution
)

from .locations_recommendation_operations import (
    generate_location_recommendations,
    _generate_sun_exposure_analysis,
    _assess_microclimate_benefits,
    _assess_container_location_compatibility,
    _calculate_optimal_watering_strategy,
    _generate_plant_placement_recommendations,
    _estimate_available_space,
    _get_microclimate_advantages,
    _assess_overall_care_complexity,
    _identify_complexity_factors
)

from .locations_metadata_operations import (
    get_all_location_profiles,
    get_garden_metadata_enhanced,
    get_garden_care_optimization,
    _calculate_garden_statistics,
    _analyze_location_usage,
    _analyze_container_distribution,
    _assess_care_requirements,
    _identify_improvement_areas
)

# Alias functions for backward compatibility
def get_garden_overview_metadata():
    """Alias for get_garden_metadata_enhanced for backward compatibility"""
    return get_garden_metadata_enhanced()

def get_all_locations_metadata():
    """Alias for get_all_location_profiles for backward compatibility"""
    return get_all_location_profiles()

def get_enhanced_garden_metadata():
    """Alias for get_garden_metadata_enhanced for backward compatibility"""
    return get_garden_metadata_enhanced()

def get_location_care_profile(location_id):
    """Generate care profile for a specific location"""
    try:
        from .care_intelligence import generate_care_profile_for_location
        return generate_care_profile_for_location(location_id)
    except ImportError:
        # Fallback implementation
        location = get_location_by_id(location_id)
        if not location:
            return None
        
        return {
            'location_info': location,
            'watering_strategy': {
                'primary_time': 'Early morning (6-8 AM)',
                'secondary_time': 'Early evening (6-7 PM)',
                'reasoning': 'Based on sun exposure patterns'
            },
            'environmental_factors': {
                'sun_exposure': {
                    'total_hours': location.get('total_sun_hours', 0),
                    'morning_hours': location.get('morning_sun_hours', 0),
                    'afternoon_hours': location.get('afternoon_sun_hours', 0),
                    'evening_hours': location.get('evening_sun_hours', 0)
                }
            },
            'general_recommendations': [
                'Monitor plants regularly for changes',
                'Adjust watering based on weather conditions',
                'Consider plant grouping by care requirements'
            ]
        }

def get_container_care_requirements(container_id):
    """Generate care requirements for a specific container"""
    try:
        from .care_intelligence import generate_container_care_requirements
        return generate_container_care_requirements(container_id)
    except ImportError:
        # Fallback implementation
        container = get_container_by_id(container_id)
        if not container:
            return None
        
        location = get_location_by_id(container.get('location_id', ''))
        
        return {
            'container_info': container,
            'location_context': location,
            'care_adjustments': {
                'watering_frequency': 'Adjust based on container material and size',
                'drainage_considerations': 'Ensure proper drainage for container type',
                'material_factors': f"Container material: {container.get('material', 'Unknown')}"
            },
            'integrated_recommendations': [
                'Check soil moisture regularly',
                'Ensure adequate drainage',
                'Monitor for container-specific issues'
            ]
        }

def analyze_location_performance(location_id):
    """Analyze performance metrics for a specific location"""
    try:
        location = get_location_by_id(location_id)
        containers = get_containers_by_location_id(location_id)
        
        if not location:
            return None
        
        # Calculate basic performance metrics
        total_containers = len(containers)
        unique_plants = len(set(c.get('Plant ID', '') for c in containers if c.get('Plant ID', '')))
        
        # Calculate utilization score
        max_sun_hours = 12  # Theoretical maximum
        actual_sun_hours = location.get('total_sun_hours', 0)
        sun_utilization = (actual_sun_hours / max_sun_hours) * 100 if max_sun_hours > 0 else 0
        
        return {
            'location_id': location_id,
            'location_name': location.get('location_name', 'Unknown'),
            'performance_metrics': {
                'container_count': total_containers,
                'plant_diversity': unique_plants,
                'sun_utilization_percentage': round(sun_utilization, 1),
                'care_complexity': 'Low' if total_containers <= 5 else 'Medium' if total_containers <= 15 else 'High'
            },
            'optimization_opportunities': [
                'Consider adding more containers if space allows' if total_containers < 10 else 'Location at good capacity',
                'Diversify plant types' if unique_plants < 3 else 'Good plant diversity',
                'Optimize sun exposure usage' if sun_utilization < 50 else 'Good sun utilization'
            ],
            'recommendations': [
                'Monitor container distribution',
                'Track plant health trends',
                'Optimize watering schedules'
            ]
        }
        
    except Exception as e:
        return {
            'error': f'Failed to analyze location performance: {str(e)}',
            'location_id': location_id
        }

# Re-export cache variables for backward compatibility
from .locations_cache_operations import (
    _locations_cache,
    _containers_cache,
    _plants_cache,
    _cache_timestamp,
    CACHE_DURATION
)

# Re-export constants for backward compatibility
from .locations_database_operations import (
    LOCATIONS_RANGE,
    CONTAINERS_RANGE
)

# All functions are now available through their original imports
# Example: from utils.locations_operations import get_all_locations, generate_location_recommendations, etc.
# This maintains 100% backward compatibility while organizing code into logical modules.
