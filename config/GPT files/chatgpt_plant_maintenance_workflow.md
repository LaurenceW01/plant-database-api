# Plant Maintenance Workflow Guide

## Overview
The plant maintenance system allows users to move plants between locations and update container details using natural language commands via the `maintainPlant` operation.

## Core Operations

### 1. Move Plant Between Locations
**User Request**: "Move the tropical hibiscus from patio to pool path"
```
maintainPlant:
  plant_name: "Tropical Hibiscus"
  source_location: "patio" 
  destination_location: "pool path"
```

### 2. Add Plant to New Location
**User Request**: "Put the rose in the front garden too"
```
maintainPlant:
  plant_name: "Rose"
  destination_location: "front garden"
```

### 3. Remove Plant from Location
**User Request**: "Remove the basil from the kitchen"
```
maintainPlant:
  plant_name: "Basil"
  source_location: "kitchen"
```

### 4. Update Container Details
**User Request**: "Change the hibiscus to a large ceramic pot"
```
maintainPlant:
  plant_name: "Hibiscus"
  container_size: "Large"
  container_type: "Pot" 
  container_material: "Ceramic"
```

### 5. Move and Update Container
**User Request**: "Move the snake plant to the office and put it in a medium plastic pot"
```
maintainPlant:
  plant_name: "Snake Plant"
  source_location: "bedroom"
  destination_location: "office"
  container_size: "Medium"
  container_type: "Pot"
  container_material: "Plastic"
```

## Error Handling

### Ambiguity Resolution
If multiple locations match (e.g., "patio" could be "front patio", "back patio"):

**Response**: 422 error with options
```json
{
  "success": false,
  "error": "Multiple locations found",
  "options": {
    "locations": ["front patio", "back patio", "side patio"],
    "message": "Please specify which patio location"
  }
}
```

**Follow-up**: Use specific location name
```
maintainPlant:
  plant_name: "Hibiscus"
  source_location: "front patio"
  destination_location: "pool path"
```

### Plant in Multiple Locations
If plant exists in multiple locations and no source specified:

**Response**: 422 error with current locations
```json
{
  "options": {
    "locations": ["patio", "front garden", "kitchen"],
    "message": "Plant exists in multiple locations. Please specify source location."
  }
}
```

## Best Practices

### 1. Natural Language Processing
- Parse user intent to determine operation type
- Extract exact plant names (no fuzzy matching needed)
- Identify source and destination locations from context
- Detect container update requests

### 2. Parameter Selection
- **Required**: Always include `plant_name`
- **Move operations**: Include both `source_location` and `destination_location`
- **Add operations**: Include only `destination_location`
- **Remove operations**: Include only `source_location`
- **Container updates**: Include relevant container parameters
- **Combination**: Mix location and container changes

### 3. Response Handling
- **Success (200)**: Confirm operation and show before/after state
- **Validation (400)**: Guide user to provide missing information
- **Not Found (404)**: Suggest alternatives or check spelling
- **Ambiguity (422)**: Present options for user selection

### 4. User Confirmation
For successful operations, summarize what was changed:
```
✅ Successfully moved Tropical Hibiscus from patio to pool path
📍 Old locations: [patio]
📍 New locations: [pool path]
🪴 Updated container: Large ceramic pot
```

## Integration Notes

- Plant locations automatically sync with main spreadsheet
- Container records are updated in Containers sheet
- All operations use exact location names from Locations sheet
- Plant IDs are automatically resolved from plant names
- Cache invalidation ensures data consistency
