"""
Weather service implementation for the Plant Database API.
Provides current weather and forecast data from Baron Weather API.
"""

from flask import jsonify, request
from utils.baron_weather_velocity_api import BaronWeatherVelocityAPI
from config.config import BARON_API_KEY, BARON_API_SECRET
import logging

# Initialize Baron Weather client
baron_client = BaronWeatherVelocityAPI(BARON_API_KEY, BARON_API_SECRET)

def get_current_weather():
    """Get current weather conditions for Houston"""
    try:
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

def register_weather_routes(app, limiter):
    """Register weather API routes"""
    
    # Current weather endpoint
    @app.route('/api/weather/current', methods=['GET'])
    @limiter.limit('60 per minute')  # More generous limit for weather endpoints
    def current_weather():
        return get_current_weather()
    
    # Hourly forecast endpoint
    @app.route('/api/weather/forecast', methods=['GET'])
    @limiter.limit('60 per minute')
    def weather_forecast():
        return get_weather_forecast()
        
    # Daily forecast endpoint (supports both query params and JSON body)
    @app.route('/api/weather/forecast/daily', methods=['GET'])
    @limiter.limit('60 per minute')
    def daily_forecast():
        return get_daily_forecast() 