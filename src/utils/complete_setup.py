#!/usr/bin/env python3
"""
Complete setup utility for Fashion Store application
This ensures everything is ready for the lecturer on first run

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import os
import sys
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from ..config.settings import Config

def get_database_connection():
    """Get MongoDB database connection"""
    client = MongoClient(Config.MONGO_URI)
    db = client.ecommerce_db
    return db

def wait_for_mongodb(max_attempts=30):
    """Wait for MongoDB to be ready"""
    print("Waiting for MongoDB to be ready...")
    
    for attempt in range(max_attempts):
        try:
            client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            client.close()
            print("MongoDB is ready!")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_attempts} - MongoDB not ready yet...")
            import time
            time.sleep(2)
    
    print("MongoDB failed to start after maximum attempts")
    return False

def load_products_from_csv():
    """Load products from CSV file and populate database"""
    try:
        print("Loading products from CSV...")
        
        # Read CSV file
        csv_path = os.path.join(Config.DATA_DIR, 'data-assignment3_II.csv')
        if not os.path.exists(csv_path):
            print(f"ERROR: CSV file not found at {csv_path}")
            return False
            
        df = pd.read_csv(csv_path)
        print(f"Loaded CSV with {len(df)} rows")
        
        # Get database connection
        db = get_database_connection()
        products_collection = db.products
        
        # Check if products already exist
        existing_count = products_collection.count_documents({})
        if existing_count > 0:
            print(f"Products already loaded ({existing_count} products), skipping...")
            return True
        
        # Group by Clothing ID to create products
        products = []
        for clothing_id, group in df.groupby('Clothing ID'):
            # Get unique product info
            product_info = group.iloc[0]
            
            product = {
                'clothing_id': int(clothing_id),
                'division_name': str(product_info['Division Name']),
                'department_name': str(product_info['Department Name']),
                'class_name': str(product_info['Class Name']),
                'title': str(product_info['Clothes Title']),
                'description': str(product_info['Clothes Description']),
                'reviews': [],
                'avg_rating': 0.0,
                'review_count': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Add reviews for this product
            for _, review_row in group.iterrows():
                if pd.notna(review_row['Review Text']):
                    review = {
                        'user_id': str(review_row.get('User ID', 'anonymous')),
                        'rating': int(review_row['Rating']),
                        'title': str(review_row.get('Title', '')),
                        'text': str(review_row['Review Text']),
                        'ml_prediction': int(review_row['Recommended IND']),
                        'final_decision': int(review_row['Recommended IND']),
                        'positive_feedback_count': int(review_row.get('Positive Feedback Count', 0)),
                        'age': int(review_row.get('Age', 0)),
                        'created_at': datetime.now().isoformat()
                    }
                    product['reviews'].append(review)
            
            # Calculate average rating
            if product['reviews']:
                product['avg_rating'] = sum(r['rating'] for r in product['reviews']) / len(product['reviews'])
                product['review_count'] = len(product['reviews'])
            
            products.append(product)
        
        # Insert products into database
        if products:
            products_collection.insert_many(products)
            print(f"[SUCCESS] Loaded {len(products)} products with {sum(len(p['reviews']) for p in products)} reviews")
            return True
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Error loading products: {str(e)}")
        return False

def add_categories_to_products():
    """Add random categories to products"""
    try:
        print("Adding categories to products...")
        
        categories = [
            "Belts", "Biker Shorts", "Blazers", "Blouses", "Bodysuit", "Bra", 
            "Camisoles", "Cardigans", "Coats", "Dresses", "Earrings", "Giftcards", 
            "Handbags", "Hats", "Jackets", "Jeans", "Jumpsuits", "Kimonos", 
            "Leggings", "Lifestyle", "Necklaces"
        ]
        
        db = get_database_connection()
        products_collection = db.products
        
        # Check if categories already added
        sample_product = products_collection.find_one({})
        if sample_product and 'category' in sample_product:
            print("Categories already added, skipping...")
            return True
        
        # Add random categories to all products
        import random
        for product in products_collection.find({}):
            category = random.choice(categories)
            products_collection.update_one(
                {'_id': product['_id']},
                {'$set': {'category': category}}
            )
        
        print(f"[SUCCESS] Added categories to all products")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error adding categories: {str(e)}")
        return False

def verify_setup():
    """Verify that the setup is complete"""
    try:
        print("Verifying setup...")
        
        db = get_database_connection()
        products_collection = db.products
        
        # Check products
        product_count = products_collection.count_documents({})
        if product_count == 0:
            print("ERROR: No products found in database")
            return False
        
        # Check reviews
        products_with_reviews = products_collection.count_documents({'reviews': {'$exists': True, '$ne': []}})
        if products_with_reviews == 0:
            print("ERROR: No products with reviews found")
            return False
        
        # Check categories
        products_with_categories = products_collection.count_documents({'category': {'$exists': True}})
        if products_with_categories == 0:
            print("WARNING: No products with categories found")
        
        print(f"[SUCCESS] Setup verified:")
        print(f"  - {product_count} products loaded")
        print(f"  - {products_with_reviews} products with reviews")
        print(f"  - {products_with_categories} products with categories")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Setup verification failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Fashion Store - Complete Setup")
    print("=" * 60)
    
    # Wait for MongoDB
    if not wait_for_mongodb():
        return False
    
    # Load products
    if not load_products_from_csv():
        return False
    
    # Add categories
    if not add_categories_to_products():
        return False
    
    # Verify setup
    if not verify_setup():
        return False
    
    print("=" * 60)
    print("[COMPLETE] Fashion Store setup completed successfully!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
