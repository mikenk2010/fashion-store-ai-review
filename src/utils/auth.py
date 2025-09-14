"""
Authentication utilities for Fashion Store application

This module provides authentication and authorization utilities for the
Fashion Store e-commerce application. It handles user authentication,
password management, session management, and route protection.

Key Features:
- Password hashing and verification using SHA-256
- Session-based authentication
- Route protection decorators
- User session management
- Database user retrieval

Security Features:
- Secure password hashing
- Session validation
- Route access control
- Error handling for authentication failures

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import hashlib
from functools import wraps
from flask import session, redirect, url_for, flash
from pymongo import MongoClient
from ..config.settings import Config

def hash_password(password):
    """
    Hash password using SHA-256
    
    Creates a secure hash of the provided password using SHA-256 algorithm.
    This function is used during user registration and password updates to
    store passwords securely in the database.
    
    Args:
        password (str): Plain text password to be hashed
        
    Returns:
        str: Hexadecimal representation of the hashed password
        
    Note:
        SHA-256 is used for simplicity in this educational project.
        In production, consider using bcrypt or Argon2 for better security.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """
    Verify password against stored hash
    
    Compares a plain text password with a stored hash to verify
    if the password is correct during login attempts.
    
    Args:
        password (str): Plain text password to verify
        hashed_password (str): Stored hash to compare against
        
    Returns:
        bool: True if password matches hash, False otherwise
    """
    return hash_password(password) == hashed_password

def login_required(f):
    """
    Decorator to require login for routes
    
    This decorator protects routes that require user authentication.
    It checks if a user is logged in by verifying the presence of
    'user_id' in the session. If not logged in, it redirects to
    the login page with an error message.
    
    Args:
        f (function): The route function to protect
        
    Returns:
        function: Decorated function that checks authentication
        
    Usage:
        @login_required
        def protected_route():
            return render_template('protected.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in by verifying session
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """
    Get current logged-in user from database
    
    Retrieves the complete user document from the database based on
    the user ID stored in the session. This function is used throughout
    the application to access current user information.
    
    Returns:
        dict or None: User document if found and logged in, None otherwise
        
    Raises:
        bson.errors.InvalidId: If session contains invalid ObjectId
        pymongo.errors.ConnectionFailure: If database connection fails
    """
    # Check if user is logged in
    if 'user_id' not in session:
        return None
    
    # Import ObjectId for MongoDB document ID conversion
    from bson import ObjectId
    
    # Create database connection
    client = MongoClient(Config.MONGO_URI)
    db = client.ecommerce_db
    users_collection = db.users
    
    try:
        # Find user by ObjectId from session
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        return user
    except Exception as e:
        # Handle any errors during user retrieval
        print(f"Error getting current user: {e}")
        return None
