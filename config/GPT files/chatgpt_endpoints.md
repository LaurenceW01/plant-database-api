# Plant Database API Documentation - Core Operations

## ✅ CORE API ENDPOINTS (ChatGPT Compatible)

**Status**: 24 essential endpoints operational - streamlined for ChatGPT's 30 operation limit.
All endpoints include AI-powered analysis, field normalization, and location intelligence.

---

## Quick Reference - All 24 Operations

### Plant Management (6 operations)
```javascript
POST   /api/plants/add              // ✅ Add new plant with upload token
POST   /api/plants/search           // ✅ Search plants (use JSON body: {"q": "vinca", "limit": 5})
GET    /api/plants/get/{id}         // ✅ Get specific plant details  
PUT    /api/plants/update/{id}      // ✅ Update plant with ID in URL path
PUT    /api/plants/update           // ✅ Update plant with ID in request body (ChatGPT-friendly)
POST   /api/plants/get-context/{plant_id} // ✅ Get plant context (supports IDs and names)
GET    /api/plants/by-location/{location_name} // ✅ Get plants by location (supports IDs and names)
```

**✅ CORRECT: Plant Search Method**
```javascript
// ✅ CORRECT: Use POST with JSON body
POST /api/plants/search
Content-Type: application/json
{"q": "vinca", "limit": 5}

// ✅ NEW: Get plant names only for AI analysis (e.g., toxicity reports)
POST /api/plants/search
Content-Type: application/json
{"names_only": true}

// ✅ COMBINED: Search with names only
POST /api/plants/search
Content-Type: application/json
{"q": "herb", "names_only": true, "limit": 10}

// Also supported: POST with query parameters
POST /api/plants/search?q=vinca&limit=5&names_only=true
```

**For ChatGPT:** The `searchPlants` operation uses POST method with JSON body, which is the natural behavior for OpenAPI clients. Send parameters in the request body as JSON.

**NEW: Names Only Parameter** - Use `names_only: true` to get just plant names as strings instead of full plant objects. Perfect for AI analysis tasks like toxicity reports, pest identification, or plant compatibility analysis.

### AI-Powered Analysis (2 operations)
```javascript
POST   /api/plants/diagnose         // ✅ AI plant diagnosis with location intelligence
POST   /api/plants/enhance-analysis // ✅ Enhanced analysis with database knowledge
```

### Health Logging (3 operations)
```javascript  
POST   /api/logs/create             // ✅ Create plant log with upload token
POST   /api/logs/create-simple      // ✅ Create simple log with field normalization  
GET    /api/logs/search             // ✅ Search logs with comprehensive results
```

### Photo Upload (2 operations)
```javascript
POST   /api/photos/upload-for-plant/{token}  // ✅ Upload photo for plant
POST   /api/photos/upload-for-log/{token}    // ✅ Upload photo for log entry
```

### Location Intelligence (8 operations)
```javascript
GET    /api/locations/get-context/{id}       // ✅ Get location context (supports IDs and names)
GET    /api/garden/get-metadata              // ✅ Get garden metadata
GET    /api/garden/optimize-care             // ✅ Get care optimization
GET    /api/plants/{plant_id}/location-context  // ✅ Legacy plant location context
GET    /api/locations/{location_id}/care-profile  // ✅ Location care profile (supports IDs and names)
GET    /api/locations/all                    // ✅ All locations
GET    /api/garden/metadata/enhanced         // ✅ Enhanced garden metadata
GET    /api/garden/care-optimization         // ✅ Care optimization analysis (FIXED: proper container-location linkage)
```

### Weather Integration (3 operations)
```javascript
GET    /api/weather/current           // ✅ Current weather conditions
GET    /api/weather/forecast          // ✅ Hourly weather forecast  
GET    /api/weather/forecast/daily    // ✅ Daily weather forecast (supports both query params and JSON body)
```

---

## Key Features

✅ **Advanced Field Normalization**: Comprehensive automatic field name conversion
- Handles ANY ChatGPT underscore pattern: `Care___Notes`, `Light___Requirements`, etc.
- Supports 66+ field aliases from centralized configuration  
- Context-aware ID mapping: `id` → `plant_id` for plant operations
- Future-proof: new fields automatically supported

✅ **AI-Powered Analysis**: Full OpenAI integration with location intelligence  
✅ **Photo Upload**: Secure token-based system with 24-hour expiration
✅ **Location Intelligence**: Container and microclimate context for precise care advice
✅ **Error Handling**: Comprehensive validation and user-friendly messages

---

## Essential Usage Guidelines

### Field Names - Flexible & Forgiving
The API now accepts **ANY** reasonable field name variation:
- **Standard**: `Plant Name`, `Care Notes`, `Light Requirements`
- **ChatGPT Patterns**: `Plant___Name`, `Care___Notes`, `Light___Requirements`  
- **Underscore**: `plant_name`, `care_notes`, `light_requirements`
- **CamelCase**: `plantName`, `careNotes`, `lightRequirements`
- **Aliases**: `name`, `notes`, `light`, `water`

**Key Plant Fields**: Plant Name (required), Description, Location, Light Requirements, Watering Needs, Care Notes  
**Field Format**: Flexible - use spaces, underscores, or camelCase (e.g., `Light Requirements`, `light_requirements`, `Light___Requirements`)

### Field Names for Log Operations  
Use these EXACT field names for best compatibility:
- **Required**: `Plant Name`
- **Optional**: `Log Title`, `Diagnosis`, `Treatment`, `Symptoms`, `User Notes`, `Follow-up Required`, `Follow-up Date`

### Weather Integration Guidelines
- **ALWAYS check weather for**: Watering schedules, planting timing, outdoor activities
- **SKIP weather for**: Plant identification, indoor plants, general characteristics

### Photo Upload Process
1. Create plant/log entry first (gets upload token)
2. Provide upload URL to user 
3. User uploads photo independently
4. Token expires in 24 hours

---

## Core API Examples

### Add Plant with Location Context
```javascript
POST /api/plants/add
Content-Type: application/json

{
  "Plant Name": "Basil",
  "Location": "Herb Garden",
  "Light Requirements": "Full Sun",
  "Watering Needs": "Water daily",
  "Care Notes": "Harvest regularly"
}

// Response includes upload_url for photo
{
  "success": true,
  "message": "Added Basil to garden",
  "plant_id": "42",
  "upload_url": "https://dev-plant-database-api.onrender.com/upload/plant/abc123",
  "upload_instructions": "To add a photo, visit: [upload_url]"
}
```

### Update Plant (Flexible Format)
```javascript
// OPTION 1: ID in URL path (standard)
PUT /api/plants/update/Basil
Content-Type: application/json

{
  "Care Notes": "Updated care instructions",
  "Watering Needs": "Water when dry"
}

// OPTION 2: ID in request body (ChatGPT-friendly) 
PUT /api/plants/update
Content-Type: application/json

{
  "id": "Basil",
  "Care___Notes": "Updated care instructions",  // Any underscore pattern works
  "Watering___Needs": "Water when dry"
}

// Both return the same response
{
  "success": true,
  "message": "Updated Basil",
  "endpoint_type": "flexible_update"  // Only for Option 2
}
```

### AI-Powered Plant Diagnosis
```javascript
POST /api/plants/diagnose
Content-Type: application/json

{
  "plant_name": "Rose",
  "user_notes": "Plant has yellow leaves and brown spots",
  "location": "Garden bed 2",
  "analysis_type": "general_care"
}

// Response with AI analysis
{
  "success": true,
  "analysis": {
    "plant_name": "Rose",
    "ai_analysis": "Based on your description...[full AI response]",
    "enhanced_with_location": true,
    "location": "Garden bed 2"
  }
}
```

### Enhanced Analysis with Database Knowledge
```javascript
POST /api/plants/enhance-analysis
Content-Type: application/json

{
  "gpt_analysis": "This rose shows signs of yellowing leaves...",
  "plant_identification": "Rose",
  "location": "Houston",
  "analysis_type": "health_assessment"
}

// Response with enhanced context
{
  "success": true,
  "enhanced_analysis": {
    "plant_match": {
      "found_in_database": false,
      "original_identification": "Rose"
    },
    "care_enhancement": {
      "ai_analysis": "[Enhanced analysis with location context]"
    },
    "diagnosis_enhancement": {
      "urgency_level": "monitor",
      "treatment_recommendations": "Follow AI analysis recommendations"
    }
  }
}
```

### Plant Context with Location Intelligence
```javascript
// Method 1: Using plant ID
GET /api/plants/get-context/1

// Method 2: Using plant name (ChatGPT-friendly)
GET /api/plants/get-context/Vinca

// Both methods return the same response format with container and location context
{
  "plant_id": "134",
  "contexts": [
    {
      "container": {
        "container_id": "107",
        "container_type": "Pot buried in ground",
        "container_size": "small",
        "container_material": "plastic"
      },
      "location": {
        "location_name": "middle ",
        "total_sun_hours": 12,
        "shade_pattern": "Full Sun"
      },
      "context": {
        "placement_description": "Pot buried in ground (small, plastic) in middle ",
        "sun_exposure_summary": "12 total hours (Full Sun)",
        "priority_considerations": [
          "Morning watering preferred to prevent root heating",
          "Daily watering checks during hot weather",
          "Frequent moisture monitoring due to small container size"
        ]
      }
    }
  ],
  "total_contexts": 1,
  "phase2_direct": true
}
```

### Create Health Log with Photo Upload
```javascript
POST /api/logs/create
Content-Type: application/json

{
  "Plant Name": "Tomato Plant #1",
  "Log Title": "Weekly Health Check",
  "Diagnosis": "Minor nitrogen deficiency", 
  "Treatment": "Apply balanced fertilizer",
  "Symptoms": "Yellow leaf edges",
  "Follow-up Required": true,
  "Follow-up Date": "2024-01-22"
}

// Response includes upload token
{
  "success": true,
  "log_id": "LOG-20240115-001",
  "upload_url": "https://dev-plant-database-api.onrender.com/upload/log/xyz789",
  "upload_instructions": "To add a photo to this log entry, visit: [upload_url]"
}
```

### Weather Integration
```javascript
GET /api/weather/current

// Current conditions for Houston
{
  "temperature": 75.5,
  "humidity": 65,
  "wind_speed": 8,
  "description": "Partly cloudy",
  "precipitation_chance": 30
}

// Daily forecast - Method 1: Query parameters
GET /api/weather/forecast/daily?days=7

// Daily forecast - Method 2: JSON body (ChatGPT-friendly)
POST /api/weather/forecast/daily
Content-Type: application/json
{
  "days": 7
}

// Both methods return the same response:
{
  "forecast": [
    {
      "date": "2024-01-21",
      "high_temp": 85,
      "low_temp": 65,
      "precipitation_chance": 30,
      "description": "Partly Cloudy"
    }
    // ... up to 7 days
  ]
}
```

---

## Response Integration Examples

### Weather-Integrated Plant Care
```javascript
// Good example combining weather with location intelligence:
"Given your hibiscus in arboretum right (6 hours afternoon sun, plastic container) 
and today's forecast of 92°F with high humidity, water very early morning 
(5:30-7:00 AM) to prevent heat stress. The plastic container will heat up quickly 
in that evening sun location."

// Bad example (generic advice):
"Current weather: 92°F, humid. Water tomatoes early."
```

### Photo Upload Instructions
```javascript
// Good example:
"I've added your Japanese Maple to the database. To add a photo, visit this link: 
[upload_url]. The link will expire in 24 hours."
```

---

## Important Notes

🔴 **ChatGPT Limitations**: This schema contains exactly 24 operations (under the 30 limit)
🔴 **Field Compatibility**: Field names are flexible - use any format (spaces, underscores, camelCase)
🔴 **Token Expiration**: All upload tokens expire in 24 hours
🔴 **Location Intelligence**: Use context endpoints for precise, location-aware advice
🔴 **Error Handling**: All endpoints provide comprehensive error messages with guidance

For detailed workflow guides and advanced patterns, see:
- `LOCATION_AWARE_WORKFLOW_GUIDE.md` - Step-by-step care workflows
- `PHASE2_ADVANCED_INTELLIGENCE.md` - Advanced garden intelligence features
- `QUERY_PATTERNS_AND_EXAMPLES.md` - Response templates and examples