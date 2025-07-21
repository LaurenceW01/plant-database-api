"""
Tests for the Baron Weather API service and weather tools.
"""

import pytest
from utils.baron_weather_velocity_api import BaronWeatherVelocityAPI
from utils.weather_tools import get_current_weather, get_weather_forecast
from config.config import BARON_API_KEY, BARON_API_SECRET

def test_baron_api_initialization():
    """Test that the Baron Weather API client initializes correctly"""
    client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    assert client is not None
    assert client.houston_lat == 29.827119
    assert client.houston_lon == -95.472232

def test_baron_api_availability():
    """Test that the Baron Weather API is available"""
    client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    assert client.is_available() is True

def test_current_weather():
    """Test getting current weather data"""
    weather = get_current_weather()
    assert weather is not None
    
    # Check required fields
    assert 'temperature' in weather
    assert 'humidity' in weather
    assert 'wind_speed' in weather
    assert 'description' in weather
    assert 'precipitation_chance' in weather
    
    # Check data types and ranges
    assert isinstance(weather['temperature'], float)
    assert isinstance(weather['humidity'], int)
    assert isinstance(weather['wind_speed'], int)
    assert isinstance(weather['description'], str)
    assert isinstance(weather['precipitation_chance'], int)
    
    # Check reasonable value ranges
    assert -20 <= weather['temperature'] <= 120  # Fahrenheit
    assert 0 <= weather['humidity'] <= 100  # Percentage
    assert 0 <= weather['wind_speed'] <= 100  # mph
    assert 0 <= weather['precipitation_chance'] <= 100  # Percentage
    
    # Check description is not empty
    assert len(weather['description']) > 0

def test_weather_forecast():
    """Test getting weather forecast data"""
    forecast = get_weather_forecast(hours=24)
    assert forecast is not None
    assert len(forecast) > 0
    
    # Check first forecast entry
    first_entry = forecast[0]
    assert 'time' in first_entry
    assert 'temperature' in first_entry
    assert 'description' in first_entry
    assert 'precipitation_chance' in first_entry
    assert 'wind_speed' in first_entry
    
    # Check data types and ranges
    assert isinstance(first_entry['time'], str)
    assert isinstance(first_entry['temperature'], float)
    assert isinstance(first_entry['description'], str)
    assert isinstance(first_entry['precipitation_chance'], int)
    assert isinstance(first_entry['wind_speed'], int)
    
    # Check reasonable value ranges
    assert -20 <= first_entry['temperature'] <= 120  # Fahrenheit
    assert 0 <= first_entry['precipitation_chance'] <= 100  # Percentage
    assert 0 <= first_entry['wind_speed'] <= 100  # mph
    
    # Check time format (e.g., "2 PM")
    assert len(first_entry['time']) >= 4
    assert "AM" in first_entry['time'] or "PM" in first_entry['time']

def test_forecast_hours_limit():
    """Test that forecast hours are properly limited"""
    # Test minimum hours
    min_forecast = get_weather_forecast(hours=0)  # Should be corrected to 1
    assert len(min_forecast) >= 1
    
    # Test maximum hours
    max_forecast = get_weather_forecast(hours=100)  # Should be limited to 48
    assert len(max_forecast) <= 48

def test_weather_caching():
    """Test that weather data is properly cached"""
    # Get weather data twice
    weather1 = get_current_weather()
    weather2 = get_current_weather()
    
    # Should be the same object due to caching
    assert weather1 == weather2
    
    # Get forecast data twice
    forecast1 = get_weather_forecast(hours=24)
    forecast2 = get_weather_forecast(hours=24)
    
    # Should be the same object due to caching
    assert forecast1 == forecast2

def test_error_handling():
    """Test error handling with invalid credentials"""
    # Create client with invalid credentials
    bad_client = BaronWeatherVelocityAPI("invalid", "credentials")
    
    # Should return None for current weather
    assert bad_client.get_current_weather() is None
    
    # Should return None for forecast
    assert bad_client.get_hourly_forecast() is None 