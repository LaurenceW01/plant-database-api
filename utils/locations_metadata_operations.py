"""
Locations Metadata Operations Module

Garden metadata and statistics functions for comprehensive garden analysis.

Author: Plant Database API
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import List, Dict
import logging

# Set up logging for this module
logger = logging.getLogger(__name__)

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
        from .locations_database_operations import get_all_locations, get_all_containers
        from .locations_intelligence_operations import _analyze_plant_distribution
        
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
            unique_plants = len(set(c.get('plant_id', '') for c in location_containers if c.get('plant_id', '')))
            
            # Aggregate container types, sizes, and materials
            container_types = list(set(c.get('container_type', 'Unknown') for c in location_containers))
            container_sizes = list(set(c.get('container_size', 'Unknown') for c in location_containers))
            container_materials = list(set(c.get('container_material', 'Unknown') for c in location_containers))
            
            # Create profile combining location and container data
            profile = {
                'location_id': location_id,
                'location_name': location.get('location_name', 'Unknown'),
                'morning_sun_hours': float(location.get('morning_sun_hours', 0) or 0),
                'afternoon_sun_hours': float(location.get('afternoon_sun_hours', 0) or 0),
                'evening_sun_hours': float(location.get('evening_sun_hours', 0) or 0),
                'total_sun_hours': float(location.get('total_sun_hours', 0) or 0),
                'shade_pattern': location.get('shade_pattern', ''),
                'microclimate_conditions': location.get('microclimate_conditions', ''),
                'total_containers': len(location_containers),
                'unique_plants': unique_plants,
                'container_types': container_types,
                'container_sizes': container_sizes,
                'container_materials': container_materials,
                'containers_detail': location_containers,
                'plant_distribution': _analyze_plant_distribution(location_containers)
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
        from .locations_database_operations import get_all_containers, get_all_locations
        
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


def get_garden_care_optimization() -> Dict:
    """
    Get garden care optimization analysis.
    
    This function provides care optimization recommendations and efficiency
    improvements based on cross-analysis of locations and containers.
    
    Returns:
        Dict: Care optimization analysis with recommendations
    """
    try:
        # Get enhanced metadata which includes optimization data
        enhanced_metadata = get_garden_metadata_enhanced()
        
        if not enhanced_metadata:
            return {
                "error": "Unable to generate care optimization",
                "message": "No data available for optimization analysis"
            }
        
        # Extract optimization-focused data
        optimization_data = {
            "optimization_analysis": {
                "garden_wide_opportunities": enhanced_metadata.get('optimization_opportunities', []),
                "care_complexity_summary": enhanced_metadata.get('care_complexity_analysis', {}),
                "location_efficiency": enhanced_metadata.get('location_distribution', {}),
                "container_insights": enhanced_metadata.get('container_intelligence', {})
            },
            "total_opportunities": len(enhanced_metadata.get('optimization_opportunities', [])),
            "priority_improvements": _extract_priority_improvements(enhanced_metadata),
            "efficiency_score": _calculate_efficiency_score(enhanced_metadata),
            "recommendations": _generate_optimization_recommendations(enhanced_metadata),
            "generated_at": enhanced_metadata.get('generated_at', ''),
            "api_version": "2.4.6"
        }
        
        logger.info("Generated garden care optimization analysis successfully")
        return optimization_data
        
    except Exception as e:
        logger.error(f"Error generating garden care optimization: {e}")
        return {
            "error": "Failed to generate care optimization",
            "details": str(e)
        }


def _extract_priority_improvements(metadata: Dict) -> List[Dict]:
    """Extract high-priority improvement recommendations."""
    try:
        opportunities = metadata.get('optimization_opportunities', [])
        priority_items = []
        
        for opportunity in opportunities[:3]:  # Top 3 priorities
            if isinstance(opportunity, str):
                priority_items.append({
                    "description": opportunity,
                    "priority": "high",
                    "category": "general"
                })
            elif isinstance(opportunity, dict):
                priority_items.append({
                    "description": opportunity.get('description', ''),
                    "priority": opportunity.get('priority', 'medium'),
                    "category": opportunity.get('category', 'general')
                })
        
        return priority_items
    except Exception:
        return []


def _calculate_efficiency_score(metadata: Dict) -> Dict:
    """Calculate overall garden efficiency score."""
    try:
        garden_overview = metadata.get('garden_overview', {})
        care_complexity = metadata.get('care_complexity_analysis', {})
        
        # Basic efficiency metrics
        total_locations = garden_overview.get('total_locations', 0)
        total_containers = garden_overview.get('total_containers', 0)
        
        if total_locations == 0:
            return {"score": 0, "description": "No data available"}
        
        # Calculate utilization efficiency (containers per location)
        utilization_score = min(100, (total_containers / total_locations) * 20) if total_locations > 0 else 0
        
        # Calculate care complexity efficiency (lower complexity = higher score)
        complexity_factors = care_complexity.get('high_complexity_count', 0)
        complexity_score = max(0, 100 - (complexity_factors * 10))
        
        # Overall efficiency score (weighted average)
        overall_score = round((utilization_score * 0.6 + complexity_score * 0.4), 1)
        
        return {
            "score": overall_score,
            "breakdown": {
                "utilization": round(utilization_score, 1),
                "complexity_management": round(complexity_score, 1)
            },
            "description": _get_efficiency_description(overall_score)
        }
    except Exception:
        return {"score": 0, "description": "Unable to calculate efficiency"}


def _get_efficiency_description(score: float) -> str:
    """Get description for efficiency score."""
    if score >= 80:
        return "Excellent - Garden is well-optimized"
    elif score >= 60:
        return "Good - Some optimization opportunities exist"
    elif score >= 40:
        return "Fair - Moderate improvements recommended"
    else:
        return "Needs attention - Significant optimization potential"


def _generate_optimization_recommendations(metadata: Dict) -> List[str]:
    """Generate specific optimization recommendations."""
    try:
        recommendations = []
        
        garden_overview = metadata.get('garden_overview', {})
        care_complexity = metadata.get('care_complexity_analysis', {})
        opportunities = metadata.get('optimization_opportunities', [])
        
        # Add general recommendations based on data
        if garden_overview.get('total_containers', 0) == 0:
            recommendations.append("Consider adding containers to increase garden productivity")
        
        if care_complexity.get('high_complexity_count', 0) > 0:
            recommendations.append("Focus on simplifying care routines for high-complexity locations")
        
        # Add opportunity-based recommendations
        for opportunity in opportunities[:3]:
            if isinstance(opportunity, str) and opportunity not in recommendations:
                recommendations.append(opportunity)
        
        # Add default recommendations if none found
        if not recommendations:
            recommendations.extend([
                "Monitor plant health regularly using the logging system",
                "Consider grouping plants with similar care requirements",
                "Review watering schedules based on location sun exposure"
            ])
        
        return recommendations[:5]  # Limit to 5 recommendations
    except Exception:
        return ["Review garden setup for optimization opportunities"]

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
    unique_plants = len(set(c.get('plant_id', '') for c in all_containers if c.get('plant_id', '')))
    
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
    high_sun_locations = {loc.get('location_id'): loc for loc in all_locations 
                         if float(loc.get('afternoon_sun_hours', '0') or '0') > 3}
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
                float(location.get('total_sun_hours', '0') or '0') > 7):
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
        'most_common_material': max([item for item in material_counts.items() if item[0].strip()], key=lambda x: x[1])[0] if any(k.strip() for k in material_counts.keys()) else 'None',
        'most_common_size': max([item for item in size_counts.items() if item[0].strip()], key=lambda x: x[1])[0] if any(k.strip() for k in size_counts.keys()) else 'None'
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
    
    from .locations_recommendation_operations import _assess_overall_care_complexity
    
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
    
    # Identify consolidation opportunities
    small_container_locations = []
    for profile in location_profiles:
        small_containers = [c for c in profile.get('containers_detail', []) 
                          if c.get('container_size', '').lower() == 'small']
        if len(small_containers) > 4:
            small_container_locations.append({
                'location_name': profile['location_name'],
                'small_container_count': len(small_containers)
            })
    
    if small_container_locations:
        opportunities.append({
            'type': 'container_consolidation',
            'priority': 'low',
            'description': f"{len(small_container_locations)} locations with many small containers",
            'recommendation': "Consider consolidating small containers to reduce watering frequency",
            'locations_affected': len(small_container_locations)
        })
    
    return opportunities
