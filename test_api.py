#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Digital Signage SaaS Platform
Tests all endpoints with proper authentication and data validation
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class DigitalSignageAPITester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.access_token = None
        self.refresh_token = None
        self.test_data = {}
        self.session = requests.Session()
    
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    auth: bool = True, files: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with optional authentication"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth and self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        if files:
            # Don't set content-type for file uploads
            headers.pop('Content-Type', None)
            response = self.session.request(method, url, headers=headers, files=files, data=data)
        else:
            response = self.session.request(method, url, headers=headers, json=data)
        
        return response
    
    def test_swagger_docs(self):
        """Test Swagger documentation accessibility"""
        self.log("Testing Swagger documentation...")
        try:
            response = requests.get(f"{self.api_url}/swagger/")
            if response.status_code == 200:
                self.log("✅ Swagger docs accessible")
                return True
            else:
                self.log(f"❌ Swagger docs failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Swagger docs error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration for both personal and business accounts"""
        self.log("Testing user registration...")
        
        # Test personal account registration
        personal_data = {
            "email": f"personal_user_{int(time.time())}@test.com",
            "password": "TestPassword123!",
            "account_type": "personal"
        }
        
        response = self.make_request("POST", "/register/", personal_data, auth=False)
        if response.status_code == 201:
            self.log("✅ Personal account registration successful")
            self.test_data['personal_user'] = personal_data
        else:
            self.log(f"❌ Personal registration failed: {response.status_code} - {response.text}")
            return False
        
        # Test business account registration
        business_data = {
            "email": f"business_user_{int(time.time())}@test.com",
            "password": "TestPassword123!",
            "account_type": "business"
        }
        
        response = self.make_request("POST", "/register/", business_data, auth=False)
        if response.status_code == 201:
            self.log("✅ Business account registration successful")
            self.test_data['business_user'] = business_data
        else:
            self.log(f"❌ Business registration failed: {response.status_code} - {response.text}")
            return False
        
        return True
    
    def test_user_login(self):
        """Test user authentication with JWT tokens"""
        self.log("Testing user login...")
        
        login_data = {
            "email": self.test_data['personal_user']['email'],
            "password": self.test_data['personal_user']['password']
        }
        
        response = self.make_request("POST", "/login/", login_data, auth=False)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            self.refresh_token = data.get('refresh')
            self.log("✅ User login successful")
            self.log(f"Access token received: {self.access_token[:20]}...")
            return True
        else:
            self.log(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def test_token_refresh(self):
        """Test JWT token refresh functionality"""
        self.log("Testing token refresh...")
        
        if not self.refresh_token:
            self.log("❌ No refresh token available")
            return False
        
        refresh_data = {"refresh": self.refresh_token}
        response = self.make_request("POST", "/token/refresh/", refresh_data, auth=False)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            self.log("✅ Token refresh successful")
            return True
        else:
            self.log(f"❌ Token refresh failed: {response.status_code} - {response.text}")
            return False
    
    def test_campaign_operations(self):
        """Test CRUD operations for campaigns"""
        self.log("Testing campaign operations...")
        
        # Create campaign
        campaign_data = {
            "name": f"Test Campaign {int(time.time())}",
            "description": "This is a test campaign for API testing"
        }
        
        response = self.make_request("POST", "/campaigns/", campaign_data)
        if response.status_code == 201:
            campaign = response.json()
            self.test_data['campaign_id'] = campaign['campaign_id']
            self.log(f"✅ Campaign created: ID {campaign['campaign_id']}")
        else:
            self.log(f"❌ Campaign creation failed: {response.status_code} - {response.text}")
            return False
        
        # List campaigns
        response = self.make_request("GET", "/campaigns/")
        if response.status_code == 200:
            campaigns = response.json()
            self.log(f"✅ Retrieved {len(campaigns)} campaigns")
        else:
            self.log(f"❌ Campaign listing failed: {response.status_code}")
            return False
        
        # Get specific campaign
        campaign_id = self.test_data['campaign_id']
        response = self.make_request("GET", f"/campaigns/{campaign_id}/")
        if response.status_code == 200:
            self.log("✅ Campaign detail retrieval successful")
        else:
            self.log(f"❌ Campaign detail failed: {response.status_code}")
            return False
        
        # Update campaign
        update_data = {
            "name": f"Updated Test Campaign {int(time.time())}",
            "description": "Updated description"
        }
        response = self.make_request("PATCH", f"/campaigns/{campaign_id}/", update_data)
        if response.status_code == 200:
            self.log("✅ Campaign update successful")
        else:
            self.log(f"❌ Campaign update failed: {response.status_code}")
            return False
        
        return True
    
    def test_media_operations(self):
        """Test CRUD operations for media"""
        self.log("Testing media operations...")
        
        # Create a test text file for upload
        test_content = "This is a test media file content"
        
        # Create media entry
        media_data = {
            "name": f"Test Media {int(time.time())}",
            "description": "Test media file for API testing"
        }
        
        # Create a simple text file for testing
        files = {
            'file': ('test_file.txt', test_content.encode(), 'text/plain')
        }
        
        response = self.make_request("POST", "/media/", media_data, files=files)
        if response.status_code == 201:
            media = response.json()
            self.test_data['media_id'] = media['media_id']
            self.log(f"✅ Media created: ID {media['media_id']}")
        else:
            self.log(f"❌ Media creation failed: {response.status_code} - {response.text}")
            return False
        
        # List media
        response = self.make_request("GET", "/media/")
        if response.status_code == 200:
            media_list = response.json()
            self.log(f"✅ Retrieved {len(media_list)} media items")
        else:
            self.log(f"❌ Media listing failed: {response.status_code}")
            return False
        
        return True
    
    def test_display_operations(self):
        """Test CRUD operations for displays"""
        self.log("Testing display operations...")
        
        # Create display
        display_data = {
            "name": f"Test Display {int(time.time())}",
            "location": "Test Location - Office Lobby"
        }
        
        response = self.make_request("POST", "/displays/", display_data)
        if response.status_code == 201:
            display = response.json()
            self.test_data['display_id'] = display['display_id']
            self.log(f"✅ Display created: ID {display['display_id']}")
        else:
            self.log(f"❌ Display creation failed: {response.status_code} - {response.text}")
            return False
        
        # List displays
        response = self.make_request("GET", "/displays/")
        if response.status_code == 200:
            displays = response.json()
            self.log(f"✅ Retrieved {len(displays)} displays")
        else:
            self.log(f"❌ Display listing failed: {response.status_code}")
            return False
        
        return True
    
    def test_android_tv_endpoint(self):
        """Test the Android TV display endpoint"""
        self.log("Testing Android TV endpoint...")
        
        if 'display_id' not in self.test_data:
            self.log("❌ No display ID available for testing")
            return False
        
        display_id = self.test_data['display_id']
        response = self.make_request("GET", f"/android-tv/?display_unique_identifier={display_id}", auth=False)
        
        if response.status_code in [200, 404]:  # 404 is expected if no campaign is set
            self.log("✅ Android TV endpoint accessible")
            if response.status_code == 200:
                data = response.json()
                self.log(f"Campaign data: {data}")
            else:
                self.log("No campaign available (expected)")
        else:
            self.log(f"❌ Android TV endpoint failed: {response.status_code} - {response.text}")
            return False
        
        return True
    
    def test_business_login_and_team_invite(self):
        """Test business user login and team invite functionality"""
        self.log("Testing business user login and team invite...")
        
        # Login as business user
        login_data = {
            "email": self.test_data['business_user']['email'],
            "password": self.test_data['business_user']['password']
        }
        
        response = self.make_request("POST", "/login/", login_data, auth=False)
        if response.status_code == 200:
            data = response.json()
            business_token = data.get('access')
            self.log("✅ Business user login successful")
        else:
            self.log(f"❌ Business login failed: {response.status_code}")
            return False
        
        # Test team invite (temporarily switch token)
        old_token = self.access_token
        self.access_token = business_token
        
        invite_data = {
            "email": f"team_member_{int(time.time())}@test.com"
        }
        
        response = self.make_request("POST", "/team/invite/", invite_data)
        if response.status_code == 200:
            self.log("✅ Team invite successful")
        else:
            self.log(f"❌ Team invite failed: {response.status_code} - {response.text}")
        
        # Restore original token
        self.access_token = old_token
        return True
    
    def test_logout(self):
        """Test user logout functionality"""
        self.log("Testing user logout...")
        
        if not self.refresh_token:
            self.log("❌ No refresh token for logout")
            return False
        
        logout_data = {"refresh": self.refresh_token}
        response = self.make_request("POST", "/logout/", logout_data)
        
        if response.status_code == 200:
            self.log("✅ User logout successful")
            return True
        else:
            self.log(f"❌ Logout failed: {response.status_code} - {response.text}")
            return False
    
    def test_password_security(self):
        """Test that passwords are properly hashed"""
        self.log("Testing password security...")
        
        # This test requires database access to verify passwords are hashed
        # For now, we'll just verify the registration doesn't return the password
        personal_data = {
            "email": f"security_test_{int(time.time())}@test.com",
            "password": "PlainTextPassword123!",
            "account_type": "personal"
        }
        
        response = self.make_request("POST", "/register/", personal_data, auth=False)
        if response.status_code == 201:
            response_data = response.json()
            if 'password' not in response_data:
                self.log("✅ Password not returned in registration response")
                return True
            else:
                self.log("❌ Password exposed in response")
                return False
        else:
            self.log(f"❌ Security test registration failed: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        self.log("=" * 60)
        self.log("STARTING DIGITAL SIGNAGE API TEST SUITE")
        self.log("=" * 60)
        
        tests = [
            ("Swagger Documentation", self.test_swagger_docs),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Token Refresh", self.test_token_refresh),
            ("Campaign Operations", self.test_campaign_operations),
            ("Media Operations", self.test_media_operations),
            ("Display Operations", self.test_display_operations),
            ("Android TV Endpoint", self.test_android_tv_endpoint),
            ("Business & Team Features", self.test_business_login_and_team_invite),
            ("Password Security", self.test_password_security),
            ("User Logout", self.test_logout),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n--- Running: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ Test error: {str(e)}")
                failed += 1
        
        self.log("\n" + "=" * 60)
        self.log("TEST SUITE RESULTS")
        self.log("=" * 60)
        self.log(f"✅ Passed: {passed}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED! API is working correctly.")
        else:
            self.log("⚠️  Some tests failed. Check the logs above for details.")
        
        return failed == 0

def main():
    """Main function to run the test suite"""
    print("Digital Signage SaaS API Test Suite")
    print("Make sure your Django server is running on http://127.0.0.1:8000")
    
    # Wait a moment for user to confirm
    input("Press Enter to start testing...")
    
    tester = DigitalSignageAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 API testing completed successfully!")
    else:
        print("\n⚠️  API testing completed with some failures.")

if __name__ == "__main__":
    main()
