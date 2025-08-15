# Advanced Query System Guide

## 🚀 Critical Optimization Overview

The Advanced Query System solves the critical GPT rate limiting problem by replacing 20+ individual API calls with a single optimized query.

### The Problem It Solves
- **Before**: Query "plants on patio in small pots" → 1 search + 26 individual context calls = **27 API calls** → Rate limits & incomplete responses
- **After**: 1 advanced query call = **1 API call** → Complete results every time

## When to Use Advanced Query (REQUIRED)

✅ **ALWAYS use for:**
- ANY question about multiple plants (3+ plants)
- Location-based queries ("plants on patio", "plants in sunny areas")  
- Container-based queries ("plants in small pots", "plastic containers")
- Condition-based queries ("sun-loving plants", "plants needing daily water")
- **ESPECIALLY when you would need 5+ individual API calls**

## Quick Usage Pattern

### Endpoint
`POST /api/garden/query`

### Basic Structure
```json
{
  "filters": {
    "plants": { /* plant conditions */ },
    "locations": { /* location conditions */ },
    "containers": { /* container conditions */ }
  },
  "response_format": "summary|detailed|minimal|ids_only",
  "limit": 50
}
```

## Common Query Examples

### 1. "Plants on patio in small pots"
```json
{
  "filters": {
    "locations": {"location_name": {"$regex": "patio"}},
    "containers": {"container_size": {"$eq": "small"}}
  },
  "response_format": "summary"
}
```

### 2. "Sun-loving plants that need daily watering"
```json
{
  "filters": {
    "plants": {
      "light_requirements": {"$regex": "sun"},
      "watering_needs": {"$regex": "daily"}
    }
  },
  "response_format": "detailed"
}
```

### 3. "All plastic containers with plants that have photos"
```json
{
  "filters": {
    "containers": {"container_material": {"$eq": "plastic"}},
    "plants": {"photo_url": {"$exists": true}}
  },
  "response_format": "minimal"
}
```

## Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equals | `{"size": {"$eq": "large"}}` |
| `$ne` | Not equals | `{"status": {"$ne": "dead"}}` |
| `$in` | In array | `{"type": {"$in": ["herb", "flower"]}}` |
| `$regex` | Pattern match | `{"name": {"$regex": "rose"}}` |
| `$exists` | Has value | `{"photo_url": {"$exists": true}}` |
| `$contains` | Contains substring | `{"notes": {"$contains": "pest"}}` |
| `$gt`, `$gte` | Greater than | `{"height": {"$gt": 12}}` |
| `$lt`, `$lte` | Less than | `{"age": {"$lt": 365}}` |

## Response Formats

- **summary**: Aggregated data with sample plants (best for large results)
- **detailed**: Full plant/location/container data
- **minimal**: Basic plant info only  
- **ids_only**: Just plant IDs (most efficient)

## Integration with Legacy Workflows

### Replace Multiple Calls Pattern
❌ **Old Pattern**:
1. Search plants
2. Loop through results calling get-context for each
3. Hit rate limits after 5-10 calls

✅ **New Pattern**:
1. Use advanced query with appropriate filters
2. Get complete results in one call
3. No rate limits, complete responses

### When to Still Use Individual Endpoints
- Single plant queries (1-2 plants)
- Specific plant by ID/name
- Weather-only queries
- Photo upload operations
- Health logging

## Error Handling

Common errors and solutions:
- **400 Bad Request**: Check JSON syntax and operator usage
- **Invalid operator**: Use only supported operators listed above
- **Empty results**: Verify filter conditions match actual data
- **Too many results**: Use `limit` parameter or more specific filters

## Performance Tips

1. **Use appropriate response_format**:
   - `summary` for 20+ results
   - `detailed` for 5-15 results
   - `minimal` for quick overviews
   - `ids_only` for subsequent processing

2. **Combine filters efficiently**:
   - More specific filters = faster queries
   - Use `$regex` sparingly for better performance

3. **Set reasonable limits**:
   - Default: 50 results
   - Maximum: 1000 results
   - Recommend: 20-100 for most queries

## Complete Documentation

For full API reference including all fields and advanced options, see `chatgpt_endpoints.md`.
