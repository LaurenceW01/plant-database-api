"""
Core API modules for Plant Database API v2.2.0+

This package contains the core functionality and utilities
shared across the modularized API structure.
"""

from .middleware import setup_middleware
from .app_factory import create_app

__all__ = ['setup_middleware', 'create_app']

