# Plant Database API

## Overview
A production-ready Plant Database API with full ChatGPT integration, deployed on render.com. This API provides secure access to a comprehensive plant database with advanced features including intelligent pagination, field name compatibility, and Redis-based rate limiting.

**🌐 Live API**: [https://plant-database-api.onrender.com](https://plant-database-api.onrender.com)

## ✅ Current Status (January 2025)

**✅ Phase 7 Complete**: ChatGPT Integration fully operational
- ✅ ChatGPT field name mapping (handles all underscore formats)
- ✅ Enhanced pagination with guidance for large datasets  
- ✅ Production-ready Redis rate limiting
- ✅ Modern dependency stack (removed deprecated packages)
- ✅ Comprehensive API documentation and OpenAPI schema

## 🚀 Key Features

### Core Functionality
- **17 Plant Fields**: Complete plant data management (basic info, growing conditions, care instructions, media)
- **CRUD Operations**: Full Create, Read, Update, Delete functionality
- **Advanced Search**: Query by name, description, location with pagination
- **Field Validation**: Centralized validation logic ensuring data integrity

### ChatGPT Integration
- **Field Name Compatibility**: Supports standard (`Plant Name`), underscore (`plant_name`), and triple underscore (`Plant___Name`) formats
- **Intelligent Pagination**: API provides guidance when datasets exceed 20 plants
- **Complete Dataset Access**: `/api/plants/all` endpoint for full data retrieval
- **Error Handling**: Automatic field name conversion prevents "connector errors"

### Production Features  
- **Redis Rate Limiting**: Persistent, scalable rate limiting (10 writes/minute)
- **API Key Authentication**: Secure write operations with audit logging
- **Auto-Fallback**: Graceful degradation to in-memory storage if Redis unavailable
- **CORS Enabled**: Cross-origin support for web applications
- **Health Monitoring**: Comprehensive logging and error tracking

## Architecture
- **/api/**: API endpoint code (controllers/routes)
- **/models/**: Database models/schema (copied from legacy project)
- **/utils/**: Validation, field specs, and helper functions
- **/tests/**: Unit and integration tests
- **/docs/**: Project and API documentation

## 🛠️ Technical Stack

- **Framework**: Flask 3.1.1 with Gunicorn
- **Database**: Google Sheets API integration
- **Rate Limiting**: Redis 5.2.1 (with in-memory fallback)
- **Authentication**: API key-based with audit logging
- **Deployment**: Render.com with automatic GitHub integration
- **Testing**: pytest with comprehensive test suite
- **Documentation**: OpenAPI 3.1.0 schema for ChatGPT Actions

## 📚 API Documentation

### Quick Start
```bash
# Health check
GET https://plant-database-api.onrender.com/

# List plants (paginated)
GET https://plant-database-api.onrender.com/api/plants

# Get all plants
GET https://plant-database-api.onrender.com/api/plants/all

# Search plants
GET https://plant-database-api.onrender.com/api/plants?q=tomato
```

### Authentication
Write operations require API key in header:
```
x-api-key: your-api-key-here
```

### Field Formats Supported
```json
// Standard format
{"Plant Name": "Basil", "Light Requirements": "Full Sun"}

// ChatGPT underscore format  
{"plant_name": "Basil", "light_requirements": "Full Sun"}

// ChatGPT triple underscore format
{"Plant___Name": "Basil", "Light___Requirements": "Full Sun"}
```

## 🚀 Deployment Guide

### Environment Variables
```bash
# Required
GARDENLLM_API_KEY=your_api_key
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
SPREADSHEET_ID=your_spreadsheet_id

# Production (recommended)
REDIS_URL=redis://your_redis_url:6379
```

### Render.com Setup
1. **Web Service**: Deploy from GitHub repository
2. **Redis Service**: Create "Key Value" service for rate limiting
3. **Environment Variables**: Configure in Render dashboard
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn "api.main:create_app()"`

## 🧪 Development & Testing

### Local Setup
```bash
git clone https://github.com/your-username/plant-database-api.git
cd plant-database-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python api/main.py
```

### Testing
```bash
# Run all tests
pytest

# Run safe tests (no API calls)
python run_safe_tests.py

# Test specific functionality
pytest tests/test_api.py
```

## 🔗 API Endpoints

### Core Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | Health check | ❌ |
| `GET` | `/api/plants` | List plants (paginated) | ❌ |
| `GET` | `/api/plants/all` | Get all plants | ❌ |
| `GET` | `/api/plants/{id}` | Get specific plant | ❌ |
| `POST` | `/api/plants` | Add new plant | ✅ |
| `PUT` | `/api/plants/{id}` | Update plant | ✅ |

### Pagination Features
- **Default**: 20 plants per page
- **Guidance**: API provides instructions for accessing more data
- **Flexible**: Support for `limit` and `offset` parameters
- **ChatGPT Optimized**: Clear instructions in API responses

## 🤖 ChatGPT Integration

### OpenAPI Schema
- **URL**: `https://plant-database-api.onrender.com/` 
- **Schema**: Available in `chatgpt_compatible_schema.yaml`
- **Authentication**: API Key (Custom Header: `x-api-key`)
- **Privacy Policy**: `https://plant-database-api.onrender.com/privacy`

### Setup Instructions
1. **ChatGPT Actions**: Import the OpenAPI schema
2. **Authentication**: Configure API key in custom header
3. **Test**: Try adding a plant with comprehensive details

### Field Compatibility
The API automatically handles ChatGPT's field name transformations:
- ✅ `"Plant Name"` → Works
- ✅ `"plant_name"` → Converts to "Plant Name" 
- ✅ `"Plant___Name"` → Converts to "Plant Name"

## 📖 Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete endpoint reference
- **[ChatGPT Integration](docs/CHATGPT_INTEGRATION.md)**: AI-specific setup guide  
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Render.com deployment instructions
- **[Production Setup](docs/PRODUCTION_SETUP.md)**: Redis and environment configuration

## 🛡️ Security & Compliance

- **Rate Limiting**: 10 write operations per minute (Redis-backed)
- **Authentication**: API key validation for all write operations
- **Audit Logging**: All operations logged with IP and payload
- **HTTPS**: Enforced by Render.com
- **CORS**: Configured for cross-origin requests
- **Privacy Policy**: GDPR-compliant privacy policy included

## 📈 Current Metrics

- **Deployment**: render.com (production)
- **Uptime**: 99.9% target
- **Response Time**: <200ms average  
- **Rate Limit**: 10 writes/minute per IP
- **Storage**: Google Sheets backend with Redis caching

## 🎯 Project Status

**✅ Complete**: All phases of the migration plan finished
- ✅ Phase 1: Project Initialization  
- ✅ Phase 2: Codebase Migration
- ✅ Phase 3: API Implementation
- ✅ Phase 4: Security & Access Control
- ✅ Phase 5: Testing & QA
- ✅ Phase 6: Documentation & Deployment  
- ✅ Phase 7: ChatGPT Integration

**🚀 Ready for Production Use** 