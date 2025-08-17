"""
Photo Upload Routes

Handles photo upload functionality for plants and logs
using token-based authentication.
"""

from flask import Blueprint, request, jsonify, render_template
from api.core.middleware import require_api_key
import logging

# Create the photos blueprint
photos_bp = Blueprint('photos', __name__, url_prefix='/api/photos')


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET']
@photos_bp.route('/upload-for-plant/<token>', methods=['GET'])  # WORKAROUND: was POST
def upload_photo_for_plant_new(token):
    """
    Phase 2 direct implementation: Upload photo for plant using token.
    Provides semantic alignment: uploadPhotoForPlant operationId → /api/photos/upload-for-plant/{token} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        # Import the original upload function
        from api.main import upload_photo_to_plant
        
        # Direct implementation using existing upload logic
        response = upload_photo_to_plant(token)
        
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
        logging.error(f"Error in Phase 2 upload_photo_for_plant: {e}")
        return jsonify({
            'error': str(e),
            'token': token,
            'phase2_direct': True
        }), 500


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET']
@photos_bp.route('/upload-for-log/<token>', methods=['GET'])  # WORKAROUND: was POST
def upload_photo_for_log_new(token):
    """
    Phase 2 direct implementation: Upload photo for log entry using token.
    Provides semantic alignment: uploadPhotoForLog operationId → /api/photos/upload-for-log/{token} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    try:
        # Import the original upload function
        from api.main import upload_photo_to_log
        
        # Direct implementation using existing upload logic
        response = upload_photo_to_log(token)
        
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
        logging.error(f"Error in Phase 2 upload_photo_for_log: {e}")
        return jsonify({
            'error': str(e),
            'token': token,
            'phase2_direct': True
        }), 500


# Upload page routes - serve HTML form when users visit upload URLs
@photos_bp.route('/upload-for-plant/<token>', methods=['GET'])
def upload_page_plant(token):
    """Serve upload page for plant photo uploads"""
    return render_template('upload.html')


@photos_bp.route('/upload-for-log/<token>', methods=['GET'])  
def upload_page_log(token):
    """Serve upload page for log photo uploads"""
    return render_template('upload.html')

