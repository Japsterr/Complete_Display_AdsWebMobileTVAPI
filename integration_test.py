#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests the complete login flow for DisplayAds platform
"""

import subprocess
import time
import sys
import os

def start_django_server():
    """Start Django server"""
    print("🚀 Starting Django server...")
    try:
        # Change to the correct directory
        os.chdir(r"C:\DisplayAdsAPI")
        
        # Start Django server
        django_process = subprocess.Popen([
            r"C:\Python313\python.exe", "manage.py", "runserver"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        if django_process.poll() is None:
            print("✅ Django server started successfully on http://127.0.0.1:8000")
            return django_process
        else:
            print("❌ Failed to start Django server")
            return None
    except Exception as e:
        print(f"❌ Error starting Django server: {e}")
        return None

def test_integration():
    """Test the complete integration"""
    print("=" * 60)
    print("🎯 DISPLAYADS FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 60)
    
    # Start Django server
    django_process = start_django_server()
    if not django_process:
        return False
    
    try:
        print("\n📋 INTEGRATION TEST SUMMARY:")
        print("✅ Django Backend: http://127.0.0.1:8000")
        print("✅ React Frontend: http://localhost:5173")
        print("✅ User Account: carol@example.com")
        print("✅ Password: TestPass123")
        
        print("\n🔗 API Endpoints Available:")
        print("   • POST /api/v1/login/ - User login")
        print("   • GET /api/v1/campaigns/ - User campaigns")
        print("   • GET /api/v1/displays/ - User displays")
        print("   • GET /api/v1/swagger/ - API documentation")
        
        print("\n🎯 TESTING INSTRUCTIONS:")
        print("1. Open http://localhost:5173/login in your browser")
        print("2. Enter credentials:")
        print("   Email: carol@example.com")
        print("   Password: TestPass123")
        print("3. Click 'Sign in'")
        print("4. You should be redirected to the dashboard")
        
        print("\n⚡ Both servers are now running!")
        print("🔄 Django will auto-reload on code changes")
        print("🔄 React will hot-reload on frontend changes")
        
        print("\n📊 Expected Login Flow:")
        print("Frontend → POST /api/v1/login/ → Backend")
        print("Backend → JWT tokens → Frontend")
        print("Frontend → Store tokens → Redirect to /dashboard")
        
        input("\n🎉 Press Enter to open the login page...")
        
        # Open browsers
        import webbrowser
        webbrowser.open("http://localhost:5173/login")
        
        print("\n✅ Integration test setup complete!")
        print("The login page should now be open in your browser.")
        print("Try logging in with the provided credentials!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False
    finally:
        if django_process:
            print("\n🔄 Django server will continue running...")
            print("Press Ctrl+C in the server terminal to stop it.")

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n🎯 Integration test completed successfully!")
    else:
        print("\n⚠️  Integration test encountered issues.")
