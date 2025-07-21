"""
Test script specifically for testing Baron Weather API hourly forecast functionality.
"""

import os
import sys
import json
import logging
import requests

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
        logging.FileHandler('baron_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_hourly_forecast():
    """Test getting hourly forecast data directly from Baron API"""
    
    # Use exact same Houston coordinates as main API
    HOUSTON_LAT = 29.827119
    HOUSTON_LON = -95.472232
    
    # Initialize client
    client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    logger.info("Testing Baron Weather API hourly forecast...")
    
    # Test direct API call first to see raw response
    hours = 1
    logger.info(f"\nTesting direct API call for {hours} hour forecast:")
    
    try:
        # Construct the same URL as the API class
        host = "https://api.velocityweather.com/v1"
        uri = f"/reports/ndfd/hourly.json?lat={HOUSTON_LAT}&lon={HOUSTON_LON}&hours={hours}"
        url = f"{host}/{BARON_API_KEY}{uri}"
        
        # Sign request using client's method
        signed_url = client._sign_request(url)
        logger.info(f"Making request to: {signed_url}")
        
        # Make direct request to see raw response
        response = requests.get(signed_url)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Raw API response: {json.dumps(response.json(), indent=2)}")
        
        # Now test through the client
        logger.info("\nTesting through client interface:")
        forecast = client.get_hourly_forecast(hours)
        
        if forecast is None:
            logger.error("Failed to get forecast - returned None")
            return
            
        logger.info(f"Successfully retrieved {len(forecast)} hours of forecast data")
        
        # Log the forecast data structure
        if len(forecast) > 0:
            first_entry = forecast[0]
            logger.info("First forecast entry structure:")
            logger.info(json.dumps(first_entry, indent=2))
            
            # Check expected keys
            expected_keys = ['time', 'temperature', 'precipitation_chance', 'description', 'wind_speed']
            missing_keys = [key for key in expected_keys if key not in first_entry]
            
            if missing_keys:
                logger.error(f"Missing expected keys in forecast data: {missing_keys}")
            else:
                logger.info("All expected keys present in forecast data")
                
        else:
            logger.error("Forecast list is empty")
            
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)

if __name__ == "__main__":
    test_hourly_forecast() 