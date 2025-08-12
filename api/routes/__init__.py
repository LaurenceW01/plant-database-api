"""
API Routes for Plant Database API v2.3.6+

This package contains all the modularized route blueprints
organized by functional area.
"""

from .plants import plants_bp
from .logs import logs_bp  
from .analysis import analysis_bp
from .locations import locations_bp
from .photos import photos_bp

__all__ = [
    'plants_bp',
    'logs_bp', 
    'analysis_bp',
    'locations_bp',
    'photos_bp'
]

def register_all_blueprints(app):
    """Register all route blueprints with the Flask app"""
    app.register_blueprint(plants_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(analysis_bp) 
    app.register_blueprint(locations_bp)
    app.register_blueprint(photos_bp)

