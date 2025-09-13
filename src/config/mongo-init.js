// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the ecommerce database
db = db.getSiblingDB('ecommerce_db');

// Create collections
db.createCollection('products');
db.createCollection('reviews');

// Create indexes for better performance
db.products.createIndex({ "clothing_id": 1 }, { unique: true });
db.products.createIndex({ "department_name": 1 });
db.products.createIndex({ "division_name": 1 });
db.products.createIndex({ "class_name": 1 });
db.products.createIndex({ "created_at": -1 });

db.reviews.createIndex({ "clothing_id": 1 });
db.reviews.createIndex({ "created_at": -1 });
db.reviews.createIndex({ "ml_prediction": 1 });
db.reviews.createIndex({ "user_confirmed": 1 });

print('MongoDB initialization completed successfully!');
