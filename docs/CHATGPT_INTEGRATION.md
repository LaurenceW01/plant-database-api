# ChatGPT & AI Integration Guide

## Overview

This guide provides specific instructions for integrating the Plant Database API with ChatGPT and other AI assistants. The API is designed to be AI-friendly with clear, structured endpoints and comprehensive field support.

## Recent Updates (January 2025)

✅ **Field Name Compatibility Fixed**: API now handles ChatGPT's field name formats (both `plant_name` and `Plant___Name`)  
✅ **Enhanced Pagination**: Intelligent pagination with guidance for accessing large datasets  
✅ **Production-Ready**: Redis-based rate limiting and improved error handling  
✅ **Dependency Modernization**: Updated to latest Python standards with `zoneinfo`

## Quick Start for AI Assistants

### Base Configuration
- **API Base URL**: `https://your-app.onrender.com`
- **Authentication**: API key in `x-api-key` header for write operations
- **Data Format**: JSON request/response
- **Rate Limit**: 10 write operations per minute

### Core Capabilities
✅ **Add plants** with comprehensive field data  
✅ **Update plants** with partial field updates  
✅ **Search plants** by name, description, or location  
✅ **Retrieve plant details** by ID or name  
✅ **Handle all 17 plant fields** including care instructions and photos  

## AI-Optimized Endpoints

### 1. Get Plant Information
**Pattern**: `GET /api/plants/{plant_name}`

**AI Use Cases**:
- User asks: "Tell me about my tomato plant"
- User asks: "What are the care instructions for roses?"

**Example Request**:
```
GET /api/plants/Tomato
```

**Expected Response**:
```json
{
  "plant": {
    "Plant Name": "Tomato",
    "Description": "Classic garden vegetable",
    "Light Requirements": "Full Sun",
    "Watering Needs": "Regular watering, keep soil moist",
    "Fertilizing Schedule": "Every 2-3 weeks during growing season",
    "Care Notes": "Support with stakes or cages"
  }
}
```

### 2. Add Plant (AI-Friendly Format)
**Pattern**: `POST /api/plants`
**Headers**: `x-api-key: {api_key}`

**AI Use Cases**:
- User says: "Add a new basil plant to my herb garden"
- User provides: "I planted Japanese Maple in the front yard, it needs partial shade"

**Minimal Addition**:
```json
{
  "Plant Name": "Basil",
  "Location": "Herb Garden"
}
```

**Comprehensive Addition** (when user provides details):
```json
{
  "Plant Name": "Japanese Maple",
  "Description": "Ornamental tree with stunning fall colors",
  "Location": "Front Yard",
  "Light Requirements": "Partial Shade to Full Sun",
  "Watering Needs": "Regular watering when young, drought tolerant once established",
  "Soil Preferences": "Well-draining, slightly acidic soil",
  "Care Notes": "Provide wind protection, avoid overwatering"
}
```

### 3. Update Plant Information
**Pattern**: `PUT /api/plants/{plant_name}`
**Headers**: `x-api-key: {api_key}`

**AI Use Cases**:
- User says: "Update my tomato plant's watering schedule"
- User provides: "The roses need pruning instructions updated"

**Example Request**:
```json
{
  "Watering Needs": "Water deeply twice per week",
  "Care Notes": "Mulch heavily during summer heat"
}
```

### 4. Search Plants
**Pattern**: `GET /api/plants?q={search_term}`

**AI Use Cases**:
- User asks: "What plants are in my vegetable garden?"
- User asks: "Show me all my herbs"

**Examples**:
```
GET /api/plants?q=vegetable garden
GET /api/plants?q=herbs
GET /api/plants?q=full sun
```

### 5. Handling Large Datasets (Pagination)

When there are many plants, the API provides intelligent pagination with guidance:

**Default Behavior**: Returns 20 plants per page with guidance for accessing more.

**Standard Paginated Request**:
```
GET /api/plants
```

**Response with Pagination Guidance**:
```json
{
  "plants": [...],
  "total": 150,
  "count": 20,
  "has_more": true,
  "remaining": 130,
  "pagination_info": {
    "message": "Showing 20 of 150 plants. 130 more plants available.",
    "next_page_instruction": "To get the next 20 plants, use: GET /api/plants?offset=20&limit=20",
    "get_all_instruction": "To get ALL remaining plants at once, use: GET /api/plants/all"
  }
}
```

**Getting All Plants (No Pagination)**:
```
GET /api/plants/all
```

**ChatGPT Best Practices**:
- Start with standard endpoint: `GET /api/plants`
- Check `has_more` field in response
- Follow `pagination_info` instructions for accessing more data
- Use `/api/plants/all` only when you need the complete dataset

## Field Mapping for AI

### Field Name Compatibility

The API supports multiple field name formats for maximum ChatGPT compatibility:

**✅ Standard Format** (preferred):
```json
{
  "Plant Name": "Basil",
  "Light Requirements": "Full Sun",
  "Watering Needs": "Regular watering"
}
```

**✅ Single Underscore Format** (ChatGPT compatible):
```json
{
  "plant_name": "Basil",
  "light_requirements": "Full Sun", 
  "watering_needs": "Regular watering"
}
```

**✅ Triple Underscore Format** (ChatGPT OpenAPI parser):
```json
{
  "Plant___Name": "Basil",
  "Light___Requirements": "Full Sun",
  "Watering___Needs": "Regular watering"
}
```

**✅ Mixed Format** (also supported):
```json
{
  "plant_name": "Basil",
  "Light___Requirements": "Full Sun",
  "Watering Needs": "Regular watering"
}
```

**Important**: The API automatically converts all formats to the canonical field names, so ChatGPT can use any format without errors.

### Required vs Optional Fields
- **REQUIRED**: `Plant Name` (only this field is mandatory)
- **OPTIONAL**: All other 16 fields can be omitted or added later

### Field Categories for AI Context

**Basic Plant Info**:
```json
{
  "Plant Name": "string (REQUIRED)",
  "Description": "string",
  "Location": "string (e.g., 'Front Yard, Herb Garden')"
}
```

**Growing Conditions**:
```json
{
  "Light Requirements": "string (e.g., 'Full Sun', 'Partial Shade')",
  "Soil Preferences": "string (e.g., 'Well-draining, fertile soil')",
  "Frost Tolerance": "string (e.g., 'Hardy to -10°C')",
  "Spacing Requirements": "string (e.g., '18-24 inches apart')"
}
```

**Care Instructions**:
```json
{
  "Watering Needs": "string",
  "Fertilizing Schedule": "string",
  "Pruning Instructions": "string",
  "Mulching Needs": "string",
  "Winterizing Instructions": "string",
  "Care Notes": "string (general care tips)"
}
```

**Media**:
```json
{
  "Photo URL": "string (image URL)",
  "Raw Photo URL": "string (auto-populated)"
}
```

### AI Field Name Flexibility
The API accepts natural language field names:

**Instead of formal names, AIs can use**:
- `name` → `Plant Name`
- `light` → `Light Requirements`  
- `water` → `Watering Needs`
- `soil` → `Soil Preferences`
- `notes` → `Care Notes`
- `photo` → `Photo URL`

## Common AI Conversation Patterns

### Pattern 1: Adding a New Plant
**User**: "I just planted some lavender in my herb garden"

**AI Action**:
```http
POST /api/plants
x-api-key: {api_key}
Content-Type: application/json

{
  "Plant Name": "Lavender",
  "Location": "Herb Garden"
}
```

### Pattern 2: Adding Plant with Care Details
**User**: "Add a tomato plant to my vegetable garden. It needs full sun, regular watering, and I should fertilize it every 2-3 weeks."

**AI Action**:
```http
POST /api/plants
x-api-key: {api_key}
Content-Type: application/json

{
  "Plant Name": "Tomato",
  "Location": "Vegetable Garden",
  "Light Requirements": "Full Sun",
  "Watering Needs": "Regular watering",
  "Fertilizing Schedule": "Every 2-3 weeks"
}
```

### Pattern 3: Updating Plant Care
**User**: "My roses need to be watered less frequently now that it's fall"

**AI Action**:
1. Find the plant: `GET /api/plants/Roses`
2. Update watering: 
```http
PUT /api/plants/Roses
x-api-key: {api_key}
Content-Type: application/json

{
  "Watering Needs": "Reduce watering frequency in fall, water when soil is dry"
}
```

### Pattern 4: Getting Plant Information
**User**: "What are the care instructions for my Japanese Maple?"

**AI Action**:
```http
GET /api/plants/Japanese Maple
```

**AI Response**: Summarize the returned care fields in natural language.

### Pattern 5: Location-Based Queries
**User**: "What plants are in my herb garden?"

**AI Action**:
```http
GET /api/plants?q=herb garden
```

## Error Handling for AI

### Common Error Scenarios

**Missing API Key**:
```json
{
  "error": "Unauthorized"
}
```
**AI Response**: "I need authentication to add or update plants. Please provide your API key."

**Plant Not Found**:
```json
{
  "error": "Plant with ID or name 'NonExistent' not found."
}
```
**AI Response**: "I couldn't find a plant with that name. Would you like me to add it as a new plant?"

**Invalid Field**:
```json
{
  "error": "Invalid field(s): WrongField"
}
```
**AI Response**: "I tried to use an unsupported field name. Let me correct that."

**Rate Limit Exceeded**:
```json
{
  "error": "Too Many Requests"
}
```
**AI Response**: "I've made too many requests recently. Let me wait a moment before trying again."

## Best Practices for AI Integration

### 1. Field Population Strategy
- **Always include Plant Name** (required)
- **Include Location** when mentioned by user
- **Add care details** when user provides specific information
- **Use comprehensive fields** when user gives detailed instructions

### 2. User-Friendly Responses
After successful plant addition:
```
✅ "I've added [Plant Name] to your [Location]. I've recorded the care information you provided."
```

After plant updates:
```
✅ "I've updated the care instructions for your [Plant Name]."
```

### 3. Proactive Information Gathering
If user mentions a plant without location:
```
"I can add [Plant Name] to your garden. Which area would you like to plant it in?"
```

### 4. Handling Ambiguous Plant Names
If multiple plants match a search:
```
"I found several plants with that name. Could you be more specific, or should I show you all of them?"
```

## Advanced AI Features

### 1. Batch Operations
For multiple plants, make separate API calls:
```javascript
// User: "Add tomatoes, peppers, and basil to my vegetable garden"
for (const plant of ["Tomatoes", "Peppers", "Basil"]) {
  await addPlant({
    "Plant Name": plant,
    "Location": "Vegetable Garden"
  });
}
```

### 2. Smart Field Inference
Extract care information from natural language:
```
User: "My new rose bush needs morning sun and weekly deep watering"

Inferred Fields:
{
  "Plant Name": "Rose Bush",
  "Light Requirements": "Morning sun",
  "Watering Needs": "Weekly deep watering"
}
```

### 3. Contextual Updates
Reference previous conversations:
```
User: "Actually, update that rose to need daily watering"

AI should remember the previously mentioned rose and update it.
```

## Integration Examples

### OpenAI Function Calling
```json
{
  "name": "add_plant",
  "description": "Add a new plant to the garden database",
  "parameters": {
    "type": "object",
    "properties": {
      "plant_name": {"type": "string", "description": "Name of the plant (required)"},
      "location": {"type": "string", "description": "Where the plant is located"},
      "light_requirements": {"type": "string", "description": "Light needs (Full Sun, Partial Shade, etc.)"},
      "watering_needs": {"type": "string", "description": "Watering requirements"},
      "care_notes": {"type": "string", "description": "General care instructions"}
    },
    "required": ["plant_name"]
  }
}
```

### Custom GPT Integration
Configure the API as an external service:
1. Set base URL: `https://your-app.onrender.com`
2. Configure authentication header: `x-api-key`
3. Import OpenAPI schema from API documentation
4. Test with sample plant additions

## Security Considerations

### API Key Management
- **Never expose API keys** in client-side code
- **Use environment variables** for key storage
- **Rotate keys regularly** for security

### Rate Limiting Awareness
- **Implement retry logic** with exponential backoff
- **Monitor request frequency** to stay under 10/minute limit
- **Cache plant data** to reduce API calls

### Input Validation
- **Sanitize user input** before sending to API
- **Validate field names** against supported fields
- **Handle malformed responses** gracefully

## Testing AI Integration

### Test Cases for AI Development

**Basic Plant Addition**:
```bash
curl -X POST https://your-app.onrender.com/api/plants \
  -H "x-api-key: test-key" \
  -H "Content-Type: application/json" \
  -d '{"Plant Name": "Test Plant AI", "Location": "Test Garden"}'
```

**Plant Information Retrieval**:
```bash
curl https://your-app.onrender.com/api/plants/Test%20Plant%20AI
```

**Plant Search**:
```bash
curl "https://your-app.onrender.com/api/plants?q=test%20garden"
```

**Plant Update**:
```bash
curl -X PUT https://your-app.onrender.com/api/plants/Test%20Plant%20AI \
  -H "x-api-key: test-key" \
  -H "Content-Type: application/json" \
  -d '{"Care Notes": "Updated by AI assistant"}'
```

## Troubleshooting

### Common AI Integration Issues

**Authentication Failures**:
- Verify `x-api-key` header is included
- Check API key is valid and active

**Field Validation Errors**:
- Use field aliases for natural language input
- Refer to supported field list in main documentation

**Rate Limiting**:
- Implement request queuing in AI logic
- Add delays between rapid requests

**Response Parsing**:
- Handle empty responses gracefully
- Validate JSON structure before processing

### Support Resources
- **Main API Documentation**: `API_DOCUMENTATION.md`
- **Field Reference**: `models/field_config.py`
- **Test Suite**: Run comprehensive tests before deployment

---

*This guide is specifically designed for AI assistants and ChatGPT integration. For general API usage, see API_DOCUMENTATION.md* 