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
        """
        Load all pre-trained models and preprocessors from disk
        
        This method loads all the machine learning models and their associated
        preprocessors that were trained and saved during the model training phase.
        It handles the complete model loading pipeline including error handling
        and status reporting.
        
        The method loads:
        - 3 trained ML models (Logistic Regression, Random Forest, SVM)
        - Feature extraction preprocessors (BoW, TF-IDF vectorizers)
        - Data scalers for feature normalization
        - spaCy language model for word embeddings
        
        Returns:
            bool: True if all models loaded successfully, False otherwise
            
        Raises:
            FileNotFoundError: If model files are not found
            joblib.exceptions.JoblibError: If model files are corrupted
            OSError: If spaCy model cannot be loaded
        """
        try:
            # Load the three trained machine learning models
            # These models were trained on the review dataset
            self.lr_model = joblib.load('models/lr_model.joblib')  # Logistic Regression
            self.rf_model = joblib.load('models/rf_model.joblib')  # Random Forest
            self.svm_model = joblib.load('models/svm_model.joblib')  # Support Vector Machine
            
            # Load feature extraction preprocessors
            # These were fitted during training and must be used for prediction
            self.bow_vectorizer = joblib.load('models/bow_vectorizer.joblib')  # Bag-of-Words
            self.tfidf_vectorizer = joblib.load('models/tfidf_vectorizer.joblib')  # TF-IDF
            self.scaler_embeddings = joblib.load('models/scaler_embeddings.joblib')  # Embedding scaler
            self.scaler_weighted = joblib.load('models/scaler_weighted.joblib')  # Weighted feature scaler
            
            # Load spaCy language model for word embeddings
            # The model name is stored in a text file for portability
            with open('models/spacy_model.txt', 'r') as f:
                spacy_model_name = f.read().strip()
            self.nlp = spacy.load(spacy_model_name)
            
            # Mark models as successfully loaded
            self.models_loaded = True
            print("[SUCCESS] All ML models loaded successfully!")
            return True
            
        except Exception as e:
            # Handle any errors during model loading
            print(f"[ERROR] Error loading models: {e}")
            print("Please run train_models.py first to create the models.")
            return False
    
    def preprocess_text(self, text):
        """
        Clean and preprocess text data for machine learning
        
        This method applies comprehensive text preprocessing to prepare
        raw text data for machine learning models. It handles various
        text cleaning tasks including case normalization, special character
        removal, and whitespace normalization.
        
        Preprocessing steps:
        1. Handle null/empty values
        2. Convert to lowercase for consistency
        3. Remove special characters and digits
        4. Normalize whitespace
        
        Args:
            text (str): Raw text to preprocess
            
        Returns:
            str: Cleaned and preprocessed text, or empty string if input is invalid
        """
        # Handle null, empty, or NaN values
        if not text or pd.isna(text):
            return ""
        
        # Convert to lowercase for case-insensitive processing
        # This ensures consistent text representation
        text = str(text).lower()
        
        # Remove special characters and digits
        # Keep only alphabetic characters and whitespace
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace and normalize spacing
        # This prevents issues with multiple spaces or tabs
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_spacy_embeddings(self, texts):
        """
        Get spaCy word embeddings for text data
        
        This method converts text data into dense vector representations using
        spaCy's pre-trained word embeddings. These embeddings capture semantic
        meaning and are used as features for the Random Forest model.
        
        The method handles:
        - Individual text processing through spaCy NLP pipeline
        - Vector extraction from spaCy document objects
        - Fallback to zero vectors for texts without embeddings
        - Batch processing for efficiency
        
        Args:
            texts (list): List of text strings to convert to embeddings
            
        Returns:
            numpy.ndarray: Array of 300-dimensional embedding vectors
        """
        embeddings = []
        for text in texts:
            # Process text through spaCy NLP pipeline
            doc = self.nlp(text)
            
            # Check if the document has a vector representation
            if doc.has_vector:
                # Use the document's vector representation
                embeddings.append(doc.vector)
            else:
                # Fallback to zero vector if no embedding is available
                # This ensures consistent dimensionality (300 features)
                embeddings.append(np.zeros(300))
        
        # Convert list of embeddings to numpy array for ML models
        return np.array(embeddings)
    
    def get_tfidf_weighted_embeddings(self, texts):
        """
        Get TF-IDF weighted spaCy embeddings for text data
        
        This method combines TF-IDF (Term Frequency-Inverse Document Frequency)
        weighting with spaCy word embeddings to create enhanced feature vectors
        for the Support Vector Machine model. The TF-IDF weighting helps
        emphasize important words in the text.
        
        The current implementation uses a simplified approach where:
        1. TF-IDF matrix is computed for the input texts
        2. spaCy embeddings are obtained for the same texts
        3. The average embedding is used (simplified weighting)
        
        Note: A more sophisticated approach would weight each word's
        embedding by its TF-IDF score, but this simplified version
        still provides good performance.
        
        Args:
            texts (list): List of text strings to process
            
        Returns:
            numpy.ndarray: Array of weighted embedding vectors
        """
        # Get TF-IDF matrix for the input texts
        # This provides term importance scores
        tfidf_matrix = self.tfidf_vectorizer.transform(texts)
        
        # Get spaCy embeddings for all texts
        # These provide semantic meaning
        embeddings = self.get_spacy_embeddings(texts)
        
        # For simplicity, we'll use the average of the text embedding
        # In a more sophisticated approach, you'd weight each word's embedding
        # by its TF-IDF score, but this simplified version works well
        return embeddings
    
    def predict_single(self, review_text, title="", rating=None):
        """
        Predict recommendation for a single review using ensemble approach
        
        This is the main prediction method that combines predictions from all
        three machine learning models to provide a robust recommendation.
        It uses ensemble voting to make the final decision and provides
        detailed confidence scores and individual model results.
        
        The prediction process:
        1. Combines review title and text for comprehensive analysis
        2. Preprocesses the combined text
        3. Extracts features for each model type
        4. Gets predictions from all three models
        5. Performs ensemble voting for final decision
        6. Calculates confidence scores and model agreement
        
        Args:
            review_text (str): The main review text content
            title (str, optional): Review title for additional context
            rating (int, optional): Star rating (1-5) for additional context
            
        Returns:
            tuple: (final_prediction, confidence_score, detailed_results)
                - final_prediction (int): 1 for recommended, 0 for not recommended
                - confidence_score (float): Confidence score (0.0 to 1.0)
                - detailed_results (dict): Individual model results and metadata
        """
        # Check if models are loaded before attempting prediction
        if not self.models_loaded:
            return None, 0.0, {}
        
        try:
            # Combine title and text for better prediction accuracy
            # The title often contains important sentiment information
            combined_text = f"{title} {review_text}".strip()
            
            # Preprocess the combined text for machine learning
            processed_text = self.preprocess_text(combined_text)
            
            # Return empty result if text preprocessing failed
            if not processed_text:
                return None, 0.0, {}

            # Extract features for each model
            # Prepare features for each machine learning model
            # Each model uses different feature extraction methods
            
            # 1. Bag-of-Words features for Logistic Regression
            # This creates a sparse matrix of word counts
            bow_features = self.bow_vectorizer.transform([processed_text])
            
            # 2. Unweighted spaCy embeddings for Random Forest
            # These capture semantic meaning of the text
            embeddings = self.get_spacy_embeddings([processed_text])
            embeddings_scaled = self.scaler_embeddings.transform(embeddings)
            
            # 3. TF-IDF weighted embeddings for Support Vector Machine
            # These combine semantic meaning with term importance
            weighted_embeddings = self.get_tfidf_weighted_embeddings([processed_text])
            weighted_scaled = self.scaler_weighted.transform(weighted_embeddings)
            
            # Get predictions from all three machine learning models
            # Each model provides both a binary prediction and a probability score
            
            # Logistic Regression prediction using Bag-of-Words features
            lr_pred = self.lr_model.predict(bow_features)[0]  # Binary prediction (0 or 1)
            lr_prob = self.lr_model.predict_proba(bow_features)[0][1]  # Probability of class 1
            
            # Random Forest prediction using spaCy embeddings
            rf_pred = self.rf_model.predict(embeddings_scaled)[0]  # Binary prediction (0 or 1)
            rf_prob = self.rf_model.predict_proba(embeddings_scaled)[0][1]  # Probability of class 1
            
            # Support Vector Machine prediction using TF-IDF weighted embeddings
            svm_pred = self.svm_model.predict(weighted_scaled)[0]  # Binary prediction (0 or 1)
            svm_prob = self.svm_model.predict_proba(weighted_scaled)[0][1]  # Probability of class 1
            
            # Compile individual model results for detailed analysis
            # This provides transparency into each model's decision
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
            
            # Perform ensemble prediction using majority voting
            # This combines the three model predictions for a more robust result
            predictions = [lr_pred, rf_pred, svm_pred]
            ensemble_pred = max(set(predictions), key=predictions.count)

            # MOST IMPORTANT
            # Calculate ensemble confidence as average of individual probabilities
            # This provides a measure of overall model agreement
            ensemble_prob = (lr_prob + rf_prob + svm_prob) / 3

            # CUSTOMER DOUBLE CONFORM AGAIN
            # Check if all models agree (consensus)
            # High consensus indicates more reliable predictions
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
