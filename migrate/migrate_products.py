#!/usr/bin/env python3
"""
Product Migration Script
Migrates CSV data to properly structured products and reviews
"""

import pandas as pd
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
from urllib.parse import urljoin
import time
import random

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.ecommerce_db
products_collection = db.products
reviews_collection = db.reviews
users_collection = db.users

def clean_text(text):
    """Clean text data"""
    if pd.isna(text):
        return ""
    return str(text).strip()

def migrate_products():
    """Migrate CSV data to structured products and reviews"""
    print("[START] Starting Product Migration...")
    
    # Load CSV data
    df = pd.read_csv('data/data-assignment3_II.csv')
    print(f"[DATA] Loaded {len(df)} rows from CSV")
    
    # Clear existing data
    print("🗑️ Clearing existing data...")
    products_collection.delete_many({})
    reviews_collection.delete_many({})
    
    # Group by Clothing ID to create unique products
    products = {}
    reviews = []
    
    print("🔄 Processing data...")
    for _, row in df.iterrows():
        clothing_id = int(row['Clothing ID'])
        
        # Create or update product
        if clothing_id not in products:
            products[clothing_id] = {
                'clothing_id': clothing_id,
                'title': clean_text(row['Clothes Title']),
                'description': clean_text(row['Clothes Description']),
                'division_name': clean_text(row['Division Name']),
                'department_name': clean_text(row['Department Name']),
                'class_name': clean_text(row['Class Name']),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        
        # Create review
        review = {
            'clothing_id': clothing_id,
            'user_id': None,  # Will be set when user submits review
            'user_name': 'Anonymous',  # Default for migrated reviews
            'user_email': None,
            'title': clean_text(row['Title']),
            'review_text': clean_text(row['Review Text']),
            'rating': int(row['Rating']),
            'age': int(row['Age']),
            'positive_feedback_count': int(row['Positive Feedback Count']),
            'recommended': bool(row['Recommended IND']),
            'ml_prediction': None,  # Will be set by ML system
            'ml_confidence': None,
            'ml_details': None,
            'user_confirmed': None,
            'is_migrated': True,  # Flag for migrated reviews
            'created_at': datetime.now()
        }
        reviews.append(review)
    
    # Insert products
    print(f"💾 Inserting {len(products)} products...")
    product_docs = list(products.values())
    products_collection.insert_many(product_docs)
    
    # Insert reviews
    print(f"💾 Inserting {len(reviews)} reviews...")
    reviews_collection.insert_many(reviews)
    
    print("[SUCCESS] Migration completed successfully!")
    print(f"📦 Products: {len(products)}")
    print(f"💬 Reviews: {len(reviews)}")
    
    return len(products), len(reviews)


def create_demo_user():
    """Create a demo user for testing"""
    print("👤 Creating demo user...")
    
    # Check if demo user already exists
    if users_collection.find_one({'email': 'demo@fashionstore.com'}):
        print("👤 Demo user already exists")
        return
    
    # Create demo user
    demo_user = {
        'name': 'Demo User',
        'email': 'demo@fashionstore.com',
        'password': 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',  # "hello" hashed
        'created_at': datetime.now()
    }
    
    users_collection.insert_one(demo_user)
    print("[SUCCESS] Demo user created successfully!")
    print("📧 Email: demo@fashionstore.com")
    print("🔑 Password: hello")

def generate_statistics():
    """Generate migration statistics"""
    print("\n[DATA] Migration Statistics:")
    print("=" * 50)
    
    # Product statistics
    total_products = products_collection.count_documents({})
    print(f"📦 Total Products: {total_products}")
    
    # Review statistics
    total_reviews = reviews_collection.count_documents({})
    print(f"💬 Total Reviews: {total_reviews}")
    
    # User statistics
    total_users = users_collection.count_documents({})
    print(f"👥 Total Users: {total_users}")
    
    # Category breakdown
    categories = products_collection.aggregate([
        {'$group': {'_id': '$department_name', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ])
    
    print("\n📂 Categories:")
    for cat in categories:
        print(f"  • {cat['_id']}: {cat['count']} products")
    
    # Rating distribution
    rating_dist = reviews_collection.aggregate([
        {'$group': {'_id': '$rating', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ])
    
    print("\n⭐ Rating Distribution:")
    for rating in rating_dist:
        stars = "★" * int(rating['_id'])
        print(f"  {stars} ({rating['_id']} stars): {rating['count']} reviews")

if __name__ == "__main__":
    try:
        # Run migration
        product_count, review_count = migrate_products()
        
        
        # Create demo user
        create_demo_user()
        
        # Generate statistics
        generate_statistics()
        
        print("\n[COMPLETE] Migration completed successfully!")
        print("[START] You can now start the application with: python app.py")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
