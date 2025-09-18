#!/usr/bin/env python3
"""
Fixed version of train_models.py with proper indentation
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import spacy
import re
from collections import Counter

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config.logging_config import setup_logging, log_ml_training_complete, log_exception

# Setup logging
loggers = setup_logging()
ml_logger = loggers['ml_training']

def load_spacy_model():
    """Load spaCy model"""
    try:
        nlp = spacy.load('en_core_web_md')
        print("spaCy model loaded successfully")
        return nlp
    except OSError:
        print("spaCy model not found. Downloading...")
        os.system("python -m spacy download en_core_web_md")
        nlp = spacy.load('en_core_web_md')
        return nlp

def preprocess_text(text):
    """Preprocess text for ML models"""
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def get_spacy_embeddings(texts, nlp):
    """Get spaCy embeddings for texts"""
    embeddings = []
    for text in texts:
        doc = nlp(text)
        if doc.has_vector:
            embeddings.append(doc.vector)
        else:
            # Use zero vector if no embedding available
            embeddings.append(np.zeros(300))
    return np.array(embeddings)

def get_tfidf_weighted_embeddings(texts, nlp, tfidf_vectorizer):
    """Get TF-IDF weighted spaCy embeddings"""
    embeddings = get_spacy_embeddings(texts, nlp)
    tfidf_matrix = tfidf_vectorizer.transform(texts)
    
    # Weight embeddings by TF-IDF scores
    weighted_embeddings = []
    for i, embedding in enumerate(embeddings):
        tfidf_scores = tfidf_matrix[i].toarray().flatten()
        # Simple weighting: multiply embedding by average TF-IDF score
        weight = np.mean(tfidf_scores) if np.sum(tfidf_scores) > 0 else 0.1
        weighted_embeddings.append(embedding * weight)
    
    return np.array(weighted_embeddings)

def train_models():
    """Train all three models with different feature representations"""
    ml_logger.info("[START] Starting Advanced ML Model Training")
    print("[START] Starting Advanced ML Model Training")
    
    try:
        # Load spaCy model
        nlp = load_spacy_model()
    
        # Load dataset
        ml_logger.info("[DATA] Loading dataset")
        print("[DATA] Loading dataset")
        df = pd.read_csv('data/data-assignment3_II.csv')
        
        dataset_size = len(df)
        ml_logger.info(f"Dataset loaded: {dataset_size} reviews")
        print(f"Dataset loaded: {dataset_size} reviews")
        print(f"Columns: {df.columns.tolist()}")
        
        # Check for missing values
        missing_review_text = df['Review Text'].isna().sum()
        missing_recommended = df['Recommended IND'].isna().sum()
        ml_logger.info(f"Missing values - Review Text: {missing_review_text}, Recommended IND: {missing_recommended}")
        print(f"Missing values in Review Text: {missing_review_text}")
        print(f"Missing values in Recommended IND: {missing_recommended}")
        
        # Remove rows with missing review text
        df = df.dropna(subset=['Review Text', 'Recommended IND'])
        final_dataset_size = len(df)
        ml_logger.info(f"After removing missing values: {final_dataset_size} reviews")
        print(f"After removing missing values: {final_dataset_size} reviews")
        
        # Preprocess the text
        print("[PROCESS] Preprocessing text")
        df['cleaned_text'] = df['Review Text'].apply(preprocess_text)
        
        # Remove empty reviews after preprocessing
        df = df[df['cleaned_text'].str.len() > 0]
        print(f"After text preprocessing: {len(df)} reviews")
        
        # Prepare features and target
        X = df['cleaned_text']
        y = df['Recommended IND']
        
        print(f"Class distribution:")
        print(f"Recommended (1): {sum(y == 1)} ({sum(y == 1)/len(y)*100:.1f}%)")
        print(f"Not Recommended (0): {sum(y == 0)} ({sum(y == 0)/len(y)*100:.1f}%)")
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Create feature representations
        print("\nCreating feature representations")
        
        # 1. Bag of Words (BoW) - for Logistic Regression
        print("Creating Bag of Words features")
        bow_vectorizer = CountVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        X_train_bow = bow_vectorizer.fit_transform(X_train)
        X_test_bow = bow_vectorizer.transform(X_test)
        
        # 2. TF-IDF - for weighted embeddings
        print("Creating TF-IDF features")
        tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = tfidf_vectorizer.transform(X_test)
        
        # 3. spaCy Unweighted Embeddings - for Random Forest
        print("Creating spaCy unweighted embeddings")
        X_train_embeddings = get_spacy_embeddings(X_train.tolist(), nlp)
        X_test_embeddings = get_spacy_embeddings(X_test.tolist(), nlp)
        
        # 4. TF-IDF Weighted Embeddings - for SVM
        print("Creating TF-IDF weighted embeddings")
        X_train_weighted = get_tfidf_weighted_embeddings(X_train.tolist(), nlp, tfidf_vectorizer)
        X_test_weighted = get_tfidf_weighted_embeddings(X_test.tolist(), nlp, tfidf_vectorizer)
        
        # Scale embeddings
        scaler_embeddings = StandardScaler()
        X_train_embeddings_scaled = scaler_embeddings.fit_transform(X_train_embeddings)
        X_test_embeddings_scaled = scaler_embeddings.transform(X_test_embeddings)
        
        scaler_weighted = StandardScaler()
        X_train_weighted_scaled = scaler_weighted.fit_transform(X_train_weighted)
        X_test_weighted_scaled = scaler_weighted.transform(X_test_weighted)
        
        # Train models
        print("\nTraining models...")
        
        # 1. Logistic Regression (BoW)
        print("Training Logistic Regression...")
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train_bow, y_train)
        lr_pred = lr_model.predict(X_test_bow)
        lr_accuracy = accuracy_score(y_test, lr_pred)
        print(f"Logistic Regression Accuracy: {lr_accuracy:.4f}")
        
        # 2. Random Forest (Embeddings)
        print("Training Random Forest...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train_embeddings_scaled, y_train)
        rf_pred = rf_model.predict(X_test_embeddings_scaled)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        print(f"Random Forest Accuracy: {rf_accuracy:.4f}")
        
        # 3. SVM (Weighted Embeddings)
        print("Training SVM...")
        svm_model = SVC(probability=True, random_state=42)
        svm_model.fit(X_train_weighted_scaled, y_train)
        svm_pred = svm_model.predict(X_test_weighted_scaled)
        svm_accuracy = accuracy_score(y_test, svm_pred)
        print(f"SVM Accuracy: {svm_accuracy:.4f}")
        
        # Save models and vectorizers
        print("\nSaving models...")
        os.makedirs('models', exist_ok=True)
        
        joblib.dump(lr_model, 'models/lr_model.joblib')
        joblib.dump(rf_model, 'models/rf_model.joblib')
        joblib.dump(svm_model, 'models/svm_model.joblib')
        joblib.dump(bow_vectorizer, 'models/bow_vectorizer.joblib')
        joblib.dump(tfidf_vectorizer, 'models/tfidf_vectorizer.joblib')
        joblib.dump(scaler_embeddings, 'models/scaler_embeddings.joblib')
        joblib.dump(scaler_weighted, 'models/scaler_weighted.joblib')
        
        # Also save as .pkl for compatibility
        joblib.dump(lr_model, 'models/lr_model.pkl')
        joblib.dump(rf_model, 'models/rf_model.pkl')
        joblib.dump(svm_model, 'models/svm_model.pkl')
        joblib.dump(bow_vectorizer, 'models/bow_vectorizer.pkl')
        joblib.dump(tfidf_vectorizer, 'models/tfidf_vectorizer.pkl')
        joblib.dump(scaler_embeddings, 'models/scaler_embeddings.pkl')
        joblib.dump(scaler_weighted, 'models/scaler_weighted.pkl')
        
        print("Models saved successfully!")
        
        # Ensemble prediction
        print("\nTesting ensemble...")
        lr_proba = lr_model.predict_proba(X_test_bow)[:, 1]
        rf_proba = rf_model.predict_proba(X_test_embeddings_scaled)[:, 1]
        svm_proba = svm_model.predict_proba(X_test_weighted_scaled)[:, 1]
        
        ensemble_proba = (lr_proba + rf_proba + svm_proba) / 3
        ensemble_pred = (ensemble_proba > 0.5).astype(int)
        ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
        
        print(f"Ensemble Accuracy: {ensemble_accuracy:.4f}")
        
        # Print detailed results
        print("\nDetailed Results:")
        print(f"Logistic Regression: {lr_accuracy:.4f}")
        print(f"Random Forest: {rf_accuracy:.4f}")
        print(f"SVM: {svm_accuracy:.4f}")
        print(f"Ensemble: {ensemble_accuracy:.4f}")
        
        return {
            'lr_accuracy': lr_accuracy,
            'rf_accuracy': rf_accuracy,
            'svm_accuracy': svm_accuracy,
            'ensemble_accuracy': ensemble_accuracy,
            'best_accuracy': max(lr_accuracy, rf_accuracy, svm_accuracy, ensemble_accuracy)
        }
        
    except Exception as e:
        print(f"[ERROR] Training failed: {str(e)}")
        ml_logger.error(f"Training failed: {str(e)}")
        raise e

if __name__ == '__main__':
    start_time = time.time()
    
    try:
        results = train_models()
        
        total_time = time.time() - start_time
        print(f"\n[COMPLETE] Training completed successfully in {total_time:.2f} seconds!")
        
    except Exception as e:
        print(f"[ERROR] Training failed: {str(e)}")
        exit(1)
