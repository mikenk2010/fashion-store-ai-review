#!/usr/bin/env python3
"""
Fashion Store - AI-Powered E-commerce Application
Main application entry point for production deployment

This module serves as the primary entry point for the Fashion Store application.
It initializes the Flask application, loads machine learning models, populates
the database with product data, and starts the web server.

The application follows a modular architecture with separate concerns for:
- Web application framework (Flask)
- Machine learning models (scikit-learn, spaCy)
- Database operations (MongoDB)
- Configuration management (Environment-based)

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import os
import sys

# Add src directory to Python path to enable module imports
# This allows importing modules from the src package structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import application components
from src.app.factory import create_app
from src.config.settings import DevelopmentConfig, ProductionConfig
from src.utils.database import load_products_from_csv
from src.models import load_ml_models

def main():
    """
    Main application entry point for the Fashion Store application.
    
    This function orchestrates the complete application startup process:
    1. Determines the appropriate configuration based on environment variables
    2. Creates and configures the Flask application instance
    3. Loads pre-trained machine learning models for review classification
    4. Populates the database with product data from CSV files
    5. Starts the web server with the specified host and port
    
    The application supports both development and production configurations,
    with different settings for debugging, logging, and performance optimization.
    
    Raises:
        ImportError: If required modules cannot be imported
        RuntimeError: If critical components fail to initialize
        ConnectionError: If database connection cannot be established
    
    Returns:
        None: This function runs the application server indefinitely
    """
    
    # Determine configuration class based on FLASK_ENV environment variable
    # Development mode enables debug features, detailed error messages, and auto-reload
    # Production mode optimizes for performance, security, and stability
    config_class = DevelopmentConfig if os.getenv('FLASK_ENV') == 'development' else ProductionConfig
    
    # Create Flask application instance with the selected configuration
    # The factory pattern allows for flexible configuration and testing
    app = create_app(config_class)
    
    # Load machine learning models for review classification
    # These models are essential for the AI-powered recommendation system
    # If models fail to load, the application continues but with limited functionality
    if not load_ml_models():
        print("Warning: ML models not loaded. Review classification will not work.")
        print("Please ensure model files are present in the models/ directory.")
    
    # Load product data from CSV file into the database
    # This populates the application with clothing items and their associated reviews
    # The data loading process includes data validation and transformation
    load_products_from_csv()
    
    # Extract server configuration from Flask app config
    # These values determine where the application will be accessible
    host = app.config['HOST']  # IP address to bind to (0.0.0.0 for all interfaces)
    port = app.config['PORT']  # Port number to listen on (6600 by default)
    
    # Display startup information to the console
    print(f"Starting Fashion Store Application")
    print(f"Application will be available at http://{host}:{port}")
    print(f"Environment: {'Development' if os.getenv('FLASK_ENV') == 'development' else 'Production'}")
    
    # Start the Flask development server
    # In production, this would typically be handled by a WSGI server like Gunicorn
    # The debug parameter controls detailed error pages and auto-reload functionality
    app.run(host=host, port=port, debug=app.config['DEBUG'])

# Standard Python idiom to ensure main() only runs when script is executed directly
# This prevents the main function from running when the module is imported
if __name__ == '__main__':
    main()
