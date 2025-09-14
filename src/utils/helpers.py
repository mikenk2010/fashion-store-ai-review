"""
Helper utility functions

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
import time

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

def format_relative_time(date_str: str) -> str:
    """Format date string as relative time (e.g., '10 seconds ago', '4 minutes ago', '2 weeks ago')"""
    try:
        if isinstance(date_str, str):
            # Parse the date string
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.fromisoformat(date_str)
        else:
            date_obj = date_str
        
        # Ensure we have timezone-aware datetime
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=timezone.utc)
        
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Calculate time difference
        diff = now - date_obj
        
        # If more than a month, show full date
        if diff.days > 30:
            return date_obj.strftime("%B %d, %Y")
        
        # Calculate time components
        total_seconds = int(diff.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} second{'s' if total_seconds != 1 else ''} ago"
        elif total_seconds < 3600:  # Less than 1 hour
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif total_seconds < 86400:  # Less than 1 day
            hours = total_seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days < 7:  # Less than 1 week
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif diff.days < 30:  # Less than 1 month
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            return date_obj.strftime("%B %d, %Y")
            
    except Exception as e:
        # Fallback to original date string if parsing fails
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
