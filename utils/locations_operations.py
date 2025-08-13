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
