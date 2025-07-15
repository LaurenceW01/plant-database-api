# Plant Database API Documentation

## Overview
This API provides secure, validated access to a plant database. All endpoints return JSON. CORS is enabled for all routes.

---

## Endpoints

### Health Check
- **GET /**
  - Returns API status.
  - **Response:**
    ```json
    { "status": "ok", "message": "Plant Database API is running." }
    ```

### List/Search Plants
- **GET /api/plants**
  - Returns a list of all plants, or search results if `q` is provided.
  - **Query Parameters:**
    - `q` (optional): Search string (matches name, description, or location)
  - **Response:**
    ```json
    { "plants": [ { ...plant fields... }, ... ] }
    ```

### Get Plant by ID or Name
- **GET /api/plants/<id_or_name>**
  - Returns a single plant by ID or name.
  - **Response (success):**
    ```json
    { "plant": { ...plant fields... } }
    ```
  - **Response (not found):**
    ```json
    { "error": "Plant with ID or name '<id_or_name>' not found." }
    ```

### Add Plant
- **POST /api/plants**
  - Adds a new plant. Requires JSON body.
  - **Required Fields:**
    - `Plant Name` (string)
  - **Optional Fields:**
    - `Description`, `Location`, `Photo URL`, ... (see field specs)
  - **Validation:**
    - All fields are validated. Invalid fields return a 400 error.
  - **Example Request:**
    ```json
    {
      "Plant Name": "Rose",
      "Description": "A beautiful flower.",
      "Location": "Front yard",
      "Photo URL": "http://example.com/rose.jpg"
    }
    ```
  - **Response (success):**
    ```json
    { "message": "Added Rose to garden" }
    ```
  - **Response (error):**
    ```json
    { "error": "'Plant Name' is required." }
    { "error": "Invalid field(s): NotAField" }
    ```

### Update Plant
- **PUT /api/plants/<id_or_name>**
  - Updates an existing plant by ID or name. Requires JSON body.
  - **Fields:**
    - Any valid field (see field specs)
  - **Validation:**
    - All fields are validated. Invalid fields return a 400 error.
  - **Example Request:**
    ```json
    { "Description": "Updated description." }
    ```
  - **Response (success):**
    ```json
    { "message": "Updated Rose" }
    ```
  - **Response (error):**
    ```json
    { "error": "No valid fields to update." }
    { "error": "Invalid field(s): NotAField" }
    { "error": "Plant not found" }
    ```

---

## Field Specifications
- See `models/field_config.py` for all valid fields and aliases.
- All fields are case-sensitive and must match the specification or a valid alias.

---

## Error Handling
- All errors return JSON with an `error` key and a descriptive message.
- Status codes:
  - `200` for success
  - `201` for resource creation
  - `400` for validation or input errors
  - `404` for not found

---

## CORS Support
- CORS is enabled for all routes. You can call this API from any origin.

---

## Deployment & Usage Notes

- **App Factory Pattern:**
  - The API uses a Flask app factory (`create_app`). For production, run the app using `create_app()`. For testing, use `create_app(testing=True)` to disable rate limiting and enable test mode.
- **Environment Variables:**
  - `GARDENLLM_API_KEY`: Required for all write operations (POST/PUT). Set this in your environment or deployment platform (e.g., Render.com dashboard).
  - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google credentials JSON file for Sheets access. Should be set in your deployment environment, not committed to git.
  - `.env` file: You can use a `.env` file for local development. All sensitive keys must be excluded from git.
- **Rate Limiting:**
  - In production, write operations are limited to 10 POST/PUT requests per minute per IP. In test mode, rate limiting is disabled.
- **Audit Logging:**
  - All write operations are logged to both `api_audit.log` (local/dev) and stdout (for cloud/Render dashboard).
- **CORS & HTTPS:**
  - CORS is enabled for all routes. Render.com enforces HTTPS for all endpoints.
- **Testing:**
  - Use the app factory with `testing=True` for all tests. See `tests/test_api.py` for examples.
- **Production Run:**
  - Use `gunicorn 'api.main:create_app()'` or similar for production WSGI servers.

---

## Example cURL Requests

**Add a plant:**
```sh
curl -X POST http://localhost:5000/api/plants \
  -H "Content-Type: application/json" \
  -d '{"Plant Name": "Rose", "Description": "A flower"}'
```

**Update a plant:**
```sh
curl -X PUT http://localhost:5000/api/plants/Rose \
  -H "Content-Type: application/json" \
  -d '{"Description": "Updated desc"}'
```

**Get a plant:**
```sh
curl http://localhost:5000/api/plants/Rose
``` 