"""
Helper utility functions for Fashion Store application

This module provides a collection of utility functions used throughout
the Fashion Store application. These functions handle common tasks such
as data formatting, time calculations, and data processing operations.

Key Features:
- Currency formatting for price display
- Date and time formatting utilities
- Relative time calculation for user-friendly timestamps
- Data processing and validation helpers
- Review statistics calculation
- Search functionality utilities

Utility Categories:
- Formatting functions (currency, dates, times)
- Time calculation functions
- Data processing functions
- Search and filtering utilities

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
import time

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount for display
    
    This function formats a numeric amount as a currency string
    with proper decimal places and currency symbol. It's used
    throughout the application for displaying product prices
    and financial information.
    
    Args:
        amount (float): The numeric amount to format
        currency (str, optional): Currency code. Defaults to "USD"
        
    Returns:
        str: Formatted currency string (e.g., "$29.99 USD")
    """
    return f"${amount:.2f} {currency}"

def format_date(date_str: str, format_str: str = "%B %d, %Y") -> str:
    """
    Format date string for display
    
    This function converts various date string formats into
    a human-readable date string. It handles ISO format dates
    and provides fallback error handling for invalid dates.
    
    Args:
        date_str (str): Date string in various formats
        format_str (str, optional): Output format string. Defaults to "%B %d, %Y"
        
    Returns:
        str: Formatted date string or original string if parsing fails
    """
    try:
        # Handle different date string formats
        if isinstance(date_str, str):
            # Parse ISO format dates with timezone handling
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Assume it's already a datetime object
            date_obj = date_str
        return date_obj.strftime(format_str)
    except:
        # Return original string if parsing fails
        return str(date_str)

def format_relative_time(date_str: str) -> str:
    """
    Format date string as relative time for user-friendly display
    
    This function converts a date string into a human-readable relative
    time format (e.g., "10 seconds ago", "4 minutes ago", "2 weeks ago").
    It's used throughout the application to display review timestamps
    and other time-sensitive information in a user-friendly format.
    
    The function handles:
    - Various date string formats (ISO, simple date strings)
    - Timezone-aware datetime calculations
    - Different time intervals (seconds, minutes, hours, days, weeks)
    - Fallback to full date format for very old dates
    
    Args:
        date_str (str): Date string to convert to relative time
        
    Returns:
        str: Human-readable relative time string or full date if very old
    """
    try:
        # Parse the date string based on its format
        if isinstance(date_str, str):
            # Handle ISO format dates with timezone information
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Handle simple date strings
                date_obj = datetime.fromisoformat(date_str)
        else:
            # Assume it's already a datetime object
            date_obj = date_str
        
        # Ensure we have timezone-aware datetime for accurate calculations
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=timezone.utc)
        
        # Get current time in UTC for consistent calculations
        now = datetime.now(timezone.utc)
        
        # Calculate the time difference
        diff = now - date_obj
        
        # If more than a month, show full date instead of relative time
        # This provides more context for older dates
        if diff.days > 30:
            return date_obj.strftime("%B %d, %Y")
        
        # Calculate time components for relative display
        total_seconds = int(diff.total_seconds())
        
        # Handle different time intervals with proper pluralization
        if total_seconds < 60:
            # Less than 1 minute - show seconds
            return f"{total_seconds} second{'s' if total_seconds != 1 else ''} ago"
        elif total_seconds < 3600:  # Less than 1 hour
            # Show minutes
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif total_seconds < 86400:  # Less than 1 day
            # Show hours
            hours = total_seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days < 7:  # Less than 1 week
            # Show days
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif diff.days < 30:  # Less than 1 month
            # Show weeks
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            # Fallback to full date for very old dates
            return date_obj.strftime("%B %d, %Y")
            
    except Exception as e:
        # Fallback to original date string if parsing fails
        # This ensures the function never crashes on invalid input
        return str(date_str)

def calculate_average_rating(reviews: List[Dict[str, Any]]) -> float:
    """
    Calculate average rating from a list of reviews
    
    This function computes the average star rating from a collection of reviews.
    It handles empty review lists gracefully and provides a rounded result
    for display purposes.
    
    Args:
        reviews (List[Dict[str, Any]]): List of review dictionaries
        
    Returns:
        float: Average rating rounded to 1 decimal place, or 0.0 if no reviews
    """
    if not reviews:
        return 0.0
    
    # Sum all ratings and calculate average
    total_rating = sum(review.get('rating', 0) for review in reviews)
    return round(total_rating / len(reviews), 1)

def get_review_stats(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get comprehensive review statistics from a list of reviews
    
    This function analyzes a collection of reviews and returns detailed
    statistics including total count, average rating, recommendation
    counts, and recommendation rate. It's used throughout the application
    for displaying product statistics and analytics.
    
    Args:
        reviews (List[Dict[str, Any]]): List of review dictionaries
        
    Returns:
        Dict[str, Any]: Dictionary containing review statistics:
            - total_reviews: Total number of reviews
            - average_rating: Average star rating
            - recommended_count: Number of recommended reviews
            - not_recommended_count: Number of not recommended reviews
            - recommendation_rate: Percentage of recommended reviews
    """
    if not reviews:
        return {
            'total_reviews': 0,
            'average_rating': 0.0,
            'recommended_count': 0,
            'not_recommended_count': 0,
            'recommendation_rate': 0.0
        }
    
    # Calculate basic statistics
    total_reviews = len(reviews)
    average_rating = calculate_average_rating(reviews)
    
    # Count recommended reviews based on final_decision or ml_prediction
    # This handles both user overrides and ML predictions
    recommended_count = 0
    for review in reviews:
        # Check for user override first, then fall back to ML prediction
        decision = review.get('final_decision')
        if decision is None:
            decision = review.get('ml_prediction')
        if decision == 1:  # Recommended
            recommended_count += 1
    
    # Calculate remaining statistics
    not_recommended_count = total_reviews - recommended_count
    recommendation_rate = (recommended_count / total_reviews) * 100 if total_reviews > 0 else 0
    
    # Return comprehensive statistics dictionary
    return {
        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'recommended_count': recommended_count,
        'not_recommended_count': not_recommended_count,
        'recommendation_rate': round(recommendation_rate, 1)
    }
