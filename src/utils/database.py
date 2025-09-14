"""
Database utilities for Fashion Store application

This module provides database connection management and data loading utilities
for the Fashion Store e-commerce application. It handles MongoDB connections,
CSV data processing, and database population operations.

Key Features:
- MongoDB connection management
- CSV data loading and processing
- Product and review data transformation
- Database population and validation
- Error handling and logging

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import pandas as pd
from pymongo import MongoClient
from ..config.settings import Config

def get_database_connection():
    """
    Get MongoDB database connection
    
    Creates and returns a connection to the MongoDB database using the
    configuration settings. This function is used throughout the application
    to access the database for all CRUD operations.
    
    Returns:
        pymongo.database.Database: MongoDB database object for ecommerce_db
        
    Raises:
        pymongo.errors.ConnectionFailure: If unable to connect to MongoDB
        pymongo.errors.ServerSelectionTimeoutError: If MongoDB server is unreachable
    """
    # Create MongoDB client using the configured URI
    client = MongoClient(Config.MONGO_URI)
    # Return the specific database used by the application
    db = client.ecommerce_db
    return db

def load_products_from_csv():
    """
    Load products from CSV file and populate database
    
    This function reads the assignment CSV file, processes the data to create
    product documents with embedded reviews, and populates the MongoDB database.
    It groups reviews by Clothing ID to create individual product documents.
    
    The function performs the following operations:
    1. Reads the CSV file using pandas
    2. Checks if products already exist to avoid duplicates
    3. Groups data by Clothing ID to create product documents
    4. Extracts product information and creates product structure
    5. Processes reviews and embeds them within product documents
    6. Calculates product statistics (average rating, review count)
    7. Inserts all products into the database
    
    Returns:
        bool: True if successful, False if an error occurs
        
    Raises:
        FileNotFoundError: If the CSV file is not found
        pandas.errors.EmptyDataError: If the CSV file is empty
        pymongo.errors.DuplicateKeyError: If duplicate products are inserted
    """
    try:
        # Read CSV file from the configured data directory
        # The CSV contains clothing reviews with product information
        df = pd.read_csv(f'{Config.DATA_DIR}/data-assignment3_II.csv')
        
        # Get database connection and access products collection
        db = get_database_connection()
        products_collection = db.products
        
        # Check if products already exist to avoid duplicate loading
        # This prevents re-loading data on application restart
        if products_collection.count_documents({}) > 0:
            print("Products already loaded, skipping...")
            return True
        
        # Group by Clothing ID to create individual product documents
        # Each group represents one product with multiple reviews
        products = []
        for clothing_id, group in df.groupby('Clothing ID'):
            # Get unique product information from the first row of each group
            # All rows in a group have the same product details
            product_info = group.iloc[0]
            
            # Create product document structure
            product = {
                'clothing_id': int(clothing_id),  # Unique product identifier
                'division_name': product_info['Division Name'],  # Product category
                'department_name': product_info['Department Name'],  # Product department
                'class_name': product_info['Class Name'],  # Product class
                'title': product_info['Clothes Title'],  # Product name
                'description': product_info['Clothes Description'],  # Product description
                'reviews': [],  # List to store embedded reviews
                'avg_rating': 0.0,  # Calculated average rating
                'review_count': 0,  # Total number of reviews
                'created_at': pd.Timestamp.now().isoformat(),  # Creation timestamp
                'updated_at': pd.Timestamp.now().isoformat()  # Last update timestamp
            }
            
            # Process all reviews for this product
            # Each row in the group represents one review
            for _, review_row in group.iterrows():
                # Only process rows with valid review text
                if pd.notna(review_row['Review Text']):
                    # Create review document structure
                    review = {
                        'user_id': str(review_row.get('User ID', 'anonymous')),  # User identifier
                        'rating': int(review_row['Rating']),  # Star rating (1-5)
                        'title': review_row.get('Title', ''),  # Review title
                        'text': review_row['Review Text'],  # Review content
                        'recommended': bool(review_row['Recommended IND']),  # Recommendation flag
                        'positive_feedback_count': int(review_row.get('Positive Feedback Count', 0)),  # Helpful votes
                        'age': int(review_row.get('Age', 0)),  # Reviewer age
                        'created_at': pd.Timestamp.now().isoformat()  # Review timestamp
                    }
                    # Add review to the product's review list
                    product['reviews'].append(review)
            
            # Calculate product statistics from embedded reviews
            if product['reviews']:
                # Calculate average rating by summing all ratings and dividing by count
                product['avg_rating'] = sum(r['rating'] for r in product['reviews']) / len(product['reviews'])
                # Set review count to the number of embedded reviews
                product['review_count'] = len(product['reviews'])
            
            # Add completed product to the products list
            products.append(product)
        
        # Insert all products into the database in a single operation
        # This is more efficient than inserting one by one
        if products:
            products_collection.insert_many(products)
            print(f"[SUCCESS] Loaded {len(products)} products with reviews")
            return True
        
        # Return False if no products were processed
        return False
        
    except Exception as e:
        # Handle any errors during the loading process
        # This includes file reading errors, database connection issues, etc.
        print(f"[ERROR] Error loading products: {str(e)}")
        return False
