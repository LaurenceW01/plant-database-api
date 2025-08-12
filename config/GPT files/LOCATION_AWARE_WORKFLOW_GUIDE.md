# Location-Aware Plant Care Workflow Guide

**📍 CRITICAL: Always use location-specific endpoints when plant care is requested**

This guide provides detailed workflows for delivering precise, location-aware plant care advice using the Phase 1 Locations & Containers integration.

## Core Principle

**NEVER give generic plant advice when specific location data is available.** Always transform generic advice into precise, actionable recommendations based on location, container, and microclimate context.

---

## Workflow 1: Plant Care Query WITH Location Mentioned

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

## Workflow 2: Plant Care Query WITHOUT Location Mentioned

**Query Examples:**
- "How should I water my hibiscus?"
- "What fertilizer for my roses?"
- "When to prune azaleas?"

**Required Steps:**
1. **Find All Plant Instances**: Call `POST /api/plants/search` with `{"q": "{plant_name}"}`
2. **Get All Location Contexts**: Call `POST /api/plants/get-context/{plant_id}` (supports both IDs and names)
3. **Check Weather**: Call `/api/weather/current` (continue if fails)
4. **Provide Multi-Location Response** showing all locations and their specific care needs

**Key Point**: Even when location isn't mentioned, ALWAYS retrieve and present location-specific information for each instance of the plant.

**⚠️ IMPORTANT**: When user asks "where are all the [plant_name]" or "find all [plant_name]", you MUST use the search endpoint first to find ALL plants with that name (e.g., both "Vinca" and "Trailing Vinca"), then get context for each individual plant. Do NOT shortcut directly to get-context with a single plant name.

---

## Response Templates

### Template 1: Single Location Response
```
🌺 {Plant Name} Care - {Location Name}

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
🌺 {Plant Name} Care - All Your Locations

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

### Plant Name Triggers (always get all locations):
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