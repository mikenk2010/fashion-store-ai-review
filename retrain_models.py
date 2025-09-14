#!/usr/bin/env python3
"""
Retrain ML models with proper class imbalance handling

Authors: 
- Hoang Chau Le <s3715228@rmit.edu.vn>
- Bao Nguyen <s4139514@rmit.edu.vn>

Version: 1.0.0
"""

import os
import re
import joblib
import numpy as np
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import warnings
warnings.filterwarnings('ignore')

def preprocess_text(text):
    """Preprocess text for ML models"""
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_spacy_embeddings(texts, nlp):
    """Get spaCy embeddings for texts"""
    embeddings = []
    for text in texts:
        doc = nlp(text)
        if doc.has_vector:
            embeddings.append(doc.vector)
        else:
            embeddings.append(np.zeros(300))  # Default vector size for en_core_web_md
    return np.array(embeddings)

def get_tfidf_weighted_embeddings(texts, nlp, tfidf_vectorizer):
    """Get TF-IDF weighted spaCy embeddings"""
    # Get TF-IDF matrix
    tfidf_matrix = tfidf_vectorizer.transform(texts)
    
    # Get spaCy embeddings
    embeddings = get_spacy_embeddings(texts, nlp)
    
    # Weight embeddings by TF-IDF scores
    weighted_embeddings = []
    for i, text in enumerate(texts):
        # Get TF-IDF scores for this text
        tfidf_scores = tfidf_matrix[i].toarray()[0]
        
        # Get word tokens and their embeddings
        doc = nlp(text)
        word_embeddings = []
        word_weights = []
        
        for token in doc:
            if not token.is_stop and not token.is_punct and token.has_vector:
                word_embeddings.append(token.vector)
                # Find corresponding TF-IDF weight
                word_idx = tfidf_vectorizer.vocabulary_.get(token.text.lower(), -1)
                if word_idx != -1:
                    word_weights.append(tfidf_scores[word_idx])
                else:
                    word_weights.append(0.0)
        
        if word_embeddings and word_weights:
            # Weighted average of word embeddings
            word_embeddings = np.array(word_embeddings)
            word_weights = np.array(word_weights)
            word_weights = word_weights / (word_weights.sum() + 1e-8)  # Normalize weights
            
            weighted_embedding = np.average(word_embeddings, axis=0, weights=word_weights)
        else:
            weighted_embedding = np.zeros(300)
        
        weighted_embeddings.append(weighted_embedding)
    
    return np.array(weighted_embeddings)

def main():
    print("Loading and preprocessing data...")
    
    # Load data
    df = pd.read_csv('data/data-assignment3_II.csv')
    print(f"Dataset shape: {df.shape}")
    print(f"Class distribution: {df['Recommended IND'].value_counts().to_dict()}")
    
    # Preprocess text
    df['processed_text'] = df['Review Text'].apply(preprocess_text)
    df['processed_title'] = df['Title'].apply(preprocess_text)
    
    # Combine title and text
    df['combined_text'] = (df['processed_title'] + ' ' + df['processed_text']).str.strip()
    
    # Remove empty texts
    df = df[df['combined_text'].str.len() > 0]
    
    print(f"After preprocessing: {df.shape}")
    
    # Load spaCy model
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_md")
    
    # Prepare features
    X_text = df['combined_text'].values
    y = df['Recommended IND'].values
    
    print(f"Features shape: {len(X_text)}")
    print(f"Target distribution: {np.bincount(y)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train set: {len(X_train)}, Test set: {len(X_test)}")
    
    # Create vectorizers
    print("Creating vectorizers...")
    bow_vectorizer = CountVectorizer(max_features=5000, ngram_range=(1, 2))
    tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    
    # Fit vectorizers
    bow_vectorizer.fit(X_train)
    tfidf_vectorizer.fit(X_train)
    
    # Prepare features for each model
    print("Preparing features...")
    
    # 1. BoW features for Logistic Regression
    X_train_bow = bow_vectorizer.transform(X_train)
    X_test_bow = bow_vectorizer.transform(X_test)
    
    # 2. SpaCy embeddings for Random Forest
    X_train_embeddings = get_spacy_embeddings(X_train, nlp)
    X_test_embeddings = get_spacy_embeddings(X_test, nlp)
    
    # 3. TF-IDF weighted embeddings for SVM
    X_train_weighted = get_tfidf_weighted_embeddings(X_train, nlp, tfidf_vectorizer)
    X_test_weighted = get_tfidf_weighted_embeddings(X_test, nlp, tfidf_vectorizer)
    
    # Scale features
    scaler_embeddings = StandardScaler()
    scaler_weighted = StandardScaler()
    
    X_train_embeddings_scaled = scaler_embeddings.fit_transform(X_train_embeddings)
    X_test_embeddings_scaled = scaler_embeddings.transform(X_test_embeddings)
    
    X_train_weighted_scaled = scaler_weighted.fit_transform(X_train_weighted)
    X_test_weighted_scaled = scaler_weighted.transform(X_test_weighted)
    
    # Train models with class balancing
    print("Training models with class balancing...")
    
    # 1. Logistic Regression with class weights
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(
        class_weight='balanced',
        random_state=42,
        max_iter=1000
    )
    lr_model.fit(X_train_bow, y_train)
    
    # 2. Random Forest with class weights
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',
        random_state=42,
        max_depth=10
    )
    rf_model.fit(X_train_embeddings_scaled, y_train)
    
    # 3. SVM with class weights
    print("Training SVM...")
    svm_model = SVC(
        class_weight='balanced',
        random_state=42,
        probability=True,
        kernel='rbf',
        C=1.0
    )
    svm_model.fit(X_train_weighted_scaled, y_train)
    
    # Evaluate models
    print("\nEvaluating models...")
    
    # Logistic Regression
    lr_pred = lr_model.predict(X_test_bow)
    lr_prob = lr_model.predict_proba(X_test_bow)[:, 1]
    print("Logistic Regression:")
    print(classification_report(y_test, lr_pred))
    
    # Random Forest
    rf_pred = rf_model.predict(X_test_embeddings_scaled)
    rf_prob = rf_model.predict_proba(X_test_embeddings_scaled)[:, 1]
    print("Random Forest:")
    print(classification_report(y_test, rf_pred))
    
    # SVM
    svm_pred = svm_model.predict(X_test_weighted_scaled)
    svm_prob = svm_model.predict_proba(X_test_weighted_scaled)[:, 1]
    print("SVM:")
    print(classification_report(y_test, svm_pred))
    
    # Test ensemble on a few examples
    print("\nTesting ensemble on examples...")
    test_examples = [
        ("terrible this is bad product", 1),
        ("amazing great quality", 5),
        ("okay decent product", 3),
        ("awful waste of money", 1),
        ("love it perfect", 5)
    ]
    
    for text, rating in test_examples:
        # Preprocess
        processed = preprocess_text(text)
        
        # Get features
        bow_feat = bow_vectorizer.transform([processed])
        emb_feat = scaler_embeddings.transform([get_spacy_embeddings([processed], nlp)[0]])
        weighted_feat = scaler_weighted.transform([get_tfidf_weighted_embeddings([processed], nlp, tfidf_vectorizer)[0]])
        
        # Predict
        lr_pred_val = lr_model.predict(bow_feat)[0]
        lr_prob_val = lr_model.predict_proba(bow_feat)[0][1]
        
        rf_pred_val = rf_model.predict(emb_feat)[0]
        rf_prob_val = rf_model.predict_proba(emb_feat)[0][1]
        
        svm_pred_val = svm_model.predict(weighted_feat)[0]
        svm_prob_val = svm_model.predict_proba(weighted_feat)[0][1]
        
        # Ensemble (majority vote + average probability)
        predictions = [lr_pred_val, rf_pred_val, svm_pred_val]
        probabilities = [lr_prob_val, rf_prob_val, svm_prob_val]
        
        ensemble_pred = 1 if sum(predictions) >= 2 else 0
        ensemble_prob = np.mean(probabilities)
        
        print(f"Text: '{text}' (Rating: {rating})")
        print(f"  LR: {lr_pred_val} ({lr_prob_val:.3f})")
        print(f"  RF: {rf_pred_val} ({rf_prob_val:.3f})")
        print(f"  SVM: {svm_pred_val} ({svm_prob_val:.3f})")
        print(f"  Ensemble: {ensemble_pred} ({ensemble_prob:.3f})")
        print()
    
    # Save models
    print("Saving models...")
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(lr_model, 'models/lr_model.joblib')
    joblib.dump(rf_model, 'models/rf_model.joblib')
    joblib.dump(svm_model, 'models/svm_model.joblib')
    joblib.dump(bow_vectorizer, 'models/bow_vectorizer.joblib')
    joblib.dump(tfidf_vectorizer, 'models/tfidf_vectorizer.joblib')
    joblib.dump(scaler_embeddings, 'models/scaler_embeddings.joblib')
    joblib.dump(scaler_weighted, 'models/scaler_weighted.joblib')
    
    print("Models saved successfully!")

if __name__ == "__main__":
    main()
