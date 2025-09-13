#!/usr/bin/env python3
"""
Add New Categories Migration Script
Adds new categories and randomly assigns them to products
"""

import random
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

# New categories to add
NEW_CATEGORIES = [
    "Belts",
    "Biker Shorts", 
    "Blazers",
    "Blouses",
    "Bodysuit",
    "Bra",
    "Camisoles",
    "Cardigans",
    "Coats",
    "Dresses",
    "Earrings",
    "Giftcards",
    "Handbags",
    "Hats",
    "Jackets",
    "Jeans",
    "Jumpsuits",
    "Kimonos",
    "Leggings",
    "Lifestyle",
    "Necklaces"
]

def add_categories_to_products():
    """Add new categories and randomly assign them to products"""
    print("[START] Adding new categories to products...")
    
    # Get all products
    products = list(products_collection.find({}))
    total_products = len(products)
    print(f"📦 Found {total_products} products to update")
    
    # Update each product with a random category
    updated_count = 0
    category_counts = {}
    
    for product in products:
        # Randomly select a category
        new_category = random.choice(NEW_CATEGORIES)
        
        # Update the product with the new category
        products_collection.update_one(
            {'_id': product['_id']},
            {
                '$set': {
                    'category': new_category,
                    'updated_at': datetime.now()
                }
            }
        )
        
        # Track category distribution
        category_counts[new_category] = category_counts.get(new_category, 0) + 1
        updated_count += 1
    
    print(f"✅ Updated {updated_count} products with new categories")
    
    # Display category distribution
    print("\n📊 Category Distribution:")
    print("=" * 40)
    for category, count in sorted(category_counts.items()):
        percentage = (count / total_products) * 100
        print(f"{category:<15}: {count:>4} products ({percentage:>5.1f}%)")
    
    return updated_count

def generate_category_statistics():
    """Generate statistics for the new categories"""
    print("\n[DATA] Category Statistics:")
    print("=" * 50)
    
    # Total products with categories
    total_with_categories = products_collection.count_documents({'category': {'$exists': True}})
    print(f"📦 Products with categories: {total_with_categories}")
    
    # Category breakdown
    categories = products_collection.aggregate([
        {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ])
    
    print("\n🏷️ Category Breakdown:")
    for cat in categories:
        if cat['_id']:  # Skip empty categories
            print(f"  • {cat['_id']}: {cat['count']} products")
    
    # Products per category (top 10)
    top_categories = products_collection.aggregate([
        {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ])
    
    print("\n🏆 Top 10 Categories:")
    for i, cat in enumerate(top_categories, 1):
        if cat['_id']:  # Skip empty categories
            print(f"  {i:2d}. {cat['_id']:<15}: {cat['count']:>4} products")

if __name__ == "__main__":
    try:
        # Add categories to products
        updated_count = add_categories_to_products()
        
        # Generate statistics
        generate_category_statistics()
        
        print(f"\n[COMPLETE] Successfully added categories to {updated_count} products!")
        print("[SUCCESS] All products now have random category assignments")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
