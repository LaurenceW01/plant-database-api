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