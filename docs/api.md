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