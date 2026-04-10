#!/usr/bin/env python3
"""
SIMPLIFIED FULL REGRESSION TEST for DJ Match France
Focus on critical functionality with better error handling.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
ADMIN_EMAIL = "adrien.sebert@gmail.com"
ADMIN_PASSWORD = "test123"
TEST_SIRET = "44306184100047"  # Google France

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.critical_errors = []
        
    def assert_test(self, condition, test_name, error_msg="", critical=False):
        if condition:
            print(f"✅ {test_name}")
            self.passed += 1
        else:
            print(f"❌ {test_name}: {error_msg}")
            self.failed += 1
            self.errors.append(f"{test_name}: {error_msg}")
            if critical:
                self.critical_errors.append(f"{test_name}: {error_msg}")
            
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*80}")
        print(f"FULL REGRESSION TEST SUMMARY: {self.passed}/{total} passed")
        if self.critical_errors:
            print(f"\n🚨 CRITICAL FAILURES:")
            for error in self.critical_errors:
                print(f"  - {error}")
        if self.errors:
            print(f"\nALL FAILURES:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*80}")
        return self.failed == 0

def make_request(method, endpoint, data=None, cookies=None, headers=None, timeout=30):
    """Make HTTP request with better error handling"""
    url = f"{BASE_URL}{endpoint}"
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    try:
        session = requests.Session()
        session.headers.update(default_headers)
        
        if method == "GET":
            response = session.get(url, cookies=cookies, timeout=timeout)
        elif method == "POST":
            response = session.post(url, json=data, cookies=cookies, timeout=timeout)
        elif method == "PUT":
            response = session.put(url, json=data, cookies=cookies, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response
    except requests.exceptions.Timeout:
        print(f"⏰ Request timeout: {method} {endpoint}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🔌 Connection error: {method} {endpoint}")
        return None
    except Exception as e:
        print(f"❌ Request failed: {method} {endpoint} - {str(e)}")
        return None

def main():
    """Main test execution"""
    print(f"🧪 DJ MATCH FRANCE - FULL REGRESSION TEST")
    print(f"Backend URL: {BASE_URL}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    print(f"{'='*80}")
    
    results = TestResults()
    
    # Test 1: Core Health Check
    print(f"\n🏗️ TESTING CORE ENDPOINTS")
    print(f"{'='*60}")
    
    response = make_request("GET", "/health")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/health",
        f"Expected 200, got {response.status_code if response else 'No response'}",
        critical=True
    )
    
    response = make_request("GET", "/event-types")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/event-types",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 2: SIRET Verification
    siret_data = {"siret": "44306184100047"}
    response = make_request("POST", "/verify-siret", siret_data)
    results.assert_test(
        response and response.status_code == 200,
        "POST /api/verify-siret",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 3: Geographic APIs
    response = make_request("GET", "/geo/regions")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/geo/regions",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    response = make_request("GET", "/geo/departments")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/geo/departments",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 4: DJ Search and Postal Code Search
    print(f"\n🔍 TESTING SEARCH BY POSTAL CODE (CRITICAL FIX)")
    print(f"{'='*60}")
    
    test_cases = [
        ("61500", "DJ AS'"),
        ("77950", "Djjoss"),
        ("27000", "Dj GUIOX")
    ]
    
    for postal_code, expected_dj in test_cases:
        response = make_request("GET", f"/djs?code_postal={postal_code}")
        results.assert_test(
            response and response.status_code == 200,
            f"GET /api/djs?code_postal={postal_code}",
            f"Expected 200, got {response.status_code if response else 'No response'}",
            critical=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            djs = data.get("djs", [])
            found_dj = any(expected_dj.lower() in dj.get("nom_de_scene", "").lower() for dj in djs)
            results.assert_test(
                found_dj,
                f"Postal code {postal_code} finds {expected_dj}",
                f"Expected to find {expected_dj} in results, got {len(djs)} DJs"
            )
    
    # Test 5: Authentication System
    print(f"\n🔐 TESTING AUTH SYSTEM")
    print(f"{'='*60}")
    
    # Register new user
    new_email = f"test-new-{datetime.now().strftime('%H%M%S')}@test.com"
    register_data = {"email": new_email, "password": "test123", "name": "Test User"}
    response = make_request("POST", "/auth/register-email", register_data)
    
    results.assert_test(
        response and response.status_code == 200,
        "POST /api/auth/register-email - Register new user",
        f"Expected 200, got {response.status_code if response else 'No response'}",
        critical=True
    )
    
    new_user_cookies = response.cookies if response and response.status_code == 200 else None
    
    # Admin login
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = make_request("POST", "/auth/login-email", login_data)
    
    results.assert_test(
        response and response.status_code == 200,
        "POST /api/auth/login-email - Admin login",
        f"Expected 200, got {response.status_code if response else 'No response'}",
        critical=True
    )
    
    admin_cookies = response.cookies if response and response.status_code == 200 else None
    
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("is_admin") == True,
            "Admin login returns is_admin=true",
            f"Expected True, got {data.get('is_admin')}"
        )
        results.assert_test(
            data.get("is_dj") == True,
            "Admin login returns is_dj=true",
            f"Expected True, got {data.get('is_dj')}"
        )
    
    # Test /api/auth/me
    if admin_cookies:
        response = make_request("GET", "/auth/me", cookies=admin_cookies)
        results.assert_test(
            response and response.status_code == 200,
            "GET /api/auth/me - Admin auth check",
            f"Expected 200, got {response.status_code if response else 'No response'}"
        )
        
        if response and response.status_code == 200:
            data = response.json()
            results.assert_test(
                data.get("is_admin") == True,
                "GET /api/auth/me returns is_admin flag",
                f"Expected True, got {data.get('is_admin')}"
            )
    
    # Test 6: Free Trial System
    print(f"\n🆓 TESTING FREE TRIAL SYSTEM")
    print(f"{'='*60}")
    
    if new_user_cookies:
        dj_data = {
            "nom": "Trial DJ",
            "prenom": "Test",
            "nom_de_scene": "DJ Trial",
            "siret": TEST_SIRET,
            "ville": "Paris",
            "code_postal": "75001",
            "telephone": "0123456789",
            "tarif_indicatif": "800-1200€",
            "types_evenements": ["mariage", "soiree_privee"],
            "zone_intervention": ["Paris"],
            "description": "Trial DJ for testing"
        }
        
        response = make_request("POST", "/dj/register", dj_data, cookies=new_user_cookies)
        results.assert_test(
            response and response.status_code == 200,
            "POST /api/dj/register - Trial DJ registration",
            f"Expected 200, got {response.status_code if response else 'No response'}",
            critical=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            profile = data.get("profile", {})
            results.assert_test(
                profile.get("subscription_status") == "trial",
                "New DJ gets subscription_status='trial'",
                f"Expected 'trial', got {profile.get('subscription_status')}"
            )
            results.assert_test(
                profile.get("is_active") == True,
                "New DJ gets is_active=true",
                f"Expected True, got {profile.get('is_active')}"
            )
        
        # Test trial dashboard
        response = make_request("GET", "/dj/dashboard", cookies=new_user_cookies)
        if response and response.status_code == 200:
            data = response.json()
            results.assert_test(
                data.get("is_trial") == True,
                "Trial DJ dashboard shows is_trial=true",
                f"Expected True, got {data.get('is_trial')}"
            )
            results.assert_test(
                data.get("is_locked") != True,
                "Trial DJ dashboard NOT locked",
                f"Trial DJ should not be locked, got is_locked={data.get('is_locked')}"
            )
    
    # Test 7: Admin Panel Endpoints
    print(f"\n👑 TESTING ADMIN PANEL ENDPOINTS")
    print(f"{'='*60}")
    
    if admin_cookies:
        response = make_request("GET", "/admin/stats", cookies=admin_cookies)
        results.assert_test(
            response and response.status_code == 200,
            "GET /api/admin/stats",
            f"Expected 200, got {response.status_code if response else 'No response'}",
            critical=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            expected_fields = ["total_djs", "active_djs", "trial_djs", "expired_djs", "boosted_djs", "total_contacts", "total_users"]
            for field in expected_fields:
                results.assert_test(
                    field in data,
                    f"Admin stats includes {field}",
                    f"{field} field missing from stats"
                )
        
        response = make_request("GET", "/admin/contact-requests", cookies=admin_cookies)
        results.assert_test(
            response and response.status_code == 200,
            "GET /api/admin/contact-requests",
            f"Expected 200, got {response.status_code if response else 'No response'}",
            critical=True
        )
        
        response = make_request("GET", "/admin/djs", cookies=admin_cookies)
        results.assert_test(
            response and response.status_code == 200,
            "GET /api/admin/djs",
            f"Expected 200, got {response.status_code if response else 'No response'}",
            critical=True
        )
    
    # Test 8: Admin Bypass Features
    print(f"\n🔓 TESTING ADMIN BYPASS FEATURES")
    print(f"{'='*60}")
    
    if admin_cookies:
        response = make_request("GET", "/dj/zone-status", cookies=admin_cookies)
        if response and response.status_code == 200:
            data = response.json()
            results.assert_test(
                data.get("max_departments") == 999,
                "Admin zone-status: max_departments=999",
                f"Expected 999, got {data.get('max_departments')}"
            )
            results.assert_test(
                data.get("extension_price") == 0,
                "Admin zone-status: extension_price=0",
                f"Expected 0, got {data.get('extension_price')}"
            )
        
        response = make_request("GET", "/boost/status", cookies=admin_cookies)
        if response and response.status_code == 200:
            data = response.json()
            results.assert_test(
                data.get("boost_active") == "Permanent",
                "Admin boost status: boost_active='Permanent'",
                f"Expected 'Permanent', got {data.get('boost_active')}"
            )
        
        response = make_request("GET", "/dj/dashboard", cookies=admin_cookies)
        if response and response.status_code == 200:
            data = response.json()
            results.assert_test(
                data.get("is_locked") == False,
                "Admin dashboard: is_locked=false",
                f"Expected False, got {data.get('is_locked')}"
            )
            results.assert_test(
                data.get("is_admin") == True,
                "Admin dashboard: is_admin=true",
                f"Expected True, got {data.get('is_admin')}"
            )
    
    # Test 9: Security - Admin endpoints without auth
    print(f"\n🚫 TESTING SECURITY")
    print(f"{'='*60}")
    
    response = make_request("GET", "/admin/stats")
    results.assert_test(
        response and response.status_code in [401, 403],
        "Admin endpoints return 401/403 without auth",
        f"Expected 401/403, got {response.status_code if response else 'No response'}"
    )
    
    # Test 10: Additional Core Endpoints
    print(f"\n📁 TESTING ADDITIONAL ENDPOINTS")
    print(f"{'='*60}")
    
    # Image upload
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    image_data = {"image": f"data:image/png;base64,{test_image_b64}"}
    response = make_request("POST", "/upload/image", image_data)
    results.assert_test(
        response and response.status_code == 200,
        "POST /api/upload/image",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # DJ list
    response = make_request("GET", "/djs")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/djs (list all)",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Boost plans
    response = make_request("GET", "/boost/plans")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/boost/plans",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Subscription plans
    response = make_request("GET", "/subscription/plans")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/subscription/plans",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Summary
    success = results.summary()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)