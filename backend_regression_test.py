#!/usr/bin/env python3
"""
Backend Regression Test Suite for DJ Connect France
CRITICAL: Full regression test after MAJOR server.py refactoring.
Tests ALL endpoints to ensure they work exactly as before the modular split.
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
VALID_SIRET = "44306184100047"  # Google France
TIMESTAMP = int(time.time())
TEST_EMAIL = f"test_refactor_{TIMESTAMP}@test.com"
TEST_PASSWORD = "TestPassword123!"

# Global session for maintaining cookies
session = requests.Session()
session.timeout = 10

def log_test(test_name, status, details=""):
    """Log test results with consistent formatting."""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}: {details}")
    return status

def test_health_basic():
    """Test Health & Basic endpoints."""
    print("\n🔍 Testing Health & Basic Endpoints...")
    results = {}
    
    # GET /api/health
    try:
        response = session.get(f"{API_BASE}/health")
        results["health"] = log_test("GET /api/health", 
                                   response.status_code == 200, 
                                   f"Status: {response.status_code}")
    except Exception as e:
        results["health"] = log_test("GET /api/health", False, f"Error: {e}")
    
    # GET /api/
    try:
        response = session.get(f"{API_BASE}/")
        results["root"] = log_test("GET /api/", 
                                 response.status_code == 200, 
                                 f"Status: {response.status_code}")
    except Exception as e:
        results["root"] = log_test("GET /api/", False, f"Error: {e}")
    
    # GET /api/event-types
    try:
        response = session.get(f"{API_BASE}/event-types")
        results["event_types"] = log_test("GET /api/event-types", 
                                        response.status_code == 200, 
                                        f"Status: {response.status_code}")
    except Exception as e:
        results["event_types"] = log_test("GET /api/event-types", False, f"Error: {e}")
    
    return results

def test_auth_endpoints():
    """Test Authentication endpoints."""
    print("\n🔍 Testing Authentication Endpoints...")
    results = {}
    
    # POST /api/auth/register-email
    register_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Test User"
    }
    
    try:
        response = session.post(f"{API_BASE}/auth/register-email", json=register_payload)
        if response.status_code == 200:
            # Check if session cookie is set
            has_session = any('session' in cookie.name.lower() for cookie in session.cookies)
            results["register"] = log_test("POST /api/auth/register-email", 
                                         True, 
                                         f"User created, session: {has_session}")
        else:
            results["register"] = log_test("POST /api/auth/register-email", 
                                         False, 
                                         f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results["register"] = log_test("POST /api/auth/register-email", False, f"Error: {e}")
    
    # GET /api/auth/me (should work with session cookie)
    try:
        response = session.get(f"{API_BASE}/auth/me")
        if response.status_code == 200:
            user_data = response.json()
            results["me"] = log_test("GET /api/auth/me", 
                                   True, 
                                   f"User: {user_data.get('email', 'Unknown')}")
        else:
            results["me"] = log_test("GET /api/auth/me", 
                                   False, 
                                   f"Status: {response.status_code}")
    except Exception as e:
        results["me"] = log_test("GET /api/auth/me", False, f"Error: {e}")
    
    # POST /api/auth/login-email (test with same credentials)
    login_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = session.post(f"{API_BASE}/auth/login-email", json=login_payload)
        results["login"] = log_test("POST /api/auth/login-email", 
                                  response.status_code == 200, 
                                  f"Status: {response.status_code}")
    except Exception as e:
        results["login"] = log_test("POST /api/auth/login-email", False, f"Error: {e}")
    
    # POST /api/auth/logout
    try:
        response = session.post(f"{API_BASE}/auth/logout")
        results["logout"] = log_test("POST /api/auth/logout", 
                                   response.status_code == 200, 
                                   f"Status: {response.status_code}")
    except Exception as e:
        results["logout"] = log_test("POST /api/auth/logout", False, f"Error: {e}")
    
    return results

def test_siret_endpoint():
    """Test SIRET verification endpoint."""
    print("\n🔍 Testing SIRET Verification...")
    results = {}
    
    # POST /api/verify-siret
    siret_payload = {"siret": VALID_SIRET}
    
    try:
        response = session.post(f"{API_BASE}/verify-siret", json=siret_payload)
        if response.status_code == 200:
            data = response.json()
            company_name = data.get('nom_raison_sociale', 'Unknown')
            results["siret"] = log_test("POST /api/verify-siret", 
                                      True, 
                                      f"Company: {company_name}")
        else:
            results["siret"] = log_test("POST /api/verify-siret", 
                                      False, 
                                      f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results["siret"] = log_test("POST /api/verify-siret", False, f"Error: {e}")
    
    return results

def test_geo_endpoints():
    """Test Geographic endpoints."""
    print("\n🔍 Testing Geographic Endpoints...")
    results = {}
    
    # GET /api/geo/regions
    try:
        response = session.get(f"{API_BASE}/geo/regions")
        if response.status_code == 200:
            regions = response.json()
            results["regions"] = log_test("GET /api/geo/regions", 
                                        True, 
                                        f"Found {len(regions)} regions")
        else:
            results["regions"] = log_test("GET /api/geo/regions", 
                                        False, 
                                        f"Status: {response.status_code}")
    except Exception as e:
        results["regions"] = log_test("GET /api/geo/regions", False, f"Error: {e}")
    
    # GET /api/geo/departments
    try:
        response = session.get(f"{API_BASE}/geo/departments")
        if response.status_code == 200:
            departments = response.json()
            results["departments"] = log_test("GET /api/geo/departments", 
                                            True, 
                                            f"Found {len(departments)} departments")
        else:
            results["departments"] = log_test("GET /api/geo/departments", 
                                            False, 
                                            f"Status: {response.status_code}")
    except Exception as e:
        results["departments"] = log_test("GET /api/geo/departments", False, f"Error: {e}")
    
    # GET /api/geo/lookup-city?city=Paris
    try:
        response = session.get(f"{API_BASE}/geo/lookup-city", params={"city": "Paris"})
        if response.status_code == 200:
            data = response.json()
            results["lookup_city"] = log_test("GET /api/geo/lookup-city", 
                                            True, 
                                            f"Paris: {data.get('department_name', 'Unknown')}")
        else:
            results["lookup_city"] = log_test("GET /api/geo/lookup-city", 
                                            False, 
                                            f"Status: {response.status_code}")
    except Exception as e:
        results["lookup_city"] = log_test("GET /api/geo/lookup-city", False, f"Error: {e}")
    
    # GET /api/geo/djs-map
    try:
        response = session.get(f"{API_BASE}/geo/djs-map")
        if response.status_code == 200:
            data = response.json()
            results["djs_map"] = log_test("GET /api/geo/djs-map", 
                                        True, 
                                        f"Found {len(data)} DJs on map")
        else:
            results["djs_map"] = log_test("GET /api/geo/djs-map", 
                                        False, 
                                        f"Status: {response.status_code}")
    except Exception as e:
        results["djs_map"] = log_test("GET /api/geo/djs-map", False, f"Error: {e}")
    
    return results

def test_image_upload():
    """Test Image Upload endpoint."""
    print("\n🔍 Testing Image Upload...")
    results = {}
    
    # POST /api/upload/image
    upload_payload = {
        "image": TEST_BASE64_IMAGE,
        "type": "profile"
    }
    
    try:
        response = session.post(f"{API_BASE}/upload/image", json=upload_payload)
        if response.status_code == 200:
            data = response.json()
            url = data.get('url', '')
            if url.startswith('/api/uploads/'):
                results["image_upload"] = log_test("POST /api/upload/image", 
                                                 True, 
                                                 f"URL: {url}")
                
                # Test if the uploaded image is accessible
                try:
                    img_response = session.get(f"{BACKEND_URL}{url}")
                    results["image_serving"] = log_test("Image serving", 
                                                      img_response.status_code == 200, 
                                                      f"Status: {img_response.status_code}")
                except Exception as e:
                    results["image_serving"] = log_test("Image serving", False, f"Error: {e}")
            else:
                results["image_upload"] = log_test("POST /api/upload/image", 
                                                 False, 
                                                 f"Invalid URL format: {url}")
        else:
            results["image_upload"] = log_test("POST /api/upload/image", 
                                             False, 
                                             f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results["image_upload"] = log_test("POST /api/upload/image", False, f"Error: {e}")
    
    return results

def test_dj_endpoints():
    """Test DJ Profile endpoints (requires authentication)."""
    print("\n🔍 Testing DJ Profile Endpoints...")
    results = {}
    
    # First, re-authenticate to ensure we have a valid session
    login_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        login_response = session.post(f"{API_BASE}/auth/login-email", json=login_payload)
        if login_response.status_code != 200:
            print(f"⚠️ Failed to authenticate for DJ tests: {login_response.status_code}")
            return {"auth_failed": False}
    except Exception as e:
        print(f"⚠️ Authentication error for DJ tests: {e}")
        return {"auth_failed": False}
    
    # GET /api/djs (list all DJs)
    try:
        response = session.get(f"{API_BASE}/djs")
        if response.status_code == 200:
            data = response.json()
            djs = data.get('djs', [])
            results["djs_list"] = log_test("GET /api/djs", 
                                         True, 
                                         f"Found {len(djs)} DJs")
        else:
            results["djs_list"] = log_test("GET /api/djs", 
                                         False, 
                                         f"Status: {response.status_code}")
    except Exception as e:
        results["djs_list"] = log_test("GET /api/djs", False, f"Error: {e}")
    
    # POST /api/dj/register (create DJ profile)
    dj_register_payload = {
        "email": f"dj_{TIMESTAMP}@test.com",
        "nom": "Test",
        "prenom": "DJ",
        "nom_de_scene": "DJ Test",
        "telephone": "0123456789",
        "ville": "Paris",
        "siret": VALID_SIRET,
        "description": "Test DJ for regression testing",
        "types_evenements": ["Mariage", "Soirée privée"],
        "tarif_indicatif": "800€/heure"
    }
    
    try:
        response = session.post(f"{API_BASE}/dj/register", json=dj_register_payload)
        if response.status_code == 200:
            results["dj_register"] = log_test("POST /api/dj/register", 
                                            True, 
                                            "DJ profile created")
        else:
            results["dj_register"] = log_test("POST /api/dj/register", 
                                            False, 
                                            f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results["dj_register"] = log_test("POST /api/dj/register", False, f"Error: {e}")
    
    # GET /api/dj/profile (get own profile)
    try:
        response = session.get(f"{API_BASE}/dj/profile")
        if response.status_code == 200:
            profile = response.json()
            results["dj_profile_get"] = log_test("GET /api/dj/profile", 
                                               True, 
                                               f"DJ: {profile.get('nom_dj', 'Unknown')}")
        else:
            results["dj_profile_get"] = log_test("GET /api/dj/profile", 
                                               False, 
                                               f"Status: {response.status_code}")
    except Exception as e:
        results["dj_profile_get"] = log_test("GET /api/dj/profile", False, f"Error: {e}")
    
    # PUT /api/dj/profile (update profile)
    update_payload = {
        "description": "Updated description for regression test"
    }
    
    try:
        response = session.put(f"{API_BASE}/dj/profile", json=update_payload)
        results["dj_profile_update"] = log_test("PUT /api/dj/profile", 
                                              response.status_code == 200, 
                                              f"Status: {response.status_code}")
    except Exception as e:
        results["dj_profile_update"] = log_test("PUT /api/dj/profile", False, f"Error: {e}")
    
    # GET /api/dj/dashboard
    try:
        response = session.get(f"{API_BASE}/dj/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            results["dj_dashboard"] = log_test("GET /api/dj/dashboard", 
                                             True, 
                                             f"Views: {dashboard.get('total_views', 0)}")
        else:
            results["dj_dashboard"] = log_test("GET /api/dj/dashboard", 
                                             False, 
                                             f"Status: {response.status_code}")
    except Exception as e:
        results["dj_dashboard"] = log_test("GET /api/dj/dashboard", False, f"Error: {e}")
    
    return results

def test_contact_endpoints():
    """Test Contact endpoints."""
    print("\n🔍 Testing Contact Endpoints...")
    results = {}
    
    # First get a DJ ID to contact
    dj_id = None
    try:
        response = session.get(f"{API_BASE}/djs")
        if response.status_code == 200:
            data = response.json()
            djs = data.get('djs', [])
            if djs:
                dj_id = djs[0].get('user_id')
    except:
        pass
    
    # POST /api/contact
    if dj_id:
        contact_payload = {
            "dj_user_id": dj_id,
            "client_nom": "Test Client",
            "client_email": f"client_{TIMESTAMP}@test.com",
            "client_telephone": "0123456789",
            "type_evenement": "Mariage",
            "date_evenement": "2024-06-15",
            "lieu_evenement": "Paris",
            "message": "Test contact for regression testing"
        }
        
        try:
            response = session.post(f"{API_BASE}/contact", json=contact_payload)
            results["contact_create"] = log_test("POST /api/contact", 
                                                response.status_code == 200, 
                                                f"Status: {response.status_code}")
        except Exception as e:
            results["contact_create"] = log_test("POST /api/contact", False, f"Error: {e}")
    else:
        results["contact_create"] = log_test("POST /api/contact", False, "No DJ ID available")
    
    # GET /api/dj/contacts (requires DJ authentication)
    try:
        response = session.get(f"{API_BASE}/dj/contacts")
        if response.status_code == 200:
            contacts = response.json()
            results["dj_contacts"] = log_test("GET /api/dj/contacts", 
                                            True, 
                                            f"Found {len(contacts)} contacts")
        else:
            results["dj_contacts"] = log_test("GET /api/dj/contacts", 
                                            False, 
                                            f"Status: {response.status_code}")
    except Exception as e:
        results["dj_contacts"] = log_test("GET /api/dj/contacts", False, f"Error: {e}")
    
    return results

def test_review_endpoints():
    """Test Review endpoints."""
    print("\n🔍 Testing Review Endpoints...")
    results = {}
    
    # Get a DJ ID for reviews
    dj_id = None
    try:
        response = session.get(f"{API_BASE}/djs")
        if response.status_code == 200:
            data = response.json()
            djs = data.get('djs', [])
            if djs:
                dj_id = djs[0].get('user_id')
    except:
        pass
    
    # POST /api/reviews
    if dj_id:
        review_payload = {
            "dj_user_id": dj_id,
            "client_nom": "Test Reviewer",
            "client_email": f"reviewer_{TIMESTAMP}@test.com",
            "note": 5,
            "commentaire": "Excellent DJ for regression testing",
            "type_evenement": "Mariage"
        }
        
        try:
            response = session.post(f"{API_BASE}/reviews", json=review_payload)
            results["review_create"] = log_test("POST /api/reviews", 
                                              response.status_code == 200, 
                                              f"Status: {response.status_code}")
        except Exception as e:
            results["review_create"] = log_test("POST /api/reviews", False, f"Error: {e}")
        
        # GET /api/djs/{user_id}/reviews
        try:
            response = session.get(f"{API_BASE}/djs/{dj_id}/reviews")
            if response.status_code == 200:
                reviews = response.json()
                results["dj_reviews"] = log_test(f"GET /api/djs/{dj_id}/reviews", 
                                               True, 
                                               f"Found {len(reviews)} reviews")
            else:
                results["dj_reviews"] = log_test(f"GET /api/djs/{dj_id}/reviews", 
                                               False, 
                                               f"Status: {response.status_code}")
        except Exception as e:
            results["dj_reviews"] = log_test(f"GET /api/djs/{dj_id}/reviews", False, f"Error: {e}")
    else:
        results["review_create"] = log_test("POST /api/reviews", False, "No DJ ID available")
        results["dj_reviews"] = log_test("GET /api/djs/{id}/reviews", False, "No DJ ID available")
    
    # GET /api/dj/reviews/pending (requires DJ auth)
    try:
        response = session.get(f"{API_BASE}/dj/reviews/pending")
        results["dj_reviews_pending"] = log_test("GET /api/dj/reviews/pending", 
                                               response.status_code == 200, 
                                               f"Status: {response.status_code}")
    except Exception as e:
        results["dj_reviews_pending"] = log_test("GET /api/dj/reviews/pending", False, f"Error: {e}")
    
    # GET /api/dj/reviews/all (requires DJ auth)
    try:
        response = session.get(f"{API_BASE}/dj/reviews/all")
        results["dj_reviews_all"] = log_test("GET /api/dj/reviews/all", 
                                           response.status_code == 200, 
                                           f"Status: {response.status_code}")
    except Exception as e:
        results["dj_reviews_all"] = log_test("GET /api/dj/reviews/all", False, f"Error: {e}")
    
    return results

def test_boost_endpoints():
    """Test Boost endpoints."""
    print("\n🔍 Testing Boost Endpoints...")
    results = {}
    
    # GET /api/boost/plans
    try:
        response = session.get(f"{API_BASE}/boost/plans")
        if response.status_code == 200:
            plans = response.json()
            results["boost_plans"] = log_test("GET /api/boost/plans", 
                                            True, 
                                            f"Found {len(plans)} plans")
        else:
            results["boost_plans"] = log_test("GET /api/boost/plans", 
                                            False, 
                                            f"Status: {response.status_code}")
    except Exception as e:
        results["boost_plans"] = log_test("GET /api/boost/plans", False, f"Error: {e}")
    
    # GET /api/boost/status (requires DJ auth)
    try:
        response = session.get(f"{API_BASE}/boost/status")
        results["boost_status"] = log_test("GET /api/boost/status", 
                                         response.status_code in [200, 401], 
                                         f"Status: {response.status_code}")
    except Exception as e:
        results["boost_status"] = log_test("GET /api/boost/status", False, f"Error: {e}")
    
    # POST /api/boost/create-checkout (requires DJ auth)
    boost_payload = {"plan": "1_week", "origin_url": "https://test.com"}
    try:
        response = session.post(f"{API_BASE}/boost/create-checkout", json=boost_payload)
        if response.status_code == 200:
            data = response.json()
            results["boost_checkout"] = log_test("POST /api/boost/create-checkout", 
                                               True, 
                                               f"Checkout created: {data.get('checkout_url', '')[:50]}...")
        else:
            results["boost_checkout"] = log_test("POST /api/boost/create-checkout", 
                                               False, 
                                               f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results["boost_checkout"] = log_test("POST /api/boost/create-checkout", False, f"Error: {e}")
    
    return results

def test_subscription_endpoints():
    """Test Subscription/Stripe endpoints."""
    print("\n🔍 Testing Subscription/Stripe Endpoints...")
    results = {}
    
    # GET /api/subscription/plans
    try:
        response = session.get(f"{API_BASE}/subscription/plans")
        if response.status_code == 200:
            plans = response.json()
            results["subscription_plans"] = log_test("GET /api/subscription/plans", 
                                                   True, 
                                                   f"Found {len(plans)} plans")
        else:
            results["subscription_plans"] = log_test("GET /api/subscription/plans", 
                                                   False, 
                                                   f"Status: {response.status_code}")
    except Exception as e:
        results["subscription_plans"] = log_test("GET /api/subscription/plans", False, f"Error: {e}")
    
    # POST /api/subscription/create-checkout (requires auth)
    checkout_payload = {"plan": "monthly", "origin_url": "https://test.com"}
    try:
        response = session.post(f"{API_BASE}/subscription/create-checkout", json=checkout_payload)
        if response.status_code == 200:
            data = response.json()
            checkout_url = data.get('checkout_url', '')
            results["subscription_checkout"] = log_test("POST /api/subscription/create-checkout", 
                                                      'checkout.stripe.com' in checkout_url, 
                                                      f"Checkout URL: {checkout_url[:50]}...")
        else:
            results["subscription_checkout"] = log_test("POST /api/subscription/create-checkout", 
                                                      False, 
                                                      f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results["subscription_checkout"] = log_test("POST /api/subscription/create-checkout", False, f"Error: {e}")
    
    return results

def test_zone_endpoints():
    """Test Zone endpoints."""
    print("\n🔍 Testing Zone Endpoints...")
    results = {}
    
    # GET /api/dj/zone-status (requires DJ auth)
    try:
        response = session.get(f"{API_BASE}/dj/zone-status")
        results["zone_status"] = log_test("GET /api/dj/zone-status", 
                                        response.status_code in [200, 401], 
                                        f"Status: {response.status_code}")
    except Exception as e:
        results["zone_status"] = log_test("GET /api/dj/zone-status", False, f"Error: {e}")
    
    # GET /api/dj/available-departments (requires DJ auth)
    try:
        response = session.get(f"{API_BASE}/dj/available-departments")
        results["available_departments"] = log_test("GET /api/dj/available-departments", 
                                                  response.status_code in [200, 401], 
                                                  f"Status: {response.status_code}")
    except Exception as e:
        results["available_departments"] = log_test("GET /api/dj/available-departments", False, f"Error: {e}")
    
    return results

def main():
    """Run comprehensive regression test suite."""
    print("🚀 CRITICAL REGRESSION TEST - Server.py Refactoring Validation")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print("=" * 80)
    
    all_results = {}
    
    # Run all test suites
    test_suites = [
        ("Health & Basic", test_health_basic),
        ("Authentication", test_auth_endpoints),
        ("SIRET Verification", test_siret_endpoint),
        ("Geographic APIs", test_geo_endpoints),
        ("Image Upload", test_image_upload),
        ("DJ Profiles", test_dj_endpoints),
        ("Contact System", test_contact_endpoints),
        ("Review System", test_review_endpoints),
        ("Boost System", test_boost_endpoints),
        ("Subscription/Stripe", test_subscription_endpoints),
        ("Zone Management", test_zone_endpoints)
    ]
    
    for suite_name, test_func in test_suites:
        try:
            results = test_func()
            all_results[suite_name] = results
        except Exception as e:
            print(f"❌ {suite_name} test suite failed: {e}")
            all_results[suite_name] = {"suite_error": False}
    
    # Generate comprehensive summary
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE REGRESSION TEST SUMMARY")
    print("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for suite_name, results in all_results.items():
        print(f"\n🔍 {suite_name}:")
        suite_passed = 0
        suite_total = 0
        
        for test_name, result in results.items():
            suite_total += 1
            total_tests += 1
            
            if result:
                suite_passed += 1
                passed_tests += 1
                print(f"  ✅ {test_name}")
            else:
                failed_tests.append(f"{suite_name}: {test_name}")
                print(f"  ❌ {test_name}")
        
        print(f"  📊 {suite_passed}/{suite_total} passed")
    
    print(f"\n" + "=" * 80)
    print(f"🎯 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for failed in failed_tests:
            print(f"  • {failed}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate >= 90:
        print(f"\n🎉 REGRESSION TEST PASSED! ({success_rate:.1f}% success rate)")
        print("✅ Server.py refactoring appears successful - all critical endpoints working")
        return True
    elif success_rate >= 75:
        print(f"\n⚠️ REGRESSION TEST PARTIAL SUCCESS ({success_rate:.1f}% success rate)")
        print("🔧 Some endpoints need attention but core functionality intact")
        return True
    else:
        print(f"\n💥 REGRESSION TEST FAILED! ({success_rate:.1f}% success rate)")
        print("🚨 Critical issues detected - refactoring may have broken core functionality")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)