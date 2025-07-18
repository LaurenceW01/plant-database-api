# Import the Flask class from the flask package
from flask import Flask, jsonify, request  # Import request to access query parameters
import sys
sys.path.append('..')  # Add parent directory to sys.path to allow imports from utils and models
from utils.plant_operations import get_plant_data, search_plants  # Import plant data functions
from models.field_config import get_canonical_field_name  # Import field name utility
from flask_cors import CORS  # Import CORS for cross-origin support
import os  # For environment variable access
from functools import wraps  # For creating decorators
from dotenv import load_dotenv  # For loading .env files
from flask_limiter import Limiter  # Import Limiter for rate limiting
from flask_limiter.util import get_remote_address  # Utility to get client IP for rate limiting
import logging  # Import logging module for audit logging
import sys  # Import sys to access stdout for logging

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
API_KEY = os.environ.get('GARDENLLM_API_KEY')

# Define a decorator to require the API key for protected endpoints
def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the API key from the request headers
        key = request.headers.get('x-api-key')
        # If the key is missing or incorrect, return 401 Unauthorized
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        # Otherwise, proceed with the request
        return func(*args, **kwargs)
    return wrapper

# Field name mapping for ChatGPT compatibility (underscore to space format)
def map_underscore_fields_to_canonical(data):
    """
    Convert underscore field names from ChatGPT to canonical field names.
    Maps fields like 'plant_name' or 'Plant___Name' to 'Plant Name' for API compatibility.
    Handles both single underscores and triple underscores from ChatGPT's OpenAPI parser.
    """
    field_mapping = {
        'plant_name': 'Plant Name',
        'plant___name': 'Plant Name',
        'description': 'Description',
        'location': 'Location',
        'light_requirements': 'Light Requirements',
        'light___requirements': 'Light Requirements',
        'frost_tolerance': 'Frost Tolerance',
        'frost___tolerance': 'Frost Tolerance',
        'watering_needs': 'Watering Needs',
        'watering___needs': 'Watering Needs',
        'soil_preferences': 'Soil Preferences',
        'soil___preferences': 'Soil Preferences',
        'pruning_instructions': 'Pruning Instructions',
        'pruning___instructions': 'Pruning Instructions',
        'mulching_needs': 'Mulching Needs',
        'mulching___needs': 'Mulching Needs',
        'fertilizing_schedule': 'Fertilizing Schedule',
        'fertilizing___schedule': 'Fertilizing Schedule',
        'winterizing_instructions': 'Winterizing Instructions',
        'winterizing___instructions': 'Winterizing Instructions',
        'spacing_requirements': 'Spacing Requirements',
        'spacing___requirements': 'Spacing Requirements',
        'care_notes': 'Care Notes',
        'care___notes': 'Care Notes',
        'photo_url': 'Photo URL',
        'photo___url': 'Photo URL',
        'raw_photo_url': 'Raw Photo URL',
        'raw___photo___url': 'Raw Photo URL',
        'last_updated': 'Last Updated',
        'last___updated': 'Last Updated',
        'id': 'ID'
    }
    
    # Convert underscore fields to canonical names
    canonical_data = {}
    for key, value in data.items():
        canonical_key = field_mapping.get(key.lower(), key)  # Use mapping or original key
        canonical_data[canonical_key] = value
    
    return canonical_data

# Define the add_plant and update_plant view functions (without decorators)
def add_plant():
    """
    Add a new plant to the database.
    Expects a JSON payload with required plant fields.
    Accepts both underscore format (from ChatGPT) and space format field names.
    Returns a success message or error details.
    """
    from utils.plant_operations import add_plant_with_fields
    from models.field_config import get_canonical_field_name, is_valid_field
    
    # Log comprehensive debug information about what ChatGPT is sending
    debug_info = {
        "method": request.method,
        "url": request.url,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'Not provided'),
        "content_type": request.content_type,
        "content_length": request.content_length,
        "x_api_key_present": request.headers.get('x-api-key') is not None,
        "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
        "json_data": request.get_json() if request.is_json else None,
        "all_headers": dict(request.headers)
    }
    
    # Log comprehensive debug info to server console
    logging.info(f"ADD_PLANT_DEBUG | {debug_info}")
    
    data = request.get_json()
    # Log the write operation for auditability
    logging.info(
        f"ADD_PLANT | IP: {get_remote_address()} | Endpoint: /api/plants | Payload: {data}"
    )
    if data is None:
        return jsonify({"error": "Missing JSON payload."}), 400
    
    # Convert underscore field names to canonical format for ChatGPT compatibility
    canonical_data = map_underscore_fields_to_canonical(data)
    
    # Validate all fields in the payload
    invalid_fields = [k for k in canonical_data.keys() if not is_valid_field(k)]
    if invalid_fields:
        return jsonify({"error": f"Invalid field(s): {', '.join(invalid_fields)}"}), 400
    # Validate required fields (at least Plant Name)
    plant_name_field = get_canonical_field_name('Plant Name')
    plant_name = canonical_data.get(plant_name_field) or canonical_data.get('Plant Name') or canonical_data.get('name')
    if not plant_name:
        return jsonify({"error": "'Plant Name' is required."}), 400
    
    # Use the comprehensive add_plant_with_fields function that handles all fields
    result = add_plant_with_fields(canonical_data)
    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Unknown error')}), 400
    return jsonify({"message": result.get('message', 'Plant added successfully')}), 201

def update_plant(id_or_name):
    """
    Update an existing plant by its ID or name.
    Expects a JSON payload with fields to update.
    Accepts both underscore format (from ChatGPT) and space format field names.
    Returns a success message or error details.
    """
    from utils.plant_operations import update_plant as update_plant_func
    from models.field_config import is_valid_field
    
    # Log comprehensive debug information about what ChatGPT is sending
    debug_info = {
        "method": request.method,
        "url": request.url,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'Not provided'),
        "content_type": request.content_type,
        "content_length": request.content_length,
        "x_api_key_present": request.headers.get('x-api-key') is not None,
        "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
        "json_data": request.get_json() if request.is_json else None,
        "plant_identifier": id_or_name,
        "all_headers": dict(request.headers)
    }
    
    # Log comprehensive debug info to server console
    logging.info(f"UPDATE_PLANT_DEBUG | {debug_info}")
    
    data = request.get_json()
    # Log the write operation for auditability
    logging.info(
        f"UPDATE_PLANT | IP: {get_remote_address()} | Endpoint: /api/plants/{id_or_name} | Payload: {data}"
    )
    if data is None:
        return jsonify({"error": "Missing JSON payload."}), 400
    
    # Convert underscore field names to canonical format for ChatGPT compatibility
    canonical_data = map_underscore_fields_to_canonical(data)
    
    # Validate all fields in the payload
    invalid_fields = [k for k in canonical_data.keys() if not is_valid_field(k)]
    if invalid_fields:
        return jsonify({"error": f"Invalid field(s): {', '.join(invalid_fields)}"}), 400
    update_fields = {k: v for k, v in canonical_data.items() if is_valid_field(k)}
    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400
    result = update_plant_func(id_or_name, update_fields)
    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Unknown error')}), 400
    return jsonify({"message": result.get('message', 'Plant updated successfully')}), 200

# Function to register all routes (GET, POST, PUT) after config is set
def register_routes(app, limiter, require_api_key):
    """
    Register all API routes after app config is set. Rate limiting is only applied if not in testing mode.
    """
    # Health check route
    @app.route('/', methods=['GET'])
    def health_check():
        """
        Health check endpoint.
        Returns a simple JSON response to confirm the API is running.
        """
        return jsonify({"status": "ok", "message": "Plant Database API is running."}), 200

    # Privacy policy route
    @app.route('/privacy', methods=['GET'])
    def privacy_policy():
        """
        Privacy policy endpoint.
        Returns the privacy policy as HTML for ChatGPT Actions compliance.
        """
        try:
            with open('privacy_policy.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        except FileNotFoundError:
            return jsonify({"error": "Privacy policy not found"}), 404

    # List/search plants route
    @app.route('/api/plants', methods=['GET'])
    def list_or_search_plants():
        """
        List all plants or search for plants by query string.
        Optional query parameters:
        - 'q': search by name, description, or location
        - 'limit': maximum number of plants to return (default: 20 for ChatGPT compatibility)
        - 'offset': number of plants to skip (default: 0)
        Returns a JSON list of plant records.
        """
        query = request.args.get('q', default='', type=str)
        limit = request.args.get('limit', default=20, type=int)  # Default limit for ChatGPT
        offset = request.args.get('offset', default=0, type=int)
        
        if query:
            plants = search_plants(query)
        else:
            plants = get_plant_data()
        
        # Apply pagination
        total_plants = len(plants)
        paginated_plants = plants[offset:offset + limit] if limit > 0 else plants
        
        # Calculate pagination info for ChatGPT guidance
        has_more = (offset + limit) < total_plants
        next_offset = offset + limit if has_more else None
        remaining_plants = max(0, total_plants - (offset + limit))
        
        # Return paginated results with metadata and ChatGPT guidance
        response = {
            "plants": paginated_plants,
            "total": total_plants,
            "count": len(paginated_plants),
            "offset": offset,
            "limit": limit,
            "has_more": has_more,
            "remaining": remaining_plants
        }
        
        # Add helpful guidance for ChatGPT when there are more plants
        if has_more:
            response["pagination_info"] = {
                "message": f"Showing {len(paginated_plants)} of {total_plants} plants. {remaining_plants} more plants available.",
                "next_page_instruction": f"To get the next {min(limit, remaining_plants)} plants, use: GET /api/plants?offset={next_offset}&limit={limit}",
                "get_all_instruction": "To get ALL remaining plants at once, use: GET /api/plants/all"
            }
        
        return jsonify(response), 200

    # Get all plants without pagination (ChatGPT-friendly endpoint)
    @app.route('/api/plants/all', methods=['GET'])
    def get_all_plants():
        """
        Get ALL plants without pagination limits.
        This endpoint is designed for ChatGPT to easily access the complete plant database.
        Optional query parameters:
        - 'q': search by name, description, or location
        Warning: This endpoint may return large amounts of data. Use with caution.
        """
        query = request.args.get('q', default='', type=str)
        
        if query:
            plants = search_plants(query)
        else:
            plants = get_plant_data()
        
        # Return all results without pagination
        response = {
            "plants": plants,
            "total": len(plants),
            "count": len(plants),
            "warning": "This endpoint returns ALL plants. For large databases, consider using paginated /api/plants endpoint.",
            "pagination_alternative": "Use GET /api/plants?limit=20&offset=0 for paginated results"
        }
        return jsonify(response), 200

    # Get plant by ID or name route
    @app.route('/api/plants/<id_or_name>', methods=['GET'])
    def get_plant_by_id_or_name(id_or_name):
        """
        Retrieve a single plant by its ID or name.
        Returns a JSON object for the plant, or a 404 error if not found.
        """
        from utils.plant_operations import find_plant_by_id_or_name
        from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
        from models.field_config import get_canonical_field_name
        
        plant_row, plant_data = find_plant_by_id_or_name(id_or_name)
        if not plant_row or not plant_data:
            return jsonify({"error": f"Plant with ID or name '{id_or_name}' not found."}), 404
        
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        headers = result.get('values', [[]])[0]
        plant_dict = dict(zip(headers, plant_data))
        
        # Get Photo URL formula if the field exists
        photo_url_field = get_canonical_field_name('Photo URL')
        if photo_url_field and photo_url_field in headers:
            try:
                photo_url_col_idx = headers.index(photo_url_field)
                col_letter = chr(65 + photo_url_col_idx)  # Convert index to column letter
                actual_row_num = plant_row + 1  # plant_row is 0-based, sheets are 1-based
                formula_range = f"Plants!{col_letter}{actual_row_num}"
                
                formula_result = sheets_client.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=formula_range,
                    valueRenderOption='FORMULA'
                ).execute()
                
                formula_values = formula_result.get('values', [])
                if formula_values and formula_values[0]:
                    plant_dict[photo_url_field] = formula_values[0][0]
            except Exception as e:
                print(f"Warning: Could not fetch Photo URL formula: {e}")
        
        return jsonify({"plant": plant_dict}), 200

    # Register POST/PUT routes with or without rate limiting
    if not app.config.get('TESTING', False):
        app.add_url_rule(
            '/api/plants',
            view_func=limiter.limit('10 per minute')(require_api_key(add_plant)),
            methods=['POST']
        )
        app.add_url_rule(
            '/api/plants/<id_or_name>',
            view_func=limiter.limit('10 per minute')(require_api_key(update_plant)),
            methods=['PUT']
        )
    else:
        app.add_url_rule(
            '/api/plants',
            view_func=require_api_key(add_plant),
            methods=['POST']
        )
        app.add_url_rule(
            '/api/plants/<id_or_name>',
            view_func=require_api_key(update_plant),
            methods=['PUT']
        )

# Enhanced analyze-plant endpoint with log integration
def analyze_plant():
    """
    Enhanced image analysis endpoint that integrates with plant logging.
    Uploads images to Google Cloud Storage and creates log entries automatically.
    """
    try:
        # Log comprehensive debug information about what ChatGPT is sending
        debug_info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "x_api_key_present": request.headers.get('x-api-key') is not None,
            "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
            "form_data_keys": list(request.form.keys()) if request.form else [],
            "files_present": list(request.files.keys()) if request.files else [],
            "json_data": request.get_json() if request.is_json else None,
            "all_headers": dict(request.headers)
        }
        
        # Add file details if present
        if request.files:
            debug_info["file_details"] = {}
            for file_key, file_obj in request.files.items():
                debug_info["file_details"][file_key] = {
                    "filename": file_obj.filename,
                    "content_type": file_obj.content_type,
                    "size": len(file_obj.read()) if file_obj else 0
                }
                if file_obj:
                    file_obj.seek(0)  # Reset file pointer after reading size
        
        # Log comprehensive debug info to server console
        logging.info(f"ANALYZE_PLANT_DEBUG | {debug_info}")
        
        # Handle both JSON and form-data requests
        if request.content_type and 'application/json' in request.content_type:
            # JSON request - TEXT ONLY (ChatGPT cannot send actual photos via JSON)
            json_data = request.get_json() or {}
            plant_name = json_data.get('plant_name', '').strip()
            user_notes = json_data.get('user_notes', '').strip()
            analysis_type = json_data.get('analysis_type', 'general_care').strip()
            location = json_data.get('location', '').strip()
            
            # JSON mode is TEXT ONLY - no photo processing
            # Note: ChatGPT may send invalid file references like 'file-ABC123' which we ignore
            has_photo_data = False
            has_file = False
            image_data_b64 = None
            
            # Log warning if ChatGPT tries to send photo references
            if json_data.get('photo_data') or json_data.get('image_data') or json_data.get('file'):
                logging.warning(f"ChatGPT sent invalid photo reference in JSON request: {json_data.get('photo_data') or json_data.get('image_data') or json_data.get('file')} - ignoring and proceeding with text-only advice")
        else:
            # Form-data request (direct photo upload)
            plant_name = request.form.get('plant_name', '').strip()
            user_notes = request.form.get('user_notes', '').strip()
            analysis_type = request.form.get('analysis_type', 'general_care').strip()
            location = request.form.get('location', '').strip()
            # Check if image file is present
            has_file = 'file' in request.files and request.files['file'].filename != ''
            has_photo_data = has_file
        
        # If no photo data provided, require plant_name for general advice
        if not has_photo_data and not plant_name:
            return jsonify({
                'success': False, 
                'error': 'Either photo data or plant_name is required. Provide plant_name for general advice without photo.'
            }), 400
        
        # Import required modules
        from utils.storage_client import upload_plant_photo, is_storage_available
        from utils.plant_log_operations import create_log_entry, validate_plant_for_log
        from config.config import openai_client
        import base64
        
        # Initialize variables
        upload_result = None
        analysis_text = ""
        image_base64 = None
        
        if has_photo_data:
            # PHOTO ANALYSIS PATH: Analyze image (with or without storage)
            
            if has_file:
                # DIRECT FILE UPLOAD (multipart/form-data)
                file = request.files['file']
                
                # Check if storage is available for photo upload
                if not is_storage_available():
                    return jsonify({
                        'success': False, 
                        'error': 'Image storage not available. Check Google Cloud Storage configuration.'
                    }), 500
                
                # Validate and upload image file
                try:
                    upload_result = upload_plant_photo(file, plant_name)
                except ValueError as e:
                    return jsonify({'success': False, 'error': str(e)}), 400
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Failed to upload image: {str(e)}'}), 500
                
                # Reset file pointer for OpenAI analysis
                file.seek(0)
                image_data = file.read()
                
                # Convert image to base64 for OpenAI Vision API
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
            else:
                # JSON requests don't support photo processing
                # This branch should never execute since has_photo_data is always False for JSON
                logging.error("Unexpected code path: JSON request trying to process photo data")
                pass
            
            # Only proceed with OpenAI analysis if we have valid image data
            if image_base64:
                # Prepare prompt for image analysis
                prompt = f"""Analyze this plant image and provide a comprehensive assessment. IMPORTANT: Start your response with the plant identification.

Please structure your response as follows:
**PLANT IDENTIFICATION:** [Species/common name]
**HEALTH ASSESSMENT:** [Current condition and any issues]
**TREATMENT RECOMMENDATIONS:** [Specific actions needed]
**GENERAL CARE:** [Ongoing care advice]

Analysis details:
- User provided name: {plant_name if plant_name else 'Not specified - please identify from image'}
- User notes: {user_notes if user_notes else 'None provided'}
- Analysis type: {analysis_type}

Be specific about the plant species/variety so it can be properly logged."""
                
                # Call OpenAI Vision API
                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4o",  # Updated from deprecated gpt-4-vision-preview
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=500
                    )
                    
                    analysis_text = response.choices[0].message.content
                    
                except Exception as e:
                    # If OpenAI analysis fails, provide fallback
                    analysis_text = f"Image analysis failed: {str(e)}"
                    logging.error(f"OpenAI Vision API error: {e}")
            else:
                analysis_text = "No valid image data provided for analysis"
        
        else:
            # TEXT-ONLY ADVICE PATH: Provide general plant advice without photo
            
            # Prepare prompt for general plant advice
            prompt = f"""Provide comprehensive plant care advice for the following:

Plant: {plant_name}
User Questions/Notes: {user_notes if user_notes else 'General care advice needed'}
Analysis Type: {analysis_type}

Please provide detailed advice covering:
1. Watering requirements and schedule
2. Light and location preferences
3. Soil and fertilization needs
4. Common problems and prevention
5. Seasonal care tips
6. Any specific concerns mentioned in user notes

Format your response clearly and practically for plant care."""
            
            # Call OpenAI text completion API
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=500
                )
                
                analysis_text = response.choices[0].message.content
                
            except Exception as e:
                analysis_text = f"Unable to provide plant advice: {str(e)}"
                logging.error(f"OpenAI text API error: {e}")
        
        # Parse analysis into structured components
        # Ensure analysis_text is a string
        if not analysis_text:
            analysis_text = "No analysis available"
        
        # Extract plant identification from AI response for automatic logging
        extracted_plant_name = plant_name  # Use provided name as fallback
        diagnosis = analysis_text
        treatment = ""
        symptoms = user_notes or ""
        confidence_score = 0.8  # Default confidence
        
        # Parse structured AI response to extract plant name and sections
        if analysis_text and "**PLANT IDENTIFICATION:**" in analysis_text:
            try:
                lines = analysis_text.split('\n')
                current_section = ""
                diagnosis_lines = []
                treatment_lines = []
                
                for line in lines:
                    line = line.strip()
                    if "**PLANT IDENTIFICATION:**" in line:
                        # Extract plant name from identification line
                        plant_id_text = line.replace("**PLANT IDENTIFICATION:**", "").strip()
                        if plant_id_text and not extracted_plant_name:
                            # Clean up the plant name (remove brackets, extra text)
                            extracted_plant_name = plant_id_text.split('(')[0].split('[')[0].strip()
                        current_section = "identification"
                    elif "**HEALTH ASSESSMENT:**" in line:
                        current_section = "health"
                    elif "**TREATMENT RECOMMENDATIONS:**" in line:
                        current_section = "treatment"
                    elif "**GENERAL CARE:**" in line:
                        current_section = "care"
                    elif line and line.startswith("**"):
                        current_section = "other"
                    elif line:
                        if current_section in ["health", "identification"]:
                            diagnosis_lines.append(line)
                        elif current_section in ["treatment", "care"]:
                            treatment_lines.append(line)
                
                # Rebuild diagnosis and treatment from parsed sections
                if diagnosis_lines:
                    diagnosis = '\n'.join(diagnosis_lines).strip()
                if treatment_lines:
                    treatment = '\n'.join(treatment_lines).strip()
                    
            except Exception as e:
                logging.warning(f"Failed to parse structured AI response: {e}")
                # Fall back to original logic
                pass
        
        # Fallback parsing for unstructured responses
        if not treatment and analysis_text and ("recommend" in analysis_text.lower() or "treatment" in analysis_text.lower()):
            lines = analysis_text.split('\n')
            diagnosis_lines = []
            treatment_lines = []
            in_treatment_section = False
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['recommend', 'treatment', 'care', 'action']):
                    in_treatment_section = True
                    treatment_lines.append(line)
                elif in_treatment_section and line.strip():
                    treatment_lines.append(line)
                elif not in_treatment_section and line.strip():
                    diagnosis_lines.append(line)
            
            if treatment_lines:
                diagnosis = '\n'.join(diagnosis_lines).strip()
                treatment = '\n'.join(treatment_lines).strip()
        
        # Create log entry if plant was identified
        log_entry_result = None
        if extracted_plant_name and has_photo_data:
            # Create log entry with or without photo storage
            photo_url = upload_result['photo_url'] if upload_result else ""
            raw_photo_url = upload_result['raw_photo_url'] if upload_result else ""
            
            log_entry_result = create_log_entry(
                plant_name=extracted_plant_name,
                photo_url=photo_url,
                raw_photo_url=raw_photo_url,
                diagnosis=diagnosis,
                treatment=treatment,
                symptoms=symptoms,
                user_notes=user_notes,
                confidence_score=confidence_score,
                analysis_type=analysis_type,
                follow_up_required=False,
                follow_up_date="",
                location=location
            )
        
        # Prepare response
        response_data = {
            'success': True,
            'analysis': {
                'diagnosis': diagnosis,
                'treatment': treatment if treatment else diagnosis,
                'confidence': confidence_score,
                'analysis_type': analysis_type,
                'advice_type': 'photo_analysis' if has_photo_data else 'text_advice_only'
            }
        }
        
        # Include identified plant name if extracted from photo
        if extracted_plant_name and extracted_plant_name != plant_name:
            response_data['analysis']['identified_plant'] = extracted_plant_name
        
        # Clear messaging about what actually happened
        if has_file:
            response_data['analysis']['photo_processed'] = True
            response_data['analysis']['photo_stored'] = True
            response_data['analysis']['note'] = "Photo was analyzed and uploaded to storage"
        elif has_photo_data:
            response_data['analysis']['photo_processed'] = True
            response_data['analysis']['photo_stored'] = False
            response_data['analysis']['note'] = "Photo was analyzed but not stored (ChatGPT mode)"
        else:
            response_data['analysis']['photo_processed'] = False
            response_data['analysis']['photo_stored'] = False
            response_data['analysis']['note'] = "Text-only advice provided - no photo was analyzed"
        
        # Add image upload info only if file was uploaded
        if has_file and upload_result:
            response_data['image_upload'] = {
                'photo_url': upload_result['raw_photo_url'],
                'filename': upload_result['filename'],
                'upload_time': upload_result['upload_time']
            }
        
        # Add log entry info if created, or explain why no log was created
        if log_entry_result and log_entry_result.get('success'):
            log_message = "Log entry successfully created in your plant database"
            if has_file:
                log_message += " (with photo)"
            else:
                log_message += " (text-based, no photo stored)"
                
            response_data['log_entry'] = {
                'log_id': log_entry_result['log_id'],
                'plant_name': log_entry_result['plant_name'],
                'created': True,
                'message': log_message
            }
        elif extracted_plant_name and has_photo_data:
            # Plant was identified from photo but log creation failed (likely not in database)
            plant_validation = validate_plant_for_log(extracted_plant_name)
            response_data['suggestions'] = {
                'plant_not_found': True,
                'identified_plant': extracted_plant_name,
                'similar_plants': plant_validation.get('suggestions', []),
                'create_new_plant': plant_validation.get('create_new_option', False),
                'message': f"I identified this as '{extracted_plant_name}' but it's not in your plant database. You can add it or link to a similar plant."
            }
            response_data['log_entry'] = {
                'created': False,
                'message': f"No log entry created - '{extracted_plant_name}' not found in plant database"
            }
        else:
            # No photo data or no plant identified
            response_data['log_entry'] = {
                'created': False,
                'message': "No log entry created - text advice only (no photo analysis performed)"
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        # Comprehensive error handling to prevent "Error talking to connector"
        error_msg = str(e)
        logging.error(f"Error in analyze-plant endpoint: {e}")
        
        # Return a user-friendly error response
        return jsonify({
            'success': False, 
            'error': f'Server error during analysis: {error_msg}',
            'advice_type': 'error',
            'analysis': {
                'diagnosis': 'Unable to complete analysis due to server error',
                'treatment': 'Please try again or contact support if the problem persists',
                'confidence': 0.0,
                'analysis_type': analysis_type if 'analysis_type' in locals() else 'unknown'
            }
        }), 500

def register_image_analysis_route(app, limiter, require_api_key):
    """Register the image analysis route with appropriate rate limiting and API key protection"""
    if not app.config.get('TESTING', False):
        app.add_url_rule(
            '/api/analyze-plant',
            view_func=limiter.limit('5 per minute')(require_api_key(analyze_plant)),  # Added API key requirement
            methods=['POST']
        )
    else:
        app.add_url_rule(
            '/api/analyze-plant',
            view_func=require_api_key(analyze_plant),  # Added API key requirement for testing too
            methods=['POST']
        )

# Plant Log endpoints
def create_plant_log():
    """
    Create a new plant log entry.
    Expects multipart/form-data with file upload and log details.
    """
    try:
        from utils.plant_log_operations import create_log_entry
        from utils.storage_client import upload_plant_photo, is_storage_available
        
        # Log comprehensive debug information about what ChatGPT is sending
        debug_info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "x_api_key_present": request.headers.get('x-api-key') is not None,
            "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
            "form_data_keys": list(request.form.keys()) if request.form else [],
            "form_data_values": {k: v[:100] + "..." if len(str(v)) > 100 else v for k, v in request.form.items()} if request.form else {},
            "files_present": list(request.files.keys()) if request.files else [],
            "all_headers": dict(request.headers)
        }
        
        # Add file details if present
        if request.files:
            debug_info["file_details"] = {}
            for file_key, file_obj in request.files.items():
                debug_info["file_details"][file_key] = {
                    "filename": file_obj.filename,
                    "content_type": file_obj.content_type,
                    "size": len(file_obj.read()) if file_obj else 0
                }
                if file_obj:
                    file_obj.seek(0)  # Reset file pointer after reading size
        
        # Log comprehensive debug info to server console
        logging.info(f"CREATE_PLANT_LOG_DEBUG | {debug_info}")
        
        # Get form data
        plant_name = request.form.get('plant_name', '').strip()
        user_notes = request.form.get('user_notes', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        treatment = request.form.get('treatment', '').strip()
        symptoms = request.form.get('symptoms', '').strip()
        analysis_type = request.form.get('analysis_type', 'health_assessment').strip()
        confidence_score = float(request.form.get('confidence_score', 0.8))
        follow_up_required = request.form.get('follow_up_required', 'false').lower() == 'true'
        follow_up_date = request.form.get('follow_up_date', '').strip()
        log_title = request.form.get('log_title', '').strip()
        location = request.form.get('location', '').strip()
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'plant_name is required'}), 400
        
        photo_url = ""
        raw_photo_url = ""
        
        # Handle optional file upload
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            if is_storage_available():
                try:
                    upload_result = upload_plant_photo(file, plant_name)
                    photo_url = upload_result['photo_url']
                    raw_photo_url = upload_result['raw_photo_url']
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Failed to upload image: {str(e)}'}), 500
            else:
                return jsonify({'success': False, 'error': 'Image storage not available'}), 500
        
        # Create log entry
        result = create_log_entry(
            plant_name=plant_name,
            photo_url="",  # No photo in JSON mode
            raw_photo_url="", 
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes,
            confidence_score=confidence_score,
            analysis_type=analysis_type,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date,
            location=location,
            log_title=log_title
        )
        
        if result['success']:
            # Generate upload token and URL for adding photos later
            from utils.upload_token_manager import generate_upload_token
            
            upload_token = generate_upload_token(
                log_id=result['log_id'],
                plant_name=plant_name,
                expiration_hours=24
            )
            
            upload_url = f"{request.host_url.rstrip('/')}/upload/{upload_token}"
            
            # Detect if user mentioned photos in their input
            photo_keywords = ['photo', 'picture', 'image', 'pic', 'camera', 'take', 'show', 'visual', 'upload']
            text_to_check = f"{user_notes} {diagnosis} {treatment} {symptoms}".lower()
            photo_mentioned = any(keyword in text_to_check for keyword in photo_keywords)
            
            # Customize response based on whether photos were mentioned
            if photo_mentioned:
                upload_instructions = f"🔥 PHOTO UPLOAD READY: Since you mentioned photos, use this link to upload them: {upload_url}"
                message = f"Log entry created successfully with photo upload ready"
            else:
                upload_instructions = f"To add a photo to this log entry, visit: {upload_url}"
                message = f"Log entry created successfully"
            
            # Enhance the response with upload information
            enhanced_result = result.copy()
            enhanced_result['upload_url'] = upload_url
            enhanced_result['upload_instructions'] = upload_instructions
            enhanced_result['message'] = message
            enhanced_result['photo_mentioned'] = photo_mentioned
            
            return jsonify(enhanced_result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error creating plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_plant_log_simple():
    """
    Create a new plant log entry using JSON (ChatGPT-friendly).
    No file upload - focuses on text-based logging.
    """
    try:
        from utils.plant_log_operations import create_log_entry
        
        # Log comprehensive debug information about what ChatGPT is sending
        debug_info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "x_api_key_present": request.headers.get('x-api-key') is not None,
            "x_api_key_preview": request.headers.get('x-api-key', '')[:10] + "..." if request.headers.get('x-api-key') else None,
            "json_data": request.get_json() if request.is_json else None,
            "all_headers": dict(request.headers)
        }
        
        # Log comprehensive debug info to server console
        logging.info(f"CREATE_PLANT_LOG_SIMPLE_DEBUG | {debug_info}")
        
        data = request.get_json()
        if data is None:
            return jsonify({'success': False, 'error': 'Missing JSON payload'}), 400
        
        # Get required and optional fields
        plant_name = data.get('plant_name', '').strip()
        user_notes = data.get('user_notes', '').strip()
        diagnosis = data.get('diagnosis', '').strip()
        treatment = data.get('treatment', '').strip()
        symptoms = data.get('symptoms', '').strip()
        analysis_type = data.get('analysis_type', 'health_assessment').strip()
        confidence_score = float(data.get('confidence_score', 0.8))
        follow_up_required = data.get('follow_up_required', False)
        follow_up_date = data.get('follow_up_date', '').strip()
        log_title = data.get('log_title', '').strip()
        location = data.get('location', '').strip()
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'plant_name is required'}), 400
        
        # Create log entry without file upload
        result = create_log_entry(
            plant_name=plant_name,
            photo_url="",  # No photo for simple JSON endpoint
            raw_photo_url="",
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes,
            confidence_score=confidence_score,
            analysis_type=analysis_type,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date,
            log_title=log_title,
            location=location
        )
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error creating simple plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_plant_log_history(plant_name):
    """Get log history for a specific plant in journal format"""
    try:
        from utils.plant_log_operations import get_plant_log_entries, format_log_entries_as_journal
        
        # Get query parameters
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        format_type = request.args.get('format', default='standard', type=str)
        
        # Get log entries
        result = get_plant_log_entries(plant_name, limit, offset)
        
        if not result.get('success'):
            return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 400
        
        # Format as journal if requested
        if format_type == 'journal':
            journal_entries = format_log_entries_as_journal(result['log_entries'])
            result['journal_entries'] = journal_entries
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error getting plant log history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_log_entry_details(log_id):
    """Get details of a specific log entry"""
    try:
        from utils.plant_log_operations import get_log_entry_by_id, format_log_entries_as_journal
        
        format_type = request.args.get('format', default='standard', type=str)
        
        result = get_log_entry_by_id(log_id)
        
        if not result.get('success'):
            return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 400
        
        # Format as journal if requested
        if format_type == 'journal':
            journal_entries = format_log_entries_as_journal([result['log_entry']])
            if journal_entries:
                result['journal_entry'] = journal_entries[0]
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error getting log entry: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def search_plant_logs():
    """Search plant log entries with various filters"""
    try:
        from utils.plant_log_operations import search_log_entries, format_log_entries_as_journal
        
        # Get query parameters
        plant_name = request.args.get('plant_name', default='', type=str)
        query = request.args.get('q', default='', type=str)
        symptoms = request.args.get('symptoms', default='', type=str)
        date_from = request.args.get('date_from', default='', type=str)
        date_to = request.args.get('date_to', default='', type=str)
        limit = request.args.get('limit', default=20, type=int)
        format_type = request.args.get('format', default='standard', type=str)
        
        # Search log entries
        result = search_log_entries(
            plant_name=plant_name,
            query=query,
            symptoms=symptoms,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Format as journal if requested
        if format_type == 'journal':
            journal_entries = format_log_entries_as_journal(result['search_results'])
            result['journal_entries'] = journal_entries
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error searching plant logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def upload_photo_to_log(token):
    """
    Upload a photo to an existing log entry using a secure upload token.
    This endpoint supports the two-step photo upload workflow where users 
    first create a log entry, then upload photos using the provided token.
    """
    try:
        # Add debugging to identify where the 500 error occurs
        logging.info(f"UPLOAD_DEBUG: Starting upload_photo_to_log function")
        
        from utils.upload_token_manager import validate_upload_token, mark_token_used
        logging.info(f"UPLOAD_DEBUG: Imported upload_token_manager")
        
        from utils.storage_client import upload_plant_photo, is_storage_available
        logging.info(f"UPLOAD_DEBUG: Imported storage_client")
        
        from utils.plant_log_operations import update_log_entry_photo
        logging.info(f"UPLOAD_DEBUG: Imported plant_log_operations")
        
        # Token is passed as function parameter from Flask route
        logging.info(f"UPLOAD_DEBUG: Received token parameter: {token[:20] if token else 'None'}...")
        
        if not token:
            logging.error(f"UPLOAD_DEBUG: No token provided")
            return jsonify({
                'success': False, 
                'error': 'Upload token is required'
            }), 400
        
        # Validate upload token
        logging.info(f"UPLOAD_DEBUG: Validating token...")
        is_valid, token_data, error_message = validate_upload_token(token)
        logging.info(f"UPLOAD_DEBUG: Token validation result: valid={is_valid}, data={token_data}")
        
        if not is_valid or not token_data:
            logging.error(f"UPLOAD_DEBUG: Token validation failed: {error_message}")
            return jsonify({
                'success': False,
                'error': f'Invalid upload token: {error_message}'
            }), 401
        
        # Check if photo file is provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No photo file provided. Please select a photo to upload.'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No photo file selected. Please choose a file.'
            }), 400
        
        # Validate storage availability
        if not is_storage_available():
            return jsonify({
                'success': False,
                'error': 'Photo storage is currently unavailable. Please try again later.'
            }), 500
        
        # Extract log information from token
        log_id = token_data.get('log_id', '')
        plant_name = token_data.get('plant_name', '')
        
        # Upload photo to storage
        try:
            upload_result = upload_plant_photo(file, plant_name)
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'Failed to upload photo: {str(e)}'
            }), 500
        
        # Update log entry with photo URLs
        update_result = update_log_entry_photo(
            log_id, 
            upload_result['photo_url'], 
            upload_result['raw_photo_url']
        )
        
        if not update_result.get('success'):
            # Photo uploaded but log update failed - log warning but continue
            logging.warning(f"Photo uploaded but log update failed for {log_id}: {update_result.get('error')}")
        
        # Mark token as used to prevent reuse
        user_ip = request.remote_addr or "unknown"
        mark_token_used(token, user_ip)
        
        # Return success response
        return jsonify({
            'success': True,
            'message': f'Photo uploaded successfully to {plant_name} log entry',
            'log_id': log_id,
            'plant_name': plant_name,
            'photo_upload': {
                'photo_url': upload_result['raw_photo_url'],
                'filename': upload_result['filename'],
                'upload_time': upload_result['upload_time'],
                'file_size': upload_result.get('file_size', 'unknown')
            },
            'log_update': {
                'updated': update_result.get('success', False),
                'message': update_result.get('message', 'Log entry updated with photo')
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error in upload_photo_to_log endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during photo upload'
        }), 500

def serve_upload_page(token):
    """
    Serve the HTML upload page for a specific token.
    Validates the token before serving the page.
    """
    try:
        from utils.upload_token_manager import validate_upload_token
        from flask import render_template
        
        # Validate the token before serving the page
        is_valid, token_data, error_message = validate_upload_token(token)
        if not is_valid or not token_data:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Invalid Upload Token</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 8px; display: inline-block; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>❌ Invalid Upload Token</h2>
                    <p>{error_message or 'This upload link has expired or is invalid.'}</p>
                    <p>Please request a new upload link from your plant logging session.</p>
                </div>
            </body>
            </html>
            """, 401
        
        # Token is valid, serve the upload page
        try:
            return render_template('upload.html')
        except Exception as template_error:
            # Fallback to inline HTML if template file not found
            logging.warning(f"Template not found, serving inline HTML: {template_error}")
            
            # Read the template file directly as fallback
            try:
                with open('templates/upload.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return html_content
            except Exception as file_error:
                logging.error(f"Could not read upload template: {file_error}")
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Upload Error</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .error {{ color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 8px; display: inline-block; }}
                    </style>
                </head>
                <body>
                    <div class="error">
                        <h2>❌ Upload Page Error</h2>
                        <p>Could not load the upload page. Please try again later.</p>
                    </div>
                </body>
                </html>
                """, 500
        
    except Exception as e:
        logging.error(f"Error serving upload page: {e}")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Server Error</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 8px; display: inline-block; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ Server Error</h2>
                <p>There was an error loading the upload page. Please try again later.</p>
            </div>
        </body>
        </html>
        """, 500

def register_plant_log_routes(app, limiter, require_api_key):
    """Register plant log API routes"""
    if not app.config.get('TESTING', False):
        # POST /api/plants/log - Create log entry with file upload (requires API key)
        app.add_url_rule(
            '/api/plants/log',
            view_func=limiter.limit('10 per minute')(require_api_key(create_plant_log)),
            methods=['POST']
        )
        
        # POST /api/plants/log/simple - Create log entry with JSON (ChatGPT-friendly)
        app.add_url_rule(
            '/api/plants/log/simple',
            view_func=limiter.limit('10 per minute')(require_api_key(create_plant_log_simple)),
            methods=['POST']
        )
        
        # POST /upload/{token} - Upload photo to existing log entry (no API key needed, token is auth)
        app.add_url_rule(
            '/upload/<token>',
            view_func=limiter.limit('20 per minute')(upload_photo_to_log),
            methods=['POST']
        )
        
        # GET /upload/{token} - Serve upload page for specific token (no API key needed, token is auth)
        app.add_url_rule(
            '/upload/<token>',
            view_func=limiter.limit('60 per minute')(serve_upload_page),
            methods=['GET']
        )
        
        # GET routes (no API key required for reading)
        app.add_url_rule(
            '/api/plants/<plant_name>/log',
            view_func=limiter.limit('30 per minute')(get_plant_log_history),
            methods=['GET']
        )
        
        app.add_url_rule(
            '/api/plants/log/<log_id>',
            view_func=limiter.limit('30 per minute')(get_log_entry_details),
            methods=['GET']
        )
        
        app.add_url_rule(
            '/api/plants/log/search',
            view_func=limiter.limit('30 per minute')(search_plant_logs),
            methods=['GET']
        )
    else:
        # Testing mode - no rate limits
        app.add_url_rule('/api/plants/log', view_func=require_api_key(create_plant_log), methods=['POST'])
        app.add_url_rule('/api/plants/log/simple', view_func=require_api_key(create_plant_log_simple), methods=['POST'])
        app.add_url_rule('/upload/<token>', view_func=upload_photo_to_log, methods=['POST'])
        app.add_url_rule('/upload/<token>', view_func=serve_upload_page, methods=['GET'])
        app.add_url_rule('/api/plants/<plant_name>/log', view_func=get_plant_log_history, methods=['GET'])
        app.add_url_rule('/api/plants/log/<log_id>', view_func=get_log_entry_details, methods=['GET'])
        app.add_url_rule('/api/plants/log/search', view_func=search_plant_logs, methods=['GET'])

# App factory function
def create_app(testing=False):
    """
    Create and configure the Flask app. If testing=True, disables rate limiting.
    """
    app = Flask(__name__, template_folder='../templates')  # Configure template folder
    CORS(app)
    # Set config flags
    app.config['TESTING'] = testing
    app.config['RATELIMIT_ENABLED'] = not testing
    # Set up Flask-Limiter with production-ready storage
    if not testing:
        # Try to use Redis for production rate limiting storage
        redis_url = os.environ.get('REDIS_URL')
        if redis_url:
            # Production: Use Redis for persistent, scalable rate limiting
            try:
                limiter = Limiter(
                    key_func=get_remote_address,
                    app=app,
                    default_limits=[],
                    storage_uri=redis_url,
                    on_breach=lambda limit: logging.warning(f"Rate limit exceeded: {limit}")
                )
                logging.info("Rate limiting configured with Redis storage")
            except Exception as e:
                logging.warning(f"Redis connection failed, falling back to in-memory storage: {e}")
                limiter = Limiter(
                    key_func=get_remote_address,
                    app=app,
                    default_limits=[]
                )
        else:
            # Fallback: Use in-memory storage with warning
            limiter = Limiter(
                key_func=get_remote_address,
                app=app,
                default_limits=[]
            )
            logging.warning("REDIS_URL not set. Using in-memory rate limiting. Set REDIS_URL for production.")
    else:
        # Testing: Use simple in-memory storage without warnings
        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            default_limits=[]
        )
    # Set up logging for auditability
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler('api_audit.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Register all routes after config is set
    register_routes(app, limiter, require_api_key)
    # Register image analysis route
    register_image_analysis_route(app, limiter, require_api_key)
    # Register plant log routes
    register_plant_log_routes(app, limiter, require_api_key)
    
    # Debug endpoint to check route registration and import status
    @app.route('/api/debug/info', methods=['GET'])
    def debug_info():
        """Debug endpoint to check what routes are registered and import status"""
        import sys
        
        debug_data = {
            "registered_routes": [],
            "import_status": {},
            "python_path": sys.path[:3],  # First few paths
            "available_modules": {}
        }
        
        # Get all registered routes
        for rule in app.url_map.iter_rules():
            debug_data["registered_routes"].append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods) if rule.methods else [],
                "rule": str(rule)
            })
        
        # Check import status for critical modules
        try:
            from utils.storage_client import upload_plant_photo, is_storage_available
            debug_data["import_status"]["storage_client"] = "SUCCESS"
            debug_data["available_modules"]["storage_available"] = is_storage_available()
        except Exception as e:
            debug_data["import_status"]["storage_client"] = f"FAILED: {str(e)}"
        
        try:
            from utils.plant_log_operations import create_log_entry
            debug_data["import_status"]["plant_log_operations"] = "SUCCESS"
        except Exception as e:
            debug_data["import_status"]["plant_log_operations"] = f"FAILED: {str(e)}"
        
        try:
            from config.config import openai_client
            debug_data["import_status"]["openai_client"] = "SUCCESS"
        except Exception as e:
            debug_data["import_status"]["openai_client"] = f"FAILED: {str(e)}"
        
        try:
            from PIL import Image
            debug_data["import_status"]["PIL"] = "SUCCESS"
        except Exception as e:
            debug_data["import_status"]["PIL"] = f"FAILED: {str(e)}"
        
        try:
            import httpx
            debug_data["import_status"]["httpx"] = "SUCCESS"
        except Exception as e:
            debug_data["import_status"]["httpx"] = f"FAILED: {str(e)}"
        
        try:
            from werkzeug.datastructures import FileStorage
            debug_data["import_status"]["werkzeug"] = "SUCCESS"
        except Exception as e:
            debug_data["import_status"]["werkzeug"] = f"FAILED: {str(e)}"
        
        return jsonify(debug_data)
    
    # ChatGPT Debug endpoint - logs exactly what ChatGPT sends
    @app.route('/api/debug/chatgpt', methods=['GET', 'POST', 'PUT'])
    def debug_chatgpt():
        """
        Debug endpoint to capture exactly what ChatGPT is sending.
        Logs all headers, method, content type, and body for debugging 403 errors.
        NO AUTHENTICATION REQUIRED - purely for debugging.
        """
        import json
        from datetime import datetime
        
        # Capture all request details
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Not provided'),
            "content_type": request.content_type,
            "content_length": request.content_length,
            "headers": {},
            "form_data": {},
            "json_data": None,
            "files": {},
            "args": dict(request.args),
            "endpoint": "debug_chatgpt",
            "auth_analysis": {}
        }
        
        # Capture all headers (safely)
        for header_name, header_value in request.headers:
            debug_data["headers"][header_name] = header_value
        
        # Check for API key specifically
        api_key_header = request.headers.get('x-api-key')
        debug_data["auth_analysis"] = {
            "x_api_key_present": api_key_header is not None,
            "x_api_key_value": api_key_header[:10] + "..." if api_key_header else None,
            "authorization_header": request.headers.get('Authorization'),
            "auth_header_count": len([h[0] for h in request.headers if 'auth' in h[0].lower() or 'key' in h[0].lower()])
        }
        
        # Capture form data if present
        try:
            if request.form:
                debug_data["form_data"] = dict(request.form)
        except Exception as e:
            debug_data["form_data"] = f"Error reading form data: {str(e)}"
        
        # Capture JSON data if present
        try:
            if request.is_json:
                debug_data["json_data"] = request.get_json()
        except Exception as e:
            debug_data["json_data"] = f"Error reading JSON data: {str(e)}"
        
        # Capture file uploads if present
        try:
            if request.files:
                for file_key, file_obj in request.files.items():
                    debug_data["files"][file_key] = {
                        "filename": file_obj.filename,
                        "content_type": file_obj.content_type,
                        "size": len(file_obj.read()) if file_obj else 0
                    }
                    # Reset file pointer
                    if file_obj:
                        file_obj.seek(0)
        except Exception as e:
            debug_data["files"] = f"Error reading files: {str(e)}"
        
        # Log to server console for debugging
        logging.info(f"CHATGPT_DEBUG | {request.method} {request.url} | Headers: {dict(request.headers)} | API Key: {'Present' if api_key_header else 'Missing'}")
        
        # Return comprehensive debug info
        return jsonify({
            "success": True,
            "message": "Debug endpoint reached successfully - no authentication required",
            "request_details": debug_data,
            "server_response": {
                "your_ip": request.remote_addr,
                "server_time": datetime.now().isoformat(),
                "endpoint_working": True,
                "auth_required": False
            },
            "next_steps": {
                "if_you_see_this": "The request successfully reached our server",
                "check_for_api_key": "Look at auth_analysis section to see if x-api-key header is present",
                "test_real_endpoint": "Try calling /api/plants/log with the x-api-key header"
            }
        }), 200
    
    @app.route('/api/debug-log', methods=['POST'])
    def debug_log():
        """
        Receive debug log messages from mobile upload debugging.
        Logs the information to server console for troubleshooting.
        """
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Missing JSON payload."}), 400
                
            token = data.get('token', 'unknown')
            log_message = data.get('logMessage', '')
            user_agent = data.get('userAgent', '')
            is_mobile = data.get('isMobile', False)
            timestamp = data.get('timestamp', '')
            
            # Log to server console with special prefix for easy identification
            logging.info(f"MOBILE_DEBUG | Token: {token[:8]}... | {log_message}")
            logging.info(f"MOBILE_DEBUG | UA: {user_agent}")
            
            return jsonify({"success": True, "message": "Debug log received"}), 200
            
        except Exception as e:
            logging.error(f"Error processing debug log: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/debug-log-bulk', methods=['POST'])
    def debug_log_bulk():
        """
        Receive bulk debug logs from mobile upload debugging.
        Logs all information to server console for comprehensive troubleshooting.
        """
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Missing JSON payload."}), 400
                
            token = data.get('token', 'unknown')
            session_start = data.get('sessionStart', '')
            logs = data.get('logs', [])
            user_agent = data.get('userAgent', '')
            is_mobile = data.get('isMobile', False)
            url = data.get('url', '')
            
            # Log session header
            logging.info(f"MOBILE_DEBUG_BULK | ===== DEBUG SESSION START =====")
            logging.info(f"MOBILE_DEBUG_BULK | Token: {token[:8]}...")
            logging.info(f"MOBILE_DEBUG_BULK | Session: {session_start}")
            logging.info(f"MOBILE_DEBUG_BULK | URL: {url}")
            logging.info(f"MOBILE_DEBUG_BULK | User Agent: {user_agent}")
            logging.info(f"MOBILE_DEBUG_BULK | Is Mobile: {is_mobile}")
            logging.info(f"MOBILE_DEBUG_BULK | Total Logs: {len(logs)}")
            
            # Log each debug message
            for i, log_entry in enumerate(logs):
                timestamp = log_entry.get('timestamp', '')
                message = log_entry.get('message', '')
                logging.info(f"MOBILE_DEBUG_BULK | {i+1:03d} | {timestamp} | {message}")
            
            logging.info(f"MOBILE_DEBUG_BULK | ===== DEBUG SESSION END =====")
            
            return jsonify({
                "success": True, 
                "message": f"Received {len(logs)} debug log entries",
                "logged": True
            }), 200
            
        except Exception as e:
            logging.error(f"Error processing bulk debug logs: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    return app



# Only run the app if this file is executed directly (not imported)
if __name__ == '__main__':
    import os
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 