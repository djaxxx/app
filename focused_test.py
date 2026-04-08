#!/usr/bin/env python3
"""
DJ Connect France - Focused Backend API Tests
Test the remaining endpoints after DJ activation
"""

import requests
import json
import time

BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_dj_profile_public():
    """Test GET /api/djs/{user_id} (public DJ profile)"""
    try:
        # Get a DJ first
        djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
        print(f"DJ search response: {djs_response.status_code}")
        
        if djs_response.status_code != 200:
            print(f"❌ Could not get DJs for profile test: {djs_response.text}")
            return False
        
        djs_data = djs_response.json()
        print(f"DJs found: {djs_data.get('total', 0)}")
        
        if not djs_data.get("djs"):
            print("❌ No DJs available for profile test")
            return False
        
        dj_user_id = djs_data["djs"][0]["user_id"]
        print(f"Testing profile for DJ: {dj_user_id}")
        
        # Get DJ profile
        response = requests.get(f"{BASE_URL}/djs/{dj_user_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("user_id") and data.get("nom_de_scene"):
                print(f"✅ DJ Profile Public: Retrieved profile for {data.get('nom_de_scene')}")
                return True
            else:
                print(f"❌ DJ Profile Public: Invalid profile data: {data}")
                return False
        else:
            print(f"❌ DJ Profile Public: HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ DJ Profile Public: Request failed: {str(e)}")
        return False

def test_contact_request():
    """Test POST /api/contact (create contact request)"""
    try:
        # First, get a DJ to contact
        djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
        if djs_response.status_code != 200:
            print(f"❌ Contact Request: Could not get DJs: {djs_response.text}")
            return False
        
        djs_data = djs_response.json()
        if not djs_data.get("djs"):
            print("❌ Contact Request: No DJs available")
            return False
        
        dj_user_id = djs_data["djs"][0]["user_id"]
        print(f"Creating contact request for DJ: {dj_user_id}")
        
        # Create contact request
        timestamp = int(time.time())
        contact_data = {
            "dj_user_id": dj_user_id,
            "client_nom": "Jean Dupont",
            "client_email": f"jean.dupont.{timestamp}@example.com",
            "client_telephone": "0123456789",
            "date_evenement": "2024-06-15",
            "lieu_evenement": "Paris, France",
            "type_evenement": "mariage",
            "message": "Bonjour, nous aimerions vous contacter pour notre mariage."
        }
        
        response = requests.post(f"{BASE_URL}/contact", json=contact_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("request_id"):
                print(f"✅ Contact Request: Created successfully - {data.get('request_id')}")
                return True
            else:
                print(f"❌ Contact Request: Invalid response format: {data}")
                return False
        else:
            print(f"❌ Contact Request: HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Contact Request: Request failed: {str(e)}")
        return False

def test_review_creation():
    """Test POST /api/reviews (create review)"""
    try:
        # First, get a DJ to review
        djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
        if djs_response.status_code != 200:
            print(f"❌ Review Creation: Could not get DJs: {djs_response.text}")
            return False
        
        djs_data = djs_response.json()
        if not djs_data.get("djs"):
            print("❌ Review Creation: No DJs available")
            return False
        
        dj_user_id = djs_data["djs"][0]["user_id"]
        print(f"Creating review for DJ: {dj_user_id}")
        
        # Create review
        timestamp = int(time.time())
        review_data = {
            "dj_user_id": dj_user_id,
            "client_nom": "Marie Martin",
            "client_email": f"marie.martin.{timestamp}@example.com",
            "note": 5,
            "commentaire": "Excellent DJ, très professionnel et musique parfaite!",
            "type_evenement": "mariage"
        }
        
        response = requests.post(f"{BASE_URL}/reviews", json=review_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("review_id"):
                print(f"✅ Review Creation: Created successfully - {data.get('review_id')}")
                return True
            else:
                print(f"❌ Review Creation: Invalid response format: {data}")
                return False
        else:
            print(f"❌ Review Creation: HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Review Creation: Request failed: {str(e)}")
        return False

def test_dj_reviews():
    """Test GET /api/djs/{user_id}/reviews"""
    try:
        # Get a DJ first
        djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
        if djs_response.status_code != 200:
            print(f"❌ DJ Reviews: Could not get DJs: {djs_response.text}")
            return False
        
        djs_data = djs_response.json()
        if not djs_data.get("djs"):
            print("❌ DJ Reviews: No DJs available")
            return False
        
        dj_user_id = djs_data["djs"][0]["user_id"]
        
        # Get DJ reviews
        response = requests.get(f"{BASE_URL}/djs/{dj_user_id}/reviews", timeout=10)
        
        if response.status_code == 200:
            reviews = response.json()
            print(f"✅ DJ Reviews: Retrieved {len(reviews)} reviews")
            return True
        else:
            print(f"❌ DJ Reviews: HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ DJ Reviews: Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎵 Testing remaining DJ Connect France APIs")
    print("=" * 50)
    
    results = []
    results.append(test_dj_profile_public())
    results.append(test_contact_request())
    results.append(test_review_creation())
    results.append(test_dj_reviews())
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All remaining tests passed!")
    else:
        print(f"❌ {total - passed} tests failed")