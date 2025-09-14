#!/usr/bin/env python3
"""
Fashion Store - AI-Powered E-commerce Application
Package entry point for development

This module serves as the development entry point for the Fashion Store application.
It initializes the Flask application, loads machine learning models, populates
the database with product data, and starts the development server.

The module handles:
- Environment-based configuration selection
- Flask application creation and configuration
- ML model loading and validation
- Database population from CSV data
- Development server startup

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import sys
import os

# Add parent directory to path for imports
# This allows importing modules from the src package
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import required modules for application initialization
from src.app.factory import create_app
from src.config.settings import DevelopmentConfig, ProductionConfig
from src.utils.database import load_products_from_csv
from src.models import load_ml_models

def main():
    """
    Main application entry point for development
    
    This function orchestrates the complete application startup process:
    1. Determines the appropriate configuration based on environment variables
    2. Creates and configures the Flask application
    3. Loads machine learning models for review classification
    4. Populates the database with product data from CSV files
    5. Starts the development server with appropriate settings
    
    The function handles both development and production configurations,
    ensuring the application starts correctly in different environments.
    """
    
    # Determine configuration based on environment
    # Uses DevelopmentConfig for development, ProductionConfig for production
    config_class = DevelopmentConfig if os.getenv('FLASK_ENV') == 'development' else ProductionConfig
    
    # Create Flask application with selected configuration
    # This initializes all blueprints, middleware, and application settings
    app = create_app(config_class)
    
    # Load ML models for review classification
    # These models are essential for the AI-powered review analysis feature
    if not load_ml_models():
        print("Warning: ML models not loaded. Review classification will not work.")
    
    # Load products from CSV file into the database
    # This populates the product catalog with clothing items and reviews
    load_products_from_csv()
    
    # Get server configuration from app config
    # These values determine where the application will be accessible
    host = app.config['HOST']
    port = app.config['PORT']
    
    # Display startup information to the user
    print(f"Starting Fashion Store Application (Development Mode)")
    print(f"Application will be available at http://{host}:{port}")
    
    # Run the Flask development server
    # debug=True enables auto-reload and detailed error pages
    app.run(host=host, port=port, debug=app.config['DEBUG'])

if __name__ == '__main__':
    # Only run main() when this script is executed directly
    # This prevents the code from running when imported as a module
    main()
