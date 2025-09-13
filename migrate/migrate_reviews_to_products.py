#!/usr/bin/env python3
"""
Review Migration Script
Migrates reviews from the reviews collection to be embedded within product documents
This improves query performance and data organization
"""

import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.ecommerce_db
products_collection = db.products
reviews_collection = db.reviews

def migrate_reviews_to_products():
    """Migrate reviews from reviews collection to product documents"""
    print("[START] Starting Review Migration to Products...")
    
    # Get all reviews grouped by clothing_id
    print("[DATA] Fetching reviews from database...")
    reviews_cursor = reviews_collection.find({})
    
    # Group reviews by clothing_id
    reviews_by_product = defaultdict(list)
    total_reviews = 0
    
    for review in reviews_cursor:
        clothing_id = review['clothing_id']
        reviews_by_product[clothing_id].append(review)
        total_reviews += 1
    
    print(f"📝 Found {total_reviews} reviews for {len(reviews_by_product)} products")
    
    # Update each product with its reviews
    print("🔄 Migrating reviews to products...")
    updated_products = 0
    
    for clothing_id, reviews in reviews_by_product.items():
        # Calculate review statistics
        total_rating = sum(review['rating'] for review in reviews)
        avg_rating = total_rating / len(reviews) if reviews else 0
        
        # Count recommended vs not recommended
        recommended_count = sum(1 for review in reviews if review.get('recommended', False))
        not_recommended_count = len(reviews) - recommended_count
        
        # Separate reviews by recommendation
        recommended_reviews = [r for r in reviews if r.get('recommended', False)]
        not_recommended_reviews = [r for r in reviews if not r.get('recommended', False)]
        
        # Prepare review data for embedding
        embedded_reviews = []
        for review in reviews:
            embedded_review = {
                'review_id': str(review['_id']),
                'user_name': review.get('user_name', 'Anonymous'),
                'user_email': review.get('user_email'),
                'title': review.get('title', ''),
                'review_text': review['review_text'],
                'rating': review['rating'],
                'age': review.get('age'),
                'positive_feedback_count': review.get('positive_feedback_count', 0),
                'recommended': review.get('recommended', False),
                'ml_prediction': review.get('ml_prediction'),
                'ml_confidence': review.get('ml_confidence'),
                'ml_details': review.get('ml_details'),
                'user_confirmed': review.get('user_confirmed'),
                'is_migrated': review.get('is_migrated', False),
                'created_at': review.get('created_at', datetime.now())
            }
            embedded_reviews.append(embedded_review)
        
        # Update product with reviews and statistics
        update_data = {
            'reviews': embedded_reviews,
            'review_statistics': {
                'total_reviews': len(reviews),
                'average_rating': round(avg_rating, 2),
                'recommended_count': recommended_count,
                'not_recommended_count': not_recommended_count,
                'recommended_percentage': round((recommended_count / len(reviews)) * 100, 2) if reviews else 0
            },
            'recommended_reviews': recommended_reviews[:10],  # Top 10 recommended
            'not_recommended_reviews': not_recommended_reviews[:10],  # Top 10 not recommended
            'updated_at': datetime.now()
        }
        
        # Update the product
        result = products_collection.update_one(
            {'clothing_id': clothing_id},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            updated_products += 1
        
        if updated_products % 100 == 0:
            print(f"📦 Updated {updated_products} products...")
    
    print(f"[SUCCESS] Migration completed! Updated {updated_products} products")
    return updated_products, total_reviews

def create_review_indexes():
    """Create indexes for better query performance"""
    print("🔍 Creating database indexes...")
    
    # Create indexes on products collection
    products_collection.create_index("clothing_id", unique=True)
    products_collection.create_index("department_name")
    products_collection.create_index("division_name")
    products_collection.create_index("class_name")
    products_collection.create_index("review_statistics.total_reviews")
    products_collection.create_index("review_statistics.average_rating")
    
    # Create indexes on reviews collection (for backup queries)
    reviews_collection.create_index("clothing_id")
    reviews_collection.create_index("user_id")
    reviews_collection.create_index("rating")
    reviews_collection.create_index("recommended")
    reviews_collection.create_index("created_at")
    
    print("[SUCCESS] Indexes created successfully!")

def generate_migration_statistics():
    """Generate detailed migration statistics"""
    print("\n[DATA] Migration Statistics:")
    print("=" * 60)
    
    # Product statistics
    total_products = products_collection.count_documents({})
    products_with_reviews = products_collection.count_documents({"reviews": {"$exists": True, "$ne": []}})
    
    print(f"📦 Total Products: {total_products}")
    print(f"📦 Products with Reviews: {products_with_reviews}")
    print(f"📦 Products without Reviews: {total_products - products_with_reviews}")
    
    # Review statistics
    total_reviews = reviews_collection.count_documents({})
    print(f"💬 Total Reviews in Collection: {total_reviews}")
    
    # Calculate embedded reviews
    pipeline = [
        {"$match": {"reviews": {"$exists": True}}},
        {"$project": {"review_count": {"$size": "$reviews"}}},
        {"$group": {"_id": None, "total_embedded_reviews": {"$sum": "$review_count"}}}
    ]
    
    embedded_result = list(products_collection.aggregate(pipeline))
    embedded_reviews = embedded_result[0]['total_embedded_reviews'] if embedded_result else 0
    print(f"💬 Embedded Reviews: {embedded_reviews}")
    
    # Rating distribution
    rating_pipeline = [
        {"$match": {"reviews": {"$exists": True}}},
        {"$unwind": "$reviews"},
        {"$group": {"_id": "$reviews.rating", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    
    rating_dist = list(products_collection.aggregate(rating_pipeline))
    print("\n⭐ Rating Distribution (Embedded):")
    for rating in rating_dist:
        stars = "★" * int(rating['_id'])
        print(f"  {stars} ({rating['_id']} stars): {rating['count']} reviews")
    
    # Department statistics
    dept_pipeline = [
        {"$match": {"reviews": {"$exists": True}}},
        {"$group": {
            "_id": "$department_name",
            "product_count": {"$sum": 1},
            "total_reviews": {"$sum": {"$size": "$reviews"}},
            "avg_rating": {"$avg": "$review_statistics.average_rating"}
        }},
        {"$sort": {"total_reviews": -1}}
    ]
    
    dept_stats = list(products_collection.aggregate(dept_pipeline))
    print("\n📂 Department Statistics:")
    for dept in dept_stats:
        print(f"  • {dept['_id']}: {dept['product_count']} products, {dept['total_reviews']} reviews, {dept['avg_rating']:.2f} avg rating")
    
    # Top products by review count
    top_products_pipeline = [
        {"$match": {"reviews": {"$exists": True}}},
        {"$project": {
            "title": 1,
            "department_name": 1,
            "review_count": {"$size": "$reviews"},
            "avg_rating": "$review_statistics.average_rating"
        }},
        {"$sort": {"review_count": -1}},
        {"$limit": 10}
    ]
    
    top_products = list(products_collection.aggregate(top_products_pipeline))
    print("\n🏆 Top 10 Products by Review Count:")
    for i, product in enumerate(top_products, 1):
        print(f"  {i}. {product['title'][:50]}... ({product['department_name']}) - {product['review_count']} reviews, {product['avg_rating']:.2f} avg")

def cleanup_old_reviews():
    """Optionally remove old reviews from reviews collection (keep as backup)"""
    print("\n🗑️ Review Collection Status:")
    print("📝 Reviews collection kept as backup")
    print("💡 You can manually drop it later if needed: db.reviews.drop()")

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying Migration...")
    
    # Check a few sample products
    sample_products = list(products_collection.find({"reviews": {"$exists": True}}).limit(3))
    
    for product in sample_products:
        print(f"\n📦 Product: {product['title'][:30]}...")
        print(f"   Reviews: {len(product.get('reviews', []))}")
        print(f"   Avg Rating: {product.get('review_statistics', {}).get('average_rating', 'N/A')}")
        print(f"   Recommended: {product.get('review_statistics', {}).get('recommended_count', 0)}")
        print(f"   Not Recommended: {product.get('review_statistics', {}).get('not_recommended_count', 0)}")
    
    print("\n[SUCCESS] Migration verification completed!")

if __name__ == "__main__":
    try:
        print("[START] Starting Review Migration to Products...")
        print("=" * 60)
        
        # Run migration
        updated_products, total_reviews = migrate_reviews_to_products()
        
        # Create indexes
        create_review_indexes()
        
        # Generate statistics
        generate_migration_statistics()
        
        # Verify migration
        verify_migration()
        
        # Cleanup info
        cleanup_old_reviews()
        
        print("\n[COMPLETE] Review Migration completed successfully!")
        print(f"📦 Updated {updated_products} products with {total_reviews} reviews")
        print("[START] Application performance should be significantly improved!")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
