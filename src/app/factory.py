"""
Flask application factory

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
    """Create and configure Flask application"""
    
    import os
    template_dir = os.path.abspath('templates')
    static_dir = os.path.abspath('static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    # Register Jinja2 filters
    app.jinja_env.filters['format_relative_time'] = format_relative_time
    
    # Setup logging
    setup_logging()
    
    # Register blueprints
    from .routes import main_bp, api_bp, auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)
    
    return app
