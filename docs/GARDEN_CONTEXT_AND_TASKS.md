# Garden Context and Task Management Enhancement Plan

## Current Challenges
1. GPT provides generic gardening advice without specific context of existing plants
2. Pagination system makes it difficult to maintain overall garden context
3. Task management and follow-ups are not proactively surfaced
4. No high-level garden metadata to inform general queries
5. Soil pH preferences not explicitly categorized
6. Watering needs not standardized across similar plant types
7. Environmental conditions not tracked by location

## Proposed Solutions

### 1. Garden Metadata System

#### Core Metadata Categories
- Total number of plants
- Plant type distribution (trees, shrubs, perennials, annuals, etc.)
- Garden locations
- Primary growing seasons representation
- Dominant plant families
- Special care requirements distribution (e.g., % drought-tolerant, % shade-loving)
- Maintenance intensity distribution
- Soil pH requirement distribution (acidic, neutral, alkaline)
- Soil amendment needs based on pH requirements and measured soil conditions
- Watering requirement distribution
- Location-based environmental conditions

#### Watering Classification System

##### Water Frequency Categories
- Multiple intrady
- Daily
- Every 2-3 days
- Weekly
- Bi-weekly
- Monthly/Seasonal
- Weather-dependent adjustments

##### Plant Characteristics Affecting Watering
- Size/maturity
- Growth phase (active/dormant)
- Root system type
- Leaf type and density
- Natural habitat conditions

##### Container/Planting Specifications
- Container size
- Container material
- Soil volume
- Drainage characteristics
- Mulch presence/type
- Ground vs. container planted

##### Location Environmental Factors
- Daily sun exposure hours
- Sun exposure period (morning/afternoon/evening)
- Shade patterns
- Wind exposure
- Heat reflection from structures
- Microclimate conditions

#### Implementation Approach
1. Create a daily/weekly metadata refresh process
2. Store metadata in a dedicated collection/table
3. Make metadata available as first context when GPT initializes
4. Include last refresh timestamp
5. Track soil pH requirements across locations
6. Monitor and update location-based environmental data
7. Calculate dynamic watering needs based on conditions and irrigation type

#### Location Profile System
Create profiles for each garden location including:
- Sun exposure map (hours and intensity by time of day)
- Shade patterns throughout seasons
- Wind exposure rating
- Irrigation type (drip line default, sprinklers in arboretum)
- Soil drainage patterns

#### Plant Database Field Updates
Enhance `Soil Preferences` field to include:
- Mandatory pH preference category (acidic/neutral/alkaline)
- pH range values (if available)
- Current soil conditions in plant's location
- Required amendments for optimal pH

Enhance `Watering Needs` field to include:
- Base watering frequency category
- Container/planting specifications
- Location reference
- Seasonal adjustments
- Weather condition modifiers
- Growth phase considerations

### 2. Enhanced Task Management

#### Daily Task Compilation
1. Upcoming follow-ups from plant logs (next 48 hours)
2. Seasonal care tasks based on plant types
3. Weather-dependent task adjustments
4. Maintenance schedule items
5. Grouped watering tasks by:
   - Location
   - Frequency category
   - Current environmental conditions
   - Weather forecast impact

#### Task Prioritization Factors
- Urgency (based on follow-up dates)
- Weather conditions and forecast
- Plant health status
- Seasonal requirements
- Resource availability (water restrictions, etc.)
- Grouped watering efficiency
- Location-based task clustering

### 3. Context-Aware Responses

#### Required GPT Behaviors
1. Always check metadata first for general questions
2. Reference specific plants only when directly relevant
3. Prioritize tasks based on urgency and conditions
4. Consider garden composition when making recommendations

#### Query Processing Flow
1. Load garden metadata
2. Check for urgent follow-ups
3. Consider weather conditions
4. Apply seasonal context
5. Filter by specific plant/area if specified

### 4. API Enhancements Needed

#### New Endpoints
1. `/api/garden/metadata`
   - Returns current garden composition and statistics
   - Includes last refresh timestamp
   - Returns watering category distributions
   - Includes irrigation system coverage

2. `/api/tasks/upcoming`
   - Returns prioritized tasks for next 48 hours
   - Includes follow-ups and seasonal tasks
   - Weather-adjusted recommendations
   - Grouped watering schedules by irrigation type

3. `/api/garden/locations`
   - Returns garden organization structure
   - Helps contextualize location-based queries
   - Provides environmental conditions by location
   - Includes real-time sun exposure data
   - Specifies irrigation type (drip/sprinkler)

4. `/api/watering/schedule`
   - Returns grouped watering tasks
   - Adjusts for weather conditions
   - Provides location-based routing
   - Includes container-specific instructions
   - Separates drip line and sprinkler zones

#### Irrigation System Context
- Default irrigation: Drip lines for all plants in database
- Exception: Arboretum uses sprinkler system
- Grass areas: Managed by sprinkler system (not tracked in plant database)

#### Response Templates

1. **General Garden Questions**
   ```
   Garden Overview (from Metadata Tab):
   - Total plants: [count]
   - In-ground: [count] ([percentage]%)
   - Containers: [count] ([percentage]%)
     * Small: [count]
     * Medium: [count]
     * Large: [count]
   - Irrigation: Drip lines (Sprinklers in arboretum)
   - Current maintenance focus: [from Maintenance Groups]
   ```

2. **Maintenance Instructions**
   ```
   Tasks grouped by:
   1. Container size (from Container Definitions)
   2. In-ground plants
   3. Location-specific needs
   4. Irrigation type (drip/sprinkler)
   ```

3. **Weather Impact Responses**
   ```
   Priority attention:
   1. Small container plants: [list from Plants Tab]
   2. Medium container plants: [list from Plants Tab]
   3. In-ground plants: [list from Plants Tab]
   Note: All plants on drip lines except arboretum (sprinklers)
   ```

### 5. ChatGPT Instructions Updates

#### Additional Guidelines
1. Always reference metadata before making general recommendations
2. Prioritize existing plants over generic advice
3. Consider garden composition for new plant suggestions
4. Include task status in daily summaries
5. Reference location-specific conditions
6. Always specify soil pH requirements when adding/updating plant information
7. Group plants by pH requirements for maintenance recommendations
8. Use watering categories for grouped instructions
9. Consider location profiles for all recommendations
10. Provide efficient watering routes by location

#### Response Structure
1. Urgent tasks/follow-ups (if any)
2. Weather-dependent considerations
3. Seasonal context
4. Specific plant needs
5. General maintenance recommendations
6. Soil pH considerations and amendment needs
7. Grouped watering instructions by location and category

### 6. Location Management System

#### Location Table Structure
```sql
CREATE TABLE garden_locations (
    location_id VARCHAR PRIMARY KEY,
    location_name VARCHAR NOT NULL,
    location_type ENUM('indoor', 'outdoor', 'greenhouse', 'covered_patio') NOT NULL,
    
    -- Sun Exposure
    morning_sun_hours DECIMAL(3,1),    -- Hours of sun from sunrise to 11:59am
    afternoon_sun_hours DECIMAL(3,1),  -- Hours of sun from 12:00pm to 4:59pm
    evening_sun_hours DECIMAL(3,1),    -- Hours of sun from 5:00pm to sunset
    total_sun_hours DECIMAL(3,1) GENERATED ALWAYS AS (COALESCE(morning_sun_hours, 0) + COALESCE(afternoon_sun_hours, 0) + COALESCE(evening_sun_hours, 0)) STORED,
    shade_type ENUM('none', 'partial', 'dappled', 'full') NOT NULL,
    seasonal_shade_pattern TEXT,  -- JSON describing shade changes by season
    
    -- Environmental Factors
    wind_exposure_rating INTEGER CHECK (wind_exposure_rating BETWEEN 1 AND 5),
    
    -- Infrastructure
    irrigation_type ENUM('none', 'manual', 'drip', 'sprinkler'),
    irrigation_notes TEXT,
    drainage_rating INTEGER CHECK (drainage_rating BETWEEN 1 AND 5),
    drainage_notes TEXT,
    
    -- Physical Characteristics
    soil_type VARCHAR,
    default_soil_ph DECIMAL(3,1),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified_date DATE
)
```

#### Location Migration Process
1. **Initial Setup**
   - Create new location table
   - Extract unique locations from existing plant records
   - Generate placeholder records for each location

2. **Manual Data Entry Interface**
   - Create simple web form for location data entry
   - Include validation for required fields
   - Provide help text for sun hours measurement
   - Allow photo uploads for location documentation

3. **Data Population Steps**
   ```
   Phase 1: Basic Information
   - Location names and types
   - Sun exposure hours (morning/afternoon/evening)
   - Irrigation information
   
   Phase 2: Environmental Data
   - Wind exposure
   - Shade patterns
   - Drainage characteristics
   
   Phase 3: Soil Information
   - Soil type
   - pH testing results
   
   Phase 4: Documentation
   - Photos of locations
   - Seasonal shade documentation
   - Maintenance notes
   ```

4. **Location-Plant Association**
   ```sql
   -- Add foreign key to plants table
   ALTER TABLE plants
   ADD COLUMN location_id VARCHAR,
   ADD FOREIGN KEY (location_id) REFERENCES garden_locations(location_id);
   
   -- Update existing plant records
   UPDATE plants
   SET location_id = (SELECT location_id FROM garden_locations WHERE location_name = plants.location);
   ```

#### API Endpoints for Location Management

1. **Location CRUD Operations**
   ```
   GET    /api/locations
   GET    /api/locations/{id}
   POST   /api/locations
   PUT    /api/locations/{id}
   DELETE /api/locations/{id}
   ```

2. **Location Analytics**
   ```
   GET /api/locations/analytics
   - Returns statistics about plants per location
   - Sun exposure distribution
   - Watering needs by location
   ```

3. **Location Environmental Data**
   ```
   GET /api/locations/{id}/environment
   - Current conditions
   - Historical data
   - Seasonal patterns
   ```

#### Location-Aware Features

1. **Task Grouping**
   - Group maintenance tasks by location
   - Optimize watering routes based on irrigation types
   - Schedule tasks based on sun exposure times

2. **Environmental Alerts**
   - Shade pattern changes by season
   - Wind protection needs
   - Optimal watering times based on sun exposure

3. **Plant Recommendations**
   - Location-suitable plant suggestions based on sun hours
   - Companion planting by location
   - Space availability tracking

#### Implementation Timeline

1. **Week 1: Database Setup**
   - Create location table
   - Migrate existing location data
   - Set up basic API endpoints

2. **Week 2: Data Entry**
   - Develop data entry interface
   - Begin manual data collection
   - Document location characteristics

3. **Week 3: Integration**
   - Update plant management system
   - Integrate with task management
   - Update GPT instruction set

4. **Week 4: Testing & Refinement**
   - Validate location data
   - Test location-based features
   - Refine API endpoints

## Implementation Phases

### Phase 1: Metadata Foundation
- Design metadata schema
- Implement metadata collection process
- Create metadata API endpoint
- Update ChatGPT instructions
- Add soil pH categorization system
- Update existing plant records with pH requirements
- Create location profiles
- Implement watering classification system
- Map existing plants to watering categories

### Phase 2: Task Management
- Implement follow-up tracking
- Create task prioritization system
- Develop task API endpoint
- Integrate weather considerations
- Implement grouped watering schedules
- Create location-based task routing

### Phase 3: Context Integration
- Update ChatGPT instruction set
- Implement zone management
- Create response templates
- Test and refine context awareness

## Success Metrics
1. Reduction in generic advice responses
2. Improved task completion rates
3. Better alignment with actual garden composition
4. More proactive maintenance recommendations
5. Higher user satisfaction with contextual responses

## Next Steps
1. Review and approve metadata schema
2. Define specific API requirements
3. Update chatgpt_instructions.md
4. Create implementation timeline
5. Begin Phase 1 development 

### 7. Plant Container and Planting Type System

#### Google Sheets Structure

1. **Plants Tab (Existing)**
   Add new columns:
   ```
   has_in_ground_plants    [YES/NO]
   has_container_plants    [YES/NO]
   small_containers_count  [number]
   medium_containers_count [number]
   large_containers_count  [number]
   ```

2. **Container Definitions Tab**
   ```
   Container Size | Diameter Range | Watering Frequency Base
   --------------|---------------|----------------------
   Small         | < 12 inches   | Daily in summer
   Medium        | 12-18 inches  | Every 2-3 days
   Large         | > 18 inches   | Weekly
   ```

3. **Garden Metadata Tab**
   ```
   Metric                    | Value  | Last Updated
   --------------------------|--------|-------------
   Total Plants             | [calc] | [timestamp]
   Total In-Ground Plants   | [calc] | [timestamp]
   Total Container Plants   | [calc] | [timestamp]
   Small Containers Count   | [calc] | [timestamp]
   Medium Containers Count  | [calc] | [timestamp]
   Large Containers Count   | [calc] | [timestamp]
   ```

4. **Maintenance Groups Tab**
   ```
   Group Name        | Plant Types           | Container Sizes | Base Schedule
   -----------------|----------------------|-----------------|---------------
   Daily Water      | [plant types list]   | Small          | Daily
   Weather Sensitive| [plant types list]   | Small, Medium  | Weather dependent
   Seasonal Care    | [plant types list]   | Large, Ground  | Seasonal
   ```

#### Metadata Aggregation
The system will use Google Sheets formulas to maintain:
1. **Distribution Summaries**
   - COUNTIF and SUM formulas for totals
   - Percentage calculations for distribution
   - Automatic updates when plant data changes

2. **Location-Based Groupings**
   - FILTER and QUERY functions for grouping
   - Cross-reference with locations tab
   - Automatic maintenance group assignment

3. **Care Requirements Summary**
   - Container size-based requirements
   - Location-specific adjustments
   - Seasonal variations

#### GPT Context Enhancement

1. **Initial Context Loading**
   The GPT will receive:
   ```
   Garden Overview from Metadata Tab:
   - Total plant counts by planting type
   - Distribution percentages
   - Current maintenance groups
   ```

2. **Query Processing**
   - Reference appropriate sheet tabs based on query type
   - Cross-reference location and planting data
   - Use maintenance groups for task organization

3. **Task Organization**
   - Group by maintenance requirements
   - Consider container sizes and locations
   - Factor in seasonal and weather impacts

#### Response Templates

1. **General Garden Questions**
   ```
   Garden Overview (from Metadata Tab):
   - Total plants: [count]
   - In-ground: [count] ([percentage]%)
   - Containers: [count] ([percentage]%)
     * Small: [count]
     * Medium: [count]
     * Large: [count]
   - Irrigation: Drip lines (Sprinklers in arboretum)
   - Current maintenance focus: [from Maintenance Groups]
   ```

2. **Maintenance Instructions**
   ```
   Tasks grouped by:
   1. Container size (from Container Definitions)
   2. In-ground plants
   3. Location-specific needs
   4. Irrigation type (drip/sprinkler)
   ```

3. **Weather Impact Responses**
   ```
   Priority attention:
   1. Small container plants: [list from Plants Tab]
   2. Medium container plants: [list from Plants Tab]
   3. In-ground plants: [list from Plants Tab]
   Note: All plants on drip lines except arboretum (sprinklers)
   ```

#### Implementation Steps

1. **Sheet Updates**
   - Add new columns to Plants tab
   - Create Container Definitions tab
   - Create Garden Metadata tab
   - Create Maintenance Groups tab

2. **Data Collection**
   - Manual entry of current planting types
   - Container counts per plant type
   - Update location associations

3. **Formula Implementation**
   - Set up automatic calculations
   - Create summary views
   - Implement cross-reference lookups

4. **GPT Integration**
   - Update instruction set
   - Add metadata tab references
   - Enhance response templates

#### Example Metadata View
```
Garden Summary (Auto-updated):
Total Plants: 150
Distribution:
- In-Ground: 45 (30%)
- Containers: 105 (70%)
  * Small: 60 (40%)
  * Medium: 35 (23%)
  * Large: 10 (7%)

Mixed Planting Types:
- Hibiscus (In-ground + Containers)
- Roses (Various container sizes)

Current Maintenance Groups:
- Daily Water: Small containers
- Weather Watch: Small + Medium containers
- Seasonal Care: In-ground + Large containers
``` 