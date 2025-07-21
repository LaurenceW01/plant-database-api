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
                'error': 'Weather service temporarily unavailable'
            }), 503
            
        return jsonify(weather_data), 200
        
    except Exception as e:
        logging.error(f"Error getting current weather: {e}")
        return jsonify({
            'error': 'Internal server error while fetching weather data'
        }), 500

def get_weather_forecast():
    """Get hourly weather forecast for Houston"""
    try:
        hours = request.args.get('hours', default=24, type=int)
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

def register_weather_routes(app, limiter):
    """Register weather API routes"""
    
    # Current weather endpoint
    @app.route('/api/weather/current', methods=['GET'])
    @limiter.limit('60 per minute')  # More generous limit for weather endpoints
    def current_weather():
        return get_current_weather()
    
    # Weather forecast endpoint
    @app.route('/api/weather/forecast', methods=['GET'])
    @limiter.limit('60 per minute')
    def weather_forecast():
        return get_weather_forecast() 