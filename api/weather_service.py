"""
Weather service implementation for the Plant Database API.
Provides unified weather endpoint with current conditions, forecasts, and rainfall data.
"""

from flask import jsonify, request
from utils.baron_weather_velocity_api import BaronWeatherVelocityAPI
from utils.harris_county_rainfall import get_harris_county_rainfall
from config.config import BARON_API_KEY, BARON_API_SECRET
import logging

# Initialize Baron Weather client with error handling
try:
    baron_client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)
    logging.info("✅ Baron Weather client initialized successfully")
except Exception as e:
    logging.error(f"❌ Failed to initialize Baron Weather client: {e}")
    baron_client = None

def get_current_weather():
    """Get current weather conditions for Houston"""
    try:
        if baron_client is None:
            return jsonify({
                'error': 'Weather service not configured. Baron Weather API credentials may be missing.',
                'fallback_advice': 'Continue with general care recommendations. Check local weather manually.'
            }), 503
            
        weather_data = baron_client.get_current_weather()
        if weather_data is None:
            return jsonify({
                'error': 'Weather service temporarily unavailable. The external weather API may be experiencing delays or connectivity issues.',
                'fallback_advice': 'Continue with general care recommendations. Check local weather manually.'
            }), 503
            
        return jsonify(weather_data), 200
        
    except Exception as e:
        logging.error(f"Error getting current weather: {e}")
        return jsonify({
            'error': 'Weather service error - this may be due to external API timeout or connectivity issues.',
            'technical_details': str(e),
            'fallback_advice': 'Continue with general care recommendations. Check local weather manually.'
        }), 500

def get_weather_forecast():
    """Get hourly weather forecast for Houston"""
    try:
        if baron_client is None:
            return jsonify({
                'error': 'Weather service not configured. Baron Weather API credentials may be missing.',
                'fallback_advice': 'Continue with general care recommendations. Check local weather manually.'
            }), 503
            
        # Handle both query parameters and JSON body parameters
        # Check query parameters first
        hours = request.args.get('hours', type=int)
        
        # If not in query params, check JSON body
        if hours is None and request.is_json:
            json_data = request.get_json()
            if json_data:
                hours = json_data.get('hours', type=int)
        
        # Set default if still None
        if hours is None:
            hours = 24
            
        if hours < 1 or hours > 48:
            return jsonify({
                'error': 'Hours parameter must be between 1 and 48'
            }), 400
            
        forecast_data = baron_client.get_hourly_forecast(hours)
        if forecast_data is None:
            return jsonify({
                'error': 'Weather service temporarily unavailable'
            }), 503
            
        return jsonify({
            'forecast': forecast_data
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting weather forecast: {e}")
        return jsonify({
            'error': 'Internal server error while fetching forecast data'
        }), 500

def get_daily_forecast():
    """Get 10-day weather forecast for Houston"""
    try:
        if baron_client is None:
            return jsonify({
                'error': 'Weather service not configured. Baron Weather API credentials may be missing.',
                'fallback_advice': 'Continue with general care recommendations. Check local weather manually.'
            }), 503
            
        # Handle both query parameters and JSON body parameters
        # Check query parameters first
        days = request.args.get('days', type=int)
        
        # If not in query params, check JSON body
        if days is None and request.is_json:
            json_data = request.get_json()
            if json_data:
                days = json_data.get('days', type=int)
        
        # Set default if still None
        if days is None:
            days = 7  # Changed default to 7 to match ChatGPT schema
            
        if days < 1 or days > 10:
            return jsonify({
                'error': 'Days parameter must be between 1 and 10'
            }), 400
            
        forecast_data = baron_client.get_daily_forecast(days)
        if forecast_data is None:
            return jsonify({
                'error': 'Weather service temporarily unavailable'
            }), 503
            
        return jsonify({
            'forecast': forecast_data
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting daily forecast: {e}")
        return jsonify({
            'error': 'Internal server error while fetching forecast data'
        }), 500

def get_unified_weather():
    """
    Unified weather endpoint that can provide current conditions, forecasts, and rainfall data.
    
    Query Parameters:
        include_current (bool): Include current weather conditions (default: True)
        include_hourly (bool): Include hourly forecast (default: False)
        hours (int): Number of hours to forecast when include_hourly=True (default: 24, max: 48)
        include_daily (bool): Include daily forecast (default: False)
        days (int): Number of days to forecast when include_daily=True (default: 7, max: 10)
        rainfall_days (int): Number of days for rainfall total calculation (default: 7, max: 30)
        include_rainfall (bool): Include Harris County rainfall data (default: False)
    """
    try:
        # Parse query parameters with defaults
        include_current = request.args.get('include_current', 'true').lower() == 'true'
        include_hourly = request.args.get('include_hourly', 'false').lower() == 'true'
        include_daily = request.args.get('include_daily', 'false').lower() == 'true'
        include_rainfall = request.args.get('include_rainfall', 'false').lower() == 'true'
        
        # Parse numeric parameters
        hours = request.args.get('hours', 24, type=int)
        days = request.args.get('days', 7, type=int)
        rainfall_days = request.args.get('rainfall_days', 7, type=int)
        
        # Validate parameters
        if hours < 1 or hours > 48:
            return jsonify({
                'error': 'Hours parameter must be between 1 and 48'
            }), 400
            
        if days < 1 or days > 10:
            return jsonify({
                'error': 'Days parameter must be between 1 and 10'
            }), 400
            
        if rainfall_days < 1 or rainfall_days > 30:
            return jsonify({
                'error': 'Rainfall days parameter must be between 1 and 30'
            }), 400
        
        # Initialize response data
        response_data = {
            'success': True,
            'timestamp': baron_client.get_current_timestamp() if baron_client and hasattr(baron_client, 'get_current_timestamp') else None
        }
        
        # Get current weather if requested
        if include_current:
            if baron_client is None:
                response_data['current_weather'] = None
                response_data['current_weather_error'] = 'Weather service not configured - Baron Weather API credentials may be missing'
            else:
                current_weather = baron_client.get_current_weather()
                if current_weather is None:
                    response_data['current_weather'] = None
                    response_data['current_weather_error'] = 'Weather service temporarily unavailable'
                else:
                    response_data['current_weather'] = current_weather
        
        # Get hourly forecast if requested
        if include_hourly:
            if baron_client is None:
                response_data['hourly_forecast'] = None
                response_data['hourly_forecast_error'] = 'Weather service not configured - Baron Weather API credentials may be missing'
            else:
                hourly_forecast = baron_client.get_hourly_forecast(hours)
                if hourly_forecast is None:
                    response_data['hourly_forecast'] = None
                    response_data['hourly_forecast_error'] = 'Hourly forecast temporarily unavailable'
                else:
                    response_data['hourly_forecast'] = hourly_forecast
                    response_data['hourly_forecast_hours'] = hours
        
        # Get daily forecast if requested
        if include_daily:
            if baron_client is None:
                response_data['daily_forecast'] = None
                response_data['daily_forecast_error'] = 'Weather service not configured - Baron Weather API credentials may be missing'
            else:
                daily_forecast = baron_client.get_daily_forecast(days)
                if daily_forecast is None:
                    response_data['daily_forecast'] = None
                    response_data['daily_forecast_error'] = 'Daily forecast temporarily unavailable'
                else:
                    response_data['daily_forecast'] = daily_forecast
                    response_data['daily_forecast_days'] = days
        
        # Get Harris County rainfall data if requested
        if include_rainfall:
            try:
                rainfall_total = get_harris_county_rainfall(days=rainfall_days)
                if rainfall_total is not None:
                    response_data['rainfall_data'] = {
                        'total_inches': round(rainfall_total, 2),
                        'period_days': rainfall_days,
                        'source': 'Harris County Flood Warning System',
                        'location': 'Cole Creek @ Deihl Road (Station 590)'
                    }
                else:
                    response_data['rainfall_data'] = None
                    response_data['rainfall_error'] = 'Harris County rainfall data temporarily unavailable'
            except Exception as e:
                logging.error(f"Error getting rainfall data: {e}")
                response_data['rainfall_data'] = None
                response_data['rainfall_error'] = 'Error retrieving rainfall data'
        
        # Check if we got any data
        has_data = any([
            response_data.get('current_weather'),
            response_data.get('hourly_forecast'),
            response_data.get('daily_forecast'),
            response_data.get('rainfall_data')
        ])
        
        if not has_data and (include_current or include_hourly or include_daily or include_rainfall):
            return jsonify({
                'error': 'All requested weather services are temporarily unavailable',
                'fallback_advice': 'Continue with general care recommendations. Check local weather manually.'
            }), 503
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"Error in unified weather endpoint: {e}")
        return jsonify({
            'error': 'Weather service error - this may be due to external API timeout or connectivity issues.',
            'technical_details': str(e),
            'fallback_advice': 'Continue with general care recommendations. Check local weather manually.'
        }), 500

def register_weather_routes(app, limiter):
    """Register weather API routes"""
    
    # NEW: Unified weather endpoint (primary endpoint for ChatGPT)
    @app.route('/api/weather', methods=['GET'])
    @limiter.limit('60 per minute')  # More generous limit for weather endpoints
    def unified_weather():
        return get_unified_weather()
    
    # LEGACY: Current weather endpoint (preserved for backward compatibility)
    @app.route('/api/weather/current', methods=['GET'])
    @limiter.limit('60 per minute')  # More generous limit for weather endpoints
    def current_weather():
        return get_current_weather()
    
    # LEGACY: Hourly forecast endpoint (preserved for backward compatibility)
    @app.route('/api/weather/forecast', methods=['GET'])
    @limiter.limit('60 per minute')
    def weather_forecast():
        return get_weather_forecast()
        
    # LEGACY: Daily forecast endpoint (preserved for backward compatibility)
    @app.route('/api/weather/forecast/daily', methods=['GET'])
    @limiter.limit('60 per minute')
    def daily_forecast():
        return get_daily_forecast() 