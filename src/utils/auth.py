"""
Authentication utilities
"""

import hashlib
from functools import wraps
from flask import session, redirect, url_for, flash
from pymongo import MongoClient
from ..config.settings import Config

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' not in session:
        return None
    
    from bson import ObjectId
    client = MongoClient(Config.MONGO_URI)
    db = client.ecommerce_db
    users_collection = db.users
    
    try:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        return user
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None
