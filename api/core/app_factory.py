"""
Flask App Factory

Creates and configures the Flask application with all necessary
components including rate limiting, CORS, and blueprint registration.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .middleware import setup_middleware
from ..routes import register_all_blueprints


def create_app(testing=False):
    """
    Create and configure the Flask app. If testing=True, disables rate limiting.
    
    This replaces the original create_app function from main.py, but with
    modularized route registration.
    
    Args:
        testing (bool): Whether to run in testing mode (disables rate limiting)
        
    Returns:
        Flask: Configured Flask application
    """
    # Get the project root directory (two levels up from this file)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    template_folder = os.path.join(project_root, 'templates')
    
    app = Flask(__name__, template_folder=template_folder)
    
    # CORS configuration
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/upload/*": {"origins": "*"}
    })
    
    # Rate limiting setup
    if not testing and not app.config.get('TESTING', False):
        # Production: Use Redis if available, otherwise in-memory
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            limiter = Limiter(
                key_func=get_remote_address,
                app=app,
                default_limits=[],
                storage_uri=redis_url
            )
        else:
            limiter = Limiter(
                key_func=get_remote_address,
                app=app,
                default_limits=[]
            )
            logging.warning("REDIS_URL not set. Using in-memory rate limiting. Set REDIS_URL for production.")
    else:
        # Testing: Use simple in-memory storage without warnings
        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            default_limits=[]
        )
    
    # Set up logging
    logger = logging.getLogger()
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    # Setup middleware (field normalization, etc.)
    setup_middleware(app)
    
    # Register all blueprints
    register_all_blueprints(app)
    
    # Register remaining non-modularized routes and components
    register_legacy_components(app, limiter)
    
    # Add cache-busting headers to prevent CloudFlare caching issues
    @app.after_request
    def add_cache_headers(response):
        """Add headers to prevent aggressive caching of API responses"""
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    logging.info("✅ Flask app created and configured successfully")
    logging.info(f"✅ Testing mode: {testing}")
    logging.info(f"✅ Rate limiting: {'disabled' if testing else 'enabled'}")
    
    return app


def register_legacy_components(app, limiter):
    """
    Register components that haven't been modularized yet.
    This is a temporary function to maintain compatibility during migration.
    """
    # Import and register weather routes
    try:
        from api.weather_service import register_weather_routes
        register_weather_routes(app, limiter)
        logging.info("✅ Weather routes registered")
    except ImportError:
        logging.warning("⚠️ Weather service not available")
    
    # Register any remaining image analysis routes
    try:
        from api.main import register_image_analysis_route, require_api_key
        register_image_analysis_route(app, limiter, require_api_key)
        logging.info("✅ Image analysis routes registered")
    except ImportError:
        logging.warning("⚠️ Image analysis routes not available")
    
    # Register any remaining plant log routes that weren't modularized
    try:
        from api.main import register_plant_log_routes, require_api_key
        register_plant_log_routes(app, limiter, require_api_key)
        logging.info("✅ Legacy plant log routes registered")
    except ImportError:
        logging.warning("⚠️ Legacy plant log routes not available")
    
    # Register any remaining plant routes that weren't modularized  
    try:
        from api.main import register_plant_routes, require_api_key
        register_plant_routes(app, limiter, require_api_key)
        logging.info("✅ Legacy plant routes registered")
    except ImportError:
        logging.warning("⚠️ Legacy plant routes not available")

