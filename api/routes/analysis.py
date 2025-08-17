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
    Phase 2 direct implementation: Diagnose plant health with action-based URL.
    Provides semantic alignment: diagnosePlant operationId → /api/plants/diagnose URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        # Import the original analyze_plant function
        from api.main import analyze_plant
        
        # Direct implementation using existing analyze logic
        response = analyze_plant()
        
        # Mark as Phase 2 direct implementation in response
        if hasattr(response, 'get_json'):
            try:
                data = response.get_json()
                if isinstance(data, dict):
                    data['phase2_direct'] = True
                    data['endpoint_type'] = 'direct_implementation'
                    return jsonify(data), response.status_code
            except:
                pass
        
        return response
        
    except Exception as e:
        logging.error(f"Error in Phase 2 diagnose_plant: {e}")
        return jsonify({
            'error': str(e),
            'phase2_direct': True
        }), 500


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again 
# Changed: methods=['POST'] → methods=['GET']
@analysis_bp.route('/enhance-analysis', methods=['GET'])  # WORKAROUND: was POST
def enhance_plant_analysis():
    """
    Phase 2 direct implementation: Enhance plant analysis with database context.
    Provides semantic alignment: enhancePlantAnalysis operationId → /api/plants/enhance-analysis URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        # Import the original enhance_analysis function
        from api.main import enhance_analysis
        
        # Direct implementation using existing enhance logic
        response = enhance_analysis()
        
        # Mark as Phase 2 direct implementation in response
        if hasattr(response, 'get_json'):
            try:
                data = response.get_json()
                if isinstance(data, dict):
                    data['phase2_direct'] = True
                    data['endpoint_type'] = 'direct_implementation'
                    return jsonify(data), response.status_code
            except:
                pass
        
        return response
        
    except Exception as e:
        logging.error(f"Error in Phase 2 enhance_plant_analysis: {e}")
        return jsonify({
            'error': str(e),
            'phase2_direct': True
        }), 500

