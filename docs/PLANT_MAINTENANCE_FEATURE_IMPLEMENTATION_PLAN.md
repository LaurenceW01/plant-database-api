# Plant Maintenance Feature Implementation Plan

## Overview
Implementation plan for a new ChatGPT plant maintenance feature that allows users to move plants between locations and update container details using natural language commands.

## User Story
User says: "Move the tropical hibiscus on the patio to the pool path and put it in a large sized pot"
- GPT parses the request and calls the plant maintenance endpoint
- Backend processes the move and updates container details
- Plant spreadsheet location column is updated with new location list

## Feature Requirements

### Core Functionality
1. **Move Plants**: Transfer plants between locations
2. **Add Locations**: Add new location for existing plant  
3. **Remove Plants**: Remove plant from specific location
4. **Update Containers**: Change container size, type, material (partial updates allowed)

### Input Handling
- AI provides exact plant name (no fuzzy matching needed)
- Natural language parsing handled by ChatGPT
- Ambiguity errors returned with options for user selection

### Business Rules
- Update existing container records (don't create new ones)
- Allow partial container updates
- Validate destination locations exist
- Handle multiple location ambiguity with error responses

## Technical Implementation

### New Files to Create

#### 1. `api/routes/plant_maintenance.py`
- **Purpose**: New standalone endpoint (no changes to existing routes)
- **Method**: GET (ChatGPT compatible)
- **Route**: `/api/plants/maintenance`

**Query Parameters:**
- `plant_name` (required): Exact plant name from AI
- `destination_location` (optional): New location name (null/empty for removal or container only change)
- `source_location` (optional): Current location (for ambiguity resolution or container change)
- `container_size` (optional): New container size
- `container_type` (optional): New container type  
- `container_material` (optional): New container material

**Success Response:**
```json
{
  "success": true,
  "message": "Plant moved successfully",
  "data": {
    "plant_name": "Tropical Hibiscus",
    "old_locations": ["Patio"],
    "new_locations": ["Pool Path"],
    "container_updates": {"size": "Large"}
  }
}
```

**Ambiguity Error Response:**
```json
{
  "success": false,
  "error": "Multiple locations found",
  "options": {
    "locations": ["Front Patio", "Back Patio", "Side Patio"],
    "message": "Please specify which patio location"
  }
}
```

#### 2. `utils/plant_maintenance_operations.py`
- **Purpose**: Main orchestrator for maintenance operations
- **Functions**:
  - `process_plant_maintenance()`: Main entry point
  - `validate_maintenance_request()`: Input validation
  - `detect_ambiguity()`: Check for multiple location matches
  - `execute_maintenance()`: Coordinate all operations

#### 3. `utils/container_operations.py`
- **Purpose**: Container CRUD operations module
- **Functions**:
  - `get_containers_for_plant(plant_name)`: Find all containers for a plant)
  - `update_container(container_id, updates)`: Partial update container details
  - `add_container(plant_name, location_id, container_details)`: Add new container
  - `remove_container(container_id)`: Remove container
  - `get_container_by_plant_and_location(plant_name, location_name)`: For ambiguity resolution

### Existing Code Reuse

#### Location Operations
- Use existing functions from `utils/locations_operations.py`
- Location validation and lookup functions
- No changes to existing location code

#### Plant Operations  
- Use existing functions from `utils/plant_operations.py`
- Plant spreadsheet location column updates
- No changes to existing plant code

#### Database Operations
- Leverage existing database utilities in files containint `utils/*database_operations.py`
- Use established connection patterns
- Follow existing error handling

### ChatGPT Integration Updates

#### Schema Updates (`config/GPT files/chatgpt_actions_schema.yaml`)
- Add new plant maintenance endpoint definition
- Follow existing GET parameter pattern
- Include all query parameters with proper types

#### Documentation Updates
- `config/GPT files/chatgpt_instructions.md`: Add maintenance workflow
- `config/GPT files/chatgpt_endpoints.md`: Document new endpoint
- remaining `config/*.md`: Support files for GPT instructions and endpoints files
- Ensure character limits maintained (under 8,000 chars for instructions)

## Implementation Flow

### Backend Processing Steps
1. **Validation**: Validate plant name and location parameters
2. **Ambiguity Check**: Detect multiple location matches
3. **Location Resolution**: Validate source/destination locations exist
4. **Container Operations**: Update/add/remove container records
5. **Spreadsheet Sync**: Update plant_location column using from containers/locations table join
6. **Response**: Return success or error with options

### Error Scenarios
1. **Plant Not Found**: Plant doesn't exist in system
2. **Location Not Found**: Invalid source or destination location
3. **Multiple Locations**: Plant exists in multiple locations, need specification
4. **Container Not Found**: Plant not in specified source location
5. **Validation Errors**: Invalid container parameters

## Testing Strategy

### Regression Tests (`tests/test_regression_comprehensive.py`)
- Add new test methods for plant maintenance endpoint
- Test all success scenarios (move, add, remove, partial updates, change cntainer attribute only)
- Test all error scenarios (ambiguity, validation, not found)
- Verify no impact on existing functionality

### Test Scenarios
1. **Successful Move**: Move plant between valid locations
2. **Successful Addition**: Add new location for existing plant
3. **Successful Removal**: Remove plant from location
4a. **Partial Container Update - Size**: Update only size, keep type/material
4b. **Partial Container Update - Type, Material**: Update type and material, keep size
4c. **Partial Container Update In Place - Size and Material**: Same location, keep container type
5. **Ambiguity Error**: Multiple location matches
6. **Validation Errors**: Invalid locations, missing plant
7. **Integration**: Verify spreadsheet updates correctly

## Development Constraints

### Critical Requirements
- **NO CHANGES** to existing endpoints or functionality
- **REUSE** existing functions wherever possible
- **PRESERVE** all current behavior and APIs
- **MAINTAIN** backward compatibility

### Code Standards
- Follow existing project patterns and conventions
- Add comprehensive inline documentation
- Use established error handling patterns
- Follow field normalization standards (lowercase_underscore)

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create `utils/container_operations.py` module
- [ ] Create `utils/plant_maintenance_operations.py` module
- [ ] Create `api/routes/plant_maintenance.py` endpoint
- [ ] Test basic functionality without ChatGPT integration

### Phase 2: ChatGPT Integration
- [ ] Update `chatgpt_actions_schema.yaml` with new endpoint
- [ ] Update `chatgpt_instructions.md` with maintenance workflow
- [ ] Update `chatgpt_endpoints.md` with endpoint documentation
- [ ] Test ChatGPT integration end-to-end

### Phase 3: Testing & Validation
- [ ] Create comprehensive regression tests
- [ ] Test all error scenarios and ambiguity handling
- [ ] Verify no impact on existing functionality
- [ ] Run full test suite to ensure no regressions

### Phase 4: Documentation & Cleanup
- [ ] Update API documentation
- [ ] Verify all memory compliance requirements met
- [ ] Final testing and validation
- [ ] Ready for production deployment

## Memory Compliance Requirements

As per established protocols, before marking this feature complete:
- [ ] Review all memories for compliance (ID: 6326158)
- [ ] Update endpoint documentation (ID: 6147568)
- [ ] Update regression tests (ID: 6106016)
- [ ] Follow code change verification protocol (ID: 6103532)
- [ ] Ensure ChatGPT schema compatibility (ID: 6037615)
- [ ] Verify character limits (ID: 5687160)
- [ ] Field normalization compliance (ID: 6319595)

## Success Criteria
1. Users can move plants using natural language via ChatGPT
2. Container details can be partially updated
3. Ambiguity errors provide clear options for resolution
4. All existing functionality remains unchanged
5. Comprehensive test coverage with no regressions
6. Full ChatGPT integration with proper schema updates

---

**Next Steps**: Begin implementation with Phase 1 (Core Infrastructure) following this plan.

