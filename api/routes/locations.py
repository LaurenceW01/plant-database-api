"""
Location and Garden Context Routes

Handles location intelligence, garden metadata, container management,
and location-aware care optimization.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging
from datetime import datetime

# Create the locations blueprint
locations_bp = Blueprint('locations', __name__, url_prefix='/api')


@locations_bp.route('/locations/get-context/<location_id>', methods=['GET'])
def get_location_context(location_id):
    """
    Phase 2 direct implementation: Get location context and care profile.
    Provides semantic alignment: getLocationContext operationId → /api/locations/get-context/{id} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    
    Supports both location IDs (numeric) and location names for ChatGPT compatibility.
    """
    try:
        from utils.locations_operations import get_location_care_profile, find_location_by_id_or_name
        
        # Convert location name to ID if necessary (ChatGPT often sends location names)
        actual_location_id = location_id
        if not location_id.isdigit():
            # Try to find location by name and get its ID
            location_data = find_location_by_id_or_name(location_id)
            if location_data is not None:
                actual_location_id = location_data.get('location_id', location_id)
                logging.info(f"Converted location name '{location_id}' to ID '{actual_location_id}'")
            else:
                return jsonify({
                    "error": f"Location '{location_id}' not found in database",
                    "message": "Please check the location name and try again",
                    "location_id": location_id,
                    "phase2_direct": True
                }), 404
        
        # Generate care profile using the actual location ID
        care_profile = get_location_care_profile(actual_location_id)
        
        if care_profile:
            return jsonify({
                "location_id": actual_location_id,
                "original_identifier": location_id,
                "care_profile": care_profile,
                "message": f"Care profile generated for location {care_profile.get('location_info', {}).get('location_name', actual_location_id)}",
                "phase2_direct": True,
                "endpoint_type": "direct_implementation"
            }), 200
        else:
            return jsonify({
                "error": f"Location {actual_location_id} not found",
                "location_id": actual_location_id,
                "original_identifier": location_id,
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


@locations_bp.route('/garden/get-metadata', methods=['GET'])
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


@locations_bp.route('/garden/optimize-care', methods=['GET'])
def optimize_garden_care():
    """
    Phase 2 direct implementation: Get garden care optimization recommendations.
    Provides semantic alignment: optimizeGardenCare operationId → /api/garden/optimize-care URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        from utils.locations_operations import get_garden_care_optimization as get_care_optimization_util
        
        # Get care optimization recommendations
        optimization = get_care_optimization_util()
        
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
@locations_bp.route('/locations/<location_id>/care-profile', methods=['GET'])
def get_location_care_profile_endpoint(location_id):
    """Get detailed care profile for a specific location"""
    return get_location_context(location_id)


@locations_bp.route('/garden/containers/<container_id>/care-requirements', methods=['GET'])
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


@locations_bp.route('/locations/all', methods=['GET'])
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


@locations_bp.route('/garden/location-analysis/<location_id>', methods=['GET'])
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


@locations_bp.route('/garden/metadata/enhanced', methods=['GET'])
def get_enhanced_garden_metadata():
    """Get enhanced garden metadata with advanced analytics"""
    
    print("🔧 DEBUG: Enhanced metadata route function called!")
    logging.info("🔧 DEBUG: Enhanced metadata route function called!")
    
    try:
        from utils.locations_operations import get_enhanced_garden_metadata as get_enhanced_metadata_util
        
        enhanced_metadata = get_enhanced_metadata_util()
        
        if enhanced_metadata:
            return jsonify({
                "enhanced_metadata": enhanced_metadata,
                "api_version": "v2.3.8 - Schema Fix Complete",
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


@locations_bp.route('/garden/location-profiles', methods=['GET'])
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


@locations_bp.route('/garden/care-optimization', methods=['GET'])
def get_garden_care_optimization_route():
    """Get comprehensive garden care optimization"""
    
    print("🔧 DEBUG: Route function called!")
    logging.info("🔧 DEBUG: Route function called!")

    try:
        from utils.locations_operations import get_garden_care_optimization as get_care_optimization_util
        
        # Get care optimization recommendations
        optimization = get_care_optimization_util()
        
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


@locations_bp.route('/garden/query', methods=['POST'])
def advanced_garden_query():
    """
    Advanced Garden Query Endpoint
    
    MongoDB-style JSON query builder for complex plant database filtering.
    Solves the critical GPT rate limiting bottleneck by replacing multiple 
    individual API calls with a single optimized query.
    """
    try:
        from utils.advanced_query_parser import parse_advanced_query, QueryParseError
        from utils.advanced_query_executor import execute_advanced_query, QueryExecutionError
        
        logging.info("=" * 80)
        logging.info("🔍 ADVANCED GARDEN QUERY ENDPOINT CALLED")
        logging.info("=" * 80)
        logging.info(f"🌐 Request Headers: {dict(request.headers)}")
        logging.info(f"🔍 User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        logging.info(f"🔍 Content-Type: {request.headers.get('Content-Type', 'Unknown')}")
        logging.info(f"🔍 Content-Length: {request.headers.get('Content-Length', 'Unknown')}")
        logging.info(f"🔍 Request Method: {request.method}")
        logging.info(f"🔍 Request URL: {request.url}")
        logging.info(f"🔍 Remote Address: {request.remote_addr}")
        
        # Detect ChatGPT requests
        user_agent = request.headers.get('User-Agent', '').lower()
        is_chatgpt = 'openai' in user_agent or 'gpt' in user_agent
        logging.info(f"🤖 IS CHATGPT REQUEST: {is_chatgpt}")
        logging.info("=" * 80)
        
        # Get and log request data
        raw_data = request.get_data(as_text=True)
        logging.info(f"📥 RAW REQUEST BODY: {raw_data[:500]}{'...' if len(raw_data) > 500 else ''}")
        
        request_data = request.get_json(force=True, silent=True)
        logging.info(f"📋 PARSED JSON: {request_data}")
        logging.info(f"📊 JSON FIELDS COUNT: {len(request_data) if request_data else 0}")
        
        # ChatGPT optimization: Set aggressive defaults for speed
        if request_data and request_data.get('response_format') == 'summary':
            if 'limit' not in request_data:
                request_data['limit'] = 10  # Reduce from default 50
            # Force minimal response for ChatGPT timeout prevention
            logging.info("🚀 ChatGPT optimization: Using speed-optimized settings")
            logging.info(f"🚀 Optimized request: {request_data}")
        
        if not request_data:
            logging.error("❌ NO REQUEST DATA RECEIVED")
            logging.error(f"❌ Raw data was: '{raw_data}'")
            return jsonify({
                "error": "Request body required",
                "example": {
                    "filters": {
                        "plants": {"Plant Name": {"$regex": "vinca"}},
                        "locations": {"location_name": {"$eq": "patio"}}
                    },
                    "response_format": "summary"
                },
                "phase2_direct": True
            }), 400
        
        # Parse and execute query
        try:
            logging.info("🔄 STARTING QUERY PARSING...")
            start_time = datetime.utcnow()
            parsed_query = parse_advanced_query(request_data)
            parse_time = (datetime.utcnow() - start_time).total_seconds()
            logging.info(f"✅ Query parsed successfully in {parse_time:.3f}s")
            logging.info(f"🔍 Parsed query structure: {parsed_query}")
            
            logging.info("🚀 STARTING QUERY EXECUTION...")
            exec_start = datetime.utcnow()
            query_results = execute_advanced_query(parsed_query)
            exec_time = (datetime.utcnow() - exec_start).total_seconds()
            logging.info(f"✅ Query executed successfully in {exec_time:.3f}s")
            logging.info(f"📊 Query results: {len(query_results.get('plants', []))} plants found")
            
            # Add endpoint metadata
            query_results['endpoint_metadata'] = {
                "endpoint": "/api/garden/query",
                "phase2_direct": True,
                "optimization": "multi_table_single_call"
            }
            
            total_request_time = (datetime.utcnow() - start_time).total_seconds()
            logging.info(f"🎉 ADVANCED QUERY COMPLETED in {total_request_time:.3f}s")
            logging.info("=" * 80)
            return jsonify(query_results), 200
            
        except QueryParseError as e:
            logging.error(f"❌ QUERY PARSE ERROR: {e}")
            logging.error(f"❌ Failed request data: {request_data}")
            return jsonify({
                "error": "Query parsing failed",
                "message": str(e),
                "phase2_direct": True,
                "debug_request": request_data
            }), 400
            
        except QueryExecutionError as e:
            logging.error(f"❌ QUERY EXECUTION ERROR: {e}")
            logging.error(f"❌ Failed parsed query: {parsed_query if 'parsed_query' in locals() else 'Not available'}")
            return jsonify({
                "error": "Query execution failed", 
                "message": str(e),
                "phase2_direct": True,
                "debug_parsed_query": parsed_query if 'parsed_query' in locals() else None
            }), 500
        
    except Exception as e:
        logging.error(f"❌ UNEXPECTED ERROR in advanced garden query: {e}")
        logging.error(f"❌ Request headers: {dict(request.headers)}")
        logging.error(f"❌ Request data: {request_data if 'request_data' in locals() else 'Not available'}")
        logging.error("=" * 80)
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
            "phase2_direct": True,
            "debug_headers": dict(request.headers),
            "debug_data": request_data if 'request_data' in locals() else None
        }), 500


@locations_bp.route('/garden/quick-query', methods=['POST'])
def quick_garden_query():
    """
    Ultra-fast garden query optimized for ChatGPT timeouts.
    Limited functionality but guaranteed fast response.
    """
    try:
        logging.info("=" * 60)
        logging.info("⚡ QUICK GARDEN QUERY ENDPOINT CALLED")
        logging.info("=" * 60)
        logging.info(f"⚡ User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        logging.info(f"⚡ Content-Type: {request.headers.get('Content-Type', 'Unknown')}")
        logging.info(f"⚡ Remote Address: {request.remote_addr}")
        
        # Detect ChatGPT requests
        user_agent = request.headers.get('User-Agent', '').lower()
        is_chatgpt = 'openai' in user_agent or 'gpt' in user_agent
        logging.info(f"⚡ IS CHATGPT REQUEST: {is_chatgpt}")
        
        raw_data = request.get_data(as_text=True)
        logging.info(f"⚡ RAW REQUEST: {raw_data}")
        
        request_data = request.get_json(force=True, silent=True)
        logging.info(f"⚡ PARSED JSON: {request_data}")
        
        if not request_data:
            logging.error("⚡ ❌ NO REQUEST DATA")
            return jsonify({"error": "Request body required"}), 400
            
        # Ultra-aggressive optimizations for ChatGPT
        request_data['response_format'] = 'minimal'  # Force minimal
        request_data['limit'] = min(request_data.get('limit', 3), 3)  # Max 3 results for speed
        
        from utils.advanced_query_parser import parse_advanced_query, QueryParseError
        from utils.advanced_query_executor import execute_advanced_query, QueryExecutionError
        
        # Parse and execute with speed optimizations
        logging.info("⚡ QUICK-QUERY: Starting parsing...")
        start_time = datetime.utcnow()
        parsed_query = parse_advanced_query(request_data)
        parse_time = (datetime.utcnow() - start_time).total_seconds()
        logging.info(f"⚡ QUICK-QUERY: Parsed in {parse_time:.3f}s")
        
        logging.info("⚡ QUICK-QUERY: Starting execution...")
        exec_start = datetime.utcnow()
        result = execute_advanced_query(parsed_query)
        exec_time = (datetime.utcnow() - exec_start).total_seconds()
        total_time = (datetime.utcnow() - start_time).total_seconds()
        logging.info(f"⚡ QUICK-QUERY: Executed in {exec_time:.3f}s (total: {total_time:.3f}s)")
        logging.info(f"⚡ QUICK-QUERY: Found {len(result.get('plants', []))} plants")
        
        logging.info(f"⚡ 🎉 QUICK-QUERY COMPLETED in {total_time:.3f}s")
        logging.info("=" * 60)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"⚡ ❌ Quick query error: {e}")
        logging.error(f"⚡ ❌ Request data: {request_data if 'request_data' in locals() else 'Not available'}")
        return jsonify({
            "error": "Query failed", 
            "details": str(e),
            "debug_data": request_data if 'request_data' in locals() else None
        }), 500


@locations_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "plant-database-api"
    })