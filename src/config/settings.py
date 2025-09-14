"""
Application settings and configuration for Fashion Store

This module defines configuration classes for the Fashion Store application,
handling environment-specific settings, database connections, and application
parameters. It uses environment variables for secure configuration management.

Configuration Features:
- Environment-based configuration inheritance
- Secure secret key management
- Database connection settings
- Machine learning model paths
- Logging configuration
- Development vs Production settings

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows configuration to be managed through environment variables
load_dotenv()

class Config:
    """
    Base configuration class for Fashion Store application
    
    This class contains all the default configuration settings used by
    the application. It reads values from environment variables with
    sensible defaults for development and testing.
    
    Configuration Categories:
    - Flask application settings
    - MongoDB database connection
    - Server host and port settings
    - Machine learning model paths
    - Logging configuration
    """
    
    # Flask application settings
    # Secret key used for session management and CSRF protection
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MongoDB database connection settings
    # URI for connecting to MongoDB instance
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ecommerce_db')
    
    # Application server settings
    # Host and port for the Flask development server
    HOST = os.getenv('HOST', '0.0.0.0')  # Listen on all interfaces
    PORT = int(os.getenv('PORT', 6600))  # Default port 6600
    
    # Machine learning model settings
    # Directories for storing trained models and data files
    MODELS_DIR = os.getenv('MODELS_DIR', 'models')  # Directory for ML models
    DATA_DIR = os.getenv('DATA_DIR', 'data')  # Directory for CSV data files
    
    # Logging configuration settings
    # Controls the verbosity and location of application logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # Default log level
    LOG_DIR = os.getenv('LOG_DIR', 'logs')  # Directory for log files

class DevelopmentConfig(Config):
    """
    Development configuration class
    
    This configuration is optimized for development work with:
    - Debug mode enabled for detailed error messages
    - Auto-reload enabled for code changes
    - Verbose logging for debugging
    - Development-specific settings
    """
    
    # Enable debug mode for development
    # This provides detailed error pages and auto-reload
    DEBUG = True
    
    # Set Flask environment to development
    # This affects how Flask handles certain features
    FLASK_ENV = 'development'
    
    # Use debug-level logging for development
    # This provides more detailed log information
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """
    Production configuration class
    
    This configuration is optimized for production deployment with:
    - Debug mode disabled for security
    - Minimal logging to reduce overhead
    - Production-specific optimizations
    - Security-focused settings
    """
    
    # Disable debug mode for production security
    # This prevents sensitive information from being exposed
    DEBUG = False
    
    # Set Flask environment to production
    # This enables production optimizations
    FLASK_ENV = 'production'
    
    # Use info-level logging for production
    # This reduces log verbosity while maintaining important information
    LOG_LEVEL = 'INFO'
