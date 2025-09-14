#!/usr/bin/env python3
"""
ML Utilities for Review Classification
Handles model loading, prediction, and ensemble fusion

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import os
import re
import joblib
import numpy as np
import spacy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ReviewClassifier:
    """Review classification using ensemble of 3 models"""
    
    def __init__(self):
        self.lr_model = None
        self.rf_model = None
        self.svm_model = None
        self.bow_vectorizer = None
        self.tfidf_vectorizer = None
        self.scaler_embeddings = None
        self.scaler_weighted = None
        self.nlp = None
        self.models_loaded = False
        
        # Load models automatically
        self.load_models()
        
    def load_models(self):
        """Load all pre-trained models and preprocessors"""
        try:
            # Load models
            self.lr_model = joblib.load('models/lr_model.joblib')
            self.rf_model = joblib.load('models/rf_model.joblib')
            self.svm_model = joblib.load('models/svm_model.joblib')
            
            # Load preprocessors
            self.bow_vectorizer = joblib.load('models/bow_vectorizer.joblib')
            self.tfidf_vectorizer = joblib.load('models/tfidf_vectorizer.joblib')
            self.scaler_embeddings = joblib.load('models/scaler_embeddings.joblib')
            self.scaler_weighted = joblib.load('models/scaler_weighted.joblib')
            
            # Load spaCy model
            with open('models/spacy_model.txt', 'r') as f:
                spacy_model_name = f.read().strip()
            self.nlp = spacy.load(spacy_model_name)
            
            self.models_loaded = True
            print("[SUCCESS] All ML models loaded successfully!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading models: {e}")
            print("Please run train_models.py first to create the models.")
            return False
    
    def preprocess_text(self, text):
        """Clean and preprocess text data"""
        if not text or pd.isna(text):
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_spacy_embeddings(self, texts):
        """Get spaCy embeddings for texts"""
        embeddings = []
        for text in texts:
            doc = self.nlp(text)
            if doc.has_vector:
                embeddings.append(doc.vector)
            else:
                # Use zero vector if no embedding available
                embeddings.append(np.zeros(300))
        return np.array(embeddings)
    
    def get_tfidf_weighted_embeddings(self, texts):
        """Get TF-IDF weighted spaCy embeddings"""
        # Get TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.transform(texts)
        
        # Get spaCy embeddings for all texts
        embeddings = self.get_spacy_embeddings(texts)
        
        # For simplicity, we'll use the average of the text embedding
        # In a more sophisticated approach, you'd weight each word's embedding
        return embeddings
    
    def predict_single(self, review_text, title="", rating=None):
        """Predict recommendation for a single review using ensemble"""
        if not self.models_loaded:
            return None, 0.0, {}
        
        try:
            # Combine title and text for better prediction
            combined_text = f"{title} {review_text}".strip()
            
            # Preprocess text
            processed_text = self.preprocess_text(combined_text)
            
            if not processed_text:
                return None, 0.0, {}
            
            # Prepare features for each model
            # 1. BoW for Logistic Regression
            bow_features = self.bow_vectorizer.transform([processed_text])
            
            # 2. Unweighted embeddings for Random Forest
            embeddings = self.get_spacy_embeddings([processed_text])
            embeddings_scaled = self.scaler_embeddings.transform(embeddings)
            
            # 3. TF-IDF weighted embeddings for SVM
            weighted_embeddings = self.get_tfidf_weighted_embeddings([processed_text])
            weighted_scaled = self.scaler_weighted.transform(weighted_embeddings)
            
            # Get predictions from all models
            lr_pred = self.lr_model.predict(bow_features)[0]
            lr_prob = self.lr_model.predict_proba(bow_features)[0][1]
            
            rf_pred = self.rf_model.predict(embeddings_scaled)[0]
            rf_prob = self.rf_model.predict_proba(embeddings_scaled)[0][1]
            
            svm_pred = self.svm_model.predict(weighted_scaled)[0]
            svm_prob = self.svm_model.predict_proba(weighted_scaled)[0][1]
            
            # Individual model results
            individual_results = {
                'logistic_regression': {
                    'prediction': int(lr_pred),
                    'confidence': float(lr_prob),
                    'label': 'Recommended' if lr_pred == 1 else 'Not Recommended'
                },
                'random_forest': {
                    'prediction': int(rf_pred),
                    'confidence': float(rf_prob),
                    'label': 'Recommended' if rf_pred == 1 else 'Not Recommended'
                },
                'svm': {
                    'prediction': int(svm_pred),
                    'confidence': float(svm_prob),
                    'label': 'Recommended' if svm_pred == 1 else 'Not Recommended'
                }
            }
            
            # Ensemble prediction (majority vote)
            predictions = [lr_pred, rf_pred, svm_pred]
            ensemble_pred = max(set(predictions), key=predictions.count)
            
            # Average probability for ensemble confidence
            ensemble_prob = (lr_prob + rf_prob + svm_prob) / 3
            
            # Check if there's consensus
            consensus = len(set(predictions)) == 1
            
            return int(ensemble_pred), float(ensemble_prob), {
                'individual_results': individual_results,
                'consensus': consensus,
                'ensemble_prediction': int(ensemble_pred),
                'ensemble_confidence': float(ensemble_prob),
                'ensemble_label': 'Recommended' if ensemble_pred == 1 else 'Not Recommended'
            }
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return None, 0.0, {}
    
    def predict_batch(self, review_texts):
        """Predict recommendations for multiple reviews"""
        if not self.models_loaded:
            return []
        
        results = []
        for text in review_texts:
            pred, conf, details = self.predict_single(text)
            results.append({
                'text': text,
                'prediction': pred,
                'confidence': conf,
                'details': details
            })
        
        return results
    
    def get_model_info(self):
        """Get information about loaded models"""
        if not self.models_loaded:
            return {"error": "Models not loaded"}
        
        return {
            "models_loaded": True,
            "models": ["Logistic Regression", "Random Forest", "SVM"],
            "features": ["Bag of Words", "spaCy Embeddings", "TF-IDF Weighted Embeddings"],
            "fusion_method": "Majority Vote + Average Probability"
        }

# Global classifier instance
classifier = ReviewClassifier()

def load_ml_models():
    """Load ML models (convenience function)"""
    return classifier.load_models()

def predict_review_sentiment(review_text, title="", rating=None):
    """Predict review sentiment (convenience function)"""
    # Ensure models are loaded
    if not classifier.models_loaded:
        classifier.load_models()
    return classifier.predict_single(review_text, title, rating)

def get_model_info():
    """Get model information (convenience function)"""
    return classifier.get_model_info()
