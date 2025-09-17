#!/usr/bin/env python3
"""
One-time ML Model Training Script
Trains models and saves them to disk for the application to use
"""

import os
import sys
from datetime import datetime

def check_models_exist():
    """Check if models already exist"""
    model_files = [
        'models/lr_model.pkl',
        'models/rf_model.pkl', 
        'models/svm_model.pkl',
        'models/tfidf_vectorizer.pkl',
        'models/spacy_embeddings.pkl'
    ]
    
    return all(os.path.exists(f) for f in model_files)

def main():
    print("[START] ML Model Training Script")
    print("=" * 50)
    
    # Check if models already exist
    if check_models_exist():
        print("[SUCCESS] Models already exist!")
        print("Found model files:")
        for model_file in [
            'models/lr_model.pkl',
            'models/rf_model.pkl', 
            'models/svm_model.pkl',
            'models/tfidf_vectorizer.pkl',
            'models/spacy_embeddings.pkl'
        ]:
            if os.path.exists(model_file):
                size = os.path.getsize(model_file) / 1024  # KB
                print(f"   • {model_file} ({size:.1f} KB)")
        
        print("\n💡 To retrain models, delete the models/ directory first")
        print("   rm -rf models/ && python train_models_once.py")
        return 0
    
    print("🔍 Models not found, starting training...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import and run the training
        from train_models import main as train_main
        train_main()
        
        print(f"[SUCCESS] Training completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
