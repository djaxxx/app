#!/usr/bin/env python3
"""
Final comprehensive test for DJ Match France Backend API
Tests all critical endpoints including non-admin functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
ADMIN_EMAIL = "adrien.sebert@gmail.com"
ADMIN_PASSWORD = "test123"

class DJMatchFinalTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.admin_authenticated = False
        self.test_results = []

    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })

    def test_admin_login(self):
        """Test admin login and authentication"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login-email", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                is_admin = data.get("is_admin", False)
                is_dj = data.get("is_dj", False)
                
                if is_admin and is_dj:
                    self.admin_authenticated = True
                    self.log_test("Admin Login", True, f"Admin authenticated successfully")
                    return True
                else:
                    self.log_test("Admin Login", False, f"Admin flags incorrect: is_admin={is_admin}, is_dj={is_dj}")
                    return False
            else:
                self.log_test("Admin Login", False, f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
            return False

    def test_boost_plans_updated_pricing(self):
        """Test boost plans with updated pricing (19€, 29€, 39€)"""
        try:
            response = self.session.get(f"{BASE_URL}/boost/plans")
            
            if response.status_code == 200:
                plans = response.json()
                
                expected_prices = {
                    "1_week": 19.00,
                    "2_weeks": 29.00,
                    "1_month": 39.00
                }
                
                if len(plans) == 3:
                    all_correct = True
                    for plan in plans:
                        plan_id = plan.get("id")
                        amount = plan.get("amount")
                        
                        if plan_id not in expected_prices or amount != expected_prices[plan_id]:
                            all_correct = False
                            break
                    
                    if all_correct:
                        self.log_test("Boost Plans Updated Pricing", True, "All 3 plans with correct pricing (19€, 29€, 39€)")
                        return True
                    else:
                        self.log_test("Boost Plans Updated Pricing", False, "Incorrect pricing found")
                        return False
                else:
                    self.log_test("Boost Plans Updated Pricing", False, f"Expected 3 plans, got {len(plans)}")
                    return False
            else:
                self.log_test("Boost Plans Updated Pricing", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Boost Plans Updated Pricing", False, f"Error: {str(e)}")
            return False

    def test_subscription_plans(self):
        """Test subscription plans (8€ monthly, 80€ annual)"""
        try:
            response = self.session.get(f"{BASE_URL}/subscription/plans")
            
            if response.status_code == 200:
                plans = response.json()
                
                expected_prices = {
                    "monthly": 8.00,
                    "annual": 80.00
                }
                
                if len(plans) == 2:
                    all_correct = True
                    for plan in plans:
                        plan_id = plan.get("id")
                        amount = plan.get("amount")
                        
                        if plan_id not in expected_prices or amount != expected_prices[plan_id]:
                            all_correct = False
                            break
                    
                    if all_correct:
                        self.log_test("Subscription Plans", True, "Both plans with correct pricing (8€ monthly, 80€ annual)")
                        return True
                    else:
                        self.log_test("Subscription Plans", False, "Incorrect pricing found")
                        return False
                else:
                    self.log_test("Subscription Plans", False, f"Expected 2 plans, got {len(plans)}")
                    return False
            else:
                self.log_test("Subscription Plans", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Subscription Plans", False, f"Error: {str(e)}")
            return False

    def test_admin_boost_status(self):
        """Test admin boost status shows permanent boost"""
        if not self.admin_authenticated:
            self.log_test("Admin Boost Status", False, "Admin not authenticated")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/boost/status")
            
            if response.status_code == 200:
                data = response.json()
                boost_active = data.get("boost_active")
                is_admin = data.get("is_admin")
                
                if boost_active == "Permanent" and is_admin:
                    self.log_test("Admin Boost Status", True, f"boost_active=Permanent, is_admin=true")
                    return True
                else:
                    self.log_test("Admin Boost Status", False, f"boost_active={boost_active}, is_admin={is_admin}")
                    return False
            else:
                self.log_test("Admin Boost Status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Boost Status", False, f"Error: {str(e)}")
            return False

    def test_admin_boost_checkout_bypass(self):
        """Test admin boost checkout bypass"""
        if not self.admin_authenticated:
            self.log_test("Admin Boost Checkout Bypass", False, "Admin not authenticated")
            return False
        
        try:
            checkout_data = {
                "plan": "1_week",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/boost/create-checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                admin_bypass = data.get("admin_bypass")
                
                if admin_bypass:
                    self.log_test("Admin Boost Checkout Bypass", True, "admin_bypass=true, no checkout_url")
                    return True
                else:
                    self.log_test("Admin Boost Checkout Bypass", False, f"admin_bypass={admin_bypass}")
                    return False
            else:
                self.log_test("Admin Boost Checkout Bypass", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Boost Checkout Bypass", False, f"Error: {str(e)}")
            return False

    def test_admin_zone_status(self):
        """Test admin zone status shows unlimited zones"""
        if not self.admin_authenticated:
            self.log_test("Admin Zone Status", False, "Admin not authenticated")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/zone-status")
            
            if response.status_code == 200:
                data = response.json()
                max_departments = data.get("max_departments")
                extension_price = data.get("extension_price")
                is_admin = data.get("is_admin")
                
                if max_departments == 999 and extension_price == 0 and is_admin:
                    self.log_test("Admin Zone Status", True, f"max_departments=999, extension_price=0, is_admin=true")
                    return True
                else:
                    self.log_test("Admin Zone Status", False, f"max_departments={max_departments}, extension_price={extension_price}, is_admin={is_admin}")
                    return False
            else:
                self.log_test("Admin Zone Status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Zone Status", False, f"Error: {str(e)}")
            return False

    def test_admin_zone_add_department_bypass(self):
        """Test admin zone add department bypass"""
        if not self.admin_authenticated:
            self.log_test("Admin Zone Add Department Bypass", False, "Admin not authenticated")
            return False
        
        try:
            zone_data = {
                "department_code": "13",  # Bouches-du-Rhône
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/dj/zone/add-department", json=zone_data)
            
            if response.status_code == 200:
                data = response.json()
                admin_bypass = data.get("admin_bypass")
                
                if admin_bypass:
                    self.log_test("Admin Zone Add Department Bypass", True, "admin_bypass=true, department added directly")
                    return True
                else:
                    self.log_test("Admin Zone Add Department Bypass", False, f"admin_bypass={admin_bypass}")
                    return False
            else:
                self.log_test("Admin Zone Add Department Bypass", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Zone Add Department Bypass", False, f"Error: {str(e)}")
            return False

    def test_subscription_checkout_creation(self):
        """Test subscription checkout creation for both plans"""
        if not self.admin_authenticated:
            self.log_test("Subscription Checkout Creation", False, "Admin not authenticated")
            return False
        
        try:
            # Test monthly plan
            checkout_data = {
                "plan": "monthly",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/subscription/create-checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                checkout_url = data.get("checkout_url")
                amount = data.get("amount")
                
                if checkout_url and amount == 8.00:
                    # Test annual plan
                    checkout_data["plan"] = "annual"
                    response = self.session.post(f"{BASE_URL}/subscription/create-checkout", json=checkout_data)
                    
                    if response.status_code == 200:
                        data = response.json()
                        checkout_url = data.get("checkout_url")
                        amount = data.get("amount")
                        
                        if checkout_url and amount == 80.00:
                            self.log_test("Subscription Checkout Creation", True, f"Monthly (8€) and Annual (80€) checkout URLs created")
                            return True
                        else:
                            self.log_test("Subscription Checkout Creation", False, f"Annual plan failed: checkout_url={bool(checkout_url)}, amount={amount}")
                            return False
                    else:
                        self.log_test("Subscription Checkout Creation", False, f"Annual plan request failed: {response.status_code}")
                        return False
                else:
                    self.log_test("Subscription Checkout Creation", False, f"Monthly plan failed: checkout_url={bool(checkout_url)}, amount={amount}")
                    return False
            else:
                self.log_test("Subscription Checkout Creation", False, f"Monthly plan request failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Subscription Checkout Creation", False, f"Error: {str(e)}")
            return False

    def test_dj_profile_update(self):
        """Test DJ profile update functionality"""
        if not self.admin_authenticated:
            self.log_test("DJ Profile Update", False, "Admin not authenticated")
            return False
        
        try:
            # Get current profile
            response = self.session.get(f"{BASE_URL}/dj/profile")
            if response.status_code != 200:
                self.log_test("DJ Profile Update", False, f"Failed to get current profile: {response.status_code}")
                return False
            
            current_profile = response.json()
            original_description = current_profile.get("description", "")
            
            # Update description
            new_description = f"Updated description at {datetime.now().isoformat()}"
            update_data = {
                "description": new_description
            }
            
            response = self.session.put(f"{BASE_URL}/dj/profile", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                updated_profile = data.get("profile", {})
                updated_description = updated_profile.get("description", "")
                
                if updated_description == new_description:
                    # Restore original description
                    restore_data = {"description": original_description}
                    self.session.put(f"{BASE_URL}/dj/profile", json=restore_data)
                    
                    self.log_test("DJ Profile Update", True, "Description updated successfully")
                    return True
                else:
                    self.log_test("DJ Profile Update", False, f"Description not updated correctly")
                    return False
            else:
                self.log_test("DJ Profile Update", False, f"Update failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("DJ Profile Update", False, f"Error: {str(e)}")
            return False

    def test_admin_dashboard_never_locked(self):
        """Test admin dashboard is never locked"""
        if not self.admin_authenticated:
            self.log_test("Admin Dashboard Never Locked", False, "Admin not authenticated")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                is_locked = data.get("is_locked")
                is_admin = data.get("is_admin")
                subscription_status = data.get("subscription_status")
                
                if not is_locked and is_admin and subscription_status == "active":
                    self.log_test("Admin Dashboard Never Locked", True, f"is_locked=false, is_admin=true, subscription_status=active")
                    return True
                else:
                    self.log_test("Admin Dashboard Never Locked", False, f"is_locked={is_locked}, is_admin={is_admin}, subscription_status={subscription_status}")
                    return False
            else:
                self.log_test("Admin Dashboard Never Locked", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Dashboard Never Locked", False, f"Error: {str(e)}")
            return False

    def test_user_registration_with_name(self):
        """Test user registration with proper name field"""
        try:
            register_data = {
                "email": f"test-dj-{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "password": "test123",
                "name": "Test DJ User"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/register-email", json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user_id")
                
                if user_id:
                    self.log_test("User Registration", True, f"User created with user_id: {user_id}")
                    return True
                else:
                    self.log_test("User Registration", False, "No user_id returned")
                    return False
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return False

    def test_trial_dj_dashboard(self):
        """Test trial DJ dashboard functionality"""
        try:
            # Get a trial DJ from the list
            response = self.session.get(f"{BASE_URL}/djs")
            if response.status_code != 200:
                self.log_test("Trial DJ Dashboard", False, "Could not get DJ list")
                return False
            
            data = response.json()
            djs = data.get("djs", [])
            trial_dj = None
            
            for dj in djs:
                if dj.get("subscription_status") == "trial":
                    trial_dj = dj
                    break
            
            if not trial_dj:
                self.log_test("Trial DJ Dashboard", False, "No trial DJ found")
                return False
            
            # Check if trial DJ shows correct trial information
            trial_days_remaining = trial_dj.get("trial_days_remaining")
            if trial_days_remaining is not None and 0 <= trial_days_remaining <= 15:
                self.log_test("Trial DJ Dashboard", True, f"Trial DJ found with {trial_days_remaining} days remaining")
                return True
            else:
                self.log_test("Trial DJ Dashboard", False, f"Trial DJ found but trial_days_remaining={trial_days_remaining}")
                return False
                
        except Exception as e:
            self.log_test("Trial DJ Dashboard", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all critical tests"""
        print("🎯 DJ Match France Backend API - Final Critical Tests")
        print("=" * 65)
        
        # Admin authentication
        if not self.test_admin_login():
            print("❌ Admin login failed - aborting admin tests")
            return False
        
        # Test all critical endpoints from review request
        print("\n📋 Testing Critical Endpoints:")
        print("-" * 40)
        
        # 1. Boost Plans & Checkout (UPDATED PRICING)
        self.test_boost_plans_updated_pricing()
        self.test_admin_boost_status()
        self.test_admin_boost_checkout_bypass()
        
        # 2. Subscription Plans & Checkout
        self.test_subscription_plans()
        self.test_subscription_checkout_creation()
        
        # 3. Zone Extension
        self.test_admin_zone_status()
        self.test_admin_zone_add_department_bypass()
        
        # 4. DJ Profile Update
        self.test_dj_profile_update()
        
        # 5. DJ Dashboard (Trial check)
        self.test_admin_dashboard_never_locked()
        self.test_trial_dj_dashboard()
        
        # 6. User Registration
        self.test_user_registration_with_name()
        
        # Summary
        print("\n" + "=" * 65)
        print("🎯 FINAL TEST SUMMARY")
        print("=" * 65)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        # Group results by category
        critical_tests = [
            "Boost Plans Updated Pricing",
            "Subscription Plans", 
            "Admin Boost Status",
            "Admin Boost Checkout Bypass",
            "Admin Zone Status",
            "Admin Zone Add Department Bypass",
            "Subscription Checkout Creation",
            "DJ Profile Update",
            "Admin Dashboard Never Locked"
        ]
        
        print("🔥 CRITICAL TESTS:")
        for result in self.test_results:
            if result["test"] in critical_tests:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}")
                if not result["success"] and result["details"]:
                    print(f"   ❌ {result['details']}")
        
        print("\n📋 ADDITIONAL TESTS:")
        for result in self.test_results:
            if result["test"] not in critical_tests:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}")
                if not result["success"] and result["details"]:
                    print(f"   ❌ {result['details']}")
        
        critical_passed = sum(1 for result in self.test_results if result["success"] and result["test"] in critical_tests)
        critical_total = len(critical_tests)
        
        print(f"\n📊 CRITICAL RESULTS: {critical_passed}/{critical_total} tests passed ({critical_passed/critical_total*100:.1f}%)")
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if critical_passed == critical_total:
            print("🎉 ALL CRITICAL TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {critical_total - critical_passed} critical tests failed")
            return False

def main():
    """Main test runner"""
    tester = DJMatchFinalTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()