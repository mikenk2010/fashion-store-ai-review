#!/usr/bin/env python3
"""
Fix Products with Embedded Reviews Migration Script
Embeds reviews into product documents and calculates average ratings
"""

import pandas as pd
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.ecommerce_db
products_collection = db.products
reviews_collection = db.reviews

def clean_text(text):
    """Clean text data"""
    if pd.isna(text):
        return ""
    return str(text).strip()

def fix_products_with_reviews():
    """Embed reviews into products and calculate average ratings"""
    print("[START] Fixing products with embedded reviews...")
    
    # Get all reviews grouped by clothing_id
    print("🔄 Processing reviews...")
    reviews_by_product = {}
    
    for review in reviews_collection.find({}):
        clothing_id = review['clothing_id']
        if clothing_id not in reviews_by_product:
            reviews_by_product[clothing_id] = []
        
        # Convert review to the format expected by the application
        embedded_review = {
            'user_id': str(review.get('user_id', 'anonymous')),
            'user_name': review.get('user_name', 'Anonymous'),
            'rating': review['rating'],
            'title': review.get('title', ''),
            'text': review['review_text'],
            'ml_prediction': review.get('ml_prediction', 1 if review.get('recommended', False) else 0),
            'ml_confidence': review.get('ml_confidence', 0.5),
            'ml_details': review.get('ml_details'),
            'user_override': review.get('user_confirmed'),
            'final_decision': review.get('ml_prediction', 1 if review.get('recommended', False) else 0),
            'created_at': review.get('created_at', datetime.now()).isoformat()
        }
        reviews_by_product[clothing_id].append(embedded_review)
    
    print(f"📊 Found reviews for {len(reviews_by_product)} products")
    
    # Update products with embedded reviews and calculate ratings
    print("🔄 Updating products with embedded reviews...")
    updated_count = 0
    
    for product in products_collection.find({}):
        clothing_id = product['clothing_id']
        product_reviews = reviews_by_product.get(clothing_id, [])
        
        # Calculate average rating
        if product_reviews:
            ratings = [review['rating'] for review in product_reviews if review.get('rating')]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
            review_count = len(ratings)
        else:
            avg_rating = 0.0
            review_count = 0
        
        # Update product with embedded reviews and calculated rating
        products_collection.update_one(
            {'clothing_id': clothing_id},
            {
                '$set': {
                    'reviews': product_reviews,
                    'avg_rating': avg_rating,
                    'review_count': review_count,
                    'updated_at': datetime.now()
                }
            }
        )
        updated_count += 1
    
    print(f"✅ Updated {updated_count} products with embedded reviews")
    
    # Verify the fix
    print("\n🔍 Verification:")
    sample_product = products_collection.find_one({})
    if sample_product:
        print(f"Sample product: {sample_product['title']}")
        print(f"Division: {sample_product['division_name']}")
        print(f"Department: {sample_product['department_name']}")
        print(f"Class: {sample_product['class_name']}")
        print(f"Reviews count: {len(sample_product.get('reviews', []))}")
        print(f"Average rating: {sample_product.get('avg_rating', 0.0)}")
    
    return updated_count

def generate_statistics():
    """Generate updated statistics"""
    print("\n[DATA] Updated Statistics:")
    print("=" * 50)
    
    # Product statistics
    total_products = products_collection.count_documents({})
    print(f"📦 Total Products: {total_products}")
    
    # Review statistics
    total_reviews = sum(len(p.get('reviews', [])) for p in products_collection.find({}))
    print(f"💬 Total Embedded Reviews: {total_reviews}")
    
    # Category breakdown
    categories = products_collection.aggregate([
        {'$group': {'_id': '$department_name', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ])
    
    print("\n📂 Categories:")
    for cat in categories:
        if cat['_id']:  # Skip empty categories
            print(f"  • {cat['_id']}: {cat['count']} products")
    
    # Division breakdown
    divisions = products_collection.aggregate([
        {'$group': {'_id': '$division_name', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ])
    
    print("\n🏢 Divisions:")
    for div in divisions:
        if div['_id']:  # Skip empty divisions
            print(f"  • {div['_id']}: {div['count']} products")
    
    # Class breakdown
    classes = products_collection.aggregate([
        {'$group': {'_id': '$class_name', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ])
    
    print("\n👗 Classes:")
    for cls in classes:
        if cls['_id']:  # Skip empty classes
            print(f"  • {cls['_id']}: {cls['count']} products")
    
    # Rating statistics
    products_with_ratings = products_collection.count_documents({'avg_rating': {'$gt': 0}})
    print(f"\n⭐ Products with ratings: {products_with_ratings}")

if __name__ == "__main__":
    try:
        # Fix products with embedded reviews
        updated_count = fix_products_with_reviews()
        
        # Generate statistics
        generate_statistics()
        
        print(f"\n[COMPLETE] Successfully updated {updated_count} products!")
        print("[SUCCESS] Products now have embedded reviews and calculated ratings")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
