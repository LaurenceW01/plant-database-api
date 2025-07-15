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

## Deployment (render.com)
- Follow the deployment instructions in `/docs/deployment.md` (to be created)
- Ensure environment variables are set in the render.com dashboard
- The API will be accessible at the public URL provided by render.com

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