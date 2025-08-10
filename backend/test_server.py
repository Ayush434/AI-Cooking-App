#!/usr/bin/env python3
"""
Test script to verify Flask server and routes
"""

import requests
import json
import time
import subprocess
import sys
import os

# Configuration - update this for Cloudflare
CLOUDFLARE_BASE_URL = 'https://hill-substantial-solaris-tie.trycloudflare.com'

def test_server():
    """Test if the Flask server is running and accessible"""
    
    print("🔍 Testing Flask server...")
    
    # Test if server is running on Cloudflare
    try:
        response = requests.get(f'{CLOUDFLARE_BASE_URL}/api/recipes/get-recipes', timeout=5)
        print(f"✅ Server is accessible via Cloudflare! Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not accessible via Cloudflare")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    
    print("\n🧪 Testing API endpoints...")
    
    # Test get-recipes endpoint
    try:
        test_data = {
            'ingredients': ['tomato', 'onion', 'garlic', 'olive oil']
        }
        
        response = requests.post(
            f'{CLOUDFLARE_BASE_URL}/api/recipes/get-recipes',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"✅ GET-RECIPES endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ GET-RECIPES endpoint failed: {str(e)}")
    
    # Test detect-ingredients endpoint (with dummy data)
    try:
        # Create a dummy image file for testing
        with open('test_image.txt', 'w') as f:
            f.write('dummy image content')
        
        with open('test_image.txt', 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(
                f'{CLOUDFLARE_BASE_URL}/api/recipes/detect-ingredients',
                files=files,
                timeout=10
            )
        
        print(f"✅ DETECT-INGREDIENTS endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
        # Clean up
        os.remove('test_image.txt')
            
    except Exception as e:
        print(f"❌ DETECT-INGREDIENTS endpoint failed: {str(e)}")

def start_server():
    """Start the Flask server"""
    
    print("🚀 Starting Flask server...")
    
    try:
        # Start the server in a subprocess
        process = subprocess.Popen(
            [sys.executable, 'run.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")
        return None

def main():
    """Main test function"""
    
    print("🔧 Flask Server Test Suite\n")
    
    # Check if server is already running
    if test_server():
        print("✅ Server is already running!")
        test_api_endpoints()
    else:
        print("⚠️  Server not running. Starting it now...")
        
        # Start the server
        process = start_server()
        
        if process:
            # Wait a bit more for server to fully start
            time.sleep(2)
            
            # Test the server
            if test_server():
                test_api_endpoints()
            else:
                print("❌ Server failed to start properly")
            
            # Stop the server
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
        else:
            print("❌ Could not start server")

if __name__ == "__main__":
    main()