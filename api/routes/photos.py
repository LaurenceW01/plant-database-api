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
@photos_bp.route('/upload-for-plant/<token>', methods=['GET', 'POST'])  # WORKAROUND: was POST only
def upload_photo_for_plant_new(token):
    """
    CHATGPT WORKAROUND: Handles both GET and POST for photo uploads.
    
    GET: Returns information about the upload endpoint or serves upload form
    POST: Handles actual file upload (original functionality)
    
    Phase 2 direct implementation: Upload photo for plant using token.
    Provides semantic alignment: uploadPhotoForPlant operationId → /api/photos/upload-for-plant/{token} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    from flask import request as flask_request
    
    try:
        # WORKAROUND: Handle GET requests (ChatGPT limitation)
        if flask_request.method == 'GET':
            # For GET requests, check if this looks like a ChatGPT request or browser request
            user_agent = flask_request.headers.get('User-Agent', '').lower()
            accept_header = flask_request.headers.get('Accept', '').lower()
            
            # If it looks like a programmatic request (ChatGPT), return JSON info
            if 'application/json' in accept_header or any(agent in user_agent for agent in ['gpt', 'openai', 'bot', 'curl']):
                from utils.upload_token_manager import validate_upload_token
                
                # Validate token and return information
                is_valid, token_data, error_message = validate_upload_token(token)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': error_message or 'Invalid or expired token',
                        'workaround': 'GET request due to ChatGPT POST issue',
                        'instructions': 'Photo uploads require POST requests with file data. ChatGPT cannot upload files directly.'
                    }), 401
                
                return jsonify({
                    'success': True,
                    'message': 'Photo upload endpoint is ready',
                    'token': token,
                    'token_type': token_data.get('token_type'),
                    'plant_id': token_data.get('plant_id'),
                    'instructions': {
                        'method': 'POST',
                        'content_type': 'multipart/form-data',
                        'required_field': 'file',
                        'note': 'ChatGPT cannot upload files directly. Use browser or curl with -F "file=@image.jpg"'
                    },
                    'workaround': 'GET request due to ChatGPT POST issue',
                    'phase2_direct': True,
                    'endpoint_type': 'direct_implementation'
                }), 200
            else:
                # For browser requests, serve the upload form
                return render_template('upload.html', token=token, upload_type='plant')
        
        # WORKAROUND: Handle POST requests (original functionality)
        elif flask_request.method == 'POST':
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
        logging.error(f"Error in upload_photo_for_plant_new: {e}")
        return jsonify({
            'error': str(e),
            'token': token,
            'method': flask_request.method,
            'phase2_direct': True,
            'workaround': 'Mixed GET/POST due to ChatGPT issue'
        }), 500


# ========== CHATGPT WORKAROUND - TEMPORARY ==========
# TODO: Revert when ChatGPT POST requests work again
# Changed: methods=['POST'] → methods=['GET']
@photos_bp.route('/upload-for-log/<token>', methods=['GET', 'POST'])  # WORKAROUND: was POST only
def upload_photo_for_log_new(token):
    """
    CHATGPT WORKAROUND: Handles both GET and POST for photo uploads.
    
    GET: Returns information about the upload endpoint or serves upload form
    POST: Handles actual file upload (original functionality)
    
    Phase 2 direct implementation: Upload photo for log entry using token.
    Provides semantic alignment: uploadPhotoForLog operationId → /api/photos/upload-for-log/{token} URL
    This was converted from a Phase 1 redirect to a Phase 2 direct implementation.
    """
    from flask import request as flask_request
    
    try:
        # WORKAROUND: Handle GET requests (ChatGPT limitation)
        if flask_request.method == 'GET':
            # For GET requests, check if this looks like a ChatGPT request or browser request
            user_agent = flask_request.headers.get('User-Agent', '').lower()
            accept_header = flask_request.headers.get('Accept', '').lower()
            
            # If it looks like a programmatic request (ChatGPT), return JSON info
            if 'application/json' in accept_header or any(agent in user_agent for agent in ['gpt', 'openai', 'bot', 'curl']):
                from utils.upload_token_manager import validate_upload_token
                
                # Validate token and return information
                is_valid, token_data, error_message = validate_upload_token(token)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': error_message or 'Invalid or expired token',
                        'workaround': 'GET request due to ChatGPT POST issue',
                        'instructions': 'Photo uploads require POST requests with file data. ChatGPT cannot upload files directly.'
                    }), 401
                
                return jsonify({
                    'success': True,
                    'message': 'Photo upload endpoint is ready',
                    'token': token,
                    'token_type': token_data.get('token_type'),
                    'log_id': token_data.get('log_id'),
                    'instructions': {
                        'method': 'POST',
                        'content_type': 'multipart/form-data',
                        'required_field': 'file',
                        'note': 'ChatGPT cannot upload files directly. Use browser or curl with -F "file=@image.jpg"'
                    },
                    'workaround': 'GET request due to ChatGPT POST issue',
                    'phase2_direct': True,
                    'endpoint_type': 'direct_implementation'
                }), 200
            else:
                # For browser requests, serve the upload form
                return render_template('upload.html', token=token, upload_type='log')
        
        # WORKAROUND: Handle POST requests (original functionality)
        elif flask_request.method == 'POST':
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
        logging.error(f"Error in upload_photo_for_log_new: {e}")
        return jsonify({
            'error': str(e),
            'token': token,
            'method': flask_request.method,
            'phase2_direct': True,
            'workaround': 'Mixed GET/POST due to ChatGPT issue'
        }), 500


# NOTE: Upload page functionality is now handled by the main upload endpoints above
# These duplicate routes have been removed to prevent conflicts

