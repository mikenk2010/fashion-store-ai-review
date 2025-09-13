"""
Authentication routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ...utils.database import get_database_connection
from ...utils.auth import hash_password, verify_password, login_required, get_current_user
from ...config.logging_config import log_user_action, log_database_operation
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        db = get_database_connection()
        users_collection = db.users
        
        user = users_collection.find_one({'email': email})
        
        if user and verify_password(password, user['password']):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            
            log_user_action('login', str(user['_id']), {'email': email}, True)
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('main.index'))
        else:
            log_user_action('login_failed', None, {'email': email}, False)
            flash('Invalid email or password.', 'error')
    
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

