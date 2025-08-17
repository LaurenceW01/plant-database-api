"""
Plant Analysis Routes

Handles plant health analysis, diagnosis, and AI-powered 
plant care recommendations.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging

# Create the analysis blueprint
analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/plants')


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET']
@analysis_bp.route('/diagnose', methods=['GET'])  # WORKAROUND: was POST
def diagnose_plant():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    
    Phase 2 direct implementation: Diagnose plant health with action-based URL.
    Provides semantic alignment: diagnosePlant operationId → /api/plants/diagnose URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    
    Expected parameters: plant_name, user_notes, analysis_type, location
    """
    try:
        # WORKAROUND: Convert GET query params to POST body format
        from flask import request as flask_request, g
        
        # Extract parameters from query string - based on analyze_plant function requirements
        plant_name = flask_request.args.get('plant_name') or flask_request.args.get('Plant Name')
        user_notes = flask_request.args.get('user_notes') or flask_request.args.get('User Notes') or ''
        analysis_type = flask_request.args.get('analysis_type') or flask_request.args.get('Analysis Type') or 'general_care'
        location = flask_request.args.get('location') or flask_request.args.get('Location') or ''
        
        # Validate required fields  
        if not plant_name:
            return jsonify({
                "error": "Plant name is required for plant diagnosis",
                "message": "Use ?plant_name=YourPlantName in the URL. Optional: &user_notes=notes&analysis_type=type&location=loc",
                "workaround": "GET endpoint due to ChatGPT POST issue",
                "received_args": dict(flask_request.args)
            }), 400
        
        # WORKAROUND: Simulate POST request body by storing in both request and g objects
        # This allows the existing analyze_plant logic to work without modification
        simulated_json = {
            'plant_name': plant_name,
            'user_notes': user_notes,
            'analysis_type': analysis_type,
            'location': location
        }
        
        # Store original data and mock request/g objects
        original_method = flask_request.method
        original_get_json = flask_request.get_json
        original_normalized_data = getattr(g, 'normalized_request_data', None)
        original_original_data = getattr(g, 'original_request_data', None)
        
        # Mock the request.get_json() to return our simulated data
        flask_request.get_json = lambda: simulated_json
        flask_request.method = 'POST'  # Temporarily set to POST for compatibility
        
        # Set g object data for field normalization middleware
        g.normalized_request_data = simulated_json.copy()
        g.original_request_data = simulated_json.copy()
        
        try:
            # Import the original analyze_plant function
            from api.main import analyze_plant
            
            # Direct implementation using existing analyze logic
            response = analyze_plant()
        finally:
            # Restore original request properties
            flask_request.get_json = original_get_json
            flask_request.method = original_method
            
            # Restore original g object data
            if original_normalized_data is not None:
                g.normalized_request_data = original_normalized_data
            elif hasattr(g, 'normalized_request_data'):
                delattr(g, 'normalized_request_data')
                
            if original_original_data is not None:
                g.original_request_data = original_original_data
            elif hasattr(g, 'original_request_data'):
                delattr(g, 'original_request_data')
        
        # Mark as Phase 2 direct implementation in response
        if hasattr(response, 'get_json'):
            try:
                data = response.get_json()
                if isinstance(data, dict):
                    data['phase2_direct'] = True
                    data['endpoint_type'] = 'direct_implementation'
                    data['workaround'] = 'GET converted from POST'
                    return jsonify(data), response.status_code
            except:
                pass
        
        return response
        
    except Exception as e:
        logging.error(f"Error in Phase 2 diagnose_plant: {e}")
        return jsonify({
            'error': str(e),
            'phase2_direct': True,
            'workaround': 'GET converted from POST'
        }), 500


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again 
# Changed: methods=['POST'] → methods=['GET']
@analysis_bp.route('/enhance-analysis', methods=['GET'])  # WORKAROUND: was POST
def enhance_plant_analysis():
    """
    CHATGPT WORKAROUND: Temporarily converted from POST to GET due to ChatGPT platform issue.
    
    Phase 2 direct implementation: Enhance plant analysis with database context.
    Provides semantic alignment: enhancePlantAnalysis operationId → /api/plants/enhance-analysis URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    
    Expected parameters: gpt_analysis, plant_identification, user_question, location
    """
    try:
        # WORKAROUND: Convert GET query params to POST body format
        from flask import request as flask_request, g
        
        # Extract parameters from query string - based on enhance_analysis function requirements
        gpt_analysis = flask_request.args.get('gpt_analysis') or flask_request.args.get('GPT Analysis') or ''
        plant_identification = flask_request.args.get('plant_identification') or flask_request.args.get('Plant Identification') or ''
        user_question = flask_request.args.get('user_question') or flask_request.args.get('User Question') or ''
        location = flask_request.args.get('location') or flask_request.args.get('Location') or ''
        
        # Validate that we have at least some analysis data
        if not any([gpt_analysis, plant_identification, user_question]):
            return jsonify({
                "error": "At least one analysis parameter is required",
                "message": "Use query parameters: ?gpt_analysis=analysis&plant_identification=id&user_question=question&location=loc",
                "workaround": "GET endpoint due to ChatGPT POST issue",
                "received_args": dict(flask_request.args)
            }), 400
        
        # WORKAROUND: Simulate POST request body by storing in both request and g objects
        # This allows the existing enhance_analysis logic to work without modification
        simulated_json = {
            'gpt_analysis': gpt_analysis,
            'plant_identification': plant_identification,
            'user_question': user_question,
            'location': location
        }
        
        # Store original data and mock request/g objects
        original_method = flask_request.method
        original_get_json = flask_request.get_json
        original_normalized_data = getattr(g, 'normalized_request_data', None)
        original_original_data = getattr(g, 'original_request_data', None)
        
        # Mock the request.get_json() to return our simulated data
        flask_request.get_json = lambda: simulated_json
        flask_request.method = 'POST'  # Temporarily set to POST for compatibility
        
        # Set g object data for field normalization middleware
        g.normalized_request_data = simulated_json.copy()
        g.original_request_data = simulated_json.copy()
        
        try:
            # Import the original enhance_analysis function
            from api.main import enhance_analysis
            
            # Direct implementation using existing enhance logic
            response = enhance_analysis()
        finally:
            # Restore original request properties
            flask_request.get_json = original_get_json
            flask_request.method = original_method
            
            # Restore original g object data
            if original_normalized_data is not None:
                g.normalized_request_data = original_normalized_data
            elif hasattr(g, 'normalized_request_data'):
                delattr(g, 'normalized_request_data')
                
            if original_original_data is not None:
                g.original_request_data = original_original_data
            elif hasattr(g, 'original_request_data'):
                delattr(g, 'original_request_data')
        
        # Mark as Phase 2 direct implementation in response
        if hasattr(response, 'get_json'):
            try:
                data = response.get_json()
                if isinstance(data, dict):
                    data['phase2_direct'] = True
                    data['endpoint_type'] = 'direct_implementation'
                    data['workaround'] = 'GET converted from POST'
                    return jsonify(data), response.status_code
            except:
                pass
        
        return response
        
    except Exception as e:
        logging.error(f"Error in Phase 2 enhance_plant_analysis: {e}")
        return jsonify({
            'error': str(e),
            'phase2_direct': True,
            'workaround': 'GET converted from POST'
        }), 500

