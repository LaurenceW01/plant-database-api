"""
Baron Weather VelocityWeather API Client for GardenLLM (v2).
Uses the official VelocityWeather API with HMAC authentication.
"""

import logging
import requests
import time
import json
import base64
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BaronWeatherVelocityAPI:
    """Baron Weather VelocityWeather API client using HMAC auth"""
    
    def __init__(self, access_key: str, access_key_secret: str):
        """
        Initialize the Baron Weather scraper
        
        Args:
            access_key (str): Baron Weather access key
            access_key_secret (str): Baron Weather access key secret
        """
        self.access_key = access_key
        self.access_key_secret = access_key_secret
        self.host = "https://api.velocityweather.com/v1"  # Updated to use HTTPS
        self.session = requests.Session()
        
        # Houston coordinates (more precise)
        self.houston_lat = 29.827119
        self.houston_lon = -95.472232
        
        # Houston timezone (Central Daylight Time)
        self.houston_tz = timezone(timedelta(hours=-5))  # CDT (UTC-5)
        
        # Cache for storing scraped data
        self.cache = {}
        self.cache_timeout = 15 * 60  # 15 minutes in seconds
        
        # Set headers for API requests
        self.session.headers.update({
            'User-Agent': 'GardenLLM/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        
        # Request delay to be respectful
        self.last_request_time = 0
        self.min_request_delay = 1  # Minimum 1 second between requests
    
    def _sign(self, string_to_sign: str, secret: str) -> str:
        """
        Returns the signature for string_to_sign using HMAC-SHA1
        
        Args:
            string_to_sign (str): String to sign
            secret (str): Secret key
            
        Returns:
            str: Base64 encoded signature
        """
        return base64.urlsafe_b64encode(
            hmac.new(
                secret.encode('utf-8'), 
                string_to_sign.encode('utf-8'), 
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
    
    def _sign_request(self, url: str) -> str:
        """
        Returns signed URL with HMAC authentication
        
        Args:
            url (str): Base URL to sign
            
        Returns:
            str: Signed URL with authentication parameters
        """
        ts = str(int(time.time()))
        sig = self._sign(self.access_key + ":" + ts, self.access_key_secret)
        
        # Add signature parameters to URL
        separator = '?' if '?' not in url else '&'
        signed_url = f"{url}{separator}sig={sig}&ts={ts}"
        
        return signed_url
    
    def _respectful_request(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
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
            
            logger.info(f"Making request to: {url}")
            response = self.session.get(url, timeout=timeout)
            self.last_request_time = time.time()
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
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
        Get current weather conditions from Baron Weather API
        
        Returns:
            Optional[Dict[str, Any]]: Current weather data or None if error
        """
        cache_key = "current_weather"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Use the METAR nearest endpoint for current conditions
            uri = f"/reports/metar/nearest.json?lat={self.houston_lat}&lon={self.houston_lon}&within_radius=500&max_age=75"
            url = f"{self.host}/{self.access_key}{uri}"
            signed_url = self._sign_request(url)
            
            response = self._respectful_request(signed_url)
            if not response:
                return None
            
            data = response.json()
            logger.info("Successfully retrieved current weather from Baron Weather API")
            
            # Parse the METAR response
            current_weather = self._parse_metar_current(data)
            if current_weather:
                self._set_cached_data(cache_key, current_weather)
                return current_weather
            
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
        
        # No fallback data - return None if API is not available
        logger.warning("Baron Weather API is not available - no weather data provided")
        return None
    
    def get_hourly_forecast(self, hours: int = 24) -> Optional[List[Dict[str, Any]]]:
        """
        Get hourly forecast from Baron Weather API
        
        Args:
            hours (int): Number of hours to forecast
            
        Returns:
            Optional[List[Dict[str, Any]]]: Hourly forecast data or None if error
        """
        cache_key = f"hourly_forecast_{hours}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Use the NDFD hourly forecast endpoint with hours parameter
            uri = f"/reports/ndfd/hourly.json?lat={self.houston_lat}&lon={self.houston_lon}&hours={hours}"
            url = f"{self.host}/{self.access_key}{uri}"
            signed_url = self._sign_request(url)
            
            response = self._respectful_request(signed_url)
            if not response:
                return None
            
            data = response.json()
            logger.info("Successfully retrieved hourly forecast from Baron Weather API")
            logger.debug(f"Raw API response: {json.dumps(data, indent=2)}")
            
            # Check response structure
            if 'ndfd_hourly' not in data:
                logger.warning(f"Missing 'ndfd_hourly' in response: {data.keys()}")
                return None
                
            if 'data' not in data['ndfd_hourly']:
                logger.warning(f"Missing 'data' in ndfd_hourly: {data['ndfd_hourly'].keys()}")
                return None
            
            # Parse the NDFD response
            hourly_data = self._parse_ndfd_hourly(data, hours)
            if hourly_data:
                self._set_cached_data(cache_key, hourly_data)
                return hourly_data
            
        except Exception as e:
            logger.error(f"Error getting hourly forecast: {e}")
            if 'response' in locals():
                try:
                    logger.error(f"Response status: {response.status_code}")
                    logger.error(f"Response text: {response.text}")
                except:
                    pass
        
        # No fallback data - return None if API is not available
        logger.warning("Baron Weather API is not available - no hourly forecast data provided")
        return None
    
    def get_daily_forecast(self, days: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get daily forecast from Baron Weather API
        
        Args:
            days (int): Number of days to forecast (default 10, max 10)
            
        Returns:
            Optional[List[Dict[str, Any]]]: Daily forecast data or None if error
        """
        cache_key = f"daily_forecast_{days}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Use the NDFD daily forecast endpoint
            uri = f"/reports/ndfd/daily.json?lat={self.houston_lat}&lon={self.houston_lon}&days={days}"
            url = f"{self.host}/{self.access_key}{uri}"
            signed_url = self._sign_request(url)
            
            response = self._respectful_request(signed_url)
            if not response:
                return None
            
            data = response.json()
            logger.info("Successfully retrieved daily forecast from Baron Weather API")
            logger.debug(f"Raw API response: {json.dumps(data, indent=2)}")
            
            # Check response structure
            if 'ndfd_daily' not in data:
                logger.warning(f"Missing 'ndfd_daily' in response: {data.keys()}")
                return None
                
            if 'data' not in data['ndfd_daily']:
                logger.warning(f"Missing 'data' in ndfd_daily: {data['ndfd_daily'].keys()}")
                return None
            
            # Parse the NDFD response
            daily_data = self._parse_ndfd_daily(data, days)
            if daily_data:
                self._set_cached_data(cache_key, daily_data)
                return daily_data
            
        except Exception as e:
            logger.error(f"Error getting daily forecast: {e}")
            if 'response' in locals():
                try:
                    logger.error(f"Response status: {response.status_code}")
                    logger.error(f"Response text: {response.text}")
                except:
                    pass
        
        # No fallback data - return None if API is not available
        logger.warning("Baron Weather API is not available - no daily forecast data provided")
        return None

    def _parse_metar_current(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse current weather data from METAR response
        
        Args:
            data (Dict[str, Any]): Raw METAR API response
            
        Returns:
            Optional[Dict[str, Any]]: Parsed current weather data
        """
        try:
            # The API response structure is: {"metars": {"data": {...}}}
            if 'metars' in data and 'data' in data['metars']:
                metar = data['metars']['data']
            else:
                logger.warning("Unexpected METAR response structure")
                return None
            
            # Extract temperature (convert from Celsius to Fahrenheit)
            temp_data = metar.get('temperature', {})
            temp_c = temp_data.get('value')
            if temp_c is not None:
                temp_f = (temp_c * 9/5) + 32
            else:
                temp_f = 75.0
            
            # Extract humidity
            humidity_data = metar.get('relative_humidity', {})
            humidity = humidity_data.get('value', 60)
            
            # Extract wind speed (convert from m/s to mph)
            wind_data = metar.get('wind', {})
            wind_mps = wind_data.get('speed')
            if wind_mps is not None:
                wind_mph = wind_mps * 2.23694  # Convert m/s to mph
            else:
                wind_mph = 5.0
            
            # Extract pressure (convert from hPa to mb - they're the same unit)
            pressure_data = metar.get('pressure', {})
            pressure = pressure_data.get('value', 1013)
            
            # Extract visibility (convert from meters to miles)
            visibility_data = metar.get('visibility', {})
            visibility_m = visibility_data.get('value')
            if visibility_m is not None:
                visibility = visibility_m * 0.000621371  # Convert meters to miles
            else:
                visibility = 10
            
            # Extract weather description from weather code
            weather_code_data = metar.get('weather_code', {})
            weather_text = weather_code_data.get('text', '')
            
            # Extract cloud cover
            cloud_data = metar.get('cloud_cover', {})
            cloud_text = cloud_data.get('text', '')
            
            # Extract raw METAR for additional context
            raw_metar = metar.get('raw_metar', '')
            
            # Determine the best weather description
            description = self._determine_weather_description(weather_text, cloud_text, raw_metar)
            
            # Extract precipitation chance from weather code
            precip_chance = 0
            if 'rain' in weather_text.lower() or 'shower' in weather_text.lower():
                precip_chance = 70
            elif 'drizzle' in weather_text.lower():
                precip_chance = 40
            elif 'thunderstorm' in weather_text.lower():
                precip_chance = 90
            
            houston_now = datetime.now(self.houston_tz)
            return {
                'temperature': round(float(temp_f), 1),
                'humidity': int(humidity) if isinstance(humidity, (int, float)) else 60,
                'description': description,
                'wind_speed': round(wind_mph),
                'precipitation_chance': precip_chance
            }
            
        except Exception as e:
            logger.error(f"Error parsing METAR current data: {e}")
            return None
    
    def _determine_weather_description(self, weather_text: str, cloud_text: str, raw_metar: str) -> str:
        """
        Determine the best weather description from METAR data
        
        Args:
            weather_text (str): Weather code text from API
            cloud_text (str): Cloud cover text from API
            raw_metar (str): Raw METAR string
            
        Returns:
            str: Best weather description
        """
        # Priority order: weather conditions > cloud cover > default
        
        # Check for significant weather conditions first
        if weather_text:
            weather_lower = weather_text.lower()
            if 'thunderstorm' in weather_lower:
                return "Thunderstorms"
            elif 'rain' in weather_lower or 'shower' in weather_lower:
                return "Rain"
            elif 'snow' in weather_lower:
                return "Snow"
            elif 'fog' in weather_lower or 'mist' in weather_lower:
                return "Fog"
            elif 'haze' in weather_lower:
                return "Hazy"
            elif 'drizzle' in weather_lower:
                return "Drizzle"
        
        # Check cloud cover if no significant weather
        if cloud_text:
            cloud_lower = cloud_text.lower()
            if 'overcast' in cloud_lower:
                return "Cloudy"
            elif 'broken' in cloud_lower:
                return "Partly Cloudy"
            elif 'scattered' in cloud_lower:
                return "Partly Cloudy"
            elif 'clear' in cloud_lower:
                return "Clear"
            elif 'few' in cloud_lower:
                return "Mostly Clear"
        
        # Parse raw METAR for additional context
        if raw_metar:
            raw_lower = raw_metar.lower()
            if 'br' in raw_lower:  # Mist/fog
                return "Mist"
            elif 'fg' in raw_lower:  # Fog
                return "Fog"
            elif 'ra' in raw_lower:  # Rain
                return "Rain"
            elif 'ts' in raw_lower:  # Thunderstorm
                return "Thunderstorms"
            elif 'sn' in raw_lower:  # Snow
                return "Snow"
            elif 'dz' in raw_lower:  # Drizzle
                return "Drizzle"
            elif 'hz' in raw_lower:  # Haze
                return "Hazy"
            elif 'clr' in raw_lower or 'skc' in raw_lower:  # Clear
                return "Clear"
            elif 'bkn' in raw_lower:  # Broken
                return "Partly Cloudy"
            elif 'ovc' in raw_lower:  # Overcast
                return "Cloudy"
            elif 'sct' in raw_lower:  # Scattered
                return "Partly Cloudy"
            elif 'few' in raw_lower:  # Few clouds
                return "Mostly Clear"
        
        # Default fallback
        return "Partly Cloudy"
    
    def _parse_ndfd_hourly(self, data: Dict[str, Any], hours: int) -> Optional[List[Dict[str, Any]]]:
        """
        Parse hourly forecast data from NDFD response
        
        Args:
            data (Dict[str, Any]): Raw NDFD API response
            hours (int): Number of hours requested
            
        Returns:
            Optional[List[Dict[str, Any]]]: Parsed hourly forecast data
        """
        try:
            # Log the raw response for debugging
            logger.debug(f"Raw NDFD response: {data}")
            
            # The API response structure is: {"ndfd_hourly": {"data": [...]}}
            if 'ndfd_hourly' in data and 'data' in data['ndfd_hourly']:
                forecast_data = data['ndfd_hourly']['data']
            else:
                logger.warning(f"Unexpected NDFD response structure. Keys: {data.keys()}")
                return None
            
            # Multiple hours returned by API
            hourly_data = []
            for i, hour_forecast in enumerate(forecast_data):
                if i >= hours:  # Limit to requested hours
                    break
                
                # Extract temperature (convert from Celsius to Fahrenheit)
                temp_data = hour_forecast.get('temperature', {})
                temp_c = temp_data.get('value')
                if temp_c is not None:
                    temp_f = (temp_c * 9/5) + 32
                else:
                    temp_f = 75.0
                
                # Extract precipitation probability
                precip_data = hour_forecast.get('precipitation', {})
                precip_prob = precip_data.get('probability', {}).get('value', 0)
                
                # Extract wind speed (convert from m/s to mph)
                wind_data = hour_forecast.get('wind', {})
                wind_mps = wind_data.get('speed')
                if wind_mps is not None:
                    wind_mph = wind_mps * 2.23694
                else:
                    wind_mph = 5.0
                
                # Extract weather description
                weather_code_data = hour_forecast.get('weather_code', {})
                weather_text = weather_code_data.get('text', 'Partly cloudy')
                
                # Extract cloud cover
                cloud_data = hour_forecast.get('cloud_cover', {})
                cloud_text = cloud_data.get('text', 'Partly cloudy')
                
                # Use weather text if available, otherwise cloud cover
                description = weather_text if weather_text else cloud_text
                
                # Calculate time for this hour - start at the next hour
                current_time = datetime.now(self.houston_tz)
                # Round up to the next hour
                next_hour = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                hour_time = next_hour + timedelta(hours=i)
                
                hourly_data.append({
                    'time': hour_time.strftime('%I %p').replace(' 0', ' '),
                    'temperature': round(temp_f, 1),
                    'precipitation_chance': round(precip_prob),
                    'description': description,
                    'wind_speed': round(wind_mph)
                })
            
            logger.info(f"Successfully parsed {len(hourly_data)} hourly entries from NDFD API")
            return hourly_data
            
        except Exception as e:
            logger.error(f"Error parsing NDFD hourly data: {e}")
            return None

    def _parse_ndfd_daily(self, data: Dict[str, Any], days: int) -> Optional[List[Dict[str, Any]]]:
        """
        Parse daily forecast data from NDFD response
        
        Args:
            data (Dict[str, Any]): Raw NDFD API response
            days (int): Number of days requested
            
        Returns:
            Optional[List[Dict[str, Any]]]: Parsed daily forecast data
        """
        try:
            # Log the raw response for debugging
            logger.debug(f"Raw NDFD daily response: {data}")
            
            # The API response structure is: {"ndfd_daily": {"data": [...]}}
            if 'ndfd_daily' in data and 'data' in data['ndfd_daily']:
                forecast_data = data['ndfd_daily']['data']
            else:
                logger.warning(f"Unexpected NDFD daily response structure. Keys: {data.keys()}")
                return None
            
            # Multiple days returned by API
            daily_data = []
            for i, day_forecast in enumerate(forecast_data):
                if i >= days:  # Limit to requested days
                    break
                
                # Extract temperatures (convert from Celsius to Fahrenheit)
                temp_data = day_forecast.get('temperature', {})
                high_c = temp_data.get('max', {}).get('value')
                low_c = temp_data.get('min', {}).get('value')
                
                high_f = (high_c * 9/5) + 32 if high_c is not None else 75.0
                low_f = (low_c * 9/5) + 32 if low_c is not None else 55.0
                
                # Extract precipitation probability
                precip_data = day_forecast.get('precipitation', {})
                precip_prob = precip_data.get('probability', {}).get('value', 0)
                
                # Extract wind speed (convert from m/s to mph)
                wind_data = day_forecast.get('wind', {})
                wind_mps = wind_data.get('speed', {}).get('value')
                wind_mph = wind_mps * 2.23694 if wind_mps is not None else 5.0
                
                # Extract weather description
                weather_code_data = day_forecast.get('weather_code', {})
                weather_text = weather_code_data.get('text', 'Partly cloudy')
                
                # Extract cloud cover
                cloud_data = day_forecast.get('cloud_cover', {})
                cloud_text = cloud_data.get('text', 'Partly cloudy')
                
                # Use weather text if available, otherwise cloud cover
                description = weather_text if weather_text else cloud_text
                
                # Extract sunrise/sunset times
                sun_data = day_forecast.get('sun', {})
                sunrise = sun_data.get('rise')
                sunset = sun_data.get('set')
                
                # Calculate date for this day
                current_time = datetime.now(self.houston_tz)
                forecast_date = current_time.date() + timedelta(days=i)
                
                daily_data.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'high_temp': round(high_f),
                    'low_temp': round(low_f),
                    'precipitation_chance': round(precip_prob),
                    'description': description,
                    'wind_speed': round(wind_mph),
                    'sunrise': sunrise,
                    'sunset': sunset
                })
            
            logger.info(f"Successfully parsed {len(daily_data)} daily entries from NDFD API")
            return daily_data
            
        except Exception as e:
            logger.error(f"Error parsing NDFD daily data: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if Baron Weather API is available
        
        Returns:
            bool: True if available, False otherwise
        """
        try:
            # Test with a simple METAR request
            uri = f"/reports/metar/nearest.json?lat={self.houston_lat}&lon={self.houston_lon}&within_radius=500&max_age=75"
            url = f"{self.host}/{self.access_key}{uri}"
            signed_url = self._sign_request(url)
            
            response = self._respectful_request(signed_url)
            return response is not None and response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
    
    def _get_houston_time(self) -> datetime:
        """Get current time in Houston timezone"""
        return datetime.now(self.houston_tz) 