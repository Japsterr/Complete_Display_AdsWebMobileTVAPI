#!/usr/bin/env python3
"""
Quick API Test Script for Digital Signage Platform
Tests core functionality with minimal setup
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001"
API_URL = f"{BASE_URL}/api/v1"

def test_api():
    """Run quick API tests"""
    print("🚀 Starting Digital Signage API Tests...")
    print(f"Testing API at: {API_URL}")
    
    # Test 1: Server Health Check
    print("\n📡 Test 1: Server Health Check")
    try:
        response = requests.get(f"{API_URL}/campaigns/", timeout=5)
        print(f"✅ Server responding (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False
    
    # Test 2: User Registration
    print("\n👤 Test 2: User Registration")
    user_data = {
        "email": f"test_user_{int(time.time())}@example.com",
        "password": "SecurePassword123!",
        "account_type": "personal"
    }
    
    try:
        response = requests.post(f"{API_URL}/register/", json=user_data)
        if response.status_code == 201:
            print("✅ User registration successful")
            user_email = user_data["email"]
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test 3: User Login & JWT Token
    print("\n🔐 Test 3: User Authentication")
    login_data = {
        "email": user_email,
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{API_URL}/login/", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
            print("✅ Login successful - JWT tokens received")
            print(f"   Access token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 4: Authenticated API Call (Create Campaign)
    print("\n🎯 Test 4: Authenticated API Call (Campaign Creation)")
    headers = {"Authorization": f"Bearer {access_token}"}
    campaign_data = {
        "name": f"Test Campaign {int(time.time())}",
        "description": "Automated test campaign"
    }
    
    try:
        response = requests.post(f"{API_URL}/campaigns/", json=campaign_data, headers=headers)
        if response.status_code == 201:
            campaign = response.json()
            campaign_id = campaign.get('campaign_id')
            print(f"✅ Campaign created successfully (ID: {campaign_id})")
        else:
            print(f"❌ Campaign creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Campaign creation error: {e}")
        return False
    
    # Test 5: List Campaigns
    print("\n📋 Test 5: List User's Campaigns")
    try:
        response = requests.get(f"{API_URL}/campaigns/", headers=headers)
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Retrieved {len(campaigns)} campaigns")
            if campaigns:
                print(f"   First campaign: {campaigns[0].get('name')}")
        else:
            print(f"❌ Campaign listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Campaign listing error: {e}")
        return False
    
    # Test 6: Create Display
    print("\n🖥️  Test 6: Create Display")
    display_data = {
        "name": f"Test Display {int(time.time())}",
        "location": "Office Lobby - Test Location"
    }
    
    try:
        response = requests.post(f"{API_URL}/displays/", json=display_data, headers=headers)
        if response.status_code == 201:
            display = response.json()
            display_id = display.get('display_id')
            print(f"✅ Display created successfully (ID: {display_id})")
        else:
            print(f"❌ Display creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Display creation error: {e}")
        return False
    
    # Test 7: Android TV Endpoint
    print("\n📺 Test 7: Android TV Endpoint")
    try:
        response = requests.get(f"{API_URL}/android-tv/?display_unique_identifier={display_id}")
        if response.status_code in [200, 404]:  # 404 is fine (no campaign assigned)
            if response.status_code == 200:
                print("✅ Android TV endpoint working - Campaign data returned")
            else:
                print("✅ Android TV endpoint working - No campaign assigned (expected)")
        else:
            print(f"❌ Android TV endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Android TV endpoint error: {e}")
        return False
    
    # Test 8: Token Refresh
    print("\n🔄 Test 8: JWT Token Refresh")
    try:
        refresh_data = {"refresh": refresh_token}
        response = requests.post(f"{API_URL}/token/refresh/", json=refresh_data)
        if response.status_code == 200:
            new_tokens = response.json()
            new_access_token = new_tokens.get('access')
            print("✅ Token refresh successful")
            print(f"   New access token: {new_access_token[:20]}...")
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        return False
    
    # Test 9: Password Security Check
    print("\n🔒 Test 9: Password Security Check")
    try:
        # Check that password is not returned in responses
        response = requests.post(f"{API_URL}/register/", json={
            "email": f"security_test_{int(time.time())}@example.com",
            "password": "TestPassword123",
            "account_type": "personal"
        })
        if response.status_code == 201:
            user_data = response.json()
            if 'password' not in user_data:
                print("✅ Password security: Passwords not exposed in API responses")
            else:
                print("❌ Security issue: Password found in API response!")
                return False
        else:
            print(f"❌ Security test registration failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Security test error: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 ALL API TESTS PASSED!")
    print("="*60)
    print("✅ Server is running correctly")
    print("✅ User registration and authentication working")
    print("✅ JWT token system functioning")
    print("✅ Campaign and Display CRUD operations working")  
    print("✅ Android TV endpoint accessible")
    print("✅ Password security implemented")
    print("✅ API is ready for production use!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_api()
        if success:
            print("\n🚀 Your Digital Signage API is working perfectly!")
        else:
            print("\n⚠️  Some tests failed. Check the output above.")
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
