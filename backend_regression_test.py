#!/usr/bin/env python3
"""
Comprehensive Backend Regression Test Suite for DJ Connect France
Tests ALL API endpoints in sequence with cookie-based authentication.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://dj-directory-fr.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test data
TEST_BASE64_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
TIMESTAMP = int(time.time())
TEST_EMAIL = f"fulltest_{TIMESTAMP}@test.com"
TEST_PASSWORD = "Test12345!"
TEST_NAME = "DJ FullTest"

# Global session for cookie persistence
session = requests.Session()
session.timeout = 10

# Test results tracking
test_results = {}
user_id = None
dj_user_id = None

def log_test(test_name, success, details=""):
    """Log test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    test_results[test_name] = {"success": success, "details": details}
    return success

def test_health_static():
    """Test health and static endpoints."""
    print("\n🔍 1. HEALTH & STATIC ENDPOINTS")
    
    # GET /api/
    try:
        response = session.get(f"{API_BASE}/")
        success = response.status_code == 200 and "message" in response.json()
        log_test("GET /api/", success, f"Status: {response.status_code}")
    except Exception as e:
        log_test("GET /api/", False, str(e))
    
    # GET /api/health
    try:
        response = session.get(f"{API_BASE}/health")
        data = response.json()
        success = response.status_code == 200 and data.get("status") == "healthy"
        log_test("GET /api/health", success, f"Status: {data.get('status')}")
    except Exception as e:
        log_test("GET /api/health", False, str(e))
    
    # GET /api/event-types
    try:
        response = session.get(f"{API_BASE}/event-types")
        data = response.json()
        success = response.status_code == 200 and len(data) == 8
        log_test("GET /api/event-types", success, f"Found {len(data)} event types")
    except Exception as e:
        log_test("GET /api/event-types", False, str(e))

def test_auth_email():
    """Test email registration and login."""
    global user_id
    print("\n🔍 2. EMAIL AUTHENTICATION")
    
    # POST /api/auth/register-email
    try:
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        }
        response = session.post(f"{API_BASE}/auth/register-email", json=payload)
        success = response.status_code == 200
        if success:
            data = response.json()
            user_id = data.get("user_id")
        log_test("POST /api/auth/register-email", success, f"User ID: {user_id}")
    except Exception as e:
        log_test("POST /api/auth/register-email", False, str(e))
    
    # GET /api/auth/me (with cookie)
    try:
        response = session.get(f"{API_BASE}/auth/me")
        data = response.json()
        success = response.status_code == 200 and data.get("email") == TEST_EMAIL
        log_test("GET /api/auth/me (after register)", success, f"Email: {data.get('email')}")
    except Exception as e:
        log_test("GET /api/auth/me (after register)", False, str(e))
    
    # POST /api/auth/logout
    try:
        response = session.post(f"{API_BASE}/auth/logout")
        success = response.status_code == 200
        log_test("POST /api/auth/logout", success)
    except Exception as e:
        log_test("POST /api/auth/logout", False, str(e))
    
    # POST /api/auth/login-email
    try:
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = session.post(f"{API_BASE}/auth/login-email", json=payload)
        success = response.status_code == 200
        log_test("POST /api/auth/login-email", success)
    except Exception as e:
        log_test("POST /api/auth/login-email", False, str(e))
    
    # GET /api/auth/me (after login)
    try:
        response = session.get(f"{API_BASE}/auth/me")
        data = response.json()
        success = response.status_code == 200 and data.get("email") == TEST_EMAIL
        log_test("GET /api/auth/me (after login)", success, f"Email: {data.get('email')}")
    except Exception as e:
        log_test("GET /api/auth/me (after login)", False, str(e))

def test_siret_verification():
    """Test SIRET verification endpoints."""
    print("\n🔍 3. SIRET VERIFICATION")
    
    # Valid SIRET
    try:
        payload = {"siret": "44306184100047"}
        response = session.post(f"{API_BASE}/verify-siret", json=payload)
        data = response.json()
        success = response.status_code == 200 and data.get("valid") == True
        log_test("POST /api/verify-siret (valid)", success, f"Company: {data.get('company_name', 'N/A')}")
    except Exception as e:
        log_test("POST /api/verify-siret (valid)", False, str(e))
    
    # Invalid SIRET (all zeros)
    try:
        payload = {"siret": "00000000000000"}
        response = session.post(f"{API_BASE}/verify-siret", json=payload)
        data = response.json()
        success = response.status_code == 200 and data.get("valid") == False
        log_test("POST /api/verify-siret (invalid zeros)", success)
    except Exception as e:
        log_test("POST /api/verify-siret (invalid zeros)", False, str(e))
    
    # Invalid SIRET (wrong length)
    try:
        payload = {"siret": "123"}
        response = session.post(f"{API_BASE}/verify-siret", json=payload)
        data = response.json()
        success = response.status_code == 200 and data.get("valid") == False and ("14 digits" in data.get("message", "") or "14 chiffres" in data.get("message", ""))
        log_test("POST /api/verify-siret (wrong length)", success, data.get("message", ""))
    except Exception as e:
        log_test("POST /api/verify-siret (wrong length)", False, str(e))

def test_geo_endpoints():
    """Test geographic endpoints."""
    print("\n🔍 4. GEOGRAPHIC ENDPOINTS")
    
    # GET /api/geo/regions
    try:
        response = session.get(f"{API_BASE}/geo/regions")
        data = response.json()
        success = response.status_code == 200 and len(data) == 18
        log_test("GET /api/geo/regions", success, f"Found {len(data)} regions")
    except Exception as e:
        log_test("GET /api/geo/regions", False, str(e))
    
    # GET /api/geo/departments
    try:
        response = session.get(f"{API_BASE}/geo/departments")
        data = response.json()
        success = response.status_code == 200 and len(data) >= 95  # Should be ~100
        log_test("GET /api/geo/departments", success, f"Found {len(data)} departments")
    except Exception as e:
        log_test("GET /api/geo/departments", False, str(e))
    
    # GET /api/geo/departments?region_code=IDF (Île-de-France)
    try:
        response = session.get(f"{API_BASE}/geo/departments?region_code=IDF")
        data = response.json()
        success = response.status_code == 200 and len(data) > 0
        log_test("GET /api/geo/departments (filtered)", success, f"Found {len(data)} departments in IDF")
    except Exception as e:
        log_test("GET /api/geo/departments (filtered)", False, str(e))
    
    # GET /api/geo/lookup-city?city=Paris
    try:
        response = session.get(f"{API_BASE}/geo/lookup-city?city=Paris")
        data = response.json()
        success = response.status_code == 200 and "department_name" in data and "region_name" in data
        log_test("GET /api/geo/lookup-city", success, f"Paris: {data.get('department_name')} / {data.get('region_name')}")
    except Exception as e:
        log_test("GET /api/geo/lookup-city", False, str(e))
    
    # GET /api/geo/djs-map
    try:
        response = session.get(f"{API_BASE}/geo/djs-map")
        data = response.json()
        success = response.status_code == 200 and "djs" in data
        djs = data.get("djs", []) if success else []
        log_test("GET /api/geo/djs-map", success, f"Found {len(djs)} DJ locations")
    except Exception as e:
        log_test("GET /api/geo/djs-map", False, str(e))

def test_dj_registration():
    """Test DJ registration with full profile."""
    global dj_user_id
    print("\n🔍 5. DJ REGISTRATION")
    
    try:
        payload = {
            "nom": "Test",
            "prenom": "Complet",
            "nom_de_scene": "DJ FullTest",
            "telephone": "0612345678",
            "ville": "Paris",
            "code_postal": "75001",
            "siret": "44306184100047",
            "tarif_indicatif": "1000€",
            "description": "Test DJ complet",
            "types_evenements": ["Mariage", "Anniversaire"],
            "annees_experience": 5,
            "zone_intervention": ["Paris"],
            "assurance_rc_numero": "RC-2024-TEST-001",
            "assurance_rc_organisme": "AXA"
        }
        response = session.post(f"{API_BASE}/dj/register", json=payload)
        success = response.status_code == 200
        if success:
            data = response.json()
            dj_user_id = user_id  # DJ registration uses current user
        log_test("POST /api/dj/register", success, f"DJ User ID: {dj_user_id}")
    except Exception as e:
        log_test("POST /api/dj/register", False, str(e))

def test_dj_profile_management():
    """Test DJ profile management endpoints."""
    print("\n🔍 6. DJ PROFILE MANAGEMENT")
    
    # GET /api/dj/profile
    try:
        response = session.get(f"{API_BASE}/dj/profile")
        data = response.json()
        success = response.status_code == 200 and "assurance_rc_numero" in data and "assurance_rc_organisme" in data
        log_test("GET /api/dj/profile", success, f"Assurance: {data.get('assurance_rc_organisme')}")
    except Exception as e:
        log_test("GET /api/dj/profile", False, str(e))
    
    # PUT /api/dj/profile
    try:
        payload = {
            "description": "Updated description",
            "assurance_rc_organisme": "MAIF"
        }
        response = session.put(f"{API_BASE}/dj/profile", json=payload)
        success = response.status_code == 200
        log_test("PUT /api/dj/profile", success)
    except Exception as e:
        log_test("PUT /api/dj/profile", False, str(e))
    
    # GET /api/dj/dashboard
    try:
        response = session.get(f"{API_BASE}/dj/dashboard")
        data = response.json()
        success = response.status_code == 200 and "is_locked" in data
        is_locked = data.get("is_locked", False)
        log_test("GET /api/dj/dashboard", success, f"is_locked: {is_locked} (expected: true for inactive subscription)")
    except Exception as e:
        log_test("GET /api/dj/dashboard", False, str(e))

def test_image_upload():
    """Test image upload endpoints."""
    print("\n🔍 7. IMAGE UPLOAD")
    
    # POST /api/upload/image
    try:
        payload = {
            "image": TEST_BASE64_IMAGE,
            "type": "profile"
        }
        response = session.post(f"{API_BASE}/upload/image", json=payload)
        data = response.json()
        success = response.status_code == 200 and "url" in data
        uploaded_url = data.get("url") if success else None
        log_test("POST /api/upload/image", success, f"URL: {uploaded_url}")
    except Exception as e:
        log_test("POST /api/upload/image", False, str(e))
        uploaded_url = None
    
    # POST /api/upload/images (batch)
    try:
        payload = {
            "images": [TEST_BASE64_IMAGE, "/api/uploads/existing.jpg"],
            "type": "gallery"
        }
        response = session.post(f"{API_BASE}/upload/images", json=payload)
        data = response.json()
        success = response.status_code == 200 and "urls" in data and len(data["urls"]) == 2
        log_test("POST /api/upload/images", success, f"URLs: {len(data.get('urls', []))}")
    except Exception as e:
        log_test("POST /api/upload/images", False, str(e))
    
    # POST /api/upload/image (pass-through)
    try:
        payload = {
            "image": "/api/uploads/existing.jpg"
        }
        response = session.post(f"{API_BASE}/upload/image", json=payload)
        data = response.json()
        success = response.status_code == 200 and data.get("url") == "/api/uploads/existing.jpg"
        log_test("POST /api/upload/image (pass-through)", success)
    except Exception as e:
        log_test("POST /api/upload/image (pass-through)", False, str(e))
    
    # GET uploaded image
    if uploaded_url:
        try:
            response = session.get(f"{BACKEND_URL}{uploaded_url}")
            success = response.status_code == 200 and "image" in response.headers.get("content-type", "")
            log_test("GET uploaded image", success, f"Content-Type: {response.headers.get('content-type')}")
        except Exception as e:
            log_test("GET uploaded image", False, str(e))

def test_dj_listing_public():
    """Test DJ listing and public profile endpoints."""
    print("\n🔍 8. DJ LISTING & PUBLIC PROFILE")
    
    # GET /api/djs
    try:
        response = session.get(f"{API_BASE}/djs")
        data = response.json()
        success = response.status_code == 200 and "djs" in data
        djs = data.get("djs", [])
        log_test("GET /api/djs", success, f"Found {len(djs)} active DJs")
    except Exception as e:
        log_test("GET /api/djs", False, str(e))
    
    # GET /api/djs?code_postal=61000
    try:
        response = session.get(f"{API_BASE}/djs?code_postal=61000")
        data = response.json()
        success = response.status_code == 200
        djs = data.get("djs", [])
        log_test("GET /api/djs (postal search)", success, f"Found {len(djs)} DJs in 61000")
    except Exception as e:
        log_test("GET /api/djs (postal search)", False, str(e))
    
    # Find an active DJ for public profile test
    active_dj_id = None
    try:
        response = session.get(f"{API_BASE}/djs")
        data = response.json()
        djs = data.get("djs", [])
        if djs:
            active_dj_id = djs[0].get("user_id")
    except:
        pass
    
    # GET /api/djs/{user_id} (public profile)
    if active_dj_id:
        try:
            response = session.get(f"{API_BASE}/djs/{active_dj_id}")
            data = response.json()
            success = response.status_code == 200
            # Check privacy - should NOT contain assurance fields
            has_assurance = "assurance_rc_numero" in data or "assurance_rc_organisme" in data
            privacy_ok = not has_assurance
            log_test("GET /api/djs/{user_id} (privacy check)", success and privacy_ok, 
                    f"Assurance fields hidden: {privacy_ok}")
        except Exception as e:
            log_test("GET /api/djs/{user_id} (privacy check)", False, str(e))

def test_contact_requests():
    """Test contact request endpoints."""
    print("\n🔍 9. CONTACT REQUESTS")
    
    # Find an active DJ for contact test
    active_dj_id = None
    try:
        response = session.get(f"{API_BASE}/djs")
        data = response.json()
        djs = data.get("djs", [])
        if djs:
            active_dj_id = djs[0].get("user_id")
    except:
        pass
    
    # POST /api/contact
    if active_dj_id:
        try:
            payload = {
                "dj_user_id": active_dj_id,
                "client_nom": "Client Test",
                "client_email": "client@test.com",
                "client_telephone": "0123456789",
                "type_evenement": "Mariage",
                "date_evenement": "2024-06-15",
                "lieu_evenement": "Paris",
                "message": "Test contact request"
            }
            response = session.post(f"{API_BASE}/contact", json=payload)
            success = response.status_code == 200
            log_test("POST /api/contact", success)
        except Exception as e:
            log_test("POST /api/contact", False, str(e))
    
    # GET /api/dj/contacts (requires DJ auth)
    try:
        response = session.get(f"{API_BASE}/dj/contacts")
        success = response.status_code == 200
        if success:
            data = response.json()
            # Response is a direct list, not wrapped in an object
            contacts = data if isinstance(data, list) else []
            log_test("GET /api/dj/contacts", success, f"Found {len(contacts)} contacts")
        else:
            log_test("GET /api/dj/contacts", success)
    except Exception as e:
        log_test("GET /api/dj/contacts", False, str(e))

def test_reviews():
    """Test review system endpoints."""
    print("\n🔍 10. REVIEWS")
    
    # Find an active DJ for review test
    active_dj_id = None
    try:
        response = session.get(f"{API_BASE}/djs")
        data = response.json()
        djs = data.get("djs", [])
        if djs:
            active_dj_id = djs[0].get("user_id")
    except:
        pass
    
    # POST /api/reviews
    if active_dj_id:
        try:
            payload = {
                "dj_user_id": active_dj_id,
                "client_nom": "Client Test",
                "client_email": "client@test.com",
                "note": 5,
                "commentaire": "Excellent DJ!",
                "type_evenement": "Mariage"
            }
            response = session.post(f"{API_BASE}/reviews", json=payload)
            success = response.status_code == 200
            log_test("POST /api/reviews", success)
        except Exception as e:
            log_test("POST /api/reviews", False, str(e))
        
        # GET /api/djs/{user_id}/reviews
        try:
            response = session.get(f"{API_BASE}/djs/{active_dj_id}/reviews")
            data = response.json()
            success = response.status_code == 200
            # Response is a direct list, not wrapped in an object
            reviews = data if isinstance(data, list) else []
            log_test("GET /api/djs/{user_id}/reviews", success, f"Found {len(reviews)} reviews")
        except Exception as e:
            log_test("GET /api/djs/{user_id}/reviews", False, str(e))

def test_subscription_stripe():
    """Test subscription and Stripe endpoints."""
    print("\n🔍 11. SUBSCRIPTION & STRIPE")
    
    # GET /api/subscription/plans
    try:
        response = session.get(f"{API_BASE}/subscription/plans")
        data = response.json()
        success = response.status_code == 200 and len(data) == 2
        plans = [plan.get("name") for plan in data]
        log_test("GET /api/subscription/plans", success, f"Plans: {plans}")
    except Exception as e:
        log_test("GET /api/subscription/plans", False, str(e))
    
    # POST /api/subscription/create-checkout
    try:
        payload = {
            "origin_url": "https://dj-directory-fr.preview.emergentagent.com",
            "plan": "monthly"
        }
        response = session.post(f"{API_BASE}/subscription/create-checkout", json=payload)
        data = response.json()
        success = response.status_code == 200 and "checkout_url" in data and "session_id" in data
        checkout_url = data.get("checkout_url", "")
        is_stripe_url = checkout_url.startswith("https://checkout.stripe.com/")
        log_test("POST /api/subscription/create-checkout", success and is_stripe_url, 
                f"Stripe URL: {is_stripe_url}")
    except Exception as e:
        log_test("POST /api/subscription/create-checkout", False, str(e))

def test_boost():
    """Test boost system endpoints."""
    print("\n🔍 12. BOOST SYSTEM")
    
    # GET /api/boost/plans
    try:
        response = session.get(f"{API_BASE}/boost/plans")
        data = response.json()
        success = response.status_code == 200 and len(data) == 3
        plans = [f"{plan.get('name')}: {plan.get('price')}€" for plan in data]
        log_test("GET /api/boost/plans", success, f"Plans: {plans}")
    except Exception as e:
        log_test("GET /api/boost/plans", False, str(e))
    
    # GET /api/boost/status
    try:
        response = session.get(f"{API_BASE}/boost/status")
        success = response.status_code == 200
        if success:
            data = response.json()
            boost_active = data.get("boost_active", False)
            log_test("GET /api/boost/status", success, f"boost_active: {boost_active}")
        else:
            log_test("GET /api/boost/status", success)
    except Exception as e:
        log_test("GET /api/boost/status", False, str(e))
    
    # POST /api/boost/create-checkout
    try:
        payload = {
            "origin_url": "https://dj-directory-fr.preview.emergentagent.com",
            "plan": "1_week"
        }
        response = session.post(f"{API_BASE}/boost/create-checkout", json=payload)
        data = response.json()
        success = response.status_code == 200 and "checkout_url" in data
        checkout_url = data.get("checkout_url", "")
        is_stripe_url = checkout_url.startswith("https://checkout.stripe.com/")
        log_test("POST /api/boost/create-checkout", success and is_stripe_url, 
                f"Stripe URL: {is_stripe_url}")
    except Exception as e:
        log_test("POST /api/boost/create-checkout", False, str(e))

def test_zone_management():
    """Test zone management endpoints."""
    print("\n🔍 13. ZONE MANAGEMENT")
    
    # GET /api/dj/zone-status
    try:
        response = session.get(f"{API_BASE}/dj/zone-status")
        success = response.status_code == 200
        if success:
            data = response.json()
            log_test("GET /api/dj/zone-status", success, f"Zone config returned")
        else:
            log_test("GET /api/dj/zone-status", success)
    except Exception as e:
        log_test("GET /api/dj/zone-status", False, str(e))
    
    # GET /api/dj/available-departments
    try:
        response = session.get(f"{API_BASE}/dj/available-departments")
        data = response.json()
        success = response.status_code == 200 and isinstance(data, list)
        log_test("GET /api/dj/available-departments", success, f"Found {len(data)} departments")
    except Exception as e:
        log_test("GET /api/dj/available-departments", False, str(e))

def test_privacy_checks():
    """Test privacy protection for assurance fields."""
    print("\n🔍 14. PRIVACY CHECKS")
    
    # Find an active DJ
    active_dj_id = None
    try:
        response = session.get(f"{API_BASE}/djs")
        data = response.json()
        djs = data.get("djs", [])
        if djs:
            active_dj_id = djs[0].get("user_id")
    except:
        pass
    
    # GET /api/djs/{user_id} - should NOT contain assurance fields
    if active_dj_id:
        try:
            response = session.get(f"{API_BASE}/djs/{active_dj_id}")
            data = response.json()
            has_assurance_numero = "assurance_rc_numero" in data
            has_assurance_organisme = "assurance_rc_organisme" in data
            success = response.status_code == 200 and not has_assurance_numero and not has_assurance_organisme
            log_test("Privacy: GET /api/djs/{user_id}", success, 
                    f"Assurance fields hidden: {not (has_assurance_numero or has_assurance_organisme)}")
        except Exception as e:
            log_test("Privacy: GET /api/djs/{user_id}", False, str(e))
    
    # GET /api/djs - list should NOT contain assurance fields
    try:
        response = session.get(f"{API_BASE}/djs")
        data = response.json()
        djs = data.get("djs", [])
        has_assurance_fields = False
        for dj in djs:
            if "assurance_rc_numero" in dj or "assurance_rc_organisme" in dj:
                has_assurance_fields = True
                break
        success = response.status_code == 200 and not has_assurance_fields
        log_test("Privacy: GET /api/djs (list)", success, 
                f"Assurance fields hidden in list: {not has_assurance_fields}")
    except Exception as e:
        log_test("Privacy: GET /api/djs (list)", False, str(e))

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🔍 15. ERROR HANDLING")
    
    # GET /api/djs/nonexistent_user_id
    try:
        response = session.get(f"{API_BASE}/djs/nonexistent_user_id")
        success = response.status_code == 404
        log_test("GET /api/djs/nonexistent_user_id", success, f"Status: {response.status_code}")
    except Exception as e:
        log_test("GET /api/djs/nonexistent_user_id", False, str(e))
    
    # POST /api/auth/login-email (wrong credentials)
    try:
        payload = {
            "email": "wrong@wrong.com",
            "password": "wrong"
        }
        response = session.post(f"{API_BASE}/auth/login-email", json=payload)
        success = response.status_code == 401
        log_test("POST /api/auth/login-email (wrong creds)", success, f"Status: {response.status_code}")
    except Exception as e:
        log_test("POST /api/auth/login-email (wrong creds)", False, str(e))
    
    # Create a new session without auth for testing protected endpoints
    unauth_session = requests.Session()
    unauth_session.timeout = 10
    
    # POST /api/dj/register without auth
    try:
        payload = {"nom": "Test"}
        response = unauth_session.post(f"{API_BASE}/dj/register", json=payload)
        # Accept both 401 (auth error) and 422 (validation error) as valid responses
        success = response.status_code in [401, 422]
        log_test("POST /api/dj/register (no auth)", success, f"Status: {response.status_code}")
    except Exception as e:
        log_test("POST /api/dj/register (no auth)", False, str(e))
    
    # GET /api/dj/contacts without auth
    try:
        response = unauth_session.get(f"{API_BASE}/dj/contacts")
        success = response.status_code == 401
        log_test("GET /api/dj/contacts (no auth)", success, f"Status: {response.status_code}")
    except Exception as e:
        log_test("GET /api/dj/contacts (no auth)", False, str(e))

def print_summary():
    """Print comprehensive test summary."""
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE REGRESSION TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ FAILED TESTS ({failed_tests}):")
        print("-" * 40)
        for test_name, result in test_results.items():
            if not result["success"]:
                print(f"• {test_name}")
                if result["details"]:
                    print(f"  └─ {result['details']}")
    
    print(f"\n✅ PASSED TESTS ({passed_tests}):")
    print("-" * 40)
    for test_name, result in test_results.items():
        if result["success"]:
            print(f"• {test_name}")
    
    return passed_tests == total_tests

def main():
    """Run comprehensive regression test suite."""
    print("🚀 DJ CONNECT FRANCE - COMPREHENSIVE REGRESSION TEST")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print("=" * 80)
    
    # Run all test suites
    test_health_static()
    test_auth_email()
    test_siret_verification()
    test_geo_endpoints()
    test_dj_registration()
    test_dj_profile_management()
    test_image_upload()
    test_dj_listing_public()
    test_contact_requests()
    test_reviews()
    test_subscription_stripe()
    test_boost()
    test_zone_management()
    test_privacy_checks()
    test_error_handling()
    
    # Print summary
    all_passed = print_summary()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Backend is fully functional.")
    else:
        print("\n⚠️ Some tests failed. See details above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)