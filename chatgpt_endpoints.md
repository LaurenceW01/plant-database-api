# Plant Database API Endpoints Documentation

## Weather Endpoints

### Current Weather
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

### Weather Forecast
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

## Plant Management Endpoints

### Search Plants
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

### Add Plant
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
  "upload_url": "https://plant-database-api.onrender.com/upload/plant/abc123xyz",
  "upload_instructions": "To add a photo of your plant, visit: [upload_url]"
}
```

### Update Plant
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

## Health Logging Endpoints

### Create Log Entry (Simple)
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
  "upload_url": "https://plant-database-api.onrender.com/upload/abc123xyz",
  "upload_instructions": "To add a photo to this log entry, visit: [upload_url]"
}
```

### Get Plant Log History
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
      "treatment": "Apply balanced fertilizer",
      // ... other log fields
    }
  ]
}
```

## Photo Upload Endpoints

### Get Upload Page
```javascript
GET /upload/{token}

// Returns HTML upload page
```

### Upload Photo
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

## Response Formats

### Weather Data Integration
```javascript
// Good example:
"Given the current temperature of 92°F and high humidity (from /api/weather/current), 
I recommend watering your tomatoes early in the morning. With a 60% chance of 
rain tomorrow (from /api/weather/forecast), hold off on fertilizing."

// Bad example:
"Current weather: 92°F, humid. Forecast: Rain 60%. Water tomatoes early."
```

### Photo Upload Instructions
```javascript
// When creating new plant:
"I've added your Japanese Maple to the database. To add a photo of your plant, 
visit this link: [upload_url]. The link will expire in 24 hours."

// When updating plant:
"I've updated your plant's information. To update its photo, visit: [upload_url]. 
The link is valid for 24 hours."
``` 