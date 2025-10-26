#!/usr/bin/env python3
"""
Test script for the Flask backend API.
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API URL from environment or default
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

def test_health():
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_generate_image():
    """Test image generation."""
    print("\n🎨 Testing image generation...")
    try:
        payload = {"prompt": "Create a funny meme about American coffee culture"}
        response = requests.post(
            f"{API_BASE_URL}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print(f"✅ Image generation successful!")
                print(f"   Content type: {data['content_type']}")
                print(f"   Data length: {len(data['data'])} characters")
                if "stages" in data:
                    print(f"   Stages: {len(data['stages'])} stages completed")
                return True
            else:
                print(f"❌ Image generation failed: {data['message']}")
                return False
        else:
            print(f"❌ Image generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        return False

def test_generate_video():
    """Test video generation."""
    print("\n🎬 Testing video generation...")
    try:
        payload = {"prompt": "Create an animated video about dogs being silly"}
        response = requests.post(
            f"{API_BASE_URL}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print(f"✅ Video generation successful!")
                print(f"   Content type: {data['content_type']}")
                print(f"   Data length: {len(data['data'])} characters")
                if "stages" in data:
                    print(f"   Stages: {len(data['stages'])} stages completed")
                return True
            else:
                print(f"❌ Video generation failed: {data['message']}")
                return False
        else:
            print(f"❌ Video generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Video generation error: {e}")
        return False

def test_error_handling():
    """Test error handling."""
    print("\n🚨 Testing error handling...")
    try:
        # Test empty prompt
        payload = {"prompt": ""}
        response = requests.post(
            f"{API_BASE_URL}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Empty prompt error handled correctly: {data['message']}")
        else:
            print(f"❌ Empty prompt should return 400, got {response.status_code}")
            return False
        
        # Test invalid JSON
        response = requests.post(
            f"{API_BASE_URL}/api/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Invalid JSON error handled correctly")
        else:
            print(f"❌ Invalid JSON should return 400, got {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting Flask Backend API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Image Generation", test_generate_image),
        ("Video Generation", test_generate_video),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the backend logs for details.")

if __name__ == "__main__":
    main()
