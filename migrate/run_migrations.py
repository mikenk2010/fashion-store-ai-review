#!/usr/bin/env python3
"""
Migration runner for Fashion Store application
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_products_migration():
    """Run products migration"""
    print("🔄 Running products migration...")
    try:
        from migrate_products import main as migrate_products
        migrate_products()
        print("[SUCCESS] Products migration completed successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Products migration failed: {e}")
        return False

def run_reviews_migration():
    """Run reviews migration"""
    print("🔄 Running reviews migration...")
    try:
        from migrate_reviews_to_products import main as migrate_reviews
        migrate_reviews()
        print("[SUCCESS] Reviews migration completed successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Reviews migration failed: {e}")
        return False

def run_ml_training():
    """Run ML model training"""
    print("[ML] Running ML model training...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'models'))
        from train_models import main as train_models
        train_models()
        print("[SUCCESS] ML model training completed successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] ML model training failed: {e}")
        return False

def main():
    """Main migration runner"""
    parser = argparse.ArgumentParser(description='Run Fashion Store migrations')
    parser.add_argument('--migration', choices=['products', 'reviews', 'ml', 'all'], 
                       default='all', help='Which migration to run')
    parser.add_argument('--force', action='store_true', 
                       help='Force run even if data exists')
    
    args = parser.parse_args()
    
    print(f"[START] Starting Fashion Store Migrations - {datetime.now().isoformat()}")
    print("=" * 60)
    
    success = True
    
    if args.migration in ['products', 'all']:
        success &= run_products_migration()
    
    if args.migration in ['reviews', 'all'] and success:
        success &= run_reviews_migration()
    
    if args.migration in ['ml', 'all'] and success:
        success &= run_ml_training()
    
    print("\n" + "=" * 60)
    if success:
        print("[COMPLETE] All migrations completed successfully!")
    else:
        print("[ERROR] Some migrations failed. Check the logs above.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
