"""
Main application routes for the Fashion Store e-commerce application.

This module contains all the primary web routes that handle user interactions
with the Fashion Store application. It includes routes for product browsing,
product details, review submission, and user authentication flows.

The routes implement a comprehensive e-commerce experience with:
- Product listing with advanced search and filtering
- Product detail pages with review management
- Review submission with AI-powered prediction
- User authentication and session management
- Review confirmation and override functionality

Key Features:
- Advanced search algorithm with keyword normalization
- Server-side pagination for performance
- Real-time ML prediction integration
- User override system for AI recommendations
- Comprehensive error handling and validation

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from datetime import datetime
from ...utils.database import get_database_connection
from ...utils.auth import login_required, get_current_user
from ...utils.helpers import get_review_stats

# Create Blueprint for main application routes
# Blueprints allow for modular organization of routes and views
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Homepage route displaying product listings with advanced search and filtering.
    
    This route serves as the main entry point for the Fashion Store application.
    It provides a comprehensive product browsing experience with:
    - Advanced search functionality with keyword normalization
    - Multi-dimensional filtering (division, department, class, category, rating)
    - Server-side pagination for optimal performance
    - Real-time statistics and analytics
    - Responsive design for all device types
    
    The search algorithm implements intelligent keyword matching that handles:
    - Plural/singular form variations (dress/dresses, shirt/shirts)
    - Case-insensitive matching across multiple fields
    - Partial word matching with regex patterns
    - Multi-field search across title, description, and metadata
    
    Query Parameters:
        search (str): Search keywords for product matching
        division (str): Filter by product division (e.g., 'General')
        department (str): Filter by department (e.g., 'Dresses', 'Tops')
        class (str): Filter by product class
        category (str): Filter by product category
        min_rating (float): Minimum average rating filter
        page (int): Page number for pagination (default: 1)
    
    Returns:
        str: Rendered HTML template with product listings and filters
    
    Raises:
        DatabaseError: If database connection or query fails
        TemplateError: If template rendering fails
    """
    # Establish database connection
    db = get_database_connection()
    products_collection = db.products
    
    # Extract and sanitize filter parameters from URL query string
    # All parameters are optional and have sensible defaults
    search = request.args.get('search', '').strip()
    division = request.args.get('division', '')
    department = request.args.get('department', '')
    class_name = request.args.get('class', '')
    category = request.args.get('category', '')
    min_rating = request.args.get('min_rating', '')
    
    # Initialize MongoDB query object for building dynamic filters
    # This approach allows for flexible query construction based on user input
    query = {}
    
    # Implement enhanced search algorithm with keyword normalization
    if search:
        # Normalize search terms to lowercase for case-insensitive matching
        search_terms = search.lower().strip()
        
        # Handle plural/singular form variations for better search results
        # This improves search accuracy by matching both "dress" and "dresses"
        normalized_terms = []
        for term in search_terms.split():
            # Simple pluralization handling for common English patterns
            if term.endswith('s') and len(term) > 3:
                # Try both singular and plural forms for existing plurals
                normalized_terms.extend([term, term[:-1]])
            else:
                # Try both singular and plural forms for singular terms
                normalized_terms.extend([term, term + 's'])
        
        # Create regex pattern for flexible matching across multiple fields
        # The 'i' option enables case-insensitive matching
        search_pattern = '|'.join(normalized_terms)
        
        # Build MongoDB $or query for multi-field search
        # This searches across title, description, and metadata fields
        query['$or'] = [
            {'title': {'$regex': search_pattern, '$options': 'i'}},
            {'description': {'$regex': search_pattern, '$options': 'i'}},
            {'division_name': {'$regex': search_pattern, '$options': 'i'}},
            {'department_name': {'$regex': search_pattern, '$options': 'i'}},
            {'class_name': {'$regex': search_pattern, '$options': 'i'}}
        ]
    if division:
        query['division_name'] = division
    if department:
        query['department_name'] = department
    if class_name:
        query['class_name'] = class_name
    if category:
        query['category'] = category
    if min_rating:
        query['avg_rating'] = {'$gte': float(min_rating)}
    
    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 12  # Products per page
    skip = (page - 1) * per_page
    
    # Get total count for pagination
    total_matches = products_collection.count_documents(query)
    total_pages = (total_matches + per_page - 1) // per_page  # Ceiling division
    
    # Get products with pagination
    products = list(products_collection.find(query).skip(skip).limit(per_page))
    
    # Calculate average rating and AI analysis count for each product
    for product in products:
        if product.get('reviews'):
            ratings = [review.get('rating', 0) for review in product['reviews'] if review.get('rating')]
            product['avg_rating'] = sum(ratings) / len(ratings) if ratings else 0.0
            product['review_count'] = len(ratings)
            
            # Count reviews with AI predictions
            ai_analyzed_count = sum(1 for review in product['reviews'] 
                                  if review.get('ml_prediction') is not None)
            product['ai_analyzed_count'] = ai_analyzed_count
        else:
            product['avg_rating'] = 0.0
            product['review_count'] = 0
            product['ai_analyzed_count'] = 0
    
    # Get user wishlist if logged in
    user_wishlist = []
    if 'user_id' in session:
        user = get_current_user()
        user_wishlist = user.get('wishlist', []) if user else []
    
    # Get unique values for filters
    divisions = products_collection.distinct('division_name')
    departments = products_collection.distinct('department_name')
    classes = products_collection.distinct('class_name')
    categories = products_collection.distinct('category')
    
    # Calculate overall statistics
    all_products = list(products_collection.find({}))
    total_reviews = sum(len(p.get('reviews', [])) for p in all_products)
    
    # Calculate overall average rating
    all_ratings = []
    for product in all_products:
        if product.get('reviews'):
            for review in product['reviews']:
                if review.get('rating'):
                    all_ratings.append(review['rating'])
    
    overall_avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0.0
    
    # Pagination variables
    current_category = division
    current_sort = 'title'
    current_order = 'asc'
    
    return render_template('index.html', 
                         products=products,
                         user_wishlist=user_wishlist,
                         divisions=divisions,
                         departments=departments,
                         classes=classes,
                         categories=categories,
                         search=search,
                         total_matches=total_matches,
                         total_reviews=total_reviews,
                         overall_avg_rating=overall_avg_rating,
                         selected_division=division,
                         selected_department=department,
                         selected_class=class_name,
                         selected_category=category,
                         selected_min_rating=min_rating,
                         total_pages=total_pages,
                         page=page,
                         per_page=per_page,
                         current_category=current_category,
                         current_sort=current_sort,
                         current_order=current_order)

@main_bp.route('/product/<int:clothing_id>')
def product_detail(clothing_id):
    """Product detail page"""
    db = get_database_connection()
    products_collection = db.products
    
    product = products_collection.find_one({'clothing_id': clothing_id})
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Calculate average rating for the product
    if product.get('reviews'):
        ratings = [review.get('rating', 0) for review in product['reviews'] if review.get('rating')]
        product['avg_rating'] = sum(ratings) / len(ratings) if ratings else 0.0
        product['review_count'] = len(ratings)
    else:
        product['avg_rating'] = 0.0
        product['review_count'] = 0
    
    # Get review statistics
    review_stats = get_review_stats(product.get('reviews', []))
    
    # Separate reviews into recommended and not recommended
    recommended_reviews = []
    not_recommended_reviews = []
    
    # Sort reviews by creation date (newest first)
    sorted_reviews = sorted(product.get('reviews', []), 
                          key=lambda x: x.get('created_at', ''), 
                          reverse=True)
    
    for review in sorted_reviews:
        # Use final_decision if available, otherwise use ml_prediction
        decision = review.get('final_decision')
        if decision is None:
            decision = review.get('ml_prediction')
        
        if decision == 1:  # Recommended
            recommended_reviews.append(review)
        else:  # Not recommended (0 or None)
            not_recommended_reviews.append(review)
    
    # Add the separated review lists to the product
    product['recommended_reviews'] = recommended_reviews
    product['not_recommended_reviews'] = not_recommended_reviews
    
    return render_template('product_detail.html', product=product, review_stats=review_stats)

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_current_user()
    return render_template('profile.html', user=user)

@main_bp.route('/submit_review/<int:clothing_id>', methods=['POST'])
@login_required
def submit_review(clothing_id):
    """Submit a product review"""
    user = get_current_user()
    
    # Get form data
    rating = request.form.get('rating')
    title = request.form.get('title', '').strip()
    text = request.form.get('review_text', '').strip()  # Fixed field name
    
    # Validate input
    if not rating or not text:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('main.product_detail', clothing_id=clothing_id))
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("Invalid rating")
    except ValueError:
        flash('Please select a valid rating.', 'error')
        return redirect(url_for('main.product_detail', clothing_id=clothing_id))
    
    # Get ML prediction using rating, title, and text
    from ...models import predict_review_sentiment
    prediction, confidence, ml_details = predict_review_sentiment(text, title, rating)
    
    # Store review data in session for confirmation
    review_data = {
        'clothing_id': clothing_id,
        'user_id': str(user['_id']),
        'user_name': user['name'],
        'rating': rating,
        'title': title,
        'text': text,
        'ml_prediction': prediction,
        'ml_confidence': confidence,
        'ml_details': ml_details
    }
    
    # Store in session for confirmation page
    session['pending_review'] = review_data
    
    # Redirect to confirmation page
    return redirect(url_for('main.review_confirmation'))

@main_bp.route('/review_confirmation')
@login_required
def review_confirmation():
    """Review confirmation page"""
    review_data = session.get('pending_review')
    if not review_data:
        flash('No pending review found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get product details
    db = get_database_connection()
    products_collection = db.products
    product = products_collection.find_one({'clothing_id': review_data['clothing_id']})
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('review_confirmation.html', review_data=review_data, product=product)

@main_bp.route('/confirm_review', methods=['POST'])
@login_required
def confirm_review():
    """Confirm review with optional override"""
    review_data = session.get('pending_review')
    if not review_data:
        flash('No pending review found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get user decision
    user_decision = request.form.get('decision')  # 'accept' or 'override'
    override_decision = request.form.get('override_decision')  # 'recommended' or 'not_recommended'
    override_reason = request.form.get('override_reason', '').strip()
    
    # Validate override decision if user chose to override
    if user_decision == 'override' and not override_decision:
        flash('Please select your recommendation when overriding the AI prediction.', 'error')
        return redirect(url_for('main.review_confirmation'))
    
    # Determine final decision
    if user_decision == 'accept':
        final_decision = review_data['ml_prediction']
        user_override = None
    else:  # override
        final_decision = 1 if override_decision == 'recommended' else 0
        user_override = {
            'original_prediction': review_data['ml_prediction'],
            'user_decision': final_decision,
            'reason': override_reason
        }
    
    # Create final review object
    review = {
        'user_id': review_data['user_id'],
        'user_name': review_data['user_name'],
        'rating': review_data['rating'],
        'title': review_data['title'],
        'text': review_data['text'],
        'ml_prediction': review_data['ml_prediction'],
        'ml_confidence': review_data['ml_confidence'],
        'ml_details': review_data['ml_details'],
        'user_override': user_override,
        'final_decision': final_decision,
        'created_at': datetime.now().isoformat()
    }
    
    # Save review to database
    db = get_database_connection()
    products_collection = db.products
    
    products_collection.update_one(
        {'clothing_id': review_data['clothing_id']},
        {'$push': {'reviews': review}}
    )
    
    # Clear pending review from session
    session.pop('pending_review', None)
    
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('main.product_detail', clothing_id=review_data['clothing_id']))

@main_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    user = get_current_user()
    if not user:
        flash('Please log in to update your profile.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get form data
    name = request.form.get('name', '').strip()
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validate input
    if not name:
        flash('Name is required.', 'error')
        return redirect(url_for('main.profile'))
    
    # Update name
    db = get_database_connection()
    users_collection = db.users
    
    update_data = {'name': name}
    
    # Update password if provided
    if new_password:
        if not current_password:
            flash('Current password is required to change password.', 'error')
            return redirect(url_for('main.profile'))
        
        # Verify current password
        from ...utils.auth import verify_password
        if not verify_password(current_password, user['password']):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('main.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('main.profile'))
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return redirect(url_for('main.profile'))
        
        from ...utils.auth import hash_password
        update_data['password'] = hash_password(new_password)
    
    # Update user
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': update_data}
    )
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))

