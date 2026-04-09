#!/usr/bin/env python3
"""
Backend Testing for DJ Match France Admin Privileges
Tests 3 new admin features:
1. Admin Unlimited Zones Bypass
2. Admin Permanent Boost Bypass  
3. Admin Dashboard Never Locked
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
ADMIN_EMAIL = "adrien.sebert@gmail.com"
ADMIN_PASSWORD = "test123"
ADMIN_PASSWORD_ALT = "admin123"
TEST_SIRET = "44306184100047"  # Google France

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def assert_test(self, condition, test_name, error_msg=""):
        if condition:
            print(f"✅ {test_name}")
            self.passed += 1
        else:
            print(f"❌ {test_name}: {error_msg}")
            self.failed += 1
            self.errors.append(f"{test_name}: {error_msg}")
            
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
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

def login_admin():
    """Login as admin and return session cookies"""
    print(f"\n🔐 Attempting admin login: {ADMIN_EMAIL}")
    
    # Try login first
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = make_request("POST", "/auth/login-email", login_data)
    
    if response and response.status_code == 200:
        print(f"✅ Admin login successful")
        return response.cookies
    
    print(f"⚠️ Login failed, trying registration with alternate password...")
    
    # Try registration with alternate password
    register_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD_ALT}
    response = make_request("POST", "/auth/register-email", register_data)
    
    if response and response.status_code == 200:
        print(f"✅ Admin registration successful")
        return response.cookies
    
    print(f"❌ Both login and registration failed")
    if response:
        print(f"Status: {response.status_code}, Response: {response.text}")
    return None

def create_dj_profile_if_needed(cookies):
    """Create DJ profile for admin if it doesn't exist"""
    print(f"\n👤 Checking/Creating DJ profile for admin...")
    
    # Check if DJ profile exists
    response = make_request("GET", "/dj/profile", cookies=cookies)
    if response and response.status_code == 200:
        print(f"✅ Admin DJ profile already exists")
        return True
    
    # Create DJ profile
    dj_data = {
        "nom": "Admin DJ",
        "prenom": "Test",
        "nom_de_scene": "DJ Admin",
        "siret": TEST_SIRET,
        "ville": "Paris",
        "code_postal": "75001",
        "telephone": "0123456789",
        "tarif_indicatif": "800-1200€",
        "types_evenements": ["mariage", "soiree_privee"],
        "zone_intervention": ["Paris", "région parisienne"],
        "description": "DJ Admin pour tests"
    }
    
    response = make_request("POST", "/dj/register", dj_data, cookies=cookies)
    if response and response.status_code == 200:
        print(f"✅ Admin DJ profile created successfully")
        return True
    else:
        print(f"❌ Failed to create DJ profile")
        if response:
            print(f"Status: {response.status_code}, Response: {response.text}")
        return False

def create_regular_user():
    """Create a regular (non-admin) user for comparison tests"""
    print(f"\n👤 Creating regular user for comparison...")
    
    regular_email = f"test-user-{datetime.now().strftime('%H%M%S')}@example.com"
    register_data = {"email": regular_email, "password": "test123"}
    
    response = make_request("POST", "/auth/register-email", register_data)
    if response and response.status_code == 200:
        print(f"✅ Regular user created: {regular_email}")
        
        # Create DJ profile for regular user
        dj_data = {
            "nom": "Regular DJ",
            "prenom": "Test",
            "nom_de_scene": "DJ Regular",
            "siret": TEST_SIRET,
            "ville": "Lyon",
            "code_postal": "69001",
            "telephone": "0123456789",
            "tarif_indicatif": "800-1000€",
            "types_evenements": ["mariage"],
            "zone_intervention": ["Lyon"],
            "description": "Regular DJ for tests"
        }
        
        dj_response = make_request("POST", "/dj/register", dj_data, cookies=response.cookies)
        if dj_response and dj_response.status_code == 200:
            print(f"✅ Regular DJ profile created")
            return response.cookies, regular_email
        else:
            print(f"❌ Failed to create regular DJ profile")
            return response.cookies, regular_email
    else:
        print(f"❌ Failed to create regular user")
        return None, None

def test_admin_unlimited_zones(admin_cookies, results):
    """Test Admin Unlimited Zones Bypass feature"""
    print(f"\n🌍 TESTING ADMIN UNLIMITED ZONES BYPASS")
    print(f"{'='*50}")
    
    # Test 1: GET /api/dj/zone-status should return admin privileges
    response = make_request("GET", "/dj/zone-status", cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("max_departments") == 999,
            "Zone status shows max_departments=999 for admin",
            f"Expected 999, got {data.get('max_departments')}"
        )
        results.assert_test(
            data.get("extension_price") == 0,
            "Zone status shows extension_price=0 for admin",
            f"Expected 0, got {data.get('extension_price')}"
        )
        results.assert_test(
            data.get("is_admin") == True,
            "Zone status shows is_admin=true",
            f"Expected True, got {data.get('is_admin')}"
        )
    else:
        results.assert_test(False, "GET /api/dj/zone-status", f"Request failed: {response.status_code if response else 'No response'}")
    
    # Test 2: POST /api/dj/zone/add-department should bypass Stripe for admin
    add_dept_data = {"department_code": "75"}  # Paris
    response = make_request("POST", "/dj/zone/add-department", add_dept_data, cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("admin_bypass") == True,
            "Add department returns admin_bypass=true",
            f"Expected True, got {data.get('admin_bypass')}"
        )
        results.assert_test(
            "checkout_url" not in data,
            "Add department has no checkout_url for admin",
            "checkout_url should not be present for admin"
        )
    else:
        results.assert_test(False, "POST /api/dj/zone/add-department (75)", f"Request failed: {response.status_code if response else 'No response'}")
    
    # Test 3: Add another department
    add_dept_data = {"department_code": "13"}  # Bouches-du-Rhône
    response = make_request("POST", "/dj/zone/add-department", add_dept_data, cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("admin_bypass") == True,
            "Add second department also bypasses Stripe",
            f"Expected admin_bypass=True, got {data.get('admin_bypass')}"
        )
    else:
        results.assert_test(False, "POST /api/dj/zone/add-department (13)", f"Request failed: {response.status_code if response else 'No response'}")
    
    # Test 4: POST /api/dj/zone/add-all-departments (admin only)
    response = make_request("POST", "/dj/zone/add-all-departments", {}, cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("total", 0) > 90,
            "Add all departments adds 90+ departments",
            f"Expected >90 departments, got {data.get('total')}"
        )
    else:
        results.assert_test(False, "POST /api/dj/zone/add-all-departments", f"Request failed: {response.status_code if response else 'No response'}")
    
    # Test 5: GET /api/dj/available-departments should return all departments
    response = make_request("GET", "/dj/available-departments", cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            len(data) > 90,
            "Available departments returns 90+ departments",
            f"Expected >90 departments, got {len(data)}"
        )
    else:
        results.assert_test(False, "GET /api/dj/available-departments", f"Request failed: {response.status_code if response else 'No response'}")

def test_admin_permanent_boost(admin_cookies, results):
    """Test Admin Permanent Boost Bypass feature"""
    print(f"\n⚡ TESTING ADMIN PERMANENT BOOST BYPASS")
    print(f"{'='*50}")
    
    # Test 1: GET /api/boost/status should return permanent boost for admin
    response = make_request("GET", "/boost/status", cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("boost_active") == "Permanent",
            "Boost status shows boost_active='Permanent' for admin",
            f"Expected 'Permanent', got {data.get('boost_active')}"
        )
        results.assert_test(
            data.get("is_admin") == True,
            "Boost status shows is_admin=true",
            f"Expected True, got {data.get('is_admin')}"
        )
        results.assert_test(
            data.get("days_remaining") == 99999,
            "Boost status shows days_remaining=99999",
            f"Expected 99999, got {data.get('days_remaining')}"
        )
    else:
        results.assert_test(False, "GET /api/boost/status", f"Request failed: {response.status_code if response else 'No response'}")
    
    # Test 2: POST /api/boost/create-checkout should bypass Stripe for admin
    checkout_data = {"plan": "1_week", "origin_url": "https://test.com"}
    response = make_request("POST", "/boost/create-checkout", checkout_data, cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("admin_bypass") == True,
            "Boost checkout returns admin_bypass=true",
            f"Expected True, got {data.get('admin_bypass')}"
        )
        results.assert_test(
            "checkout_url" not in data,
            "Boost checkout has no checkout_url for admin",
            "checkout_url should not be present for admin"
        )
    else:
        results.assert_test(False, "POST /api/boost/create-checkout", f"Request failed: {response.status_code if response else 'No response'}")
    
    # Test 3: POST /api/boost/activate-admin should work for admin
    response = make_request("POST", "/boost/activate-admin", {}, cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("boost_active") == "Permanent",
            "Admin boost activation returns permanent boost",
            f"Expected 'Permanent', got {data.get('boost_active')}"
        )
    else:
        results.assert_test(False, "POST /api/boost/activate-admin", f"Request failed: {response.status_code if response else 'No response'}")

def test_admin_dashboard_never_locked(admin_cookies, results):
    """Test Admin Dashboard Never Locked feature"""
    print(f"\n🔓 TESTING ADMIN DASHBOARD NEVER LOCKED")
    print(f"{'='*50}")
    
    # Test 1: GET /api/dj/dashboard should never be locked for admin
    response = make_request("GET", "/dj/dashboard", cookies=admin_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            data.get("is_locked") == False,
            "Dashboard shows is_locked=false for admin",
            f"Expected False, got {data.get('is_locked')}"
        )
        results.assert_test(
            data.get("is_admin") == True,
            "Dashboard shows is_admin=true",
            f"Expected True, got {data.get('is_admin')}"
        )
        results.assert_test(
            data.get("subscription_status") == "active",
            "Dashboard shows subscription_status='active' for admin",
            f"Expected 'active', got {data.get('subscription_status')}"
        )
    else:
        results.assert_test(False, "GET /api/dj/dashboard", f"Request failed: {response.status_code if response else 'No response'}")

def test_regular_user_normal_flow(regular_cookies, results):
    """Test that regular users still get normal Stripe checkout flow"""
    print(f"\n👤 TESTING REGULAR USER NORMAL FLOW")
    print(f"{'='*50}")
    
    if not regular_cookies:
        results.assert_test(False, "Regular user tests", "No regular user cookies available")
        return
    
    # Test 1: Regular user zone addition should return checkout_url
    add_dept_data = {"department_code": "75", "origin_url": "https://test.com"}
    response = make_request("POST", "/dj/zone/add-department", add_dept_data, cookies=regular_cookies)
    if response:
        if response.status_code == 200:
            data = response.json()
            results.assert_test(
                "checkout_url" in data,
                "Regular user gets checkout_url for zone addition",
                "checkout_url should be present for regular users"
            )
            results.assert_test(
                data.get("admin_bypass") != True,
                "Regular user does not get admin_bypass",
                f"admin_bypass should not be True, got {data.get('admin_bypass')}"
            )
        else:
            # Could be 400 if max departments reached, that's also valid
            results.assert_test(
                response.status_code in [200, 400],
                "Regular user zone addition returns valid response",
                f"Expected 200 or 400, got {response.status_code}"
            )
    else:
        results.assert_test(False, "Regular user zone addition", "Request failed")
    
    # Test 2: Regular user boost checkout should return checkout_url
    checkout_data = {"plan": "1_week", "origin_url": "https://test.com"}
    response = make_request("POST", "/boost/create-checkout", checkout_data, cookies=regular_cookies)
    if response and response.status_code == 200:
        data = response.json()
        results.assert_test(
            "checkout_url" in data,
            "Regular user gets checkout_url for boost",
            "checkout_url should be present for regular users"
        )
        results.assert_test(
            data.get("admin_bypass") != True,
            "Regular user does not get boost admin_bypass",
            f"admin_bypass should not be True, got {data.get('admin_bypass')}"
        )
    else:
        results.assert_test(False, "Regular user boost checkout", f"Request failed: {response.status_code if response else 'No response'}")
    
    # Test 3: Regular user cannot access admin boost activation
    response = make_request("POST", "/boost/activate-admin", {}, cookies=regular_cookies)
    results.assert_test(
        response and response.status_code == 403,
        "Regular user gets 403 for admin boost activation",
        f"Expected 403, got {response.status_code if response else 'No response'}"
    )
    
    # Test 4: Regular user cannot access add-all-departments
    response = make_request("POST", "/dj/zone/add-all-departments", {}, cookies=regular_cookies)
    results.assert_test(
        response and response.status_code == 403,
        "Regular user gets 403 for add-all-departments",
        f"Expected 403, got {response.status_code if response else 'No response'}"
    )

def main():
    """Main test execution"""
    print(f"🧪 DJ MATCH FRANCE - ADMIN PRIVILEGES TESTING")
    print(f"Backend URL: {BASE_URL}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    print(f"{'='*60}")
    
    results = TestResults()
    
    # Step 1: Login as admin
    admin_cookies = login_admin()
    if not admin_cookies:
        print(f"❌ CRITICAL: Cannot login as admin. Aborting tests.")
        return False
    
    # Step 2: Create DJ profile if needed
    if not create_dj_profile_if_needed(admin_cookies):
        print(f"❌ CRITICAL: Cannot create admin DJ profile. Aborting tests.")
        return False
    
    # Step 3: Create regular user for comparison
    regular_cookies, regular_email = create_regular_user()
    
    # Step 4: Test admin features
    test_admin_unlimited_zones(admin_cookies, results)
    test_admin_permanent_boost(admin_cookies, results)
    test_admin_dashboard_never_locked(admin_cookies, results)
    
    # Step 5: Test regular user flow
    test_regular_user_normal_flow(regular_cookies, results)
    
    # Step 6: Summary
    success = results.summary()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)