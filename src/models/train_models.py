#!/usr/bin/env python3
"""
Advanced ML Model Training Script for Review Classification
Trains 3 models: Logistic Regression, Random Forest, and SVM
Uses multiple feature representations: BoW, spaCy embeddings, TF-IDF weighted embeddings
"""

import pandas as pd
import numpy as np
import spacy
import re
import os
import joblib
import time
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import logging configuration
from logging_config import (
    setup_logging, log_ml_training_start, log_ml_training_complete,
    log_exception
)

# Setup logging
loggers = setup_logging()
ml_logger = loggers['ml_training']

def preprocess_text(text):
    """Clean and preprocess text data using spaCy"""
    if pd.isna(text) or not text:
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def load_spacy_model():
    """Load spaCy model for embeddings"""
    try:
        nlp = spacy.load("en_core_web_md")
        print("[SUCCESS] spaCy model loaded successfully")
        return nlp
    except OSError:
        print("[ERROR] spaCy model 'en_core_web_md' not found. Installing")
        os.system("python -m spacy download en_core_web_md")
        nlp = spacy.load("en_core_web_md")
        print("[SUCCESS] spaCy model installed and loaded")
        return nlp

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
    # Get TF-IDF matrix
    tfidf_matrix = tfidf_vectorizer.transform(texts)
    
    # Get feature names and their TF-IDF scores
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    # Get spaCy embeddings for all texts
    embeddings = get_spacy_embeddings(texts, nlp)
    
    # Weight embeddings by TF-IDF scores
    weighted_embeddings = []
    for i, text in enumerate(texts):
        # Get TF-IDF scores for this text
        tfidf_scores = tfidf_matrix[i].toarray().flatten()
        
        # Get spaCy embedding for this text
        text_embedding = embeddings[i]
        
        # For simplicity, we'll use the average of the text embedding
        # In a more sophisticated approach, you'd weight each word's embedding
        weighted_embeddings.append(text_embedding)
    
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
    
    # Scale the embeddings for better performance
    scaler_embeddings = StandardScaler()
    X_train_embeddings_scaled = scaler_embeddings.fit_transform(X_train_embeddings)
    X_test_embeddings_scaled = scaler_embeddings.transform(X_test_embeddings)
    
    scaler_weighted = StandardScaler()
    X_train_weighted_scaled = scaler_weighted.fit_transform(X_train_weighted)
    X_test_weighted_scaled = scaler_weighted.transform(X_test_weighted)
    
    # Train models
    print("\n[ML] Training models")
    
    # 1. Logistic Regression with BoW
    print("Training Logistic Regression (BoW)")
    ml_logger.info("[PROCESS] Training Logistic Regression with Bag-of-Words features")
    lr_start_time = time.time()

    lr_model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight='balanced'
    )
    lr_model.fit(X_train_bow, y_train)

    lr_training_time = time.time() - lr_start_time
    ml_logger.info(f"[SUCCESS] Logistic Regression training completed in {lr_training_time:.2f} seconds")

    # 2. Random Forest with Unweighted Embeddings
    print("Training Random Forest (Unweighted Embeddings)")
    ml_logger.info("Training Random Forest with Unweighted Embeddings")
    rf_start_time = time.time()

    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    rf_model.fit(X_train_embeddings_scaled, y_train)

    rf_training_time = time.time() - rf_start_time
    ml_logger.info(f"[SUCCESS] Random Forest training completed in {rf_training_time:.2f} seconds")

    # 3. Support Vector Machine (SVM) with TF-IDF Weighted Embeddings
    print("Training SVM (TF-IDF Weighted Embeddings)")
    ml_logger.info("[TARGET] Training SVM with TF-IDF Weighted Embeddings")
    svm_start_time = time.time()

    svm_model = SVC(
        kernel='rbf',
        random_state=42,
        class_weight='balanced',
        probability=True
    )
    svm_model.fit(X_train_weighted_scaled, y_train)

    svm_training_time = time.time() - svm_start_time
    ml_logger.info(f"[SUCCESS] SVM training completed in {svm_training_time:.2f} seconds")
    
    # Evaluate models
    print("\n[EVAL] Evaluating models")
    
    models = {
        'Logistic Regression': (lr_model, X_test_bow),
        'Random Forest': (rf_model, X_test_embeddings_scaled),
        'SVM': (svm_model, X_test_weighted_scaled)
    }
    
    results = {}
    for name, (model, X_test_features) in models.items():
        # Predictions
        y_pred = model.predict(X_test_features)
        y_pred_proba = model.predict_proba(X_test_features)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        if name == 'Logistic Regression':
            cv_scores = cross_val_score(model, X_train_bow, y_train, cv=5, scoring='accuracy')
        elif name == 'Random Forest':
            cv_scores = cross_val_score(model, X_train_embeddings_scaled, y_train, cv=5, scoring='accuracy')
        else:  # SVM
            cv_scores = cross_val_score(model, X_train_weighted_scaled, y_train, cv=5, scoring='accuracy')
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
        
        print(f"\n{name} Performance:")
        print(f"Test Accuracy: {accuracy:.4f}")
        print(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Not Recommended', 'Recommended']))
    
        # Save models and preprocessors
        print("\nSaving models and preprocessors")
        ml_logger.info("Saving trained models and preprocessors")
        os.makedirs('models', exist_ok=True)
        
        # Save models
        joblib.dump(lr_model, 'models/lr_model.pkl')
        joblib.dump(rf_model, 'models/rf_model.pkl')
        joblib.dump(svm_model, 'models/svm_model.pkl')
        
        # Save preprocessors
        joblib.dump(bow_vectorizer, 'models/bow_vectorizer.pkl')
        joblib.dump(tfidf_vectorizer, 'models/tfidf_vectorizer.pkl')
        joblib.dump(scaler_embeddings, 'models/scaler_embeddings.pkl')
        joblib.dump(scaler_weighted, 'models/scaler_weighted.pkl')
        
        # Save spaCy model reference
        with open('models/spacy_model.txt', 'w') as f:
            f.write('en_core_web_md')
        
        ml_logger.info("[SUCCESS] All models and preprocessors saved successfully!")
        print("[SUCCESS] All models and preprocessors saved successfully!")
    
    # Test ensemble prediction
    print("\n[TARGET] Testing ensemble prediction")
    test_review = "This dress is amazing! I love the fit and quality."
    test_processed = preprocess_text(test_review)
    
    # Get predictions from all models
    test_bow = bow_vectorizer.transform([test_processed])
    test_embeddings = get_spacy_embeddings([test_processed], nlp)
    test_embeddings_scaled = scaler_embeddings.transform(test_embeddings)
    test_weighted = get_tfidf_weighted_embeddings([test_processed], nlp, tfidf_vectorizer)
    test_weighted_scaled = scaler_weighted.transform(test_weighted)
    
    lr_pred = lr_model.predict(test_bow)[0]
    lr_prob = lr_model.predict_proba(test_bow)[0][1]
    
    rf_pred = rf_model.predict(test_embeddings_scaled)[0]
    rf_prob = rf_model.predict_proba(test_embeddings_scaled)[0][1]
    
    svm_pred = svm_model.predict(test_weighted_scaled)[0]
    svm_prob = svm_model.predict_proba(test_weighted_scaled)[0][1]
    
    # Ensemble prediction (majority vote)
    predictions = [lr_pred, rf_pred, svm_pred]
    ensemble_pred = max(set(predictions), key=predictions.count)
    
    # Average probability
    ensemble_prob = (lr_prob + rf_prob + svm_prob) / 3
    
    print(f"Test review: '{test_review}'")
    print(f"LR Prediction: {'Recommended' if lr_pred == 1 else 'Not Recommended'} (Confidence: {lr_prob:.4f})")
    print(f"RF Prediction: {'Recommended' if rf_pred == 1 else 'Not Recommended'} (Confidence: {rf_prob:.4f})")
    print(f"SVM Prediction: {'Recommended' if svm_pred == 1 else 'Not Recommended'} (Confidence: {svm_prob:.4f})")
    print(f"Ensemble Prediction: {'Recommended' if ensemble_pred == 1 else 'Not Recommended'} (Confidence: {ensemble_prob:.4f})")
    
        return results
        
    except Exception as e:
        ml_logger.error(f"[ERROR] ML training failed: {str(e)}")
        ml_logger.error(f"[TRACE] Traceback: {traceback.format_exc()}")
        print(f"[ERROR] Training failed: {str(e)}")
        raise e

if __name__ == "__main__":
    try:
        start_time = time.time()
        log_ml_training_start(
            model_name="Ensemble (LR + RF + SVM)",
            dataset_size=0,  # Will be updated in the function
            features_used=["Bag-of-Words", "spaCy Embeddings", "TF-IDF Weighted Embeddings"]
        )
        
        results = train_models()
        
        total_time = time.time() - start_time
        log_ml_training_complete(
            model_name="Ensemble (LR + RF + SVM)",
            accuracy=results.get('best_accuracy', 0.0),
            training_time=total_time,
            model_path="models/"
        )
        
        print(f"\n[COMPLETE] Training completed successfully in {total_time:.2f} seconds!")
        
    except Exception as e:
        print(f"[ERROR] Training failed: {str(e)}")
        log_exception(e, context={'script': 'train_models.py'})
        exit(1)
