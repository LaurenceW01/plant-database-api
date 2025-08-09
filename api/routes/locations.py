"""
Location and Garden Context Routes

Handles location intelligence, garden metadata, container management,
and location-aware care optimization.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging

# Create the locations blueprint
locations_bp = Blueprint('locations', __name__)


@locations_bp.route('/api/locations/get-context/<location_id>', methods=['GET'])
def get_location_context(location_id):
    """
    Phase 2 direct implementation: Get location context and care profile.
    Provides semantic alignment: getLocationContext operationId → /api/locations/get-context/{id} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        from utils.locations_operations import get_location_care_profile
        
        # Get location care profile
        care_profile = get_location_care_profile(location_id)
        
        if care_profile:
            return jsonify({
                "location_id": location_id,
                "care_profile": care_profile,
                "message": f"Care profile generated for location {care_profile.get('location_info', {}).get('location_name', location_id)}",
                "phase2_direct": True,
                "endpoint_type": "direct_implementation"
            }), 200
        else:
            return jsonify({
                "error": f"Location {location_id} not found",
                "location_id": location_id,
                "phase2_direct": True
            }), 404
            
    except Exception as e:
        logging.error(f"Error getting location context: {e}")
        return jsonify({
            "error": "Failed to get location context",
            "details": str(e),
            "location_id": location_id,
            "phase2_direct": True
        }), 500


@locations_bp.route('/api/garden/get-metadata', methods=['GET'])
def get_garden_metadata():
    """
    Phase 2 direct implementation: Get comprehensive garden metadata.
    Provides semantic alignment: getGardenMetadata operationId → /api/garden/get-metadata URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        from utils.locations_operations import get_garden_overview_metadata
        
        # Get comprehensive garden metadata
        metadata = get_garden_overview_metadata()
        
        return jsonify({
            **metadata,
            "phase2_direct": True,
            "endpoint_type": "direct_implementation"
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting garden metadata: {e}")
        return jsonify({
            "error": "Failed to get garden metadata",
            "details": str(e),
            "phase2_direct": True
        }), 500


@locations_bp.route('/api/garden/optimize-care', methods=['GET'])
def optimize_garden_care():
    """
    Phase 2 direct implementation: Get garden care optimization recommendations.
    Provides semantic alignment: optimizeGardenCare operationId → /api/garden/optimize-care URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        from utils.locations_operations import get_garden_care_optimization
        
        # Get care optimization recommendations
        optimization = get_garden_care_optimization()
        
        return jsonify({
            **optimization,
            "phase2_direct": True,
            "endpoint_type": "direct_implementation"
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting garden care optimization: {e}")
        return jsonify({
            "error": "Failed to get care optimization",
            "details": str(e),
            "phase2_direct": True
        }), 500


# Additional location and garden routes
@locations_bp.route('/api/locations/<location_id>/care-profile', methods=['GET'])
def get_location_care_profile_endpoint(location_id):
    """Get detailed care profile for a specific location"""
    return get_location_context(location_id)


@locations_bp.route('/api/garden/containers/<container_id>/care-requirements', methods=['GET'])
def get_container_care_requirements(container_id):
    """Get care requirements for a specific container"""
    try:
        from utils.locations_operations import get_container_care_requirements
        
        requirements = get_container_care_requirements(container_id)
        
        if requirements:
            return jsonify({
                "container_id": container_id,
                "care_requirements": requirements,
                "phase2_direct": True
            }), 200
        else:
            return jsonify({
                "error": f"Container {container_id} not found",
                "container_id": container_id,
                "phase2_direct": True
            }), 404
            
    except Exception as e:
        logging.error(f"Error getting container care requirements: {e}")
        return jsonify({
            "error": "Failed to get container requirements",
            "details": str(e),
            "container_id": container_id,
            "phase2_direct": True
        }), 500


@locations_bp.route('/api/locations/all', methods=['GET'])
def get_all_locations():
    """Get all available locations"""
    try:
        from utils.locations_operations import get_all_locations_metadata
        
        locations = get_all_locations_metadata()
        
        return jsonify({
            "locations": locations,
            "count": len(locations) if locations else 0,
            "phase2_direct": True
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting all locations: {e}")
        return jsonify({
            "error": "Failed to get locations",
            "details": str(e),
            "phase2_direct": True
        }), 500


@locations_bp.route('/api/garden/location-analysis/<location_id>', methods=['GET'])
def get_location_analysis(location_id):
    """Get detailed analysis for a specific location"""
    try:
        from utils.locations_operations import analyze_location_performance
        
        analysis = analyze_location_performance(location_id)
        
        return jsonify({
            "location_id": location_id,
            "analysis": analysis,
            "phase2_direct": True
        }), 200
        
    except Exception as e:
        logging.error(f"Error analyzing location: {e}")
        return jsonify({
            "error": "Failed to analyze location",
            "details": str(e),
            "location_id": location_id,
            "phase2_direct": True
        }), 500


@locations_bp.route('/api/garden/metadata/enhanced', methods=['GET'])
def get_enhanced_garden_metadata():
    """Get enhanced garden metadata with advanced analytics"""
    try:
        from utils.locations_operations import get_enhanced_garden_metadata
        
        enhanced_metadata = get_enhanced_garden_metadata()
        
        if enhanced_metadata:
            return jsonify({
                "enhanced_metadata": enhanced_metadata,
                "api_version": "v2.3.0 - AI-Friendly API Design Complete",
                "message": "Enhanced garden metadata generated successfully",
                "phase2_direct": True
            }), 200
        else:
            return jsonify({
                "error": "No enhanced metadata available",
                "message": "No location or container data available",
                "phase2_direct": True
            }), 404
            
    except Exception as e:
        logging.error(f"Error generating enhanced metadata: {e}")
        return jsonify({
            "error": "Failed to generate enhanced metadata",
            "details": str(e),
            "phase2_direct": True
        }), 500


@locations_bp.route('/api/garden/location-profiles', methods=['GET'])
def get_location_profiles():
    """Get profiles for all garden locations"""
    try:
        from utils.locations_operations import get_all_location_profiles
        
        profiles = get_all_location_profiles()
        
        return jsonify({
            "location_profiles": profiles,
            "count": len(profiles) if profiles else 0,
            "phase2_direct": True
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting location profiles: {e}")
        return jsonify({
            "error": "Failed to get location profiles",
            "details": str(e),
            "phase2_direct": True
        }), 500


@locations_bp.route('/api/garden/care-optimization', methods=['GET'])
def get_garden_care_optimization():
    """Get comprehensive garden care optimization"""
    return optimize_garden_care()

