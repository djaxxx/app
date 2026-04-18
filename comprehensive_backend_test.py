#!/usr/bin/env python3
"""
DJ Match France Comprehensive Backend API Testing
Tests ALL endpoints systematically as requested in review
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

class ComprehensiveDJMatchTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.admin_authenticated = False
        self.dj_authenticated = False
        self.test_user_id = None
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

    # ========== PUBLIC ENDPOINTS (NO AUTH) ==========
    
    def test_health_endpoint(self):
        """Test GET /api/health"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            self.log_test("GET /api/health", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("GET /api/health", False, f"Error: {str(e)}")
            return False

    def test_event_types_endpoint(self):
        """Test GET /api/event-types"""
        try:
            response = self.session.get(f"{BASE_URL}/event-types")
            success = response.status_code == 200
            if success:
                data = response.json()
                self.log_test("GET /api/event-types", True, f"Returned {len(data)} event types")
            else:
                self.log_test("GET /api/event-types", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("GET /api/event-types", False, f"Error: {str(e)}")
            return False

    def test_boost_plans_endpoint(self):
        """Test GET /api/boost/plans → must return 19€/29€/39€"""
        try:
            response = self.session.get(f"{BASE_URL}/boost/plans")
            if response.status_code == 200:
                plans = response.json()
                expected_prices = {"1_week": 19.00, "2_weeks": 29.00, "1_month": 39.00}
                
                if len(plans) == 3:
                    all_correct = True
                    for plan in plans:
                        plan_id = plan.get("id")
                        amount = plan.get("amount")
                        if plan_id not in expected_prices or amount != expected_prices[plan_id]:
                            all_correct = False
                            break
                    
                    if all_correct:
                        self.log_test("GET /api/boost/plans", True, "Correct pricing: 19€/29€/39€")
                        return True
                    else:
                        self.log_test("GET /api/boost/plans", False, "Incorrect pricing")
                        return False
                else:
                    self.log_test("GET /api/boost/plans", False, f"Expected 3 plans, got {len(plans)}")
                    return False
            else:
                self.log_test("GET /api/boost/plans", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/boost/plans", False, f"Error: {str(e)}")
            return False

    def test_subscription_plans_endpoint(self):
        """Test GET /api/subscription/plans → must return 8€/80€"""
        try:
            response = self.session.get(f"{BASE_URL}/subscription/plans")
            if response.status_code == 200:
                plans = response.json()
                expected_prices = {"monthly": 8.00, "annual": 80.00}
                
                if len(plans) == 2:
                    all_correct = True
                    for plan in plans:
                        plan_id = plan.get("id")
                        amount = plan.get("amount")
                        if plan_id not in expected_prices or amount != expected_prices[plan_id]:
                            all_correct = False
                            break
                    
                    if all_correct:
                        self.log_test("GET /api/subscription/plans", True, "Correct pricing: 8€/80€")
                        return True
                    else:
                        self.log_test("GET /api/subscription/plans", False, "Incorrect pricing")
                        return False
                else:
                    self.log_test("GET /api/subscription/plans", False, f"Expected 2 plans, got {len(plans)}")
                    return False
            else:
                self.log_test("GET /api/subscription/plans", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/subscription/plans", False, f"Error: {str(e)}")
            return False

    def test_geo_regions_endpoint(self):
        """Test GET /api/geo/regions"""
        try:
            response = self.session.get(f"{BASE_URL}/geo/regions")
            if response.status_code == 200:
                regions = response.json()
                self.log_test("GET /api/geo/regions", True, f"Returned {len(regions)} regions")
                return True
            else:
                self.log_test("GET /api/geo/regions", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/geo/regions", False, f"Error: {str(e)}")
            return False

    def test_geo_departments_endpoint(self):
        """Test GET /api/geo/departments"""
        try:
            response = self.session.get(f"{BASE_URL}/geo/departments")
            if response.status_code == 200:
                departments = response.json()
                self.log_test("GET /api/geo/departments", True, f"Returned {len(departments)} departments")
                return True
            else:
                self.log_test("GET /api/geo/departments", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/geo/departments", False, f"Error: {str(e)}")
            return False

    def test_djs_list_endpoint(self):
        """Test GET /api/djs?page=1&limit=5"""
        try:
            response = self.session.get(f"{BASE_URL}/djs?page=1&limit=5")
            if response.status_code == 200:
                data = response.json()
                djs = data.get("djs", [])
                self.log_test("GET /api/djs?page=1&limit=5", True, f"Returned {len(djs)} DJs")
                return True
            else:
                self.log_test("GET /api/djs?page=1&limit=5", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/djs?page=1&limit=5", False, f"Error: {str(e)}")
            return False

    def test_djs_postal_search_endpoint(self):
        """Test GET /api/djs?code_postal=75001"""
        try:
            response = self.session.get(f"{BASE_URL}/djs?code_postal=75001")
            if response.status_code == 200:
                data = response.json()
                djs = data.get("djs", [])
                self.log_test("GET /api/djs?code_postal=75001", True, f"Returned {len(djs)} DJs for postal code 75001")
                return True
            else:
                self.log_test("GET /api/djs?code_postal=75001", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/djs?code_postal=75001", False, f"Error: {str(e)}")
            return False

    def test_dj_profile_security(self):
        """Test GET /api/djs/{user_id} → MUST NOT return email, telephone, siret"""
        try:
            # First get a DJ user_id from the list
            response = self.session.get(f"{BASE_URL}/djs?page=1&limit=1")
            if response.status_code != 200:
                self.log_test("GET /api/djs/{user_id} Security Check", False, "Could not get DJ list")
                return False
            
            data = response.json()
            djs = data.get("djs", [])
            if not djs:
                self.log_test("GET /api/djs/{user_id} Security Check", False, "No DJs found")
                return False
            
            user_id = djs[0].get("user_id")
            if not user_id:
                self.log_test("GET /api/djs/{user_id} Security Check", False, "No user_id found")
                return False
            
            # Test the specific DJ profile
            response = self.session.get(f"{BASE_URL}/djs/{user_id}")
            if response.status_code == 200:
                profile = response.json()
                
                # Check that sensitive fields are NOT present
                sensitive_fields = ["email", "telephone", "siret", "company_name", "subscription_status", "trial_end"]
                found_sensitive = []
                
                for field in sensitive_fields:
                    if field in profile:
                        found_sensitive.append(field)
                
                if found_sensitive:
                    self.log_test("GET /api/djs/{user_id} Security Check", False, f"Sensitive fields exposed: {found_sensitive}")
                    return False
                else:
                    self.log_test("GET /api/djs/{user_id} Security Check", True, "No sensitive fields exposed")
                    return True
            else:
                self.log_test("GET /api/djs/{user_id} Security Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/djs/{user_id} Security Check", False, f"Error: {str(e)}")
            return False

    def test_siret_verification_endpoint(self):
        """Test POST /api/verify-siret with valid SIRET"""
        try:
            siret_data = {"siret": TEST_SIRET}
            response = self.session.post(f"{BASE_URL}/verify-siret", json=siret_data)
            
            if response.status_code == 200:
                data = response.json()
                company_name = data.get("company_name", "")
                if "GOOGLE" in company_name.upper():
                    self.log_test("POST /api/verify-siret", True, f"Valid SIRET verified: {company_name}")
                    return True
                else:
                    self.log_test("POST /api/verify-siret", False, f"Unexpected company: {company_name}")
                    return False
            else:
                self.log_test("POST /api/verify-siret", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/verify-siret", False, f"Error: {str(e)}")
            return False

    def test_contact_endpoint(self):
        """Test POST /api/contact with full contact data"""
        try:
            contact_data = {
                "client_nom": "Test Client",
                "client_email": "test-contact@example.com",
                "client_telephone": "0123456789",
                "lieu_evenement": "Paris",
                "type_evenement": "mariage",
                "date_evenement": "2024-06-15",
                "message": "Test contact message",
                "dj_user_id": "user_949db2539456"
            }
            response = self.session.post(f"{BASE_URL}/contact", json=contact_data)
            
            if response.status_code == 200:
                self.log_test("POST /api/contact", True, "Contact request created successfully")
                return True
            else:
                self.log_test("POST /api/contact", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/contact", False, f"Error: {str(e)}")
            return False

    def test_reviews_endpoint(self):
        """Test POST /api/reviews with review data"""
        try:
            review_data = {
                "dj_user_id": "user_949db2539456",
                "client_nom": "Test Reviewer",
                "client_email": "reviewer@example.com",
                "note": 5,
                "commentaire": "Excellent DJ service!",
                "type_evenement": "mariage",
                "date_evenement": "2024-05-01"
            }
            response = self.session.post(f"{BASE_URL}/reviews", json=review_data)
            
            if response.status_code == 200:
                self.log_test("POST /api/reviews", True, "Review created successfully")
                return True
            else:
                self.log_test("POST /api/reviews", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/reviews", False, f"Error: {str(e)}")
            return False

    # ========== AUTH ENDPOINTS ==========
    
    def test_register_email_endpoint(self):
        """Test POST /api/auth/register-email (create test user)"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            register_data = {
                "email": f"test-user-{timestamp}@example.com",
                "password": "test123",
                "name": "Test User"
            }
            response = self.session.post(f"{BASE_URL}/auth/register-email", json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data.get("user_id")
                self.log_test("POST /api/auth/register-email", True, f"User created with ID: {self.test_user_id}")
                return True
            else:
                self.log_test("POST /api/auth/register-email", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/auth/register-email", False, f"Error: {str(e)}")
            return False

    def test_login_email_endpoint(self):
        """Test POST /api/auth/login-email (admin login)"""
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
                
                if is_admin:
                    self.admin_authenticated = True
                    self.dj_authenticated = is_dj
                    self.log_test("POST /api/auth/login-email", True, f"Admin login successful, is_admin={is_admin}, is_dj={is_dj}")
                    return True
                else:
                    self.log_test("POST /api/auth/login-email", False, f"Login successful but not admin: is_admin={is_admin}")
                    return False
            else:
                self.log_test("POST /api/auth/login-email", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/auth/login-email", False, f"Error: {str(e)}")
            return False

    def test_auth_me_endpoint(self):
        """Test GET /api/auth/me (check auth)"""
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                email = data.get("email")
                is_admin = data.get("is_admin", False)
                
                if email == ADMIN_EMAIL and is_admin:
                    self.log_test("GET /api/auth/me", True, f"Auth check successful for admin: {email}")
                    return True
                else:
                    self.log_test("GET /api/auth/me", False, f"Unexpected user data: email={email}, is_admin={is_admin}")
                    return False
            else:
                self.log_test("GET /api/auth/me", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/auth/me", False, f"Error: {str(e)}")
            return False

    def test_logout_endpoint(self):
        """Test POST /api/auth/logout"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/logout")
            
            if response.status_code == 200:
                self.log_test("POST /api/auth/logout", True, "Logout successful")
                # Re-login for subsequent tests
                self.test_login_email_endpoint()
                return True
            else:
                self.log_test("POST /api/auth/logout", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/auth/logout", False, f"Error: {str(e)}")
            return False

    # ========== DJ ENDPOINTS (REQUIRES DJ AUTH) ==========
    
    def test_dj_register_endpoint(self):
        """Test POST /api/dj/register (register as DJ)"""
        if not self.admin_authenticated:
            self.log_test("POST /api/dj/register", False, "Not authenticated")
            return False
        
        try:
            dj_data = {
                "nom": "Test DJ Admin",
                "prenom": "Profile",
                "nom_de_scene": "DJ Test Admin",
                "email": ADMIN_EMAIL,
                "telephone": "0123456789",
                "ville": "Paris",
                "code_postal": "75001",
                "siret": TEST_SIRET,
                "tarif_indicatif": "500-1000€",
                "types_evenements": ["mariage", "anniversaire"],
                "description": "Test DJ profile for comprehensive testing"
            }
            response = self.session.post(f"{BASE_URL}/dj/register", json=dj_data)
            
            if response.status_code == 200:
                data = response.json()
                profile = data.get("profile", {})
                self.log_test("POST /api/dj/register", True, f"DJ profile created/updated successfully")
                return True
            else:
                self.log_test("POST /api/dj/register", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/dj/register", False, f"Error: {str(e)}")
            return False

    def test_dj_dashboard_endpoint(self):
        """Test GET /api/dj/dashboard"""
        if not self.dj_authenticated:
            self.log_test("GET /api/dj/dashboard", False, "Not authenticated as DJ")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                is_locked = data.get("is_locked", True)
                is_admin = data.get("is_admin", False)
                
                if is_admin and not is_locked:
                    self.log_test("GET /api/dj/dashboard", True, f"Admin dashboard accessible, is_locked={is_locked}")
                    return True
                else:
                    self.log_test("GET /api/dj/dashboard", False, f"Unexpected dashboard state: is_locked={is_locked}, is_admin={is_admin}")
                    return False
            else:
                self.log_test("GET /api/dj/dashboard", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/dj/dashboard", False, f"Error: {str(e)}")
            return False

    def test_dj_profile_get_endpoint(self):
        """Test GET /api/dj/profile"""
        if not self.dj_authenticated:
            self.log_test("GET /api/dj/profile", False, "Not authenticated as DJ")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/profile")
            
            if response.status_code == 200:
                data = response.json()
                email = data.get("email")
                if email == ADMIN_EMAIL:
                    self.log_test("GET /api/dj/profile", True, f"Profile retrieved for {email}")
                    return True
                else:
                    self.log_test("GET /api/dj/profile", False, f"Unexpected profile email: {email}")
                    return False
            else:
                self.log_test("GET /api/dj/profile", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/dj/profile", False, f"Error: {str(e)}")
            return False

    def test_dj_profile_update_endpoint(self):
        """Test PUT /api/dj/profile (update profile)"""
        if not self.dj_authenticated:
            self.log_test("PUT /api/dj/profile", False, "Not authenticated as DJ")
            return False
        
        try:
            update_data = {
                "description": f"Updated description at {datetime.now().isoformat()}"
            }
            response = self.session.put(f"{BASE_URL}/dj/profile", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                profile = data.get("profile", {})
                updated_description = profile.get("description", "")
                
                if updated_description == update_data["description"]:
                    self.log_test("PUT /api/dj/profile", True, "Profile updated successfully")
                    return True
                else:
                    self.log_test("PUT /api/dj/profile", False, "Description not updated correctly")
                    return False
            else:
                self.log_test("PUT /api/dj/profile", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("PUT /api/dj/profile", False, f"Error: {str(e)}")
            return False

    def test_dj_contacts_endpoint(self):
        """Test GET /api/dj/contacts"""
        if not self.dj_authenticated:
            self.log_test("GET /api/dj/contacts", False, "Not authenticated as DJ")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/contacts")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", [])
                self.log_test("GET /api/dj/contacts", True, f"Retrieved {len(contacts)} contacts")
                return True
            else:
                self.log_test("GET /api/dj/contacts", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/dj/contacts", False, f"Error: {str(e)}")
            return False

    def test_dj_reviews_pending_endpoint(self):
        """Test GET /api/dj/reviews/pending"""
        if not self.dj_authenticated:
            self.log_test("GET /api/dj/reviews/pending", False, "Not authenticated as DJ")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/reviews/pending")
            
            if response.status_code == 200:
                data = response.json()
                reviews = data.get("reviews", [])
                self.log_test("GET /api/dj/reviews/pending", True, f"Retrieved {len(reviews)} pending reviews")
                return True
            else:
                self.log_test("GET /api/dj/reviews/pending", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/dj/reviews/pending", False, f"Error: {str(e)}")
            return False

    def test_dj_reviews_all_endpoint(self):
        """Test GET /api/dj/reviews/all"""
        if not self.dj_authenticated:
            self.log_test("GET /api/dj/reviews/all", False, "Not authenticated as DJ")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/reviews/all")
            
            if response.status_code == 200:
                data = response.json()
                reviews = data.get("reviews", [])
                self.log_test("GET /api/dj/reviews/all", True, f"Retrieved {len(reviews)} total reviews")
                return True
            else:
                self.log_test("GET /api/dj/reviews/all", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/dj/reviews/all", False, f"Error: {str(e)}")
            return False

    def test_boost_status_endpoint(self):
        """Test GET /api/boost/status"""
        if not self.dj_authenticated:
            self.log_test("GET /api/boost/status", False, "Not authenticated as DJ")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/boost/status")
            
            if response.status_code == 200:
                data = response.json()
                boost_active = data.get("boost_active")
                is_admin = data.get("is_admin", False)
                
                if is_admin and boost_active == "Permanent":
                    self.log_test("GET /api/boost/status", True, f"Admin boost status: {boost_active}")
                    return True
                else:
                    self.log_test("GET /api/boost/status", True, f"Boost status retrieved: {boost_active}")
                    return True
            else:
                self.log_test("GET /api/boost/status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/boost/status", False, f"Error: {str(e)}")
            return False

    def test_dj_zone_status_endpoint(self):
        """Test GET /api/dj/zone-status"""
        if not self.dj_authenticated:
            self.log_test("GET /api/dj/zone-status", False, "Not authenticated as DJ")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/dj/zone-status")
            
            if response.status_code == 200:
                data = response.json()
                max_departments = data.get("max_departments")
                is_admin = data.get("is_admin", False)
                
                if is_admin and max_departments == 999:
                    self.log_test("GET /api/dj/zone-status", True, f"Admin zone status: max_departments={max_departments}")
                    return True
                else:
                    self.log_test("GET /api/dj/zone-status", True, f"Zone status retrieved: max_departments={max_departments}")
                    return True
            else:
                self.log_test("GET /api/dj/zone-status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/dj/zone-status", False, f"Error: {str(e)}")
            return False

    # ========== PAYMENT ENDPOINTS (REQUIRES DJ AUTH) ==========
    
    def test_boost_create_checkout_1_week(self):
        """Test POST /api/boost/create-checkout with plan=1_week → 19€"""
        if not self.dj_authenticated:
            self.log_test("POST /api/boost/create-checkout (1_week)", False, "Not authenticated as DJ")
            return False
        
        try:
            checkout_data = {
                "plan": "1_week",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/boost/create-checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                amount = data.get("amount")
                admin_bypass = data.get("admin_bypass")
                
                if admin_bypass:
                    self.log_test("POST /api/boost/create-checkout (1_week)", True, "Admin bypass activated")
                    return True
                elif amount == 19.00:
                    self.log_test("POST /api/boost/create-checkout (1_week)", True, f"Checkout created for 19€")
                    return True
                else:
                    self.log_test("POST /api/boost/create-checkout (1_week)", False, f"Wrong amount: {amount}€")
                    return False
            else:
                self.log_test("POST /api/boost/create-checkout (1_week)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/boost/create-checkout (1_week)", False, f"Error: {str(e)}")
            return False

    def test_boost_create_checkout_2_weeks(self):
        """Test POST /api/boost/create-checkout with plan=2_weeks → 29€"""
        if not self.dj_authenticated:
            self.log_test("POST /api/boost/create-checkout (2_weeks)", False, "Not authenticated as DJ")
            return False
        
        try:
            checkout_data = {
                "plan": "2_weeks",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/boost/create-checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                amount = data.get("amount")
                admin_bypass = data.get("admin_bypass")
                
                if admin_bypass:
                    self.log_test("POST /api/boost/create-checkout (2_weeks)", True, "Admin bypass activated")
                    return True
                elif amount == 29.00:
                    self.log_test("POST /api/boost/create-checkout (2_weeks)", True, f"Checkout created for 29€")
                    return True
                else:
                    self.log_test("POST /api/boost/create-checkout (2_weeks)", False, f"Wrong amount: {amount}€")
                    return False
            else:
                self.log_test("POST /api/boost/create-checkout (2_weeks)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/boost/create-checkout (2_weeks)", False, f"Error: {str(e)}")
            return False

    def test_boost_create_checkout_1_month(self):
        """Test POST /api/boost/create-checkout with plan=1_month → 39€"""
        if not self.dj_authenticated:
            self.log_test("POST /api/boost/create-checkout (1_month)", False, "Not authenticated as DJ")
            return False
        
        try:
            checkout_data = {
                "plan": "1_month",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/boost/create-checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                amount = data.get("amount")
                admin_bypass = data.get("admin_bypass")
                
                if admin_bypass:
                    self.log_test("POST /api/boost/create-checkout (1_month)", True, "Admin bypass activated")
                    return True
                elif amount == 39.00:
                    self.log_test("POST /api/boost/create-checkout (1_month)", True, f"Checkout created for 39€")
                    return True
                else:
                    self.log_test("POST /api/boost/create-checkout (1_month)", False, f"Wrong amount: {amount}€")
                    return False
            else:
                self.log_test("POST /api/boost/create-checkout (1_month)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/boost/create-checkout (1_month)", False, f"Error: {str(e)}")
            return False

    def test_subscription_create_checkout_monthly(self):
        """Test POST /api/subscription/create-checkout with plan=monthly → 8€"""
        if not self.dj_authenticated:
            self.log_test("POST /api/subscription/create-checkout (monthly)", False, "Not authenticated as DJ")
            return False
        
        try:
            checkout_data = {
                "plan": "monthly",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/subscription/create-checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                amount = data.get("amount")
                checkout_url = data.get("checkout_url")
                
                if amount == 8.00 and checkout_url:
                    self.log_test("POST /api/subscription/create-checkout (monthly)", True, f"Checkout created for 8€")
                    return True
                else:
                    self.log_test("POST /api/subscription/create-checkout (monthly)", False, f"amount={amount}€, checkout_url={bool(checkout_url)}")
                    return False
            else:
                self.log_test("POST /api/subscription/create-checkout (monthly)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/subscription/create-checkout (monthly)", False, f"Error: {str(e)}")
            return False

    def test_subscription_create_checkout_annual(self):
        """Test POST /api/subscription/create-checkout with plan=annual → 80€"""
        if not self.dj_authenticated:
            self.log_test("POST /api/subscription/create-checkout (annual)", False, "Not authenticated as DJ")
            return False
        
        try:
            checkout_data = {
                "plan": "annual",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/subscription/create-checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                amount = data.get("amount")
                checkout_url = data.get("checkout_url")
                
                if amount == 80.00 and checkout_url:
                    self.log_test("POST /api/subscription/create-checkout (annual)", True, f"Checkout created for 80€")
                    return True
                else:
                    self.log_test("POST /api/subscription/create-checkout (annual)", False, f"amount={amount}€, checkout_url={bool(checkout_url)}")
                    return False
            else:
                self.log_test("POST /api/subscription/create-checkout (annual)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/subscription/create-checkout (annual)", False, f"Error: {str(e)}")
            return False

    def test_dj_zone_add_department(self):
        """Test POST /api/dj/zone/add-department with department_code=33 → 20€"""
        if not self.dj_authenticated:
            self.log_test("POST /api/dj/zone/add-department", False, "Not authenticated as DJ")
            return False
        
        try:
            zone_data = {
                "department_code": "33",  # Gironde
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/dj/zone/add-department", json=zone_data)
            
            if response.status_code == 200:
                data = response.json()
                admin_bypass = data.get("admin_bypass")
                department_code = data.get("department_code")
                
                if admin_bypass:
                    self.log_test("POST /api/dj/zone/add-department", True, f"Admin bypass: department {department_code} added")
                    return True
                else:
                    amount = data.get("amount")
                    if amount == 20.00:
                        self.log_test("POST /api/dj/zone/add-department", True, f"Zone extension for 20€")
                        return True
                    else:
                        self.log_test("POST /api/dj/zone/add-department", False, f"Wrong amount: {amount}€")
                        return False
            else:
                self.log_test("POST /api/dj/zone/add-department", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/dj/zone/add-department", False, f"Error: {str(e)}")
            return False

    # ========== ADMIN ENDPOINTS (REQUIRES ADMIN AUTH) ==========
    
    def test_admin_stats_endpoint(self):
        """Test GET /api/admin/stats"""
        if not self.admin_authenticated:
            self.log_test("GET /api/admin/stats", False, "Not authenticated as admin")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/stats")
            
            if response.status_code == 200:
                data = response.json()
                total_djs = data.get("total_djs")
                active_djs = data.get("active_djs")
                
                if total_djs is not None and active_djs is not None:
                    self.log_test("GET /api/admin/stats", True, f"Stats: {total_djs} total DJs, {active_djs} active")
                    return True
                else:
                    self.log_test("GET /api/admin/stats", False, "Missing stats data")
                    return False
            else:
                self.log_test("GET /api/admin/stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/admin/stats", False, f"Error: {str(e)}")
            return False

    def test_admin_djs_endpoint(self):
        """Test GET /api/admin/djs"""
        if not self.admin_authenticated:
            self.log_test("GET /api/admin/djs", False, "Not authenticated as admin")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/djs")
            
            if response.status_code == 200:
                data = response.json()
                djs = data.get("djs", [])
                self.log_test("GET /api/admin/djs", True, f"Retrieved {len(djs)} DJs for admin")
                return True
            else:
                self.log_test("GET /api/admin/djs", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/admin/djs", False, f"Error: {str(e)}")
            return False

    def test_admin_contact_requests_endpoint(self):
        """Test GET /api/admin/contact-requests"""
        if not self.admin_authenticated:
            self.log_test("GET /api/admin/contact-requests", False, "Not authenticated as admin")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/contact-requests")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", [])
                self.log_test("GET /api/admin/contact-requests", True, f"Retrieved {len(contacts)} contact requests")
                return True
            else:
                self.log_test("GET /api/admin/contact-requests", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/admin/contact-requests", False, f"Error: {str(e)}")
            return False

    def test_admin_toggle_subscription_endpoint(self):
        """Test PUT /api/admin/djs/{user_id}/toggle-subscription"""
        if not self.admin_authenticated:
            self.log_test("PUT /api/admin/djs/{user_id}/toggle-subscription", False, "Not authenticated as admin")
            return False
        
        try:
            # Get a DJ user_id first
            response = self.session.get(f"{BASE_URL}/admin/djs")
            if response.status_code != 200:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-subscription", False, "Could not get DJ list")
                return False
            
            data = response.json()
            djs = data.get("djs", [])
            if not djs:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-subscription", False, "No DJs found")
                return False
            
            user_id = djs[0].get("user_id")
            if not user_id:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-subscription", False, "No user_id found")
                return False
            
            # Test toggle subscription
            response = self.session.put(f"{BASE_URL}/admin/djs/{user_id}/toggle-subscription")
            
            if response.status_code == 200:
                data = response.json()
                new_status = data.get("subscription_status")
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-subscription", True, f"Subscription toggled to: {new_status}")
                return True
            else:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-subscription", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("PUT /api/admin/djs/{user_id}/toggle-subscription", False, f"Error: {str(e)}")
            return False

    def test_admin_toggle_boost_endpoint(self):
        """Test PUT /api/admin/djs/{user_id}/toggle-boost"""
        if not self.admin_authenticated:
            self.log_test("PUT /api/admin/djs/{user_id}/toggle-boost", False, "Not authenticated as admin")
            return False
        
        try:
            # Get a DJ user_id first
            response = self.session.get(f"{BASE_URL}/admin/djs")
            if response.status_code != 200:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-boost", False, "Could not get DJ list")
                return False
            
            data = response.json()
            djs = data.get("djs", [])
            if not djs:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-boost", False, "No DJs found")
                return False
            
            user_id = djs[0].get("user_id")
            if not user_id:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-boost", False, "No user_id found")
                return False
            
            # Test toggle boost
            response = self.session.put(f"{BASE_URL}/admin/djs/{user_id}/toggle-boost")
            
            if response.status_code == 200:
                data = response.json()
                boost_active = data.get("boost_active")
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-boost", True, f"Boost toggled to: {boost_active}")
                return True
            else:
                self.log_test("PUT /api/admin/djs/{user_id}/toggle-boost", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("PUT /api/admin/djs/{user_id}/toggle-boost", False, f"Error: {str(e)}")
            return False

    # ========== ERROR HANDLING ==========
    
    def test_error_nonexistent_dj(self):
        """Test GET /api/djs/nonexistent_id → should return 404"""
        try:
            response = self.session.get(f"{BASE_URL}/djs/nonexistent_id_12345")
            
            if response.status_code == 404:
                self.log_test("GET /api/djs/nonexistent_id (404 test)", True, "Correctly returned 404")
                return True
            else:
                self.log_test("GET /api/djs/nonexistent_id (404 test)", False, f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/djs/nonexistent_id (404 test)", False, f"Error: {str(e)}")
            return False

    def test_error_invalid_boost_plan(self):
        """Test POST /api/boost/create-checkout with plan=invalid → should return 400"""
        if not self.dj_authenticated:
            self.log_test("POST /api/boost/create-checkout (invalid plan)", False, "Not authenticated as DJ")
            return False
        
        try:
            checkout_data = {
                "plan": "invalid_plan",
                "origin_url": "https://test.com"
            }
            response = self.session.post(f"{BASE_URL}/boost/create-checkout", json=checkout_data)
            
            if response.status_code == 400:
                self.log_test("POST /api/boost/create-checkout (invalid plan)", True, "Correctly returned 400")
                return True
            else:
                self.log_test("POST /api/boost/create-checkout (invalid plan)", False, f"Expected 400, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /api/boost/create-checkout (invalid plan)", False, f"Error: {str(e)}")
            return False

    def test_error_unauthorized_dashboard(self):
        """Test GET /api/dj/dashboard without auth → should return 401"""
        # Temporarily clear session
        temp_session = requests.Session()
        temp_session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        try:
            response = temp_session.get(f"{BASE_URL}/dj/dashboard")
            
            if response.status_code == 401:
                self.log_test("GET /api/dj/dashboard (no auth)", True, "Correctly returned 401")
                return True
            else:
                self.log_test("GET /api/dj/dashboard (no auth)", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /api/dj/dashboard (no auth)", False, f"Error: {str(e)}")
            return False

    # ========== MAIN TEST RUNNER ==========
    
    def run_all_tests(self):
        """Run all tests systematically"""
        print("🎯 DJ Match France - Comprehensive Backend API Testing")
        print("=" * 80)
        
        # 1. PUBLIC ENDPOINTS (NO AUTH)
        print("\n📋 1. PUBLIC ENDPOINTS (NO AUTH)")
        print("-" * 40)
        self.test_health_endpoint()
        self.test_event_types_endpoint()
        self.test_boost_plans_endpoint()
        self.test_subscription_plans_endpoint()
        self.test_geo_regions_endpoint()
        self.test_geo_departments_endpoint()
        self.test_djs_list_endpoint()
        self.test_djs_postal_search_endpoint()
        self.test_dj_profile_security()
        self.test_siret_verification_endpoint()
        self.test_contact_endpoint()
        self.test_reviews_endpoint()
        
        # 2. AUTH ENDPOINTS
        print("\n🔐 2. AUTH ENDPOINTS")
        print("-" * 40)
        self.test_register_email_endpoint()
        self.test_login_email_endpoint()
        self.test_auth_me_endpoint()
        self.test_logout_endpoint()
        
        # 3. DJ ENDPOINTS (REQUIRES DJ AUTH)
        print("\n🎧 3. DJ ENDPOINTS (REQUIRES DJ AUTH)")
        print("-" * 40)
        self.test_dj_register_endpoint()
        self.test_dj_dashboard_endpoint()
        self.test_dj_profile_get_endpoint()
        self.test_dj_profile_update_endpoint()
        self.test_dj_contacts_endpoint()
        self.test_dj_reviews_pending_endpoint()
        self.test_dj_reviews_all_endpoint()
        self.test_boost_status_endpoint()
        self.test_dj_zone_status_endpoint()
        
        # 4. PAYMENT ENDPOINTS (REQUIRES DJ AUTH)
        print("\n💳 4. PAYMENT ENDPOINTS (REQUIRES DJ AUTH)")
        print("-" * 40)
        self.test_boost_create_checkout_1_week()
        self.test_boost_create_checkout_2_weeks()
        self.test_boost_create_checkout_1_month()
        self.test_subscription_create_checkout_monthly()
        self.test_subscription_create_checkout_annual()
        self.test_dj_zone_add_department()
        
        # 5. ADMIN ENDPOINTS (REQUIRES ADMIN AUTH)
        print("\n👑 5. ADMIN ENDPOINTS (REQUIRES ADMIN AUTH)")
        print("-" * 40)
        self.test_admin_stats_endpoint()
        self.test_admin_djs_endpoint()
        self.test_admin_contact_requests_endpoint()
        self.test_admin_toggle_subscription_endpoint()
        self.test_admin_toggle_boost_endpoint()
        
        # 6. ERROR HANDLING
        print("\n⚠️  6. ERROR HANDLING")
        print("-" * 40)
        self.test_error_nonexistent_dj()
        self.test_error_invalid_boost_plan()
        self.test_error_unauthorized_dashboard()
        
        # SUMMARY
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        # Group results by category
        categories = {
            "Public Endpoints": [],
            "Auth Endpoints": [],
            "DJ Endpoints": [],
            "Payment Endpoints": [],
            "Admin Endpoints": [],
            "Error Handling": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if any(x in test_name for x in ["health", "event-types", "boost/plans", "subscription/plans", "geo/", "djs?", "djs/{user_id}", "verify-siret", "contact", "reviews"]):
                categories["Public Endpoints"].append(result)
            elif "auth/" in test_name:
                categories["Auth Endpoints"].append(result)
            elif any(x in test_name for x in ["dj/register", "dj/dashboard", "dj/profile", "dj/contacts", "dj/reviews", "boost/status", "dj/zone-status"]):
                categories["DJ Endpoints"].append(result)
            elif any(x in test_name for x in ["boost/create-checkout", "subscription/create-checkout", "dj/zone/add-department"]):
                categories["Payment Endpoints"].append(result)
            elif "admin/" in test_name or "toggle-" in test_name:
                categories["Admin Endpoints"].append(result)
            else:
                categories["Error Handling"].append(result)
        
        for category, results in categories.items():
            if results:
                print(f"\n{category}:")
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"  {status} {result['test']}")
                    if not result["success"] and result["details"]:
                        print(f"     ❌ {result['details']}")
        
        print(f"\n📊 FINAL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Backend is fully functional.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. See details above.")
            return False

def main():
    """Main test runner"""
    tester = ComprehensiveDJMatchTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()