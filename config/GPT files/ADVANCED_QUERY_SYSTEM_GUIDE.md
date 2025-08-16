# Garden Filter System Guide

## 🚀 Reliable Plant Filtering Overview

The Garden Filter System provides a simple, reliable way to filter plants using GET query parameters. This approach is consistent with other working endpoints and avoids the complexity of JSON body requests.

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

## Response Format

Standard response includes:
- `count`: Number of matching plants
- `plants`: Array of plant objects with details
- `debug_signature`: Endpoint identifier
- `filters_applied`: Summary of filters used

```javascript
{
  "count": 8,
  "plants": [
    {
      "Plant Name": "Vinca",
      "Location": "Front Patio",
      "container_info": "small plastic pot",
      // ... other plant details
    }
    // ... more plants
  ],
  "debug_signature": "filter_garden_endpoint",
  "filters_applied": {
    "location": "patio",
    "container_size": "small"
  }
}
```

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