"""
Authentication routes for Fashion Store application

This module handles all user authentication-related routes including
login, registration, logout, and profile management. It provides
secure user session management and integrates with the application's
logging system for audit trails.

Key Features:
- User registration with email validation
- Secure login with password verification
- Session management and user state tracking
- Profile management and password updates
- Comprehensive logging for security auditing
- Input validation and error handling

Authentication Flow:
1. User registration with email/password validation
2. Secure login with session creation
3. Session-based authentication for protected routes
4. Profile management for authenticated users
5. Secure logout with session cleanup

Security Features:
- Password hashing using SHA-256
- Session-based authentication
- Input validation and sanitization
- Comprehensive audit logging
- CSRF protection through Flask sessions

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ...utils.database import get_database_connection
from ...utils.auth import hash_password, verify_password, login_required, get_current_user
from ...config.logging_config import log_user_action, log_database_operation
from datetime import datetime

# Create Blueprint for authentication routes
# This organizes all auth-related routes under the /auth prefix
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route
    
    This route handles user authentication for the Fashion Store application.
    It supports both GET (display login form) and POST (process login) methods.
    
    Login Process:
    1. Validate input fields (email and password)
    2. Query database for user by email
    3. Verify password using secure hashing
    4. Create user session if authentication succeeds
    5. Log authentication attempt for security auditing
    6. Redirect to appropriate page based on result
    
    Security Features:
    - Input validation and sanitization
    - Secure password verification
    - Session management
    - Comprehensive audit logging
    - Error handling without information disclosure
    
    Returns:
        str: Rendered login template or redirect response
    """
    if request.method == 'POST':
        # Extract and sanitize form data
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validate required fields
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        # Get database connection and access users collection
        db = get_database_connection()
        users_collection = db.users
        
        # Find user by email address
        user = users_collection.find_one({'email': email})
        
        # Verify password and authenticate user
        if user and verify_password(password, user['password']):
            # Create user session with essential information
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            
            # Log successful login for security auditing
            log_user_action('login', str(user['_id']), {'email': email}, True)
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('main.index'))
        else:
            # Log failed login attempt for security monitoring
            log_user_action('login_failed', None, {'email': email}, False)
            flash('Invalid email or password.', 'error')
    
    # Display login form for GET requests
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([name, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        db = get_database_connection()
        users_collection = db.users
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        user_data = {
            'name': name,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = users_collection.insert_one(user_data)
        
        if result.inserted_id:
            log_database_operation('insert', 'users', result.inserted_id, True)
            log_user_action('register', str(result.inserted_id), {'email': email}, True)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            log_database_operation('insert', 'users', None, False, 'Failed to insert user')
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    user_id = session.get('user_id')
    if user_id:
        log_user_action('logout', user_id, {}, True)
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    user = get_current_user()
    name = request.form.get('name', '').strip()
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not name:
        flash('Name is required.', 'error')
        return redirect(url_for('main.profile'))
    
    db = get_database_connection()
    users_collection = db.users
    
    # Update name
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': {'name': name, 'updated_at': datetime.now().isoformat()}}
    )
    session['user_name'] = name
    
    # Update password if provided
    if new_password:
        if not current_password:
            flash('Current password is required to change password.', 'error')
            return redirect(url_for('main.profile'))
        
        if not verify_password(current_password, user['password']):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('main.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('main.profile'))
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return redirect(url_for('main.profile'))
        
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'password': hash_password(new_password), 'updated_at': datetime.now().isoformat()}}
        )
        flash('Profile and password updated successfully!', 'success')
    else:
        flash('Profile updated successfully!', 'success')
    
    log_user_action('profile_update', str(user['_id']), {'name': name}, True)
    return redirect(url_for('main.profile'))

