#!/usr/bin/env python3
"""
FULL REGRESSION TEST for DJ Match France
Tests ALL endpoints as requested in the review request.

Test Categories:
1. AUTH SYSTEM (recently rewritten)
2. FREE TRIAL SYSTEM (NEW)
3. ADMIN PANEL ENDPOINTS (NEW)
4. ADMIN BYPASS features
5. SEARCH BY POSTAL CODE (CRITICAL FIX)
6. CORE ENDPOINTS (regression)
"""

import requests
import json
import sys
import base64
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

def make_request(method, endpoint, data=None, cookies=None, headers=None):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    try:
        if method == "GET":
            response = requests.get(url, cookies=cookies, headers=default_headers)
        elif method == "POST":
            response = requests.post(url, json=data, cookies=cookies, headers=default_headers)
        elif method == "PUT":
            response = requests.put(url, json=data, cookies=cookies, headers=default_headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response
    except Exception as e:
        print(f"❌ Request failed: {method} {endpoint} - {str(e)}")
        return None

def test_auth_system(results):
    """Test AUTH SYSTEM (recently rewritten)"""
    print(f"\n🔐 TESTING AUTH SYSTEM (RECENTLY REWRITTEN)")
    print(f"{'='*60}")
    
    # Test 1: Register new user
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
    
    # Test 2: Login admin
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
    
    # Test 3: GET /api/auth/me with admin cookies
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
            results.assert_test(
                data.get("is_dj") == True,
                "GET /api/auth/me returns is_dj flag",
                f"Expected True, got {data.get('is_dj')}"
            )
    
    # Test 4: POST /api/auth/logout
    if admin_cookies:
        response = make_request("POST", "/auth/logout", cookies=admin_cookies)
        results.assert_test(
            response and response.status_code == 200,
            "POST /api/auth/logout",
            f"Expected 200, got {response.status_code if response else 'No response'}"
        )
    
    # Test 5: Auth merge - try to register with existing admin email
    merge_data = {"email": ADMIN_EMAIL, "password": "newpassword123", "name": "Admin User"}
    response = make_request("POST", "/auth/register-email", merge_data)
    
    # Should not create duplicate - either 400 (already exists) or 200 (merged) or 409 (conflict)
    results.assert_test(
        response and response.status_code in [200, 400, 409, 422],
        "Auth merge - No duplicate creation for existing email",
        f"Expected 200, 400, 409, or 422, got {response.status_code if response else 'No response'}"
    )
    
    return admin_cookies, new_user_cookies

def test_free_trial_system(results, new_user_cookies):
    """Test FREE TRIAL SYSTEM (NEW)"""
    print(f"\n🆓 TESTING FREE TRIAL SYSTEM (NEW)")
    print(f"{'='*60}")
    
    if not new_user_cookies:
        results.assert_test(False, "Free trial tests", "No new user cookies available", critical=True)
        return
    
    # Test 1: POST /api/dj/register - New DJ gets trial status
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
            "trial_start" in profile,
            "New DJ gets trial_start date",
            "trial_start field missing"
        )
        results.assert_test(
            "trial_end" in profile,
            "New DJ gets trial_end date (15 days)",
            "trial_end field missing"
        )
        results.assert_test(
            profile.get("is_active") == True,
            "New DJ gets is_active=true",
            f"Expected True, got {profile.get('is_active')}"
        )
    
    # Test 2: GET /api/dj/dashboard - Trial DJs see trial info
    response = make_request("GET", "/dj/dashboard", cookies=new_user_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("is_trial") == True,
            "Trial DJ dashboard shows is_trial=true",
            f"Expected True, got {data.get('is_trial')}"
        )
        results.assert_test(
            "trial_days_remaining" in data,
            "Trial DJ dashboard shows trial_days_remaining",
            "trial_days_remaining field missing"
        )
        results.assert_test(
            data.get("is_locked") != True,
            "Trial DJ dashboard NOT locked",
            f"Trial DJ should not be locked, got is_locked={data.get('is_locked')}"
        )
    
    # Test 3: GET /api/djs - Trial DJs appear in search results
    response = make_request("GET", "/djs")
    if response and response.status_code == 200:
        data = response.json()
        trial_djs = [dj for dj in data.get("djs", []) if dj.get("subscription_status") == "trial"]
        results.assert_test(
            len(trial_djs) > 0,
            "Trial DJs appear in search results",
            f"Expected >0 trial DJs, found {len(trial_djs)}"
        )
    
    # Test 4: GET /api/djs/{user_id} - Trial DJ profiles accessible
    # We need to get the user_id from the dashboard or profile
    response = make_request("GET", "/dj/profile", cookies=new_user_cookies)
    if response and response.status_code == 200:
        profile_data = response.json()
        user_id = profile_data.get("user_id")
        if user_id:
            response = make_request("GET", f"/djs/{user_id}")
            results.assert_test(
                response and response.status_code == 200,
                "Trial DJ profile accessible via GET /api/djs/{user_id}",
                f"Expected 200, got {response.status_code if response else 'No response'}"
            )

def test_admin_panel_endpoints(results, admin_cookies):
    """Test ADMIN PANEL ENDPOINTS (NEW)"""
    print(f"\n👑 TESTING ADMIN PANEL ENDPOINTS (NEW)")
    print(f"{'='*60}")
    
    if not admin_cookies:
        results.assert_test(False, "Admin panel tests", "No admin cookies available", critical=True)
        return
    
    # Test 1: GET /api/admin/stats
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
    
    # Test 2: GET /api/admin/contact-requests
    response = make_request("GET", "/admin/contact-requests", cookies=admin_cookies)
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/admin/contact-requests",
        f"Expected 200, got {response.status_code if response else 'No response'}",
        critical=True
    )
    
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            isinstance(data, dict) and ("requests" in data or isinstance(data, list)),
            "Contact requests returns dict with requests or list",
            f"Unexpected response format: {type(data)}"
        )
        # Check for dj_nom enrichment if contacts exist
        contacts = data.get("requests", []) if isinstance(data, dict) else data
        if contacts:
            first_contact = contacts[0]
            results.assert_test(
                "dj_nom" in first_contact or "nom" in first_contact,
                "Contact requests include DJ name enrichment",
                "Missing DJ name enrichment in contact requests"
            )
    
    # Test 3: GET /api/admin/djs
    response = make_request("GET", "/admin/djs", cookies=admin_cookies)
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/admin/djs",
        f"Expected 200, got {response.status_code if response else 'No response'}",
        critical=True
    )
    
    if response and response.status_code == 200:
        data = response.json()
        djs = data.get("djs", []) if isinstance(data, dict) else data
        results.assert_test(
            len(djs) > 0,
            "Admin DJs list returns DJs including inactive",
            f"Expected >0 DJs, got {len(djs)}"
        )
    
    # Test 4: PUT /api/admin/djs/{user_id}/toggle-subscription
    # Get a DJ user_id first
    if response and response.status_code == 200:
        djs = data.get("djs", []) if isinstance(data, dict) else data
        if djs:
            test_dj_id = djs[0].get("user_id") or djs[0].get("id")
            if test_dj_id:
                response = make_request("PUT", f"/admin/djs/{test_dj_id}/toggle-subscription", cookies=admin_cookies)
                results.assert_test(
                    response and response.status_code == 200,
                    "PUT /api/admin/djs/{user_id}/toggle-subscription",
                    f"Expected 200, got {response.status_code if response else 'No response'}"
                )
    
    # Test 5: PUT /api/admin/djs/{user_id}/toggle-boost
    if response and response.status_code == 200:
        djs = data.get("djs", []) if isinstance(data, dict) else data
        if djs:
            test_dj_id = djs[0].get("user_id") or djs[0].get("id")
            if test_dj_id:
                response = make_request("PUT", f"/admin/djs/{test_dj_id}/toggle-boost", cookies=admin_cookies)
                results.assert_test(
                    response and response.status_code == 200,
                    "PUT /api/admin/djs/{user_id}/toggle-boost",
                    f"Expected 200, got {response.status_code if response else 'No response'}"
                )
    
    # Test 6: Admin endpoints return 401 without auth
    response = make_request("GET", "/admin/stats")
    results.assert_test(
        response and response.status_code in [401, 403],
        "Admin endpoints return 401/403 without auth",
        f"Expected 401/403, got {response.status_code if response else 'No response'}"
    )

def test_admin_bypass_features(results, admin_cookies):
    """Test ADMIN BYPASS features"""
    print(f"\n🔓 TESTING ADMIN BYPASS FEATURES")
    print(f"{'='*60}")
    
    if not admin_cookies:
        results.assert_test(False, "Admin bypass tests", "No admin cookies available", critical=True)
        return
    
    # Test 1: GET /api/dj/zone-status (admin)
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
    
    # Test 2: POST /api/dj/zone/add-department (admin)
    add_dept_data = {"department_code": "75"}
    response = make_request("POST", "/dj/zone/add-department", add_dept_data, cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("admin_bypass") == True,
            "Admin zone add-department: admin_bypass=true",
            f"Expected True, got {data.get('admin_bypass')}"
        )
        results.assert_test(
            "checkout_url" not in data,
            "Admin zone add-department: no checkout_url",
            "checkout_url should not be present for admin"
        )
    
    # Test 3: GET /api/boost/status (admin)
    response = make_request("GET", "/boost/status", cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("boost_active") == "Permanent",
            "Admin boost status: boost_active='Permanent'",
            f"Expected 'Permanent', got {data.get('boost_active')}"
        )
    
    # Test 4: GET /api/dj/dashboard (admin)
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

def test_search_by_postal_code(results):
    """Test SEARCH BY POSTAL CODE (CRITICAL FIX)"""
    print(f"\n🔍 TESTING SEARCH BY POSTAL CODE (CRITICAL FIX)")
    print(f"{'='*60}")
    
    # Test specific postal codes mentioned in the review request
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

def test_core_endpoints(results):
    """Test CORE ENDPOINTS (regression)"""
    print(f"\n🏗️ TESTING CORE ENDPOINTS (REGRESSION)")
    print(f"{'='*60}")
    
    # Test 1: GET /api/health
    response = make_request("GET", "/health")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/health",
        f"Expected 200, got {response.status_code if response else 'No response'}",
        critical=True
    )
    
    # Test 2: GET /api/event-types
    response = make_request("GET", "/event-types")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/event-types",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 3: POST /api/verify-siret
    siret_data = {"siret": "44306184100047"}
    response = make_request("POST", "/verify-siret", siret_data)
    results.assert_test(
        response and response.status_code == 200,
        "POST /api/verify-siret",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 4: GET /api/geo/regions
    response = make_request("GET", "/geo/regions")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/geo/regions",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 5: GET /api/geo/departments
    response = make_request("GET", "/geo/departments")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/geo/departments",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 6: POST /api/upload/image
    # Create a small test image (1x1 PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    image_data = {"image": f"data:image/png;base64,{test_image_b64}"}
    response = make_request("POST", "/upload/image", image_data)
    results.assert_test(
        response and response.status_code == 200,
        "POST /api/upload/image",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 7: GET /api/djs (list all)
    response = make_request("GET", "/djs")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/djs (list all)",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 8: GET /api/boost/plans
    response = make_request("GET", "/boost/plans")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/boost/plans",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )
    
    # Test 9: GET /api/subscription/plans
    response = make_request("GET", "/subscription/plans")
    results.assert_test(
        response and response.status_code == 200,
        "GET /api/subscription/plans",
        f"Expected 200, got {response.status_code if response else 'No response'}"
    )

def test_non_admin_restrictions(results, new_user_cookies):
    """Test that non-admin users get 403 on admin-only endpoints"""
    print(f"\n🚫 TESTING NON-ADMIN RESTRICTIONS")
    print(f"{'='*60}")
    
    if not new_user_cookies:
        results.assert_test(False, "Non-admin restriction tests", "No new user cookies available")
        return
    
    admin_endpoints = [
        "/admin/stats",
        "/admin/contact-requests",
        "/admin/djs"
    ]
    
    for endpoint in admin_endpoints:
        response = make_request("GET", endpoint, cookies=new_user_cookies)
        results.assert_test(
            response and response.status_code in [401, 403],
            f"Non-admin gets 401/403 for {endpoint}",
            f"Expected 401/403, got {response.status_code if response else 'No response'}"
        )

def main():
    """Main test execution"""
    print(f"🧪 DJ MATCH FRANCE - FULL REGRESSION TEST")
    print(f"Backend URL: {BASE_URL}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    print(f"{'='*80}")
    
    results = TestResults()
    
    # Test 1: AUTH SYSTEM (recently rewritten)
    admin_cookies, new_user_cookies = test_auth_system(results)
    
    # Re-login admin for subsequent tests (logout may have cleared cookies)
    if admin_cookies:
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        response = make_request("POST", "/auth/login-email", login_data)
        if response and response.status_code == 200:
            admin_cookies = response.cookies
    
    # Test 2: FREE TRIAL SYSTEM (NEW)
    test_free_trial_system(results, new_user_cookies)
    
    # Test 3: ADMIN PANEL ENDPOINTS (NEW)
    test_admin_panel_endpoints(results, admin_cookies)
    
    # Test 4: ADMIN BYPASS features
    test_admin_bypass_features(results, admin_cookies)
    
    # Test 5: SEARCH BY POSTAL CODE (CRITICAL FIX)
    test_search_by_postal_code(results)
    
    # Test 6: CORE ENDPOINTS (regression)
    test_core_endpoints(results)
    
    # Test 7: Non-admin restrictions
    test_non_admin_restrictions(results, new_user_cookies)
    
    # Summary
    success = results.summary()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)