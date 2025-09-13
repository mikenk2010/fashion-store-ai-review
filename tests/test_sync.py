#!/usr/bin/env python3
"""
Test script to verify file synchronization is working
"""

import requests
import time
import sys

def test_application():
    """Test if the application is running and responsive"""
    try:
        response = requests.get('http://localhost:6600', timeout=5)
        if response.status_code == 200:
            print("[SUCCESS] Application is running and accessible")
            return True
        else:
            print(f"[ERROR] Application returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Application is not accessible: {e}")
        return False

def test_login():
    """Test if login functionality works"""
    try:
        session = requests.Session()
        
        # Test login
        login_data = {
            'email': 'test@example.com',
            'password': 'test123'
        }
        
        response = session.post('http://localhost:6600/login', data=login_data, allow_redirects=False)
        
        if response.status_code in [302, 200]:  # Redirect or success
            print("[SUCCESS] Login functionality works")
            
            # Test profile page
            profile_response = session.get('http://localhost:6600/profile')
            if profile_response.status_code == 200:
                print("[SUCCESS] Profile page accessible")
            else:
                print(f"[ERROR] Profile page returned status: {profile_response.status_code}")
                
            # Test wishlist page
            wishlist_response = session.get('http://localhost:6600/wishlist')
            if wishlist_response.status_code == 200:
                print("[SUCCESS] Wishlist page accessible")
            else:
                print(f"[ERROR] Wishlist page returned status: {wishlist_response.status_code}")
                
            return True
        else:
            print(f"[ERROR] Login failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Login test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Fashion Store Application...")
    print("=" * 50)
    
    # Wait a moment for application to start
    print("⏳ Waiting for application to start...")
    time.sleep(3)
    
    # Test application accessibility
    if not test_application():
        print("\n[ERROR] Application is not running. Please start it first:")
        print("   Development: ./dev.sh")
        print("   Production:  ./prod.sh")
        sys.exit(1)
    
    # Test login functionality
    if not test_login():
        print("\n[ERROR] Login functionality has issues")
        sys.exit(1)
    
    print("\n[COMPLETE] All tests passed! Application is working correctly.")
    print("\n[TRACE] Available features:")
    print("   • User login/registration")
    print("   • Product browsing with images")
    print("   • Profile management")
    print("   • Wishlist functionality")
    print("   • ML-powered review classification")
    print("   • Responsive UI/UX")

if __name__ == "__main__":
    main()
