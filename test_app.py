#!/usr/bin/env python3
"""
Test script for NSE Indices Fetcher App
Run this script to test the application functionality
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoint(url, endpoint_name):
    """Test a specific API endpoint"""
    print(f"\n🔍 Testing {endpoint_name}...")
    print(f"URL: {url}")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {endpoint_name} - SUCCESS")
            
            # Print some basic info about the response
            if 'success' in data:
                print(f"   Success: {data['success']}")
            if 'data' in data:
                if isinstance(data['data'], list):
                    print(f"   Data items: {len(data['data'])}")
                else:
                    print(f"   Data type: {type(data['data'])}")
            if 'timestamp' in data:
                print(f"   Timestamp: {data['timestamp']}")
                
            return True
        else:
            print(f"❌ {endpoint_name} - FAILED")
            print(f"   Error: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint_name} - ERROR")
        print(f"   Exception: {str(e)}")
        return False

def test_application():
    """Test the NSE Indices Fetcher application"""
    print("🚀 NSE Indices Fetcher - Application Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "http://localhost:5000"
    
    # Test endpoints
    endpoints = [
        ("/api/status", "API Status"),
        ("/api/indices", "All Indices"),
        ("/api/index/NIFTY%2050", "NIFTY 50 Index"),
        ("/api/index/NIFTY%20BANK", "NIFTY Bank Index"),
        ("/api/trending", "Trending Stocks"),
        ("/api/most-active", "Most Active Stocks"),
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = base_url + endpoint
        success = test_api_endpoint(url, name)
        results.append((name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the application setup.")
        
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_web_interface():
    """Test if the web interface is accessible"""
    print("\n🌐 Testing Web Interface...")
    
    try:
        response = requests.get("http://localhost:5000", timeout=10)
        if response.status_code == 200:
            print("✅ Web interface is accessible")
            print("   You can open http://localhost:5000 in your browser")
            return True
        else:
            print(f"❌ Web interface returned HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Web interface is not accessible: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 NSE Indices Fetcher - Test Suite")
    print("Make sure the application is running on http://localhost:5000")
    print("\nTo start the application, run: python app.py")
    
    input("\nPress Enter to start testing...")
    
    # Test web interface first
    web_success = test_web_interface()
    
    if web_success:
        # Test API endpoints
        test_application()
    else:
        print("\n❌ Cannot test API endpoints because web interface is not accessible.")
        print("Please make sure the application is running:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the app: python app.py")
        print("3. Wait for the server to start")
        print("4. Run this test again")
    
    print("\n" + "=" * 50)
    print("Test completed. Check the results above.")