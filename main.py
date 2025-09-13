#!/usr/bin/env python3
"""
Fashion Store - AI-Powered E-commerce Application
Main application entry point for production
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app.factory import create_app
from src.config.settings import DevelopmentConfig, ProductionConfig
from src.utils.database import load_products_from_csv
from src.models import load_ml_models

def main():
    """Main application entry point"""
    
    # Determine configuration based on environment
    config_class = DevelopmentConfig if os.getenv('FLASK_ENV') == 'development' else ProductionConfig
    
    # Create Flask application
    app = create_app(config_class)
    
    # Load ML models
    if not load_ml_models():
        print("Warning: ML models not loaded. Review classification will not work.")
    
    # Load products from CSV
    load_products_from_csv()
    
    # Get configuration
    host = app.config['HOST']
    port = app.config['PORT']
    
    print(f"Starting Fashion Store Application")
    print(f"Application will be available at http://{host}:{port}")
    
    # Run application
    app.run(host=host, port=port, debug=app.config['DEBUG'])

if __name__ == '__main__':
    main()
