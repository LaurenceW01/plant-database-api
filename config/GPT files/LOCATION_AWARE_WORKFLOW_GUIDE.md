# Location-Aware Plant Care Workflow Guide

**📍 CRITICAL: Always use location-specific endpoints when plant care is requested**

This guide provides detailed workflows for delivering precise, location-aware plant care advice using the Phase 1 Locations & Containers integration.

## Core Principle

**NEVER give generic plant advice when specific location data is available.** Always transform generic advice into precise, actionable recommendations based on location, container, and microclimate context.

---

## 🚀 NEW: Advanced Query System (PRIMARY METHOD)

**🔥 CRITICAL OPTIMIZATION: Use this for ANY query involving multiple plants or complex filtering**

**When to Use Advanced Query:**
- ANY question about multiple plants (3+ plants)
- Location-based queries ("plants on patio", "plants in sunny areas")
- Container-based queries ("plants in small pots", "plastic containers")
- Condition-based queries ("sun-loving plants", "plants needing daily water")
- **ESPECIALLY when you would need 5+ individual API calls**

**Single Endpoint Replaces Multiple Calls:**
- ❌ Old: 1 search + 26 individual context calls = 27 API calls
- ✅ New: 1 advanced query call = 1 API call (96% reduction!)

### Workflow: Advanced Query Method

**Step 1: Use Advanced Query for Complex Scenarios**
```javascript
POST /api/garden/query
{
  "filters": {
    "locations": {"location_name": {"$regex": "patio"}},
    "containers": {"container_size": {"$eq": "small"}}
  },
  "response_format": "summary",
  "include": ["plants", "locations", "containers", "context"]
}
```

**Step 2: Get Weather (optional)**
```javascript
GET /api/weather/current
```

**Step 3: Provide Comprehensive Response**
Use the aggregated summary to provide intelligent care advice for all matched plants.

### Common Advanced Query Patterns

**Plants by Location + Container:**
```javascript
{
  "filters": {
    "locations": {"location_name": {"$regex": "patio"}},
    "containers": {"container_size": {"$eq": "small"}}
  },
  "response_format": "summary"
}
```

**Plants by Care Requirements:**
```javascript
{
  "filters": {
    "plants": {
      "Light Requirements": {"$regex": "Full Sun"},
      "Watering Needs": {"$regex": "daily"}
    }
  },
  "response_format": "detailed"
}
```

**Plants by Container Material:**
```javascript
{
  "filters": {
    "containers": {"container_material": {"$eq": "plastic"}},
    "plants": {"Photo URL": {"$exists": true}}
  },
  "response_format": "summary"
}
```

**High-Sun Locations with Specific Container Types:**
```javascript
{
  "filters": {
    "locations": {"total_sun_hours": {"$gte": 8}},
    "containers": {"container_material": {"$in": ["ceramic", "terracotta"]}}
  },
  "response_format": "summary"
}
```

### Advanced Query Response Formats

**Use "summary" for:**
- Large result sets (10+ plants)
- Overview questions ("what plants are...")
- When you need plant type breakdowns

**Use "detailed" for:**
- Specific care advice needed
- 5-10 plants maximum
- When context is crucial

**Use "minimal" for:**
- Quick lists
- Follow-up queries
- Simple verification

**Use "ids_only" for:**
- Very large sets
- When you need just counts
- Performance-critical queries

---

## Workflow 1: Single Plant Care Query WITH Location Mentioned (LEGACY - Use Advanced Query Instead)

**Query Examples:**
- "How should I water my hibiscus in the right arboretum?"
- "What's the best care for my roses in the patio area?"
- "Watering schedule for plants in the rear middle bed?"

**Required Steps:**
1. **Identify Plant**: Search for the plant mentioned
2. **Get Location Context**: Call `POST /api/plants/get-context/{plant_id}` (supports both IDs and names)
3. **Get Care Profile**: Call `/api/locations/get-context/{location_id}` 
4. **Check Weather**: Call `/api/weather/current` (continue if fails)
5. **Provide Integrated Response** (see templates below)

**Example API Sequence:**
```javascript
POST /api/plants/search (body: {"q": "tropical hibiscus"})
POST /api/plants/get-context/1  // or POST /api/plants/get-context/tropical hibiscus
GET /api/locations/get-context/1
GET /api/weather/current
```

---

## Workflow 2: Plant Care Query WITHOUT Location Mentioned (LEGACY - Use Advanced Query Instead)

**🚨 IMPORTANT: If this would result in 5+ API calls, use Advanced Query instead**

**Query Examples:**
- "How should I water my hibiscus?" (if you have multiple hibiscus)
- "What fertilizer for my roses?" (if you have multiple rose locations)
- "When to prune azaleas?" (if you have multiple azalea plants)

**Legacy Steps (use only for 1-4 plants):**
1. **Find All Plant Instances**: Call `POST /api/plants/search` with `{"q": "{plant_name}"}`
2. **Check Plant Count**: If 5+ plants found, use Advanced Query instead
3. **Get All Location Contexts**: Call `POST /api/plants/get-context/{plant_id}` (supports both IDs and names)
4. **Check Weather**: Call `/api/weather/current` (continue if fails)
5. **Provide Multi-Location Response** showing all locations and their specific care needs

**Advanced Query Alternative (PREFERRED for multiple plants):**
```javascript
POST /api/garden/query
{
  "filters": {
    "plants": {"Plant Name": {"$regex": "hibiscus"}}
  },
  "response_format": "summary",
  "include": ["plants", "locations", "containers", "context"]
}
```

**⚠️ IMPORTANT**: When user asks "where are all the [plant_name]" or "find all [plant_name]", you MUST use the search endpoint first to find ALL plants with that name (e.g., both "Vinca" and "Trailing Vinca"), then get context for each individual plant. Do NOT shortcut directly to get-context with a single plant name.

---

## Response Templates

### Template 1: Single Location Response
```
🌺 {plant_name} Care - {location_name}

**Current Setup:**
- Location: {location_name} ({shade_pattern})
- Container: {container_type}, {size}, {material}
- Sun exposure: {total_sun_hours} hours ({exposure_pattern})
- Microclimate: {microclimate_conditions}

**Optimized Watering Plan:**
- Best time: {primary_time}
- Alternative: {secondary_time}
- Avoid: {avoid_times}
- Why: {reasoning}

**Container Considerations:**
- {material_specific_adjustments}

**Current Weather Impact:**
- {weather_based_recommendations}
```

### Template 2: Multi-Location Response
```
🌺 {plant_name} Care - All Your Locations

I found your {plant_name} in {X} different locations. Here's the specific care for each:

**Location 1: {location_name}**
- Setup: {container_info}
- Best watering: {primary_time}
- Special notes: {priority_considerations}

**Location 2: {location_name}**
- Setup: {container_info}
- Best watering: {primary_time}
- Special notes: {priority_considerations}

**Weather Context:** {current_conditions_impact}
```

---

## Query Pattern Recognition

### ALWAYS Use Location-Aware Endpoints For:
- Any plant care question (watering, fertilizing, pruning, etc.)
- Plant health assessments
- Seasonal care planning
- Container-specific questions
- "How to care for..." questions
- "When should I..." questions

### Location Triggers (call location-specific endpoints):
- Specific location names: "arboretum", "patio", "rear left", etc.
- Location descriptors: "in the shade", "sunny spot", "by the pool"
- Container references: "potted plants", "containers", "plastic pots"

### plant_name Triggers (always get all locations):
- Any specific plant name mentioned
- "My hibiscus", "the roses", "azalea care"
- Multiple plants: "hibiscus and roses"

---

## Critical Integration Points

### 1. Weather Integration
ALWAYS combine location data with current weather:
```javascript
// After getting location data, always call:
GET /api/weather/current

// Then integrate in response:
"Given today's temperature of {temp}°F and {humidity}% humidity, your {plant} in {location} should be watered {timing} because {location_specific_reasoning}"
```

### 2. Container Material Considerations
Transform generic advice based on container material:

**Generic**: "Water regularly"
**Plastic Container**: "Water very early morning (5:30-7:00 AM) as plastic containers heat quickly in your {location} location with {sun_hours} hours of {exposure_pattern}"
**Ceramic Container**: "Water early morning (7:00-8:30 AM) as ceramic retains moisture better in your {location} setup"

### 3. Microclimate Adjustments
Always factor in microclimate conditions:

**North Facing**: "Cooler microclimate - adjust watering frequency accordingly"
**South Facing Wall**: "Intense heat reflection - increase watering frequency"
**Tree Canopy**: "Filtered light and moisture - monitor soil more closely"

---

## Error Handling

### If Plant Not Found:
1. Suggest similar plants in database
2. Offer to add the plant with location details
3. Provide general advice BUT note it's not location-specific

### If Location Data Missing:
1. Ask user to specify location
2. Show all available locations: `GET /api/locations/all`
3. Offer to update plant location information

### If Multiple Matches:
1. Show all instances with their locations
2. Ask user to specify which location they mean
3. Provide care for all locations as backup

---

## Quality Checklist

Before responding to ANY plant care query:
- [ ] Did I call the location-context endpoint?
- [ ] Did I include specific watering times?
- [ ] Did I mention container material considerations?
- [ ] Did I factor in microclimate conditions?
- [ ] Did I check current weather?
- [ ] Did I transform generic advice into specific recommendations?

**Remember**: The goal is to never give generic advice when specific location data exists. Every response should feel personalized to their exact garden setup.