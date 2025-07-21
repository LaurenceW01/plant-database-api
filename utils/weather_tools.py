"""
Weather tool functions for the AI to access current weather and forecast data.
"""

from typing import Dict, List, Optional, Any
from config.config import weather_client
import logging

logger = logging.getLogger(__name__)

def get_current_weather() -> Optional[Dict[str, Any]]:
    """
    Get current weather conditions in Houston.
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing:
            - temperature (float): Temperature in Fahrenheit
            - humidity (int): Humidity percentage
            - wind_speed (int): Wind speed in mph
            - description (str): Weather description
            - precipitation_chance (int): Chance of precipitation as percentage
            
        Returns None if weather data is unavailable.
    """
    if not weather_client:
        logger.error("Weather client not available")
        return None
        
    try:
        return weather_client.get_current_weather()
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        return None

def get_weather_forecast(hours: int = 24) -> Optional[List[Dict[str, Any]]]:
    """
    Get hourly weather forecast for Houston.
    
    Args:
        hours (int): Number of hours to forecast (default 24, max 48)
        
    Returns:
        Optional[List[Dict[str, Any]]]: List of forecast entries, each containing:
            - time (str): Formatted time (e.g., "2 PM")
            - temperature (float): Temperature in Fahrenheit
            - description (str): Weather description
            - precipitation_chance (int): Chance of precipitation as percentage
            - wind_speed (int): Wind speed in mph
            
        Returns None if forecast data is unavailable.
    """
    if not weather_client:
        logger.error("Weather client not available")
        return None
        
    try:
        # Limit hours to 48
        hours = min(max(1, hours), 48)
        return weather_client.get_hourly_forecast(hours)
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        return None 