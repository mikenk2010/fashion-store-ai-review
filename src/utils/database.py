"""
Database utilities

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import pandas as pd
from pymongo import MongoClient
from ..config.settings import Config

def get_database_connection():
    """Get MongoDB database connection"""
    client = MongoClient(Config.MONGO_URI)
    db = client.ecommerce_db
    return db

def load_products_from_csv():
    """Load products from CSV file and populate database"""
    try:
        # Read CSV file
        df = pd.read_csv(f'{Config.DATA_DIR}/data-assignment3_II.csv')
        
        # Get database connection
        db = get_database_connection()
        products_collection = db.products
        
        # Check if products already exist
        if products_collection.count_documents({}) > 0:
            print("Products already loaded, skipping...")
            return True
        
        # Group by Clothing ID to create products
        products = []
        for clothing_id, group in df.groupby('Clothing ID'):
            # Get unique product info
            product_info = group.iloc[0]
            
            product = {
                'clothing_id': int(clothing_id),
                'division_name': product_info['Division Name'],
                'department_name': product_info['Department Name'],
                'class_name': product_info['Class Name'],
                'title': product_info['Clothes Title'],
                'description': product_info['Clothes Description'],
                'reviews': [],
                'avg_rating': 0.0,
                'review_count': 0,
                'created_at': pd.Timestamp.now().isoformat(),
                'updated_at': pd.Timestamp.now().isoformat()
            }
            
            # Add reviews for this product
            for _, review_row in group.iterrows():
                if pd.notna(review_row['Review Text']):
                    review = {
                        'user_id': str(review_row.get('User ID', 'anonymous')),
                        'rating': int(review_row['Rating']),
                        'title': review_row.get('Title', ''),
                        'text': review_row['Review Text'],
                        'recommended': bool(review_row['Recommended IND']),
                        'positive_feedback_count': int(review_row.get('Positive Feedback Count', 0)),
                        'age': int(review_row.get('Age', 0)),
                        'created_at': pd.Timestamp.now().isoformat()
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
            print(f"[SUCCESS] Loaded {len(products)} products with reviews")
            return True
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Error loading products: {str(e)}")
        return False
