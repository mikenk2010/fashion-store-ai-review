"""
Flask application factory for Fashion Store

This module implements the Flask application factory pattern, providing
a centralized way to create and configure the Fashion Store application
instance. It handles all application initialization, configuration,
and component registration.

Key Features:
- Application factory pattern for flexible configuration
- Blueprint registration for modular route organization
- Jinja2 filter registration for template functionality
- Logging system initialization
- Configuration management
- Template and static file path resolution

Application Components:
- Main routes (product browsing, details, reviews)
- API routes (AJAX endpoints, ML predictions)
- Authentication routes (login, register, profile)
- Custom Jinja2 filters for template rendering
- Comprehensive logging system

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

from flask import Flask
from ..config.settings import Config
from ..config.logging_config import setup_logging
from ..utils.helpers import format_relative_time

def create_app(config_class=Config):
    """
    Create and configure Flask application instance
    
    This function implements the Flask application factory pattern,
    creating a new Flask application instance with all necessary
    configurations, blueprints, and extensions registered.
    
    The factory pattern allows for:
    - Flexible configuration management
    - Easy testing with different configurations
    - Modular application structure
    - Clean separation of concerns
    
    Args:
        config_class: Configuration class to use (defaults to Config)
        
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Resolve template and static file directories
    # These paths are resolved relative to the application root
    import os
    template_dir = os.path.abspath('templates')
    static_dir = os.path.abspath('static')
    
    # Create Flask application instance with custom directories
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load configuration from the specified config class
    app.config.from_object(config_class)
    
    # Register custom Jinja2 filters for template functionality
    # These filters extend Jinja2's built-in functionality
    app.jinja_env.filters['format_relative_time'] = format_relative_time
    
    # Initialize the application logging system
    # This sets up file logging, console logging, and log rotation
    setup_logging()
    
    # Register application blueprints for modular route organization
    # Each blueprint handles a specific aspect of the application
    from .routes import main_bp, api_bp, auth_bp
    app.register_blueprint(main_bp)  # Main application routes
    app.register_blueprint(api_bp, url_prefix='/api')  # API endpoints
    app.register_blueprint(auth_bp)  # Authentication routes
    
    return app
