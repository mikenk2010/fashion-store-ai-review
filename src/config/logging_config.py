#!/usr/bin/env python3
"""
Comprehensive logging configuration for Fashion Store application

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import logging
import logging.handlers
import os
from datetime import datetime
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle ObjectId and other non-serializable objects"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def setup_logging():
    """Set up comprehensive logging for the application"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # 2. General application log file (DEBUG and above)
    app_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_handler)
    
    # 3. Error log file (ERROR and above)
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # 4. ML training log file
    ml_handler = logging.handlers.RotatingFileHandler(
        'logs/ml_training.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    ml_handler.setLevel(logging.INFO)
    ml_handler.setFormatter(detailed_formatter)
    
    # Create ML logger
    ml_logger = logging.getLogger('ml_training')
    ml_logger.setLevel(logging.INFO)
    ml_logger.addHandler(ml_handler)
    ml_logger.addHandler(console_handler)
    ml_logger.propagate = False
    
    # 5. API requests log file
    api_handler = logging.handlers.RotatingFileHandler(
        'logs/api_requests.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(detailed_formatter)
    
    # Create API logger
    api_logger = logging.getLogger('api_requests')
    api_logger.setLevel(logging.INFO)
    api_logger.addHandler(api_handler)
    api_logger.propagate = False
    
    # 6. Database operations log file
    db_handler = logging.handlers.RotatingFileHandler(
        'logs/database.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(detailed_formatter)
    
    # Create DB logger
    db_logger = logging.getLogger('database')
    db_logger.setLevel(logging.INFO)
    db_logger.addHandler(db_handler)
    db_logger.propagate = False
    
    # 7. User actions log file
    user_handler = logging.handlers.RotatingFileHandler(
        'logs/user_actions.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    user_handler.setLevel(logging.INFO)
    user_handler.setFormatter(detailed_formatter)
    
    # Create User logger
    user_logger = logging.getLogger('user_actions')
    user_logger.setLevel(logging.INFO)
    user_logger.addHandler(user_handler)
    user_logger.propagate = False
    
    return {
        'app': root_logger,
        'ml_training': ml_logger,
        'api_requests': api_logger,
        'database': db_logger,
        'user_actions': user_logger
    }

def log_ml_training_start(model_name, dataset_size, features_used):
    """Log the start of ML model training"""
    ml_logger = logging.getLogger('ml_training')
    ml_logger.info(f"[START] Starting ML training for {model_name}")
    ml_logger.info(f"[DATA] Dataset size: {dataset_size} samples")
    ml_logger.info(f"[PROCESS] Features used: {', '.join(features_used)}")
    ml_logger.info(f"Training started at: {datetime.now().isoformat()}")

def log_ml_training_complete(model_name, accuracy, training_time, model_path):
    """Log the completion of ML model training"""
    ml_logger = logging.getLogger('ml_training')
    ml_logger.info(f"[SUCCESS] ML training completed for {model_name}")
    ml_logger.info(f"[TARGET] Accuracy: {accuracy:.4f}")
    ml_logger.info(f"⏱Training time: {training_time:.2f} seconds")
    ml_logger.info(f"Model saved to: {model_path}")
    ml_logger.info(f"Training completed at: {datetime.now().isoformat()}")

def log_ml_prediction(review_text, prediction, confidence, model_used, user_override=None):
    """Log ML prediction results"""
    ml_logger = logging.getLogger('ml_training')
    prediction_data = {
        'timestamp': datetime.now().isoformat(),
        'review_text': review_text[:100] + '...' if len(review_text) > 100 else review_text,
        'prediction': prediction,
        'confidence': confidence,
        'model_used': model_used,
        'user_override': user_override
    }
    ml_logger.info(f"ML Prediction: {json.dumps(prediction_data, cls=JSONEncoder)}")

def log_api_request(endpoint, method, status_code, response_time, user_id=None, error=None):
    """Log API request details"""
    api_logger = logging.getLogger('api_requests')
    request_data = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'response_time_ms': response_time,
        'user_id': user_id,
        'error': error
    }
    api_logger.info(f"API Request: {json.dumps(request_data, cls=JSONEncoder)}")

def log_database_operation(operation, collection, document_id=None, success=True, error=None):
    """Log database operations"""
    db_logger = logging.getLogger('database')
    db_data = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'collection': collection,
        'document_id': str(document_id) if document_id else None,
        'success': success,
        'error': str(error) if error else None
    }
    db_logger.info(f"Database: {json.dumps(db_data, cls=JSONEncoder)}")

def log_user_action(action, user_id, details=None, success=True):
    """Log user actions"""
    user_logger = logging.getLogger('user_actions')
    action_data = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'user_id': str(user_id) if user_id else None,
        'details': details,
        'success': success
    }
    user_logger.info(f"User Action: {json.dumps(action_data, cls=JSONEncoder)}")

def log_exception(exception, context=None):
    """Log exceptions with context"""
    error_logger = logging.getLogger('errors')
    exception_data = {
        'timestamp': datetime.now().isoformat(),
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        'context': context,
        'traceback': None  # Will be filled by the calling code
    }
    error_logger.error(f"[ERROR] Exception: {json.dumps(exception_data, cls=JSONEncoder)}")

# Initialize logging when module is imported
loggers = setup_logging()
