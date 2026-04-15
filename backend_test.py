#!/usr/bin/env python3
"""
DJ Match France Backend API Testing
Tests critical endpoints with updated pricing and admin features
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
ADMIN_EMAIL = "adrien.sebert@gmail.com"
ADMIN_PASSWORD = "test123"

class DJMatchTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.admin_authenticated = False
        self.test_dj_user_id = None
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

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            self.log_test("Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False

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
                    self.log_test("Admin Login", True, f"Admin authenticated successfully, is_admin={is_admin}, is_dj={is_dj}")
                    return True
                else:
                    self.log_test("Admin Login", False, f"Login successful but admin flags incorrect: is_admin={is_admin}, is_dj={is_dj}")
                    return False
            else:
                self.log_test("Admin Login", False, f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
            return False

    def test_boost_plans(self):
        """Test boost plans endpoint - should return updated pricing"""
        try:
            response = self.session.get(f"{BASE_URL}/boost/plans")
            
            if response.status_code == 200:
                plans = response.json()
                
                # Check if we have 3 plans
                if len(plans) != 3:
                    self.log_test("Boost Plans", False, f"Expected 3 plans, got {len(plans)}")
                    return False
                
                # Check pricing
                expected_prices = {
                    "1_week": 19.00,
                    "2_weeks": 29.00,
                    "1_month": 39.00
                }
                
                for plan in plans:
                    plan_id = plan.get("id")
                    amount = plan.get("amount")
                    
                    if plan_id not in expected_prices:
                        self.log_test("Boost Plans", False, f"Unexpected plan ID: {plan_id}")
                        return False
                    
                    if amount != expected_prices[plan_id]:
                        self.log_test("Boost Plans", False, f"Wrong price for {plan_id}: expected {expected_prices[plan_id]}€, got {amount}€")
                        return False
                
                self.log_test("Boost Plans", True, "All 3 plans with correct pricing (19€, 29€, 39€)")
                return True
            else:
                self.log_test("Boost Plans", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Boost Plans", False, f"Error: {str(e)}")
            return False

    def test_subscription_plans(self):
        """Test subscription plans endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/subscription/plans")
            
            if response.status_code == 200:
                plans = response.json()
                
                # Check if we have 2 plans
                if len(plans) != 2:
                    self.log_test("Subscription Plans", False, f"Expected 2 plans, got {len(plans)}")
                    return False
                
                # Check pricing
                expected_prices = {
                    "monthly": 8.00,
                    "annual": 80.00
                }
                
                for plan in plans:
                    plan_id = plan.get("id")
                    amount = plan.get("amount")
                    
                    if plan_id not in expected_prices:
                        self.log_test("Subscription Plans", False, f"Unexpected plan ID: {plan_id}")
                        return False
                    
                    if amount != expected_prices[plan_id]:
                        self.log_test("Subscription Plans", False, f"Wrong price for {plan_id}: expected {expected_prices[plan_id]}€, got {amount}€")
                        return False
                
                self.log_test("Subscription Plans", True, "Both plans with correct pricing (8€ monthly, 80€ annual)")
                return True
            else:
                self.log_test("Subscription Plans", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Subscription Plans", False, f"Error: {str(e)}")
            return False

    def test_admin_boost_status(self):
        """Test admin boost status - should show permanent boost"""
        if not self.admin_authenticated:
            self.log_test("Admin Boost Status", False, "Admin not authenticated")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/boost/status")
            
            if response.status_code == 200:
                data = response.json()
                boost_active = data.get("boost_active")
                is_admin = data.get("is_admin")
                days_remaining = data.get("days_remaining")
                
                if boost_active == "Permanent" and is_admin and days_remaining == 99999:
                    self.log_test("Admin Boost Status", True, f"boost_active=Permanent, is_admin=true, days_remaining=99999")
                    return True
                else:
                    self.log_test("Admin Boost Status", False, f"boost_active={boost_active}, is_admin={is_admin}, days_remaining={days_remaining}")
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
                boost_active = data.get("boost_active")
                
                if admin_bypass and boost_active == "Permanent":
                    self.log_test("Admin Boost Checkout Bypass", True, "admin_bypass=true, no checkout_url")
                    return True
                else:
                    self.log_test("Admin Boost Checkout Bypass", False, f"admin_bypass={admin_bypass}, boost_active={boost_active}")
                    return False
            else:
                self.log_test("Admin Boost Checkout Bypass", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Boost Checkout Bypass", False, f"Error: {str(e)}")
            return False

    def test_admin_zone_status(self):
        """Test admin zone status - should show unlimited zones"""
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
                department_code = data.get("department_code")
                
                if admin_bypass and department_code == "13":
                    self.log_test("Admin Zone Add Department Bypass", True, "admin_bypass=true, department added directly")
                    return True
                else:
                    self.log_test("Admin Zone Add Department Bypass", False, f"admin_bypass={admin_bypass}, department_code={department_code}")
                    return False
            else:
                self.log_test("Admin Zone Add Department Bypass", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Zone Add Department Bypass", False, f"Error: {str(e)}")
            return False

    def test_subscription_checkout_creation(self):
        """Test subscription checkout creation"""
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
                    self.log_test("Subscription Checkout Creation (Monthly)", True, f"checkout_url present, amount=8€")
                    
                    # Test annual plan
                    checkout_data["plan"] = "annual"
                    response = self.session.post(f"{BASE_URL}/subscription/create-checkout", json=checkout_data)
                    
                    if response.status_code == 200:
                        data = response.json()
                        checkout_url = data.get("checkout_url")
                        amount = data.get("amount")
                        
                        if checkout_url and amount == 80.00:
                            self.log_test("Subscription Checkout Creation (Annual)", True, f"checkout_url present, amount=80€")
                            return True
                        else:
                            self.log_test("Subscription Checkout Creation (Annual)", False, f"checkout_url={bool(checkout_url)}, amount={amount}")
                            return False
                    else:
                        self.log_test("Subscription Checkout Creation (Annual)", False, f"Status: {response.status_code}")
                        return False
                else:
                    self.log_test("Subscription Checkout Creation (Monthly)", False, f"checkout_url={bool(checkout_url)}, amount={amount}")
                    return False
            else:
                self.log_test("Subscription Checkout Creation (Monthly)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Subscription Checkout Creation", False, f"Error: {str(e)}")
            return False

    def test_dj_profile_update(self):
        """Test DJ profile update"""
        if not self.admin_authenticated:
            self.log_test("DJ Profile Update", False, "Admin not authenticated")
            return False
        
        try:
            # First get current profile
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
                    self.log_test("DJ Profile Update", True, "Description updated successfully")
                    
                    # Restore original description
                    restore_data = {"description": original_description}
                    self.session.put(f"{BASE_URL}/dj/profile", json=restore_data)
                    return True
                else:
                    self.log_test("DJ Profile Update", False, f"Description not updated correctly")
                    return False
            else:
                self.log_test("DJ Profile Update", False, f"Status: {response.status_code}")
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

    def create_test_dj_user(self):
        """Create a test non-admin DJ user for testing"""
        try:
            # Register a new user
            register_data = {
                "email": f"test-dj-{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "password": "test123"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/register-email", json=register_data)
            
            if response.status_code == 200:
                # Create DJ profile
                dj_data = {
                    "nom": "Test DJ",
                    "prenom": "User",
                    "email": register_data["email"],
                    "telephone": "0123456789",
                    "ville": "Paris",
                    "code_postal": "75001",
                    "siret": "44306184100047",  # Google France SIRET
                    "tarif_indicatif": "500-1000€",
                    "types_evenements": ["mariage"],
                    "description": "Test DJ for automated testing"
                }
                
                response = self.session.post(f"{BASE_URL}/dj/register", json=dj_data)
                
                if response.status_code == 200:
                    data = response.json()
                    profile = data.get("profile", {})
                    self.test_dj_user_id = profile.get("user_id")
                    self.log_test("Create Test DJ User", True, f"Created test DJ with user_id: {self.test_dj_user_id}")
                    return True
                else:
                    self.log_test("Create Test DJ User", False, f"DJ registration failed: {response.status_code}")
                    return False
            else:
                self.log_test("Create Test DJ User", False, f"User registration failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Test DJ User", False, f"Error: {str(e)}")
            return False

    def test_trial_dj_dashboard(self):
        """Test trial DJ dashboard shows trial information"""
        if not self.test_dj_user_id:
            self.log_test("Trial DJ Dashboard", False, "No test DJ user created")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                is_trial = data.get("is_trial")
                trial_days_remaining = data.get("trial_days_remaining")
                subscription_status = data.get("subscription_status")
                
                if is_trial and trial_days_remaining is not None and subscription_status == "trial":
                    if 14 <= trial_days_remaining <= 15:  # Should be 14-15 days for new user
                        self.log_test("Trial DJ Dashboard", True, f"is_trial=true, trial_days_remaining={trial_days_remaining}, subscription_status=trial")
                        return True
                    else:
                        self.log_test("Trial DJ Dashboard", False, f"Unexpected trial days remaining: {trial_days_remaining}")
                        return False
                else:
                    self.log_test("Trial DJ Dashboard", False, f"is_trial={is_trial}, trial_days_remaining={trial_days_remaining}, subscription_status={subscription_status}")
                    return False
            else:
                self.log_test("Trial DJ Dashboard", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Trial DJ Dashboard", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in order"""
        print("🎯 Starting DJ Match France Backend API Testing")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return False
        
        # Admin authentication
        if not self.test_admin_login():
            print("❌ Admin login failed - aborting admin tests")
            return False
        
        # Test boost plans and pricing
        self.test_boost_plans()
        
        # Test subscription plans
        self.test_subscription_plans()
        
        # Test admin boost features
        self.test_admin_boost_status()
        self.test_admin_boost_checkout_bypass()
        
        # Test admin zone features
        self.test_admin_zone_status()
        self.test_admin_zone_add_department_bypass()
        
        # Test subscription checkout
        self.test_subscription_checkout_creation()
        
        # Test DJ profile update
        self.test_dj_profile_update()
        
        # Test admin dashboard
        self.test_admin_dashboard_never_locked()
        
        # Create test DJ user and test trial features
        if self.create_test_dj_user():
            self.test_trial_dj_dashboard()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if not result["success"] and result["details"]:
                print(f"   ❌ {result['details']}")
        
        print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed")
            return False

def main():
    """Main test runner"""
    tester = DJMatchTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()