"""
Helper utility functions
"""

from datetime import datetime
from typing import List, Dict, Any

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    return f"${amount:.2f} {currency}"

def format_date(date_str: str, format_str: str = "%B %d, %Y") -> str:
    """Format date string"""
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str
        return date_obj.strftime(format_str)
    except:
        return str(date_str)

def calculate_average_rating(reviews: List[Dict[str, Any]]) -> float:
    """Calculate average rating from reviews"""
    if not reviews:
        return 0.0
    
    total_rating = sum(review.get('rating', 0) for review in reviews)
    return round(total_rating / len(reviews), 1)

def get_review_stats(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get review statistics"""
    if not reviews:
        return {
            'total_reviews': 0,
            'average_rating': 0.0,
            'recommended_count': 0,
            'not_recommended_count': 0,
            'recommendation_rate': 0.0
        }
    
    total_reviews = len(reviews)
    average_rating = calculate_average_rating(reviews)
    
    # Count recommended reviews based on final_decision or ml_prediction
    recommended_count = 0
    for review in reviews:
        decision = review.get('final_decision')
        if decision is None:
            decision = review.get('ml_prediction')
        if decision == 1:  # Recommended
            recommended_count += 1
    
    not_recommended_count = total_reviews - recommended_count
    recommendation_rate = (recommended_count / total_reviews) * 100 if total_reviews > 0 else 0
    
    return {
        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'recommended_count': recommended_count,
        'not_recommended_count': not_recommended_count,
        'recommendation_rate': round(recommendation_rate, 1)
    }
