"""
Visual Crossing Weather API Client for Plant Database API.
Replaces Baron Weather API with Visual Crossing Timeline Weather API.
Provides identical interface to maintain compatibility with existing weather service.
"""

import logging
import requests
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import os

# Set up logging
logger = logging.getLogger(__name__)

class VisualCrossingWeatherAPI:
    """Visual Crossing Timeline Weather API client"""
    
    def __init__(self, api_key: str, username: str = None):
        """
        Initialize the Visual Crossing Weather API client
        
        Args:
            api_key (str): Visual Crossing API key
            username (str): Visual Crossing username (optional)
        """
        self.api_key = api_key
        self.username = username
        self.base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        self.session = requests.Session()
        
        # Houston coordinates (same as Baron API for consistency)
        self.houston_lat = 29.827119
        self.houston_lon = -95.472232
        self.location = f"{self.houston_lat},{self.houston_lon}"
        
        # Houston timezone (Central Time)
        self.houston_tz = timezone(timedelta(hours=-6))  # CST (UTC-6) - will adjust for DST
        
        # Cache for storing weather data to respect API limits
        self.cache = {}
        self.cache_timeout = 5 * 60  # 5 minutes in seconds (same as Baron API)
        
        # Set headers for API requests
        self.session.headers.update({
            'User-Agent': 'PlantDatabaseAPI/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        
        # Request delay to be respectful to API
        self.last_request_time = 0
        self.min_request_delay = 1  # Minimum 1 second between requests
        self.default_timeout = 20  # Default timeout for requests
    
    def _respectful_request(self, url: str, timeout: int = 20) -> Optional[requests.Response]:
        """
        Make a respectful request with delays and error handling
        
        Args:
            url (str): URL to request
            timeout (int): Request timeout in seconds
            
        Returns:
            Optional[requests.Response]: Response object or None if failed
        """
        try:
            # Ensure minimum delay between requests
            time_since_last = time.time() - self.last_request_time
            if time_since_last < self.min_request_delay:
                time.sleep(self.min_request_delay - time_since_last)
            
            logger.info(f"Making request to Visual Crossing API: {url}")
            response = self.session.get(url, timeout=timeout)
            self.last_request_time = time.time()
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Visual Crossing API request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error requesting {url}: {e}")
            return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        cache_time, _ = self.cache[cache_key]
        return (time.time() - cache_time) < self.cache_timeout
    
    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            logger.info(f"Using cached data for {cache_key}")
            return data
        return None
    
    def _set_cached_data(self, cache_key: str, data: Any) -> None:
        """Set cached data with current timestamp"""
        self.cache[cache_key] = (time.time(), data)
        logger.info(f"Cached data for {cache_key}")
    
    def get_current_weather(self) -> Optional[Dict[str, Any]]:
        """
        Get current weather conditions from Visual Crossing API
        
        Returns:
            Optional[Dict[str, Any]]: Current weather data in Baron API compatible format
        """
        cache_key = "current_weather"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Build URL for current conditions
            url = f"{self.base_url}/{self.location}"
            params = {
                'key': self.api_key,
                'unitGroup': 'us',  # Use US units (Fahrenheit, mph, etc.)
                'include': 'current',  # Only current conditions to reduce cost
                'contentType': 'json'
            }
            
            # Add parameters to URL
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            response = self._respectful_request(full_url)
            if not response:
                return None
            
            data = response.json()
            logger.info("Successfully retrieved current weather from Visual Crossing API")
            
            # Parse the Visual Crossing response to match Baron API format
            current_weather = self._parse_current_conditions(data)
            if current_weather:
                self._set_cached_data(cache_key, current_weather)
                return current_weather
            
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
        
        logger.warning("Visual Crossing API is not available - no weather data provided")
        return None
    
    def get_hourly_forecast(self, hours: int = 24) -> Optional[List[Dict[str, Any]]]:
        """
        Get hourly forecast from Visual Crossing API
        
        Args:
            hours (int): Number of hours to forecast (max 48)
            
        Returns:
            Optional[List[Dict[str, Any]]]: Hourly forecast data in Baron API compatible format
        """
        cache_key = f"hourly_forecast_{hours}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Limit hours to maximum supported
        hours = min(hours, 48)
        
        try:
            # Calculate date range for hourly forecast
            current_time = datetime.now(self.houston_tz)
            end_time = current_time + timedelta(hours=hours)
            
            # Visual Crossing uses date format YYYY-MM-DD
            start_date = current_time.strftime('%Y-%m-%d')
            end_date = end_time.strftime('%Y-%m-%d')
            
            # Build URL for hourly forecast
            url = f"{self.base_url}/{self.location}/{start_date}/{end_date}"
            params = {
                'key': self.api_key,
                'unitGroup': 'us',  # Use US units
                'include': 'hours',  # Only hourly data
                'contentType': 'json'
            }
            
            # Add parameters to URL
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            response = self._respectful_request(full_url)
            if not response:
                return None
            
            data = response.json()
            logger.info("Successfully retrieved hourly forecast from Visual Crossing API")
            
            # Parse the Visual Crossing response to match Baron API format
            hourly_data = self._parse_hourly_forecast(data, hours)
            if hourly_data:
                self._set_cached_data(cache_key, hourly_data)
                return hourly_data
            
        except Exception as e:
            logger.error(f"Error getting hourly forecast: {e}")
        
        logger.warning("Visual Crossing API is not available - no hourly forecast data provided")
        return None
    
    def get_daily_forecast(self, days: int = 7) -> Optional[List[Dict[str, Any]]]:
        """
        Get daily forecast from Visual Crossing API
        
        Args:
            days (int): Number of days to forecast (max 15)
            
        Returns:
            Optional[List[Dict[str, Any]]]: Daily forecast data in Baron API compatible format
        """
        cache_key = f"daily_forecast_{days}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Limit days to maximum supported by Visual Crossing
        days = min(days, 15)
        
        try:
            # Calculate date range for daily forecast
            current_time = datetime.now(self.houston_tz)
            end_time = current_time + timedelta(days=days)
            
            # Visual Crossing uses date format YYYY-MM-DD
            start_date = current_time.strftime('%Y-%m-%d')
            end_date = end_time.strftime('%Y-%m-%d')
            
            # Build URL for daily forecast
            url = f"{self.base_url}/{self.location}/{start_date}/{end_date}"
            params = {
                'key': self.api_key,
                'unitGroup': 'us',  # Use US units
                'include': 'days',  # Only daily data
                'contentType': 'json'
            }
            
            # Add parameters to URL
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            response = self._respectful_request(full_url)
            if not response:
                return None
            
            data = response.json()
            logger.info("Successfully retrieved daily forecast from Visual Crossing API")
            
            # Parse the Visual Crossing response to match Baron API format
            daily_data = self._parse_daily_forecast(data, days)
            if daily_data:
                self._set_cached_data(cache_key, daily_data)
                return daily_data
            
        except Exception as e:
            logger.error(f"Error getting daily forecast: {e}")
        
        logger.warning("Visual Crossing API is not available - no daily forecast data provided")
        return None
    
    def _parse_current_conditions(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse current weather data from Visual Crossing response to match Baron API format
        
        Args:
            data (Dict[str, Any]): Raw Visual Crossing API response
            
        Returns:
            Optional[Dict[str, Any]]: Parsed current weather data in Baron API format
        """
        try:
            # Extract current conditions from Visual Crossing response
            current_conditions = data.get('currentConditions')
            if not current_conditions:
                logger.warning("No current conditions in Visual Crossing response")
                return None
            
            # Extract temperature (already in Fahrenheit due to unitGroup=us)
            temp_f = current_conditions.get('temp', 75.0)
            
            # Extract humidity
            humidity = current_conditions.get('humidity', 60)
            
            # Extract wind speed (already in mph due to unitGroup=us)
            wind_speed = current_conditions.get('windspeed', 5.0)
            
            # Extract weather description
            description = current_conditions.get('conditions', 'Partly Cloudy')
            
            # Visual Crossing doesn't provide precipitation chance for current conditions
            # This is forecast data, so we'll omit it for current weather
            
            # Build result in Baron API compatible format
            result = {
                'temperature': round(float(temp_f), 1),
                'humidity': int(humidity),
                'description': description,
                'wind_speed': round(wind_speed)
            }
            
            logger.info(f"Parsed current weather: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Visual Crossing current conditions: {e}")
            return None
    
    def _parse_hourly_forecast(self, data: Dict[str, Any], hours: int) -> Optional[List[Dict[str, Any]]]:
        """
        Parse hourly forecast data from Visual Crossing response to match Baron API format
        
        Args:
            data (Dict[str, Any]): Raw Visual Crossing API response
            hours (int): Number of hours requested
            
        Returns:
            Optional[List[Dict[str, Any]]]: Parsed hourly forecast data in Baron API format
        """
        try:
            # Extract days array from Visual Crossing response
            days = data.get('days', [])
            if not days:
                logger.warning("No days data in Visual Crossing response")
                return None
            
            # Collect all hourly data from all days
            all_hours = []
            for day in days:
                day_hours = day.get('hours', [])
                all_hours.extend(day_hours)
            
            if not all_hours:
                logger.warning("No hourly data found in Visual Crossing response")
                return None
            
            # Parse hourly data to match Baron API format
            hourly_data = []
            current_time = datetime.now(self.houston_tz)
            
            for i, hour_data in enumerate(all_hours):
                if i >= hours:  # Limit to requested hours
                    break
                
                # Extract temperature (already in Fahrenheit)
                temp_f = hour_data.get('temp', 75.0)
                
                # Extract humidity
                humidity = hour_data.get('humidity', 60)
                
                # Extract precipitation probability
                precip_prob = hour_data.get('precipprob', 0)
                
                # Extract wind speed and gust (already in mph) - use the higher value
                wind_speed = hour_data.get('windspeed', 5.0)
                wind_gust = hour_data.get('windgust', 0)
                max_wind = max(wind_speed, wind_gust) if wind_gust else wind_speed
                
                # Extract weather description
                description = hour_data.get('conditions', 'Partly Cloudy')
                
                # Calculate time for this hour
                # Start from next hour and add offset
                next_hour = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                hour_time = next_hour + timedelta(hours=i)
                
                # Build hourly entry in Baron API compatible format
                hourly_entry = {
                    'time': hour_time.strftime('%I %p').replace(' 0', ' '),  # Format like "2 PM"
                    'temperature': round(temp_f, 1),
                    'precipitation_chance': round(precip_prob),
                    'description': description,
                    'wind_speed': round(max_wind)
                }
                
                hourly_data.append(hourly_entry)
            
            logger.info(f"Successfully parsed {len(hourly_data)} hourly entries from Visual Crossing API")
            return hourly_data
            
        except Exception as e:
            logger.error(f"Error parsing Visual Crossing hourly forecast: {e}")
            return None
    
    def _parse_daily_forecast(self, data: Dict[str, Any], days: int) -> Optional[List[Dict[str, Any]]]:
        """
        Parse daily forecast data from Visual Crossing response to match Baron API format
        
        Args:
            data (Dict[str, Any]): Raw Visual Crossing API response
            days (int): Number of days requested
            
        Returns:
            Optional[List[Dict[str, Any]]]: Parsed daily forecast data in Baron API format
        """
        try:
            # Extract days array from Visual Crossing response
            forecast_days = data.get('days', [])
            if not forecast_days:
                logger.warning("No days data in Visual Crossing response")
                return None
            
            # Parse daily data to match Baron API format
            daily_data = []
            
            for i, day_data in enumerate(forecast_days):
                if i >= days:  # Limit to requested days
                    break
                
                # Extract temperatures (already in Fahrenheit)
                high_temp = day_data.get('tempmax')
                low_temp = day_data.get('tempmin')
                
                # Extract humidity (daily average)
                humidity = day_data.get('humidity', 60)
                
                # Extract precipitation probability
                precip_prob = day_data.get('precipprob', 0)
                
                # Extract wind speeds (already in mph) - use max available
                wind_speed_max = day_data.get('windspeedmax')
                wind_gust = day_data.get('windgust')
                wind_speed = day_data.get('windspeed', 5.0)
                
                # Use windspeedmax if available, otherwise windgust, otherwise windspeed
                if wind_speed_max is not None:
                    max_wind = wind_speed_max
                elif wind_gust is not None:
                    max_wind = max(wind_gust, wind_speed)
                else:
                    max_wind = wind_speed
                
                # Extract weather description
                description = day_data.get('conditions', 'No data')
                
                # Extract date
                date_str = day_data.get('datetime')
                
                # Build daily entry in Baron API compatible format (exact match)
                forecast_entry = {
                    'date': date_str,
                    'description': description
                }
                
                # Only include fields if available (matches Baron API behavior)
                if high_temp is not None:
                    forecast_entry['high_temp'] = round(high_temp)
                if low_temp is not None:
                    forecast_entry['low_temp'] = round(low_temp)
                if precip_prob is not None:
                    forecast_entry['precipitation_chance'] = round(precip_prob)
                if max_wind is not None:
                    forecast_entry['wind_speed'] = round(max_wind)
                
                daily_data.append(forecast_entry)
            
            logger.info(f"Successfully parsed {len(daily_data)} daily entries from Visual Crossing API")
            return daily_data
            
        except Exception as e:
            logger.error(f"Error parsing Visual Crossing daily forecast: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if Visual Crossing API is available
        
        Returns:
            bool: True if available, False otherwise
        """
        try:
            # Test with a simple current conditions request
            url = f"{self.base_url}/{self.location}"
            params = {
                'key': self.api_key,
                'unitGroup': 'us',
                'include': 'current',
                'contentType': 'json'
            }
            
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            response = self._respectful_request(full_url)
            return response is not None and response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error checking Visual Crossing API availability: {e}")
            return False
    
    def _get_houston_time(self) -> datetime:
        """
        Get current time in Houston timezone
        
        Returns:
            datetime: Current time in Houston timezone
        """
        utc_now = datetime.now(timezone.utc)
        return utc_now.astimezone(self.houston_tz)


# Convenience function to initialize from environment variables
def create_visual_crossing_client() -> Optional[VisualCrossingWeatherAPI]:
    """
    Create Visual Crossing client from environment variables
    
    Returns:
        Optional[VisualCrossingWeatherAPI]: Initialized client or None if missing credentials
    """
    api_key = os.getenv('VISUAL_CROSSING_API_KEY')
    username = os.getenv('VISUAL_CROSSING_USERNAME')
    
    if not api_key:
        logger.error("VISUAL_CROSSING_API_KEY not found in environment variables")
        return None
    
    try:
        client = VisualCrossingWeatherAPI(api_key, username)
        logger.info("Visual Crossing weather client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Visual Crossing client: {e}")
        return None
