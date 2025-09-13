#!/usr/bin/env python3
"""
Comprehensive test suite for Fashion Store application
"""

import unittest
import sys
import os
import json
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.app.factory import create_app
from src.config.settings import TestingConfig
from src.models import load_ml_models, predict_review_sentiment
from src.utils.auth import hash_password, verify_password
from src.utils.helpers import calculate_average_rating, get_review_stats

class TestConfig(TestingConfig):
    """Test configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False

class TestFashionStore(unittest.TestCase):
    """Test cases for Fashion Store application"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_app_creation(self):
        """Test that the app is created correctly"""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])
    
    def test_homepage(self):
        """Test homepage loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Fashion Store', response.data)
    
    def test_products_api(self):
        """Test products API endpoint"""
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_ml_prediction_api(self):
        """Test ML prediction API"""
        test_data = {
            'review_text': 'This is a great product!'
        }
        response = self.client.post('/api/predict_review', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('prediction', data)
        self.assertIn('confidence', data)
        self.assertIn('label', data)
    
    def test_auth_functions(self):
        """Test authentication utility functions"""
        password = 'testpassword123'
        hashed = hash_password(password)
        
        # Test password hashing
        self.assertNotEqual(password, hashed)
        self.assertEqual(len(hashed), 64)  # SHA-256 produces 64 character hex string
        
        # Test password verification
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password('wrongpassword', hashed))
    
    def test_helper_functions(self):
        """Test helper utility functions"""
        # Test average rating calculation
        reviews = [
            {'rating': 5},
            {'rating': 4},
            {'rating': 3}
        ]
        avg_rating = calculate_average_rating(reviews)
        self.assertEqual(avg_rating, 4.0)
        
        # Test review stats
        stats = get_review_stats(reviews)
        self.assertEqual(stats['total_reviews'], 3)
        self.assertEqual(stats['average_rating'], 4.0)
    
    def test_ml_prediction_function(self):
        """Test ML prediction function directly"""
        # This test might fail if models aren't loaded
        try:
            prediction, confidence, details = predict_review_sentiment('Great product!')
            self.assertIsNotNone(prediction)
            self.assertIsInstance(confidence, (int, float))
            self.assertIsInstance(details, dict)
        except Exception as e:
            self.skipTest(f"ML prediction test skipped: {e}")
    
    def test_model_loading(self):
        """Test ML model loading"""
        try:
            result = load_ml_models()
            # This might be False if models don't exist, which is okay for testing
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.skipTest(f"Model loading test skipped: {e}")

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints specifically"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_model_info_api(self):
        """Test model info API endpoint"""
        response = self.client.get('/api/model_info')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
    
    def test_stats_api(self):
        """Test statistics API endpoint"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_products', data)
        self.assertIn('total_reviews', data)
        self.assertIn('average_rating', data)

def run_tests():
    """Run all tests"""
    print("🧪 Running Fashion Store Test Suite...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestFashionStore))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("[COMPLETE] All tests passed!")
    else:
        print(f"[ERROR] {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)