# Garden Filter System Guide

## 🔄 CHATGPT WORKAROUND: Perfect Timing!

**✅ ADVANTAGE:** The Garden Filter System uses GET query parameters, making it IDEAL during the ChatGPT POST/PUT workaround period. This system continues to work perfectly without any changes needed.

## 🚀 Reliable Plant Filtering Overview

The Garden Filter System provides a simple, reliable way to filter plants using GET query parameters. This approach is consistent with our new workaround pattern and avoids the complexity of JSON body requests.

### The Solution It Provides
- **Reliable**: GET-based filtering using query parameters
- **Simple**: No complex JSON body construction required
- **Consistent**: Follows same pattern as other working endpoints
- **ChatGPT-friendly**: Easy parameter-based queries

## When to Use Garden Filter

✅ **Use for:**
- Location-based filtering ("plants on patio", "plants in sunny areas")  
- Container-based filtering ("plants in small pots", "plastic containers")
- Plant name filtering ("find vinca plants")
- Multiple criteria filtering ("plants on patio in small containers")

## Quick Usage Pattern

### Endpoint
`GET /api/garden/filter`

### Available Parameters
- `location` - Filter by location name (e.g., "patio", "garden")
- `container_size` - Filter by container size ("small", "medium", "large") 
- `container_material` - Filter by material ("plastic", "ceramic", "terracotta")
- `plant_name` - Filter by plant name

### Basic Structure
```
GET /api/garden/filter?parameter=value&parameter2=value2
```

## Common Query Examples

### 1. "Plants on patio in small pots"
```
GET /api/garden/filter?location=patio&container_size=small
```

### 2. "All plastic containers"
```
GET /api/garden/filter?container_material=plastic
```

### 3. "Find all vinca plants"
```
GET /api/garden/filter?plant_name=vinca
```

### 4. "Large ceramic containers on patio"
```
GET /api/garden/filter?location=patio&container_material=ceramic&container_size=large
```

## Response Format - NEW HIERARCHICAL STRUCTURE ✨

**🎉 IMPROVED 2025**: The garden filter now returns a clear hierarchical structure that eliminates confusion and provides complete information.

### Key Improvements:
- **No Misleading Data**: Each plant shows ALL locations where it exists
- **Complete Information**: Location names are resolved (no ID lookups needed)
- **Clear Hierarchy**: Plant → Locations → Containers structure
- **No Inference Required**: GPT gets exact, explicit information

### New Response Structure:
```javascript
{
  "count": 2,
  "total_matches": 2,
  "debug_signature": "GET-FILTER-HIERARCHICAL-2025",
  "filters_applied": {
    "plants": {"plant_name": {"$regex": "hibiscus"}}
  },
  "plants": [
    {
      "plant_name": "Tropical Hibiscus",
      "plant_id": "1",
      "locations": [
        {
          "location_name": "arboretum right",
          "location_id": "1",
          "containers": [
            {
              "container_id": "1",
              "container_type": "Pot buried in ground",
              "container_size": "Medium",
              "container_material": "Plastic"
            }
          ]
        },
        {
          "location_name": "patio",
          "location_id": "25",
          "containers": [
            {
              "container_id": "5",
              "container_type": "Pot",
              "container_size": "Large", 
              "container_material": "Ceramic"
            }
          ]
        }
        // ... all other locations where this plant exists
      ]
    }
    // ... other plants
  ]
}
```

### Benefits of New Structure:
✅ **Accurate**: Shows plant exists in multiple locations clearly  
✅ **Complete**: All location names resolved, no IDs to lookup  
✅ **Organized**: Logical plant → locations → containers hierarchy  
✅ **GPT-Friendly**: No confusion about where plants actually are

## Integration with Other Endpoints

### Replace Complex Queries Pattern
❌ **Old Complex Pattern**:
1. Multiple API calls with complex JSON
2. Timeout risks with large responses
3. Difficult parameter construction

✅ **New Simple Pattern**:
1. Single GET request with clear parameters
2. Reliable responses
3. Easy parameter construction

### When to Still Use Individual Endpoints
- Single plant details (use `/api/plants/get/{id}`)
- Plant context with location (use `/api/plants/get-context/{id}`)
- Weather queries (use `/api/weather/*`)
- Health logging (use `/api/logs/*`)
- Photo uploads (use `/api/photos/*`)

## Error Handling

Common scenarios and solutions:
- **No results**: Check parameter spelling and available data
- **Too many results**: Add more specific filter parameters
- **Parameter errors**: Verify parameter names and values match available options

## Performance Tips

1. **Combine filters for specificity**:
   - More specific filters = more targeted results
   - Combine location + container for best results

2. **Use appropriate filter combinations**:
   - `location + container_size` for placement-based queries
   - `container_material + plant_name` for specific plant-container combinations

3. **Check response counts**:
   - Large result sets may indicate need for more specific filtering
   - Use additional parameters to narrow results

## Integration Examples

### For Location-Based Questions
**Query**: "What plants are on the patio?"
**API Call**: `GET /api/garden/filter?location=patio`

### For Container-Based Questions  
**Query**: "Show me all small containers"
**API Call**: `GET /api/garden/filter?container_size=small`

### For Specific Plant Queries
**Query**: "Where are all my vinca plants?"
**API Call**: `GET /api/garden/filter?plant_name=vinca`

### For Complex Multi-Criteria
**Query**: "Plastic containers on the patio"
**API Call**: `GET /api/garden/filter?location=patio&container_material=plastic`

## Complete Documentation

For full API reference and additional examples, see `chatgpt_endpoints.md`.