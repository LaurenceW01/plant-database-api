# Plant Database API Documentation

## Core API Guidelines

### Weather Integration
- ALWAYS check weather for:
  * Watering needs/schedules
  * Planting timing
  * Outdoor activities
  * Plant stress/protection
  * Chemical applications
  * Transplanting
- SKIP weather for:
  * Plant identification
  * Indoor plants
  * General characteristics
  * Historical info

### Weather Endpoints

#### Current Weather
```javascript
GET /api/weather/current

// Example response:
{
  "temperature": 75.5,      // Fahrenheit
  "humidity": 65,          // Percentage
  "wind_speed": 8,        // MPH
  "description": "Partly cloudy",
  "precipitation_chance": 30  // Percentage
}
```

#### Hourly Forecast
```javascript
GET /api/weather/forecast?hours=24

// Example response:
{
  "forecast": [
    {
      "time": "2 PM",
      "temperature": 78.5,
      "description": "Clear",
      "precipitation_chance": 20,
      "wind_speed": 10
    }
    // ... more hourly entries
  ]
}
```

#### Daily Forecast
```javascript
GET /api/weather/forecast/daily?days=7

// Example response:
{
  "forecast": [
    {
      "date": "2024-01-21",
      "high_temp": 85,       // Fahrenheit
      "low_temp": 65,        // Fahrenheit
      "precipitation_chance": 30,  // Percentage
      "description": "Partly Cloudy",
      "wind_speed": 10       // MPH
    }
    // ... up to 7 daily entries (NDFD limit)
  ]
}
```

### Photo Upload Process
1. Create entry first (ChatGPT can't handle files)
2. Provide upload link to user
3. Explain 24-hour expiration
4. User uploads independently

### Plant Health Logging
1. Photo Analysis:
   - Use `/api/analyze-plant` for AI diagnosis
   - Automatic log creation
   - Link to existing plant
   - Set follow-up tracking
2. Manual Logging:
   - Use `/api/plants/log` for observations
   - Include photos when available
   - Use exact field names
   - Set follow-up dates

## API Endpoints

### Weather Endpoints

#### Current Weather
```javascript
GET /api/weather/current

// Example response:
{
  "temperature": 75.5,      // Fahrenheit
  "humidity": 65,          // Percentage
  "wind_speed": 8,        // MPH
  "description": "Partly cloudy",
  "precipitation_chance": 30  // Percentage
}
```

#### Hourly Forecast
```javascript
GET /api/weather/forecast?hours=24

// Example response:
{
  "forecast": [
    {
      "time": "2 PM",
      "temperature": 78.5,
      "description": "Clear",
      "precipitation_chance": 20,
      "wind_speed": 10
    }
    // ... more hourly entries
  ]
}
```

#### Daily Forecast
```javascript
GET /api/weather/forecast/daily?days=10

// Example response:
{
  "forecast": [
    {
      "date": "2024-01-21",
      "high_temp": 85,
      "low_temp": 65,
      "precipitation_chance": 30,
      "description": "Partly Cloudy",
      "wind_speed": 10,
      "sunrise": "7:15 AM",
      "sunset": "5:45 PM"
    }
    // ... more daily entries
  ]
}
```

### Image Analysis Integration

#### Enhanced /api/analyze-plant

The existing `/api/analyze-plant` endpoint now supports an optional `gpt_analysis` field for enhanced ChatGPT integration:

```javascript
POST /api/analyze-plant
Content-Type: application/json

{
  "plant_name": "Tomato Plant",
  "user_notes": "I'm concerned about yellowing leaves",
  "analysis_type": "health_assessment",
  "location": "Houston, TX",
  "gpt_analysis": "This tomato plant shows yellowing leaves on the lower portion, which could indicate overwatering or nutrient deficiency..."
}
```

**When `gpt_analysis` is provided**:
- Triggers enhanced mode with database knowledge integration
- Provides personalized care instructions based on location
- Matches plants against user's database
- Includes seasonal advice and treatment recommendations
- Maintains backward compatibility with existing usage

**Enhanced Response Example**:
```javascript
{
  "success": true,
  "analysis": {
    "diagnosis": "Enhanced Analysis for Tomato Plant:\n\nORIGINAL ANALYSIS:\nThis tomato plant shows yellowing...\n\nENHANCED CARE RECOMMENDATIONS:\nFor Houston's humid subtropical climate...",
    "treatment": "Enhanced analysis with database knowledge",
    "confidence": 0.8,
    "advice_type": "photo_analysis"
  }
}
```

### Plant Management

#### Search Plants
```javascript
GET /api/plants?q=tomato&limit=20&offset=0

// Example response:
{
  "plants": [
    {
      "Plant Name": "Cherry Tomato",
      "Description": "...",
      // ... other plant fields
    }
  ],
  "total": 50,
  "count": 20,
  "offset": 0,
  "limit": 20
}
```

#### Add Plant
```javascript
POST /api/plants
Content-Type: application/json

{
  "Plant Name": "Basil",  // Required
  "Location": "Herb Garden",
  "Light Requirements": "Full Sun",
  // ... other optional fields
}

// Example response:
{
  "message": "Added Basil to garden",
  "upload_url": "https://dev-plant-database-api.onrender.com/upload/plant/abc123xyz",
  "upload_instructions": "To add a photo of your plant, visit: [upload_url]"
}
```

#### Update Plant
```javascript
PUT /api/plants/{id_or_name}
Content-Type: application/json

{
  "Watering Needs": "Water deeply twice per week",
  "Care Notes": "Mulch heavily during summer heat"
}

// Example response:
{
  "message": "Updated Tomato",
  "upload_url": "...",
  "upload_instructions": "..."
}
```

### Enhanced Plant Analysis

#### POST /api/enhance-analysis

**Purpose**: Enhance ChatGPT's image analysis with database knowledge and personalized care instructions.

**When to Use**:
- After ChatGPT analyzes plant images using native vision capabilities
- To get personalized care instructions based on user's database and location
- For consultation-only analysis (does NOT force log creation)
- To match identified plants against user's existing plant database

**Request Format**:
```javascript
POST /api/enhance-analysis
Content-Type: application/json

{
  "gpt_analysis": "This appears to be a tomato plant with yellowing leaves showing brown spots...",
  "plant_identification": "Tomato Plant", 
  "user_question": "What's wrong with my plant?",
  "location": "Garden bed 2",
  "analysis_type": "health_assessment"
}
```

**Response Format**:
```javascript
{
  "success": true,
  "enhanced_analysis": {
    "plant_match": {
      "found_in_database": true,
      "plant_name": "Tomato",
      "confidence": "high",
      "database_info": "Found exact match in your plant database"
    },
    "care_enhancement": {
      "specific_care_instructions": "For Houston's humid subtropical climate...",
      "common_issues": "Tomatoes in Houston commonly experience...",
      "seasonal_advice": "For January in Houston...",
      "watering_recommendations": "Water deeply but less frequently..."
    },
    "diagnosis_enhancement": {
      "likely_causes": ["Overwatering", "Fungal infection"],
      "treatment_recommendations": "Reduce watering frequency...",
      "urgency_level": "moderate",
      "symptoms_identified": ["yellowing leaves", "brown spots"]
    },
    "database_context": {
      "your_plant_history": "You have 3 tomato plants logged",
      "previous_issues": ["Similar yellowing reported in Plant Log #123"]
    }
  },
  "suggested_actions": {
    "immediate_care": ["Begin recommended treatment within 24-48 hours"],
    "monitoring": ["Check plant daily for changes"],
    "follow_up": "Re-evaluate in 1 week"
  },
  "logging_offer": {
    "recommended": true,
    "reason": "Track treatment progress",
    "pre_filled_data": {
      "plant_name": "Tomato",
      "symptoms": "Yellow patches on leaves",
      "diagnosis": "Likely overwatering stress",
      "treatment": "Reduce watering frequency"
    }
  }
}
```

**Key Features**:
- **Plant Matching**: Fuzzy logic matching against user's database with confidence scoring
- **Location-Specific Advice**: Houston climate considerations and seasonal timing
- **Urgency Assessment**: Classifies issues as urgent/moderate/monitor
- **Optional Logging**: Recommends but doesn't force log creation
- **Pre-filled Data**: Ready-to-use data if user chooses to log

**Error Handling**:
```javascript
// 400 - Missing required fields
{
  "success": false,
  "error": "Both gpt_analysis and plant_identification are required"
}

// 500 - Server error with graceful degradation
{
  "success": false,
  "error": "Server error during enhanced analysis",
  "enhanced_analysis": {
    "plant_match": {"error": "Analysis failed"},
    "care_enhancement": {"error": "Could not generate care instructions"}
  }
}
```

### Health Logging

#### Create Log Entry
```javascript
POST /api/plants/log/simple
Content-Type: application/json

{
  "plant_name": "Tomato Plant #1",  // Required
  "log_title": "Weekly Health Check",
  "diagnosis": "Minor nitrogen deficiency",
  "treatment": "Apply balanced fertilizer",
  "symptoms": "Yellow leaf edges",
  "follow_up_required": true,
  "follow_up_date": "2024-01-22"
}

// Example response:
{
  "success": true,
  "log_id": "LOG-20240115-001",
  "upload_url": "https://dev-plant-database-api.onrender.com/upload/abc123xyz",
  "upload_instructions": "To add a photo to this log entry, visit: [upload_url]"
}
```

#### Get Log History
```javascript
GET /api/plants/{plant_name}/log?format=standard&limit=20

// Example response:
{
  "plant_name": "Tomato Plant #1",
  "total_entries": 50,
  "log_entries": [
    {
      "log_id": "LOG-20240115-001",
      "log_date": "2024-01-15",
      "diagnosis": "Minor nitrogen deficiency",
      "treatment": "Apply balanced fertilizer"
    }
  ]
}
```

### Photo Upload

#### Get Upload Page
```javascript
GET /upload/{token}
// Returns HTML upload page
```

#### Upload Photo
```javascript
POST /upload/{token}
Content-Type: multipart/form-data

file: [binary photo data]

// Example response:
{
  "success": true,
  "message": "Photo uploaded successfully",
  "photo_upload": {
    "photo_url": "https://storage.googleapis.com/...",
    "filename": "tomato_20240115.jpg",
    "upload_time": "2024-01-15T15:03:27"
  }
}
```

## Response Examples

### Weather Integration
```javascript
// Good example:
"Given the current temperature of 92°F and high humidity, I recommend watering 
your tomatoes early in the morning. With a 60% chance of rain tomorrow, you 
might want to hold off on fertilizing."

// Bad example:
"Current weather: 92°F, humid. Forecast: Rain 60%. Water tomatoes early."
```

### Photo Upload Instructions
```javascript
// New plant:
"I've added your Japanese Maple to the database. To add a photo of your plant, 
visit this link: [upload_url]. The link will expire in 24 hours."

// Update plant:
"I've updated your plant's information. To update its photo, visit: [upload_url]. 
The link is valid for 24 hours."
```

## Field Descriptions

### Plant Fields
- `Plant Name` (Required): Exact name for database
- `Description`: Plant details and notes
- `Location`: Where plant is located
- `Light Requirements`: Sunlight needs
- `Soil Preferences`: Soil type and pH
- `Soil pH Type`: pH classification (high alkalinity, medium alkalinity, slightly alkaline, neutral, slightly acidic, medium acidity, high acidity)
- `Soil pH Range`: Numerical pH range (e.g., "6.0 - 6.5")
- `Frost Tolerance`: Cold hardiness
- `Spacing Requirements`: Plant spacing
- `Watering Needs`: Water frequency/amount
- `Fertilizing Schedule`: Nutrient timing
- `Pruning Instructions`: Trimming guidance
- `Mulching Needs`: Mulch requirements
- `Winterizing Instructions`: Winter care
- `Care Notes`: Additional care info
- `Photo URL`: Image location

### Log Fields
- `Log ID`: Unique identifier (auto)
- `Plant Name`: Must match database
- `Log Title`: Entry description
- `Diagnosis`: Health assessment
- `Treatment`: Care recommendations
- `Symptoms`: Observed issues
- `User Notes`: Additional comments
- `Follow-up Required`: Need monitoring
- `Follow-up Date`: Next check date

---

## Phase 1: Locations & Containers Integration (NEW)

### Location-Aware Plant Care Endpoints

These endpoints provide **precise, context-aware plant care recommendations** based on specific location and container data. Use these for individual plant care queries where precise advice is needed.

#### Plant Location Context
```javascript
GET /api/plants/{plant_id}/location-context

// Returns comprehensive location and container context for a specific plant
// Use when: User asks about care for a specific plant
// Example: "How should I care for my hibiscus?" (plant ID 1)

{
  "plant_id": "1",
  "contexts": [
    {
      "container": {
        "container_id": "1",
        "plant_id": "1", 
        "location_id": "1",
        "container_type": "Pot in ground",
        "container_size": "Medium",
        "container_material": "Plastic"
      },
      "location": {
        "location_id": "1",
        "location_name": "arboretum right",
        "morning_sun_hours": 0,
        "afternoon_sun_hours": 2,
        "evening_sun_hours": 4,
        "shade_pattern": "Afternoon Sun",
        "microclimate_conditions": "North Facing",
        "total_sun_hours": 6
      },
      "context": {
        "placement_description": "Pot in ground (Medium, Plastic) in arboretum right",
        "sun_exposure_summary": "6 total hours (Afternoon Sun)",
        "care_complexity": "low",
        "priority_considerations": [
          "Water early morning to prepare for evening heat stress",
          "Cooler microclimate - adjust watering frequency accordingly"
        ]
      }
    }
    // ... more containers if plant is in multiple locations
  ],
  "total_contexts": 1
}
```

#### Location Care Profile
```javascript
GET /api/locations/{location_id}/care-profile

// Returns comprehensive care analysis for a specific location
// Use when: User asks about a specific location or plants in that location
// Example: "What's the best care strategy for plants in the arboretum right?"

{
  "location_id": "1",
  "care_profile": {
    "location_info": {
      "location_id": "1",
      "location_name": "arboretum right",
      "classification": "Moderate full sun"
    },
    "watering_strategy": {
      "primary_time": "Very early morning (5:30-7:00 AM)",
      "secondary_time": "Early morning (7:00-8:30 AM)", 
      "avoid_times": ["Afternoon (2:00-6:00 PM)", "Evening (6:00-8:00 PM)"],
      "reasoning": "Location receives 4 hours of evening sun, requiring very early watering to prepare for heat stress"
    },
    "environmental_factors": {
      "sun_exposure": {
        "morning_hours": 0,
        "afternoon_hours": 2,
        "evening_hours": 4,
        "total_hours": 6,
        "pattern_description": "Afternoon Sun"
      },
      "microclimate": {
        "conditions": "North Facing",
        "implications": [
          "Cooler temperatures, less intense sun",
          "May need less frequent watering"
        ]
      }
    },
    "general_recommendations": [
      "Evening sun location - ensure morning watering to prepare for heat"
    ]
  }
}
```

#### Container Care Requirements
```javascript
GET /api/garden/containers/{container_id}/care-requirements

// Returns specific care requirements for an individual container
// Use when: User asks about a specific container or plant-container combination
// Example: "What care does container 1 need?"

{
  "container_id": "1",
  "care_requirements": {
    "container_info": {
      "container_id": "1",
      "plant_id": "1",
      "type": "Pot in ground",
      "size": "Medium", 
      "material": "Plastic"
    },
    "location_context": {
      "location_id": "1",
      "location_name": "arboretum right",
      "sun_exposure": "6 hours (Afternoon Sun)",
      "microclimate": "North Facing"
    },
    "care_adjustments": {
      "material_considerations": [
        "Plastic containers heat up quickly in direct sun",
        "High heat retention risk - monitor soil temperature"
      ],
      "size_adjustments": [
        "Medium containers offer good balance of moisture retention and drainage"
      ],
      "drainage_recommendations": [
        "Ground placement provides temperature stability"
      ],
      "temperature_management": [
        "Water early morning to cool container before peak heat"
      ]
    },
    "watering_strategy": {
      "primary_time": "Very early morning (5:30-7:00 AM)",
      "secondary_time": "Early morning (7:00-8:30 AM)",
      "avoid_times": ["Afternoon (2:00-6:00 PM)", "Evening (6:00-8:00 PM)"],
      "reasoning": "Location receives 4 hours of evening sun, requiring very early watering to prepare for heat stress"
    },
    "integrated_recommendations": [
      "Water Very early morning (5:30-7:00 AM)",
      "Plastic containers heat up quickly in direct sun",
      "Medium containers offer good balance of moisture retention and drainage"
    ]
  }
}
```

### Location & Container Data Endpoints

#### All Locations
```javascript
GET /api/locations/all

// Returns all locations with metadata
// Use when: Need to understand all available locations or location options

{
  "locations": [
    {
      "location_id": "1",
      "location_name": "arboretum right",
      "morning_sun_hours": 0,
      "afternoon_sun_hours": 2,
      "evening_sun_hours": 4,
      "shade_pattern": "Afternoon Sun",
      "microclimate_conditions": "North Facing",
      "total_sun_hours": 6
    }
    // ... more locations (36 total)
  ],
  "total": 36
}
```

#### All Containers
```javascript
GET /api/containers/all

// Returns all containers with metadata  
// Use when: Need to understand container distribution or find specific containers

{
  "containers": [
    {
      "container_id": "1",
      "plant_id": "1",
      "location_id": "1", 
      "container_type": "Pot in ground",
      "container_size": "Medium",
      "container_material": "Plastic"
    }
    // ... more containers (71 total)
  ],
  "total": 71
}
```

### Usage Guidelines for Location-Aware Care

**🎯 Primary Use Cases (High Value)**
1. **Individual Plant Care Queries**: "How should I water my hibiscus?" → Use `/api/plants/{id}/location-context`
2. **Location-Specific Questions**: "What's the best watering time for arboretum right?" → Use `/api/locations/{id}/care-profile`  
3. **Container-Specific Care**: "How do I care for my plastic containers?" → Use `/api/garden/containers/{id}/care-requirements`

**✅ When to Use These Endpoints**
- User asks about specific plant care
- Questions about watering times or frequencies
- Container material considerations needed
- Location-specific advice required
- Microclimate factors are relevant

**🔄 Integration Pattern**
1. Get plant location context for specific care advice
2. Use location care profile for general location guidance
3. Get container requirements for material-specific considerations
4. **Always combine with weather data** for current conditions

**💡 Response Enhancement**
Transform generic advice like:
> "Water regularly, ensuring soil doesn't dry out"

Into precise, location-aware guidance:
> "Your hibiscus in arboretum right (4 hours evening sun) in a medium plastic container: Water very early morning (5:30-7:00 AM) to prevent afternoon heat stress on the plastic container. Check soil daily during hot weather as plastic containers in evening sun locations dry faster." 