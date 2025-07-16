# Plant Database API Documentation

## Overview

The Plant Database API provides secure access to a comprehensive plant database with full CRUD (Create, Read, Update, Delete) operations. The API is designed for both human developers and AI assistants (including ChatGPT integration).

**Base URL**: `https://your-app.onrender.com` (replace with actual deployment URL)

## Authentication

All write operations (POST, PUT) require API key authentication.

### API Key Header
```
x-api-key: your-api-key-here
```

### Obtaining an API Key
Contact the administrator to obtain your API key. Keep it secure and do not share it publicly.

## Rate Limiting

- **Read Operations (GET)**: No rate limiting
- **Write Operations (POST, PUT)**: 10 requests per minute per IP address
- **Storage**: Production-ready Redis-based rate limiting (with automatic fallback to in-memory storage)

## Field Reference

The plant database supports **17 fields** organized into categories:

### ChatGPT Field Compatibility

The API supports both standard field names and ChatGPT-compatible field names:

- **Standard format**: `"Plant Name"`, `"Light Requirements"`, etc.
- **ChatGPT format**: `"plant_name"`, `"Plant___Name"`, `"light_requirements"`, `"Light___Requirements"`, etc.

The API automatically converts ChatGPT's underscore formats to the correct field names, ensuring seamless integration.

### Basic Information
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ID` | string | No* | Unique identifier (auto-generated) |
| `Plant Name` | string | **Yes** | Name of the plant |
| `Description` | string | No | Plant description |
| `Location` | string | No | Location in garden (comma-separated for multiple) |

### Care Requirements
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Light Requirements` | string | No | Sunlight needs (e.g., "Full Sun", "Partial Shade") |
| `Frost Tolerance` | string | No | Cold hardiness information |
| `Watering Needs` | string | No | Watering frequency and requirements |
| `Soil Preferences` | string | No | Soil type and pH requirements |
| `Pruning Instructions` | string | No | When and how to prune |
| `Mulching Needs` | string | No | Mulching recommendations |
| `Fertilizing Schedule` | string | No | Fertilization timing and type |
| `Winterizing Instructions` | string | No | Winter care instructions |
| `Spacing Requirements` | string | No | Plant spacing recommendations |
| `Care Notes` | string | No | Additional care information |

### Media
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Photo URL` | string | No | Image URL (stored as IMAGE formula) |
| `Raw Photo URL` | string | No | Direct image URL |

### Metadata
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Last Updated` | string | No* | Timestamp (auto-generated) |

*Auto-generated fields should not be provided in requests

### Field Aliases

The API accepts multiple field name variations for convenience:

- **Plant Name**: `name`, `plant`, `plant name`
- **Description**: `desc`, `description`
- **Location**: `location`, `where`, `place`
- **Light Requirements**: `light`, `sun`, `sunlight`
- **Watering Needs**: `water`, `watering`
- **Photo URL**: `photo`, `image`, `picture`, `url`
- *(See full list in field_config.py)*

## API Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint**: `GET /`

**Authentication**: None required

**Response**:
```json
{
  "status": "ok",
  "message": "Plant Database API is running."
}
```

### 2. List Plants (Paginated)

Retrieve plants with pagination support. Returns 20 plants per page by default.

**Endpoint**: `GET /api/plants`

**Authentication**: None required

**Parameters**:
- `limit` (integer, optional): Maximum number of plants to return (default: 20)
- `offset` (integer, optional): Number of plants to skip (default: 0)
- `q` (string, optional): Search query to filter results

**Examples**:
- `GET /api/plants` - First 20 plants
- `GET /api/plants?limit=10&offset=20` - Plants 21-30
- `GET /api/plants?q=tomato&limit=5` - First 5 plants matching "tomato"

**Response**:
```json
{
  "plants": [
    {
      "ID": "1",
      "Plant Name": "Tomato",
      "Description": "Classic garden vegetable",
      "Location": "Vegetable Garden",
      "Light Requirements": "Full Sun",
      "Watering Needs": "Regular watering",
      "Last Updated": "2024-01-15 10:30:45"
    }
  ],
  "total": 150,
  "count": 20,
  "offset": 0,
  "limit": 20,
  "has_more": true,
  "remaining": 130,
  "pagination_info": {
    "message": "Showing 20 of 150 plants. 130 more plants available.",
    "next_page_instruction": "To get the next 20 plants, use: GET /api/plants?offset=20&limit=20",
    "get_all_instruction": "To get ALL remaining plants at once, use: GET /api/plants/all"
  }
}
```

### 2a. Get All Plants (No Pagination)

Retrieve ALL plants in the database without pagination limits. **Warning**: May return large amounts of data.

**Endpoint**: `GET /api/plants/all`

**Authentication**: None required

**Parameters**:
- `q` (string, optional): Search query to filter all results

**Examples**:
- `GET /api/plants/all` - All plants in database
- `GET /api/plants/all?q=herb` - All plants matching "herb"

**Response**:
```json
{
  "plants": [...],
  "total": 150,
  "count": 150,
  "warning": "This endpoint returns ALL plants. For large databases, consider using paginated /api/plants endpoint.",
  "pagination_alternative": "Use GET /api/plants?limit=20&offset=0 for paginated results"
}
```

### 3. Search Plants

Search for plants by name, description, or location. Supports pagination like the main list endpoint.

**Endpoint**: `GET /api/plants?q={query}`

**Authentication**: None required

**Parameters**:
- `q` (string): Search query
- `limit` (integer, optional): Maximum number of results (default: 20)
- `offset` (integer, optional): Number of results to skip (default: 0)

**Examples**: 
- `GET /api/plants?q=tomato` - First 20 plants matching "tomato"
- `GET /api/plants?q=herb&limit=5` - First 5 plants matching "herb"

**Response**: Same format as List Plants (Paginated), but with filtered results.

### 4. Get Plant by ID or Name

Retrieve a specific plant by its ID or name.

**Endpoint**: `GET /api/plants/{id_or_name}`

**Authentication**: None required

**Parameters**:
- `id_or_name` (string): Plant ID or exact name

**Example**: `GET /api/plants/1` or `GET /api/plants/Tomato`

**Response**:
```json
{
  "plant": {
    "ID": "1",
    "Plant Name": "Tomato",
    "Description": "Classic garden vegetable",
    "Location": "Vegetable Garden",
    "Light Requirements": "Full Sun",
    "Frost Tolerance": "Not frost tolerant",
    "Watering Needs": "Regular watering, keep soil moist",
    "Soil Preferences": "Well-draining, rich soil",
    "Pruning Instructions": "Remove suckers, prune lower leaves",
    "Mulching Needs": "2-3 inch layer around base",
    "Fertilizing Schedule": "Every 2-3 weeks during growing season",
    "Winterizing Instructions": "Harvest before first frost",
    "Spacing Requirements": "18-24 inches apart",
    "Care Notes": "Support with stakes or cages",
    "Photo URL": "=IMAGE(\"https://example.com/tomato.jpg\")",
    "Raw Photo URL": "https://example.com/tomato.jpg",
    "Last Updated": "2024-01-15 10:30:45"
  }
}
```

**Error Response (404)**:
```json
{
  "error": "Plant with ID or name 'nonexistent' not found."
}
```

### 5. Add New Plant

Add a new plant to the database.

**Endpoint**: `POST /api/plants`

**Authentication**: **Required** (`x-api-key` header)

**Request Body**:
```json
{
  "Plant Name": "Basil",
  "Description": "Aromatic herb perfect for cooking",
  "Location": "Herb Garden",
  "Light Requirements": "Full Sun to Partial Shade",
  "Watering Needs": "Keep soil consistently moist",
  "Soil Preferences": "Well-draining, fertile soil",
  "Photo URL": "https://example.com/basil.jpg"
}
```

**Minimal Request** (only Plant Name required):
```json
{
  "Plant Name": "Simple Plant"
}
```

**Success Response (201)**:
```json
{
  "message": "Added Basil to garden"
}
```

**Error Responses**:

*Missing Plant Name (400)*:
```json
{
  "error": "'Plant Name' is required."
}
```

*Invalid Field (400)*:
```json
{
  "error": "Invalid field(s): InvalidField"
}
```

*Unauthorized (401)*:
```json
{
  "error": "Unauthorized"
}
```

### 6. Update Plant

Update an existing plant by ID or name.

**Endpoint**: `PUT /api/plants/{id_or_name}`

**Authentication**: **Required** (`x-api-key` header)

**Request Body** (partial updates supported):
```json
{
  "Description": "Updated description",
  "Watering Needs": "Water twice weekly",
  "Photo URL": "https://example.com/new-photo.jpg"
}
```

**Success Response (200)**:
```json
{
  "message": "Updated Basil"
}
```

**Error Responses**:

*Plant Not Found (400)*:
```json
{
  "error": "Plant not found"
}
```

*No Valid Fields (400)*:
```json
{
  "error": "No valid fields to update."
}
```

## Special Field Handling

### Photo URLs
- **Photo URL**: Stored as Google Sheets IMAGE formula `=IMAGE("url")`
- **Raw Photo URL**: Stored as direct URL for API access
- When you provide a Photo URL, both fields are automatically populated

### Location Field
- Supports multiple locations: `"Front Yard, Back Garden, Patio"`
- Comma-separated values are automatically parsed for search

### Timestamps
- **Last Updated**: Automatically set on create/update operations
- Format: `YYYY-MM-DD HH:MM:SS`

## Error Handling

### HTTP Status Codes
- **200**: Success (GET, PUT)
- **201**: Created (POST)
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (missing/invalid API key)
- **404**: Not Found (plant doesn't exist)
- **429**: Too Many Requests (rate limit exceeded)

### Error Response Format
```json
{
  "error": "Description of the error"
}
```

## Examples for Different Use Cases

### Adding a Comprehensive Plant Entry
```bash
curl -X POST https://your-app.onrender.com/api/plants \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "Plant Name": "Japanese Maple",
    "Description": "Beautiful ornamental tree with stunning fall colors",
    "Location": "Front Yard",
    "Light Requirements": "Partial Shade to Full Sun",
    "Frost Tolerance": "Hardy to -15°C (zones 5-9)",
    "Watering Needs": "Regular watering, drought tolerant once established",
    "Soil Preferences": "Well-draining, slightly acidic soil",
    "Pruning Instructions": "Prune in late winter, remove dead branches",
    "Mulching Needs": "3-inch layer of organic mulch",
    "Fertilizing Schedule": "Feed in early spring with balanced fertilizer",
    "Winterizing Instructions": "Protect young trees from harsh winds",
    "Spacing Requirements": "Plant 6-8 feet apart",
    "Care Notes": "Avoid wet feet, provide wind protection",
    "Photo URL": "https://example.com/japanese-maple.jpg"
  }'
```

### Quick Plant Addition
```bash
curl -X POST https://your-app.onrender.com/api/plants \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "Plant Name": "Mint",
    "Location": "Herb Garden"
  }'
```

### Updating Plant Information
```bash
curl -X PUT https://your-app.onrender.com/api/plants/Mint \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "Description": "Fast-growing herb, can be invasive",
    "Watering Needs": "Keep soil moist, loves water",
    "Care Notes": "Contain in pots to prevent spreading"
  }'
```

### Searching for Plants
```bash
# Search by name
curl "https://your-app.onrender.com/api/plants?q=tomato"

# Search by location
curl "https://your-app.onrender.com/api/plants?q=herb%20garden"

# Search by description
curl "https://your-app.onrender.com/api/plants?q=aromatic"
```

## Data Validation

### Required Fields
- Only **Plant Name** is required
- All other fields are optional

### Field Validation
- Invalid field names are rejected with a 400 error
- Field aliases are automatically converted to canonical names
- Empty strings are allowed (will clear field values in updates)

### Input Sanitization
- JSON injection attempts are blocked
- Malformed JSON returns 400 error
- Large payloads are handled appropriately

## Security Features

### Authentication
- API key required for all write operations
- Keys are validated on every protected request

### Rate Limiting
- Write operations limited to 10 requests per minute
- Prevents abuse and protects backend services

### Audit Logging
- All write operations are logged with IP address and payload
- Logs stored in `api_audit.log` for monitoring

### CORS Support
- Cross-Origin Resource Sharing enabled for web applications
- Secure configuration for production deployment

## Monitoring and Logging

### Log Files
- **api_audit.log**: All write operations with full details
- Application logs include error tracking and performance metrics

### Health Monitoring
- Use `GET /` endpoint for health checks
- Response time and availability monitoring recommended

## Support and Troubleshooting

### Common Issues

**401 Unauthorized**
- Check that `x-api-key` header is included
- Verify API key is correct

**400 Bad Request**
- Ensure Plant Name is provided for new plants
- Check field names against supported fields
- Validate JSON syntax

**429 Too Many Requests**
- Reduce request frequency to under 10 per minute
- Implement exponential backoff in your client

### Getting Help
For technical support or API key requests, contact the system administrator.

---

*This documentation covers Plant Database API v1.0. Last updated: January 2024* 