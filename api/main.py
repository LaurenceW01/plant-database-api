# Import the Flask class from the flask package
from flask import Flask, jsonify, request  # Import request to access query parameters
import sys
sys.path.append('..')  # Add parent directory to sys.path to allow imports from utils and models
from utils.plant_operations import get_plant_data, search_plants  # Import plant data functions
from models.field_config import get_canonical_field_name  # Import field name utility
from flask_cors import CORS  # Import CORS for cross-origin support

# Create a Flask application instance
# The __name__ variable helps Flask determine the root path for the app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define a health check route at the root URL ('/')
# This route can be used to verify that the API server is running
@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns a simple JSON response to confirm the API is running.
    """
    # Return a JSON response with a status message
    return jsonify({"status": "ok", "message": "Plant Database API is running."}), 200

# Define a route for listing or searching plants
# This endpoint supports optional query parameter 'q' for search
@app.route('/api/plants', methods=['GET'])
def list_or_search_plants():
    """
    List all plants or search for plants by query string.
    Optional query parameter 'q' can be used to search by name, description, or location.
    Returns a JSON list of plant records.
    """
    # Get the 'q' query parameter from the request (default to empty string if not provided)
    query = request.args.get('q', default='', type=str)

    # If a search query is provided, use the search_plants function
    if query:
        # Search for plants matching the query
        plants = search_plants(query)
    else:
        # Otherwise, return all plant data
        plants = get_plant_data()

    # Return the list of plants as a JSON response
    return jsonify({"plants": plants}), 200

# Define a route for adding a new plant
# This endpoint accepts JSON data and adds a new plant to the database
@app.route('/api/plants', methods=['POST'])
def add_plant():
    """
    Add a new plant to the database.
    Expects a JSON payload with required plant fields.
    Returns a success message or error details.
    """
    from utils.plant_operations import add_plant as add_plant_func
    from models.field_config import get_canonical_field_name, is_valid_field
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing JSON payload."}), 400
    # Validate all fields in the payload
    invalid_fields = [k for k in data.keys() if not is_valid_field(k)]
    if invalid_fields:
        return jsonify({"error": f"Invalid field(s): {', '.join(invalid_fields)}"}), 400
    # Validate required fields (at least Plant Name)
    plant_name = data.get(get_canonical_field_name('Plant Name')) or data.get('Plant Name') or data.get('name')
    if not plant_name:
        return jsonify({"error": "'Plant Name' is required."}), 400
    description = data.get(get_canonical_field_name('Description')) or data.get('Description') or data.get('description', '')
    location = data.get(get_canonical_field_name('Location')) or data.get('Location') or data.get('location', '')
    photo_url = data.get(get_canonical_field_name('Photo URL')) or data.get('Photo URL') or data.get('photo_url', '')
    result = add_plant_func(plant_name, description, location, photo_url)
    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Unknown error')}), 400
    return jsonify({"message": result.get('message', 'Plant added successfully')}), 201

# Define a route for retrieving a single plant by ID or name
# This endpoint returns a single plant record or a 404 if not found
@app.route('/api/plants/<id_or_name>', methods=['GET'])
def get_plant_by_id_or_name(id_or_name):
    """
    Retrieve a single plant by its ID or name.
    Returns a JSON object for the plant, or a 404 error if not found.
    """
    from utils.plant_operations import find_plant_by_id_or_name
    from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
    # Attempt to find the plant by ID or name
    plant_row, plant_data = find_plant_by_id_or_name(id_or_name)
    if not plant_row or not plant_data:
        return jsonify({"error": f"Plant with ID or name '{id_or_name}' not found."}), 404
    # Fetch headers to map the row to a dictionary
    result = sheets_client.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    headers = result.get('values', [[]])[0]
    # Map the plant_data list to a dictionary using headers
    plant_dict = dict(zip(headers, plant_data))
    return jsonify({"plant": plant_dict}), 200

# Define a route for updating an existing plant by ID or name
# This endpoint accepts JSON data and updates the plant in the database
@app.route('/api/plants/<id_or_name>', methods=['PUT'])
def update_plant(id_or_name):
    """
    Update an existing plant by its ID or name.
    Expects a JSON payload with fields to update.
    Returns a success message or error details.
    """
    from utils.plant_operations import update_plant as update_plant_func
    from models.field_config import is_valid_field
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing JSON payload."}), 400
    # Validate all fields in the payload
    invalid_fields = [k for k in data.keys() if not is_valid_field(k)]
    if invalid_fields:
        return jsonify({"error": f"Invalid field(s): {', '.join(invalid_fields)}"}), 400
    update_fields = {k: v for k, v in data.items() if is_valid_field(k)}
    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400
    result = update_plant_func(id_or_name, update_fields)
    if not result.get('success'):
        return jsonify({"error": result.get('error', 'Unknown error')}), 400
    return jsonify({"message": result.get('message', 'Plant updated successfully')}), 200

# Only run the app if this file is executed directly (not imported)
if __name__ == '__main__':
    # Start the Flask development server on host 0.0.0.0 and port 5000
    # In production, use gunicorn as described in the README
    app.run(host='0.0.0.0', port=5000, debug=True) 