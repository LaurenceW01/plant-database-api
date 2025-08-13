# ChatGPT OpenAPI Schema Requirements - Critical Learning

## Overview

This document captures critical learnings about ChatGPT's unique OpenAPI parser requirements that differ significantly from standard OpenAPI implementations. Understanding these requirements is essential for creating functional ChatGPT custom actions.

## The Problem: UnrecognizedKwargsError

When ChatGPT custom actions fail with `UnrecognizedKwargsError`, it indicates that ChatGPT's OpenAPI parser is rejecting fields before they even reach your API server. This manifests as:

- Error messages like: `UnrecognizedKwargsError: ('Field Name 1', 'Field Name 2')`
- Extremely small Content-Length in server logs (e.g., 13 bytes vs expected 1000+ bytes)
- Only core parameters (like `id`) reaching your API, while all other fields are stripped

## Key Discovery: ChatGPT vs Standard OpenAPI Parsers

### Standard OpenAPI Behavior
```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
        additionalProperties: true  # This alone works for most parsers
```

### ChatGPT's Requirements
```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:           # MUST explicitly define expected fields
          Field Name:
            type: string
          Another Field:
            type: string
          # ... all expected fields
        additionalProperties: true  # Still needed for flexibility
```

## The Solution: Explicit Field Definitions

ChatGPT requires **both** explicit field definitions AND `additionalProperties: true`:

1. **Define All Expected Fields**: List every field you expect to receive in the `properties` section
2. **Keep additionalProperties**: Set to `true` for flexibility with field variations
3. **Apply to Each Endpoint**: Component schemas don't automatically apply - each endpoint needs its own definitions

## Real-World Example: Plant Update Endpoint

### Before (Failed Approach)
```yaml
/api/plants/update:
  post:
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              id:
                type: string
            additionalProperties: true  # Not enough for ChatGPT!
```

**Result**: Only `id` field reaches server, all plant care fields stripped

### After (Working Solution)
```yaml
/api/plants/update:
  post:
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              id:
                type: string
              Description:
                type: string
              Light Requirements:
                type: string
              Watering Needs:
                type: string
              Soil Preferences:
                type: string
              Fertilizing Schedule:
                type: string
              Pruning Instructions:
                type: string
              Mulching Needs:
                type: string
              Winterizing Instructions:
                type: string
              Care Notes:
                type: string
            additionalProperties: true
```

**Result**: All fields successfully transmitted to server

## Common Misconceptions

### ❌ "Component Schemas Apply Automatically"
```yaml
components:
  schemas:
    Plant:
      type: object
      properties:
        # ... field definitions
```
Component schemas are just reusable templates. They don't automatically apply to endpoints unless explicitly referenced with `$ref`.

### ❌ "additionalProperties: true Is Sufficient"
While this works for standard OpenAPI parsers, ChatGPT's parser treats undefined fields as "not allowed" regardless of `additionalProperties`.

### ❌ "Field Names Must Be Exact"
ChatGPT can handle field name variations (spaces, underscores, camelCase) if your API has proper field normalization middleware.

## Debugging Techniques

### 1. Monitor Content-Length
Check your server logs for `Content-Length` headers:
- **Suspicious**: Very small values (< 50 bytes) when expecting large requests
- **Healthy**: Proportional to the amount of data being sent

### 2. Log Request Body Size
Add debugging to see exactly what reaches your server:
```python
content_length = request.headers.get('Content-Length', 'unknown')
logging.info(f"Content-Length: {content_length}")
```

### 3. Count Received Fields
Log how many fields your API actually receives:
```python
data = request.get_json() or {}
logging.info(f"Received {len(data)} fields: {list(data.keys())}")
```

## Best Practices for ChatGPT Schemas

### 1. Always Define Expected Fields Explicitly
Never rely solely on `additionalProperties: true`. Always list the fields you expect to receive.

### 2. Use Descriptive Field Names
ChatGPT works well with human-readable field names like "Light Requirements" rather than "light_req".

### 3. Group Related Fields Logically
For complex objects, consider grouping related fields in the schema for better organization.

### 4. Test with Actual ChatGPT Calls
Standard OpenAPI validators won't catch ChatGPT-specific issues. Always test with real ChatGPT custom actions.

### 5. Monitor Field Transmission
Implement logging to verify that all expected fields are reaching your API server.

## Implementation Checklist

When creating ChatGPT-compatible endpoints:

- [ ] Define explicit `properties` for all expected fields
- [ ] Include `additionalProperties: true` for flexibility
- [ ] Test field transmission with Content-Length monitoring
- [ ] Verify all expected fields reach your server
- [ ] Implement field normalization middleware for variations
- [ ] Document any field name transformations
- [ ] Test with real ChatGPT custom action calls

## Error Patterns to Watch For

1. **UnrecognizedKwargsError**: Missing explicit field definitions
2. **Empty request bodies**: Schema too restrictive
3. **Partial field transmission**: Some fields defined, others missing from schema
4. **Field name mismatches**: Normalization issues between schema and API

## Conclusion

ChatGPT's OpenAPI parser is more restrictive than standard implementations. Success requires explicit field definitions even when allowing additional properties. This pattern applies to all ChatGPT custom actions accepting flexible field data.

The key insight: ChatGPT strips "unrecognized" fields before sending HTTP requests. By explicitly defining fields in the schema, you tell ChatGPT these fields are acceptable and should be transmitted to your API.

---

**Version**: Based on learnings from Plant Database API v2.3.8 schema fix  
**Date**: August 2025  
**Status**: Critical knowledge for ChatGPT custom action development

