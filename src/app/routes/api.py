"""
API routes

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import time
import traceback
from flask import Blueprint, request, jsonify, session
from ...utils.database import get_database_connection
from ...utils.auth import login_required, get_current_user
from ...models import predict_review_sentiment, get_model_info
from ...config.logging_config import log_ml_prediction, log_api_request, log_exception

api_bp = Blueprint('api', __name__)

@api_bp.route('/products')
def api_products():
    """API endpoint for products (for AJAX requests)"""
    from bson import ObjectId
    
    db = get_database_connection()
    products_collection = db.products
    
    products = list(products_collection.find({}, {'_id': 0}))
    
    # Convert ObjectId to string for JSON serialization
    def convert_objectid(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_objectid(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_objectid(item) for item in obj]
        else:
            return obj
    
    # Convert all ObjectIds in the products
    products = convert_objectid(products)
    
    return jsonify(products)

@api_bp.route('/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        db = get_database_connection()
        products_collection = db.products
        
        # Get basic counts
        total_products = products_collection.count_documents({})
        total_reviews = sum(len(p.get('reviews', [])) for p in products_collection.find({}))
        
        # Get categories
        categories = products_collection.distinct('category')
        
        # Get rating distribution
        rating_distribution = []
        for product in products_collection.find({}):
            if product.get('reviews'):
                for review in product['reviews']:
                    if review.get('rating'):
                        rating_distribution.append(review['rating'])
        
        # Calculate rating distribution
        from collections import Counter
        rating_counts = Counter(rating_distribution)
        rating_dist = [{"_id": rating, "count": count} for rating, count in rating_counts.items()]
        
        return jsonify({
            'total_products': total_products,
            'total_reviews': total_reviews,
            'categories': categories,
            'rating_distribution': rating_dist
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predict_review', methods=['POST'])
def api_predict_review():
    """API endpoint for real-time review prediction"""
    start_time = time.time()
    user_id = session.get('user_id')
    
    try:
        data = request.get_json()
        review_text = data.get('review_text', '').strip()
        title = data.get('title', '').strip()
        rating = data.get('rating')
        
        if not review_text:
            return jsonify({'error': 'Review text is required'}), 400
        
        # Convert rating to int if provided
        if rating:
            try:
                rating = int(rating)
            except (ValueError, TypeError):
                rating = None
        
        # Get ML prediction
        prediction, confidence, ml_details = predict_review_sentiment(review_text, title, rating)
        
        if prediction is None:
            return jsonify({'error': 'Error processing review'}), 500
        
        # Log the prediction
        log_ml_prediction(
            review_text=review_text,
            prediction=prediction,
            confidence=confidence,
            model_used='ensemble',
            user_override=None
        )
        
        # Prepare response data with proper serialization
        response_data = {
            'prediction': int(prediction),
            'confidence': float(confidence),
            'label': 'Recommended' if prediction == 1 else 'Not Recommended',
            'details': {
                'model_used': 'ensemble',
                'individual_results': ml_details.get('individual_results', {}),
                'consensus': ml_details.get('consensus', False),
                'ensemble_prediction': ml_details.get('ensemble_prediction', prediction),
                'ensemble_confidence': ml_details.get('ensemble_confidence', confidence),
                'ensemble_label': ml_details.get('ensemble_label', 'Recommended' if prediction == 1 else 'Not Recommended')
            }
        }
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(
            endpoint='/api/predict_review',
            method='POST',
            status_code=200,
            response_time=response_time,
            user_id=user_id
        )
        
        return jsonify(response_data)
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log the exception
        log_exception(e, context={
            'endpoint': '/api/predict_review',
            'user_id': user_id,
            'review_text': review_text[:100] if 'review_text' in locals() else None
        })
        
        log_api_request(
            endpoint='/api/predict_review',
            method='POST',
            status_code=500,
            response_time=response_time,
            user_id=user_id,
            error=error_msg
        )
        
        return jsonify({'error': 'Error processing review'}), 500

@api_bp.route('/model_info')
def api_model_info():
    """API endpoint for model information"""
    return jsonify(get_model_info())

