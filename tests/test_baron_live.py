"""
Comprehensive live tests for Baron Weather API functionality.
Tests all endpoints and features against the live API.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.baron_weather_velocity_api import BaronWeatherVelocityAPI
from config.config import BARON_API_KEY, BARON_API_SECRET

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('baron_live_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_api_availability():
    """Test basic API availability and authentication"""
    logger.info("\n=== Testing API Availability ===")
    
    client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    is_available = client.is_available()
    
    logger.info(f"API Available: {is_available}")
    assert is_available, "Baron Weather API should be available"

def test_current_weather():
    """Test current weather retrieval"""
    logger.info("\n=== Testing Current Weather ===")
    
    client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    current = client.get_current_weather()
    
    assert current is not None, "Should get current weather data"
    
    # Log the current weather data
    logger.info("Current Weather Data:")
    logger.info(json.dumps(current, indent=2))
    
    # Verify all required fields are present
    required_fields = ['temperature', 'humidity', 'description', 'wind_speed', 'precipitation_chance']
    for field in required_fields:
        assert field in current, f"Current weather should include {field}"
        
    # Verify data types and ranges
    assert isinstance(current['temperature'], (int, float)), "Temperature should be numeric"
    assert isinstance(current['humidity'], (int, float)), "Humidity should be numeric"
    assert isinstance(current['wind_speed'], (int, float)), "Wind speed should be numeric"
    assert isinstance(current['precipitation_chance'], (int, float)), "Precipitation chance should be numeric"
    assert isinstance(current['description'], str), "Description should be string"
    
    # Verify reasonable ranges
    assert -20 <= current['temperature'] <= 120, "Temperature should be in reasonable range (°F)"
    assert 0 <= current['humidity'] <= 100, "Humidity should be 0-100%"
    assert 0 <= current['wind_speed'] <= 200, "Wind speed should be in reasonable range (mph)"
    assert 0 <= current['precipitation_chance'] <= 100, "Precipitation chance should be 0-100%"

def test_hourly_forecast():
    """Test hourly forecast retrieval for various durations"""
    logger.info("\n=== Testing Hourly Forecast ===")
    
    client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    
    # Test different forecast durations
    hours_to_test = [1, 6, 12, 24]
    
    for hours in hours_to_test:
        logger.info(f"\nTesting {hours} hour forecast:")
        forecast = client.get_hourly_forecast(hours)
        
        assert forecast is not None, f"Should get {hours}-hour forecast data"
        assert len(forecast) <= hours, f"Should not get more than {hours} hours of data"
        assert len(forecast) > 0, "Should get at least one hour of data"
        
        # Log first and last entries
        logger.info(f"Got {len(forecast)} hours of forecast data")
        logger.info("First hour:")
        logger.info(json.dumps(forecast[0], indent=2))
        if len(forecast) > 1:
            logger.info("Last hour:")
            logger.info(json.dumps(forecast[-1], indent=2))
        
        # Verify each hour's data
        for hour_data in forecast:
            # Check required fields
            required_fields = ['time', 'temperature', 'precipitation_chance', 'description', 'wind_speed']
            for field in required_fields:
                assert field in hour_data, f"Hourly forecast should include {field}"
            
            # Verify data types and ranges
            assert isinstance(hour_data['temperature'], (int, float)), "Temperature should be numeric"
            assert isinstance(hour_data['wind_speed'], (int, float)), "Wind speed should be numeric"
            assert isinstance(hour_data['precipitation_chance'], (int, float)), "Precipitation chance should be numeric"
            assert isinstance(hour_data['description'], str), "Description should be string"
            assert isinstance(hour_data['time'], str), "Time should be string"
            
            # Verify reasonable ranges
            assert -20 <= hour_data['temperature'] <= 120, "Temperature should be in reasonable range (°F)"
            assert 0 <= hour_data['wind_speed'] <= 200, "Wind speed should be in reasonable range (mph)"
            assert 0 <= hour_data['precipitation_chance'] <= 100, "Precipitation chance should be 0-100%"

def test_caching():
    """Test that caching works correctly"""
    logger.info("\n=== Testing Caching ===")
    
    client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    
    # Get initial data
    logger.info("First request (should hit API):")
    start_time = datetime.now()
    first_current = client.get_current_weather()
    first_duration = datetime.now() - start_time
    
    # Get cached data
    logger.info("Second request (should use cache):")
    start_time = datetime.now()
    second_current = client.get_current_weather()
    second_duration = datetime.now() - start_time
    
    # Verify data matches
    assert first_current == second_current, "Cached data should match original"
    
    # Second request should be significantly faster
    logger.info(f"First request took: {first_duration.total_seconds():.3f}s")
    logger.info(f"Second request took: {second_duration.total_seconds():.3f}s")
    assert second_duration < first_duration, "Cached request should be faster"

def run_all_tests():
    """Run all Baron Weather API tests"""
    logger.info("Starting comprehensive Baron Weather API tests...")
    
    try:
        test_api_availability()
        test_current_weather()
        test_hourly_forecast()
        test_caching()
        
        logger.info("\n=== All tests passed successfully! ===")
        return True
        
    except AssertionError as e:
        logger.error(f"\n!!! Test failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"\n!!! Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    run_all_tests() 