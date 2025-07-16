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

# App factory function
def create_app(testing=False):
    """
    Create and configure the Flask app. If testing=True, disables rate limiting.
    """
    app = Flask(__name__)
    CORS(app)
    # Set config flags
    app.config['TESTING'] = testing
    app.config['RATELIMIT_ENABLED'] = not testing
    # Set up Flask-Limiter for rate limiting
    limiter = Limiter(
        get_remote_address,
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
    return app

# Only run the app if this file is executed directly (not imported)
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True) 