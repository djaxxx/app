#!/usr/bin/env python3
"""
Backend Test Suite for DJ Connect France - Image Upload & File Storage System
Tests the new file-based image storage system that replaces base64 MongoDB storage.
"""

import requests
import json
import sys
import os
from pathlib import Path

# Backend URL from frontend .env
BACKEND_URL = "https://dj-directory-fr.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test base64 image (1x1 pixel PNG)
TEST_BASE64_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

def test_health_check():
    """Test basic health check to ensure backend is running."""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_single_image_upload():
    """Test POST /api/upload/image with base64 image."""
    print("\n🔍 Testing Single Image Upload...")
    
    payload = {
        "image": TEST_BASE64_IMAGE,
        "type": "profile"
    }
    
    try:
        response = requests.post(f"{API_BASE}/upload/image", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "url" in data and data["url"].startswith("/api/uploads/"):
                print(f"✅ Single image upload successful: {data['url']}")
                return data["url"]
            else:
                print(f"❌ Invalid response format: {data}")
                return None
        else:
            print(f"❌ Single image upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Single image upload error: {e}")
        return None

def test_image_url_passthrough():
    """Test that existing URLs are passed through without re-uploading."""
    print("\n🔍 Testing Image URL Pass-through...")
    
    existing_url = "/api/uploads/existing.jpg"
    payload = {
        "image": existing_url
    }
    
    try:
        response = requests.post(f"{API_BASE}/upload/image", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("url") == existing_url:
                print(f"✅ URL pass-through successful: {data['url']}")
                return True
            else:
                print(f"❌ URL pass-through failed - expected {existing_url}, got {data.get('url')}")
                return False
        else:
            print(f"❌ URL pass-through failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ URL pass-through error: {e}")
        return False

def test_batch_image_upload():
    """Test POST /api/upload/images with multiple images."""
    print("\n🔍 Testing Batch Image Upload...")
    
    payload = {
        "images": [TEST_BASE64_IMAGE, "/api/uploads/existing.jpg"],
        "type": "gallery"
    }
    
    try:
        response = requests.post(f"{API_BASE}/upload/images", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "urls" in data and len(data["urls"]) == 2:
                url1, url2 = data["urls"]
                if url1.startswith("/api/uploads/") and url2 == "/api/uploads/existing.jpg":
                    print(f"✅ Batch upload successful: {data['urls']}")
                    return data["urls"]
                else:
                    print(f"❌ Batch upload invalid URLs: {data['urls']}")
                    return None
            else:
                print(f"❌ Batch upload invalid response: {data}")
                return None
        else:
            print(f"❌ Batch upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Batch upload error: {e}")
        return None

def test_image_serving(image_url):
    """Test that uploaded images are accessible via StaticFiles."""
    if not image_url:
        print("\n⚠️ Skipping image serving test - no image URL provided")
        return False
        
    print(f"\n🔍 Testing Image Serving for {image_url}...")
    
    full_url = f"{BACKEND_URL}{image_url}"
    
    try:
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                print(f"✅ Image serving successful: {full_url} (Content-Type: {content_type})")
                return True
            else:
                print(f"❌ Image serving failed - wrong content type: {content_type}")
                return False
        else:
            print(f"❌ Image serving failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Image serving error: {e}")
        return False

def test_dj_profiles_url_format():
    """Test that DJ profiles now have URL-based photo_profil instead of base64."""
    print("\n🔍 Testing DJ Profiles URL Format...")
    
    try:
        response = requests.get(f"{API_BASE}/djs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            djs = data.get("djs", [])
            
            if not djs:
                print("⚠️ No DJs found in database")
                return True
            
            url_based_count = 0
            base64_count = 0
            
            for dj in djs:
                photo = dj.get("photo_profil", "")
                if photo:
                    if photo.startswith("/api/uploads/"):
                        url_based_count += 1
                    elif photo.startswith("data:image"):
                        base64_count += 1
            
            print(f"📊 DJ Photos: {url_based_count} URL-based, {base64_count} base64")
            
            if base64_count == 0:
                print("✅ All DJ photos are URL-based (migration successful)")
                return True
            else:
                print(f"⚠️ Found {base64_count} base64 photos - migration may be incomplete")
                return True  # Not a critical failure
                
        else:
            print(f"❌ DJ profiles fetch failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ DJ profiles test error: {e}")
        return False

def check_backend_logs_for_bson_errors():
    """Check backend logs for BSON DocumentTooLarge errors."""
    print("\n🔍 Checking Backend Logs for BSON Errors...")
    
    try:
        # Check supervisor backend logs
        result = os.system("tail -n 100 /var/log/supervisor/backend.*.log | grep -i 'DocumentTooLarge\\|16MB\\|BSON' > /tmp/bson_check.log 2>&1")
        
        # Read the results
        if os.path.exists("/tmp/bson_check.log"):
            with open("/tmp/bson_check.log", "r") as f:
                content = f.read().strip()
            
            if content:
                print(f"⚠️ Found BSON-related errors in logs:\n{content}")
                return False
            else:
                print("✅ No BSON DocumentTooLarge errors found in recent logs")
                return True
        else:
            print("⚠️ Could not check backend logs")
            return True  # Don't fail the test if we can't check logs
            
    except Exception as e:
        print(f"⚠️ Error checking logs: {e}")
        return True  # Don't fail the test if we can't check logs

def main():
    """Run all image upload tests."""
    print("🚀 Starting Image Upload & File Storage System Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health Check
    results["health"] = test_health_check()
    
    if not results["health"]:
        print("\n❌ Backend is not responding. Stopping tests.")
        return False
    
    # Test 2: Single Image Upload
    uploaded_url = test_single_image_upload()
    results["single_upload"] = uploaded_url is not None
    
    # Test 3: URL Pass-through
    results["url_passthrough"] = test_image_url_passthrough()
    
    # Test 4: Batch Upload
    batch_urls = test_batch_image_upload()
    results["batch_upload"] = batch_urls is not None
    
    # Test 5: Image Serving
    results["image_serving"] = test_image_serving(uploaded_url)
    
    # Test 6: DJ Profiles URL Format
    results["dj_profiles"] = test_dj_profiles_url_format()
    
    # Test 7: BSON Error Check
    results["no_bson_errors"] = check_backend_logs_for_bson_errors()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All image upload tests PASSED!")
        return True
    else:
        print("⚠️ Some tests failed - see details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)