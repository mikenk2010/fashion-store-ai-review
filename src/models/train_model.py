#!/usr/bin/env python3
"""
ML Model Training Script for Review Classification
Trains a Logistic Regression model using TF-IDF vectorization
Development/Testing version - To quickly test the ML models
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import re
import os

def preprocess_text(text):
    """Clean and preprocess text data"""
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# This script runs once during setup to train models on the full dataset
def train_review_classifier():
    # Loads CSV data
    # Preprocesses text
    # Trains 3 models (LR, RF, SVM)
    # Saves models to disk
    """Train the review classification model"""
    print("Loading dataset...")
    
    # Load the dataset
    df = pd.read_csv('data/data-assignment3_II.csv')
    
    print(f"Dataset loaded: {len(df)} reviews")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check for missing values
    print(f"Missing values in Review Text: {df['Review Text'].isna().sum()}")
    print(f"Missing values in Recommended IND: {df['Recommended IND'].isna().sum()}")
    
    # Remove rows with missing review text
    df = df.dropna(subset=['Review Text', 'Recommended IND'])
    
    print(f"After removing missing values: {len(df)} reviews")
    
    # Preprocess the text
    print("Preprocessing text...")
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
    
    # Create TF-IDF vectorizer
    print("Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )
    
    # Fit and transform training data
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"TF-IDF matrix shape: {X_train_tfidf.shape}")
    
    # Train Logistic Regression model
    print("Training Logistic Regression model...")
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight='balanced'
    )
    
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Not Recommended', 'Recommended']))
    
    # Save the model and vectorizer
    print("\nSaving model and vectorizer...")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save the model
    with open('models/review_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Save the vectorizer
    with open('models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("Model and vectorizer saved successfully!")
    
    # Test the saved model
    print("\nTesting saved model...")
    with open('models/review_model.pkl', 'rb') as f:
        loaded_model = pickle.load(f)
    
    with open('models/tfidf_vectorizer.pkl', 'rb') as f:
        loaded_vectorizer = pickle.load(f)
    
    # Test with a sample review
    sample_review = "This dress is amazing! I love the fit and quality."
    sample_processed = preprocess_text(sample_review)
    sample_tfidf = loaded_vectorizer.transform([sample_processed])
    sample_pred = loaded_model.predict(sample_tfidf)[0]
    sample_prob = loaded_model.predict_proba(sample_tfidf)[0]
    
    print(f"Sample review: '{sample_review}'")
    print(f"Prediction: {'Recommended' if sample_pred == 1 else 'Not Recommended'}")
    print(f"Confidence: {max(sample_prob):.4f}")
    
    return model, vectorizer

if __name__ == "__main__":
    train_review_classifier()
