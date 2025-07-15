# Plant Database API

## Overview
This project exposes the existing plant database as a secure, modern API, enabling both human users and AI assistants (such as ChatGPT) to add, update, and query plant data. The API is designed for deployment on render.com and strictly preserves the original database model and field specifications.

## Objectives
- Provide a robust, secure API for CRUD operations on the plant database
- Reuse centralized add/update logic, field specifications, and validation from the legacy codebase
- Enable safe integration with ChatGPT and other AI clients
- Ensure the database schema remains unchanged

## Features
- RESTful API endpoints for adding, updating, retrieving, and searching plants
- Centralized validation and field specification logic
- Authentication and rate limiting for secure access
- Audit logging for all write operations
- Comprehensive documentation and example payloads
- Designed for easy deployment on render.com

## Architecture
- **/api/**: API endpoint code (controllers/routes)
- **/models/**: Database models/schema (copied from legacy project)
- **/utils/**: Validation, field specs, and helper functions
- **/tests/**: Unit and integration tests
- **/docs/**: Project and API documentation

## Setup Instructions
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd plant-database-api
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   - Set up database connection string and any required secrets in a `.env` file or via render.com dashboard.
4. **Run the server locally:**
   ```sh
   # Example for Flask
   flask run
   # Example for FastAPI
   uvicorn api.main:app --reload
   ```

## Deployment (Render.com)

1. **Set Environment Variables in Render Dashboard:**
   - `GARDENLLM_API_KEY`: Your API key for write operations.
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google credentials JSON file (upload as a secret file or set as an env var).
2. **Deploy the App:**
   - Use the following start command: `gunicorn 'api.main:create_app()'`
   - Ensure your requirements.txt includes all dependencies (Flask, Flask-Limiter, Flask-CORS, python-dotenv, etc.).
3. **Security Features:**
   - API key authentication for all write operations (POST/PUT)
   - Rate limiting (10 POST/PUT per minute per IP)
   - Audit logging to file and stdout
   - CORS enabled for all routes
   - HTTPS enforced by Render.com

## Local Development & Testing

- Use the app factory: `from api.main import create_app`
- For local dev: `app = create_app()`
- For testing: `app = create_app(testing=True)` (disables rate limiting)
- Run locally: `flask run` or `python -m api.main`
- Run tests: `pytest`

## Quickstart

1. Clone the repo and set up your virtual environment.
2. Create a `.env` file with your API key and credentials (do not commit this file).
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `flask run` or `gunicorn 'api.main:create_app()'`
5. Deploy to Render.com following the steps above.

## API Usage Basics
- All endpoints accept and return JSON
- Authentication is required for write operations (see `/docs/authentication.md`)
- Example endpoints:
  - `POST /api/plants` — Add a new plant
  - `PUT /api/plants/{id}` — Update an existing plant
  - `GET /api/plants/{id}` — Retrieve plant details
  - `GET /api/plants` — List/search plants
- See `/docs/api.md` for full endpoint documentation and example payloads

## ChatGPT Integration
- The API is designed for safe use by ChatGPT and other AI clients
- Structured command formats (JSON) are supported for add/update requests
- See `/docs/chatgpt_integration.md` for details on connecting and using the API with ChatGPT, including authentication and example requests

## Constraints
- **The plant database schema/model must remain unchanged**
- **All field specifications and validation logic are reused from the legacy project**
- **No direct database access from AI—only via the secure API layer**

## License
[Specify your license here]

## Contact
[Your name/contact info] 