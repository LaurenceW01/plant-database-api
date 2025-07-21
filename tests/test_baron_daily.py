"""
Test the Baron Weather API daily forecast functionality
"""

import pytest
from utils.baron_weather_velocity_api import BaronWeatherVelocityAPI
from config.config import BARON_API_KEY, BARON_API_SECRET
import logging
from datetime import datetime, timedelta
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def baron_client():
    """Create a Baron Weather API client"""
    return BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)

def test_daily_forecast_live(baron_client):
    """Test getting a 7-day forecast from the live Baron Weather API"""
    
    # Get the forecast (NDFD has 7-day limit)
    forecast_data = baron_client.get_daily_forecast(7)
    
    # Log the full response for inspection
    logger.info("7-day forecast response:")
    for day in forecast_data:
        logger.info(f"\nDate: {day['date']}")
        logger.info(f"Description: {day.get('description', 'N/A')}")
        
        # Optional fields - use get() with default values
        if 'high_temp' in day:
            logger.info(f"High: {day['high_temp']}°F")
        if 'low_temp' in day:
            logger.info(f"Low: {day['low_temp']}°F")
        if 'precipitation_chance' in day:
            logger.info(f"Precipitation Chance: {day['precipitation_chance']}%")
        if 'wind_speed' in day:
            logger.info(f"Wind Speed: {day['wind_speed']} mph")
    
    # Basic validation
    assert forecast_data is not None, "Forecast data should not be None"
    assert len(forecast_data) > 0, "Forecast data should not be empty"
    assert len(forecast_data) <= 7, "Should not exceed 7 days (NDFD limit)"
    
    # Validate first day's data structure
    first_day = forecast_data[0]
    assert 'date' in first_day, "Missing date"
    assert 'description' in first_day, "Missing description"
    
    # Validate dates are sequential
    houston_tz = pytz.timezone('America/Chicago')
    current_date = datetime.now(houston_tz).date()
    for i, day in enumerate(forecast_data):
        forecast_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
        expected_date = current_date + timedelta(days=i)
        assert forecast_date == expected_date, f"Date {forecast_date} should be {expected_date}"
        
        # Validate temperature ranges if present
        if 'high_temp' in day and 'low_temp' in day:
            assert 0 <= day['high_temp'] <= 120, f"High temp {day['high_temp']}°F outside reasonable range"
            assert 0 <= day['low_temp'] <= 100, f"Low temp {day['low_temp']}°F outside reasonable range"
            assert day['high_temp'] >= day['low_temp'], "High temp should be >= low temp"
        
        # Validate precipitation chance if present
        if 'precipitation_chance' in day:
            assert 0 <= day['precipitation_chance'] <= 100, f"Precipitation chance {day['precipitation_chance']}% outside valid range"
        
        # Validate wind speed if present
        if 'wind_speed' in day:
            assert 0 <= day['wind_speed'] <= 200, f"Wind speed {day['wind_speed']} mph outside reasonable range"

def test_daily_forecast_cache(baron_client):
    """Test that daily forecast caching works"""
    
    # First call should hit the API
    first_call = baron_client.get_daily_forecast(7)
    assert first_call is not None
    
    # Second call should use cache
    second_call = baron_client.get_daily_forecast(7)
    assert second_call is not None
    
    # Results should be identical since cached
    assert first_call == second_call, "Cached results should match" 