# Plant Database API Documentation - Core Operations

## ✅ CORE API ENDPOINTS (ChatGPT Compatible)

**Status**: 27 essential endpoints operational - streamlined for ChatGPT's 30 operation limit.
All endpoints include AI-powered analysis, field normalization, and location intelligence.

---

## Quick Reference - All 27 Operations

### Plant Management (7 operations)
```javascript
POST   /api/plants/add              // ✅ Add new plant with upload token
POST   /api/plants/search           // ✅ Search plants (use JSON body: {"q": "vinca", "limit": 5})
GET    /api/plants/get/{id}         // ✅ Get specific plant details  
GET    /api/plants/get-all-fields/{id} // ✅ Get ALL plant fields from spreadsheet
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

### 🚀 Advanced Query System (1 operation)
```javascript
GET    /api/garden/filter                    // ✅ RELIABLE: Advanced plant filtering with query parameters
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

**Key Plant Fields**: plant_name (required), description, location, light_requirements, watering_needs, care_notes  
**Field Format**: API returns normalized lowercase_underscore format. Input accepts flexible formats for backward compatibility.

### Field Names for Log Operations  
Use these EXACT field names for best compatibility:
- **Required**: `plant_name`
- **Optional**: `log_title`, `diagnosis`, `treatment`, `symptoms`, `user_notes`, `follow_up_required`, `follow_up_date`

### Weather Integration Guidelines
- **ALWAYS check weather for**: Watering schedules, planting timing, outdoor activities
- **SKIP weather for**: Plant identification, indoor plants, general characteristics

### Photo Upload Process
1. Create plant/log entry first (gets upload token)
2. Provide upload URL to user 
3. User uploads photo independently
4. Token expires in 24 hours

---

## 🧪 POST Request Testing

### Simple POST Test Endpoint
**Use this to test if POST requests are working:**

```javascript
POST /api/test/simple-post
Content-Type: application/json

{
  "test_message": "Hello from GPT"
}

// Expected Response:
{
  "status": "success",
  "message": "POST request received successfully", 
  "timestamp": "2025-01-16T18:45:00.000Z",
  "received_data": {
    "test_message": "Hello from GPT"
  },
  "test_type": "simple_post_test",
  "version": "v2.4.0"
}
```

**Benefits:**
- ✅ Ultra-simple - accepts any JSON or empty body
- ✅ No complex validation or processing
- ✅ Clear success/failure indication
- ✅ Helps diagnose POST request issues

---

## Core API Examples

### 🚀 Advanced Query System - Garden Filter

**✅ CURRENT: Use `/api/garden/filter` for advanced plant filtering** (GET method - reliable)

**🔥 Key Benefits:**
- ✅ Reliable GET method like other working endpoints  
- ✅ Query parameter based (ChatGPT compatible)
- ✅ Advanced filtering capabilities
- ✅ No complex JSON body requirements

#### "Plants on Patio in Small Containers"
```javascript
GET /api/garden/filter?location=patio&container_size=small

// Simple, reliable filtering using query parameters
```

#### "Plants in Medium Containers"  
```javascript
GET /api/garden/filter?container_size=medium

// Filter by container size
```

#### "Plants by Container Material"
```javascript
GET /api/garden/filter?container_material=plastic

// Filter by container material (plastic, ceramic, terracotta, etc.)
```

#### "Plants by Specific Plant Name"
```javascript
GET /api/garden/filter?plant_name=vinca

// Filter by plant name
```

#### Multiple Filters Combined
```javascript
GET /api/garden/filter?location=patio&container_material=ceramic&container_size=large

// Combine multiple filters for precise results
```

#### NEW Hierarchical Response Format ✨
**🎉 IMPROVED 2025**: Clear plant → locations → containers structure

```javascript
{
  "count": 9,
  "total_matches": 9,
  "debug_signature": "GET-FILTER-HIERARCHICAL-2025",
  "filters_applied": {
    "containers": {"container_size": {"$eq": "small"}},
    "locations": {"location_name": {"$regex": "patio"}}
  },
  "plants": [
    {
      "plant_name": "Rose",
      "plant_id": "2", 
      "locations": [
        {
          "location_name": "patio",
          "location_id": "25",
          "containers": [
            {
              "container_id": "22",
              "container_type": "Pot",
              "container_size": "small",
              "container_material": "ceramic"
            }
          ]
        }
      ]
    },
    {
      "plant_name": "African Daisy",
      "plant_id": "15",
      "locations": [
        {
          "location_name": "patio", 
          "location_id": "25",
          "containers": [
            {
              "container_id": "63",
              "container_type": "Pot",
              "container_size": "Small",
              "container_material": "Ceramic"
            }
          ]
        }
      ]
    }
    // ... 7 more plants on patio in small containers
  ]
}
```

**Key Benefits:**
- ✅ **No Misleading Data**: Each plant clearly shows ALL locations where it exists
- ✅ **Complete Info**: Location names resolved, no ID lookups needed
- ✅ **Clear Structure**: Easy to understand plant distribution across garden
- ✅ **GPT-Ready**: No inference required, all information is explicit

### Add Plant with Location Context
```javascript
POST /api/plants/add
Content-Type: application/json

{
  "plant_name": "Basil",
  "Location": "Herb Garden",
  "light_requirements": "Full Sun",
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
  "Watering___Needs": "Water when dry",
  "Soil___pH___Type": "neutral to slightly acidic",  // pH fields supported
  "Soil___pH___Range": "6.0 - 7.0"
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
  "plant_name": "Tomato Plant #1",
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

## NEW: Complete Plant Field Retrieval

### GET /api/plants/get-all-fields/{id}
**Purpose**: Retrieve ALL available fields from the plant spreadsheet for comprehensive plant data analysis.

**Key Features**:
- Returns complete plant object with all spreadsheet fields (ID, Plant Name, Description, Location, Light Requirements, Watering Needs, Soil Preferences, Frost Tolerance, etc.)
- Supports both plant IDs (e.g., "1") and plant names (e.g., "Vinca")
- Includes metadata about field counts and completeness
- Perfect for comprehensive plant analysis and data export

**Usage Examples**:
```javascript
// Get all fields by plant ID
GET /api/plants/get-all-fields/1

// Get all fields by plant name
GET /api/plants/get-all-fields/Vinca

// Response includes complete plant data:
{
  "success": true,
  "plant": {
    "ID": "1",
    "plant_name": "Vinca",
    "Description": "Flowering annual",
    "Location": "Front patio",
    "light_requirements": "Full sun",
    "Watering Needs": "Daily",
    "Soil Preferences": "Well-draining",
    "Frost Tolerance": "None",
    "Fertilizing Schedule": "Monthly",
    // ... all other fields
  },
  "metadata": {
    "total_fields": 20,
    "non_empty_fields": 15,
    "field_names": ["ID", "Plant Name", "Description", ...]
  }
}
```

**When to Use**:
- Need complete plant data for analysis
- Exporting plant information
- Comprehensive plant reports
- Detailed care planning

**Difference from /api/plants/get/{id}**:
- `get/{id}`: Returns basic plant info (subset of fields)
- `get-all-fields/{id}`: Returns ALL available spreadsheet fields + metadata

---

## Important Notes

🔴 **ChatGPT Limitations**: This schema contains exactly 25 operations (under the 30 limit)
🔴 **Field Compatibility**: Field names are flexible - use any format (spaces, underscores, camelCase)
🔴 **Token Expiration**: All upload tokens expire in 24 hours
🔴 **Location Intelligence**: Use context endpoints for precise, location-aware advice
🔴 **Error Handling**: All endpoints provide comprehensive error messages with guidance

For detailed workflow guides and advanced patterns, see:
- `LOCATION_AWARE_WORKFLOW_GUIDE.md` - Step-by-step care workflows
- `PHASE2_ADVANCED_INTELLIGENCE.md` - Advanced garden intelligence features
- `QUERY_PATTERNS_AND_EXAMPLES.md` - Response templates and examples