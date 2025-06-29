#!/usr/bin/env python3
"""
Simple test script for the Music Recommendation Tool
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import spotipy
        print("✅ Spotipy imported successfully")
    except ImportError as e:
        print(f"❌ Spotipy import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✅ Scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the Flask app can be created."""
    print("\n🧪 Testing app creation...")
    
    try:
        # Set test environment variables
        os.environ['SPOTIFY_CLIENT_ID'] = 'test_id'
        os.environ['SPOTIFY_CLIENT_SECRET'] = 'test_secret'
        os.environ['SECRET_KEY'] = 'test_key'
        
        from app import app
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_modules():
    """Test if our custom modules can be imported."""
    print("\n🧪 Testing custom modules...")
    
    try:
        from spotify_client import SpotifyClient
        print("✅ SpotifyClient imported successfully")
    except Exception as e:
        print(f"❌ SpotifyClient import failed: {e}")
        return False
    
    try:
        from recommendation_engine import RecommendationEngine
        print("✅ RecommendationEngine imported successfully")
    except Exception as e:
        print(f"❌ RecommendationEngine import failed: {e}")
        return False
    
    try:
        from utils import format_duration, get_feature_description
        print("✅ Utils imported successfully")
    except Exception as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment setup."""
    print("\n🧪 Testing environment...")
    
    load_dotenv()
    
    required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Create a .env file with your Spotify credentials")
        return False
    else:
        print("✅ Environment variables found")
        return True

def main():
    """Run all tests."""
    print("🎵 Music Recommendation Tool - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_modules,
        test_app_creation,
        test_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To run the application:")
        print("   python app.py")
        print("   Then open http://localhost:8080 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 