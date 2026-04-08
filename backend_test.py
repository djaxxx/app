#!/usr/bin/env python3
"""
DJ Connect France Backend API Tests
Tests all backend APIs for the DJ directory platform
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class DJConnectTester:
    def __init__(self):
        self.session_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test GET /api/health"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Check", True, "API is healthy")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Request failed: {str(e)}")
            return False
    
    def test_event_types(self):
        """Test GET /api/event-types"""
        try:
            response = requests.get(f"{BASE_URL}/event-types", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    expected_types = ["mariage", "anniversaire", "entreprise", "soiree_privee"]
                    found_types = [item.get("id") for item in data]
                    if any(t in found_types for t in expected_types):
                        self.log_result("Event Types", True, f"Retrieved {len(data)} event types")
                        return True
                    else:
                        self.log_result("Event Types", False, f"Missing expected event types: {data}")
                        return False
                else:
                    self.log_result("Event Types", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Event Types", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Event Types", False, f"Request failed: {str(e)}")
            return False
    
    def test_siret_verification(self):
        """Test POST /api/verify-siret with valid SIRET"""
        try:
            # Test with Google France SIRET
            payload = {"siret": "44306184100047"}
            response = requests.post(f"{BASE_URL}/verify-siret", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") == True and data.get("company_name"):
                    self.log_result("SIRET Verification", True, 
                                  f"Valid SIRET verified: {data.get('company_name')}")
                    return True
                else:
                    self.log_result("SIRET Verification", False, 
                                  f"SIRET validation failed: {data}")
                    return False
            else:
                self.log_result("SIRET Verification", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("SIRET Verification", False, f"Request failed: {str(e)}")
            return False
    
    def test_siret_verification_invalid(self):
        """Test POST /api/verify-siret with invalid SIRET"""
        try:
            payload = {"siret": "12345678901234"}  # Invalid SIRET
            response = requests.post(f"{BASE_URL}/verify-siret", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") == False:
                    self.log_result("SIRET Verification (Invalid)", True, 
                                  "Invalid SIRET correctly rejected")
                    return True
                else:
                    self.log_result("SIRET Verification (Invalid)", False, 
                                  f"Invalid SIRET incorrectly accepted: {data}")
                    return False
            else:
                self.log_result("SIRET Verification (Invalid)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("SIRET Verification (Invalid)", False, f"Request failed: {str(e)}")
            return False
    
    def create_test_session(self):
        """Create a test user session using MongoDB directly"""
        try:
            import subprocess
            
            # Generate unique test data
            timestamp = int(time.time())
            user_id = f"test-user-{timestamp}"
            session_token = f"test_session_{timestamp}"
            email = f"test.user.{timestamp}@example.com"
            
            # MongoDB command to create test user and session
            mongo_cmd = f"""
            mongosh --eval "
            use('test_database');
            var userId = '{user_id}';
            var sessionToken = '{session_token}';
            var email = '{email}';
            
            db.users.insertOne({{
              user_id: userId,
              email: email,
              name: 'Test User DJ',
              picture: '',
              created_at: new Date(),
              updated_at: new Date()
            }});
            
            db.user_sessions.insertOne({{
              user_id: userId,
              session_token: sessionToken,
              expires_at: new Date(Date.now() + 7*24*60*60*1000),
              created_at: new Date()
            }});
            
            print('Session created successfully');
            "
            """
            
            result = subprocess.run(mongo_cmd, shell=True, capture_output=True, text=True)
            
            if "Session created successfully" in result.stdout:
                self.session_token = session_token
                self.user_id = user_id
                self.log_result("Test Session Creation", True, f"Created test user: {user_id}")
                return True
            else:
                self.log_result("Test Session Creation", False, 
                              f"MongoDB command failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result("Test Session Creation", False, f"Failed to create test session: {str(e)}")
            return False
    
    def test_dj_search_public(self):
        """Test GET /api/djs (public DJ search)"""
        try:
            # Test basic search
            response = requests.get(f"{BASE_URL}/djs", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "djs" in data and "total" in data:
                    self.log_result("DJ Search (Public)", True, 
                                  f"Retrieved {data.get('total', 0)} DJs")
                    
                    # Test with filters
                    params = {
                        "ville": "Paris",
                        "type_evenement": "mariage",
                        "note_min": 4.0,
                        "verifie_uniquement": True
                    }
                    response_filtered = requests.get(f"{BASE_URL}/djs", params=params, timeout=10)
                    
                    if response_filtered.status_code == 200:
                        filtered_data = response_filtered.json()
                        self.log_result("DJ Search (Filtered)", True, 
                                      f"Filtered search returned {filtered_data.get('total', 0)} DJs")
                        return True
                    else:
                        self.log_result("DJ Search (Filtered)", False, 
                                      f"Filtered search failed: HTTP {response_filtered.status_code}")
                        return False
                else:
                    self.log_result("DJ Search (Public)", False, 
                                  f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("DJ Search (Public)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("DJ Search (Public)", False, f"Request failed: {str(e)}")
            return False
    
    def test_contact_request(self):
        """Test POST /api/contact (create contact request)"""
        try:
            # First, get a DJ to contact
            djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
            if djs_response.status_code != 200:
                self.log_result("Contact Request", False, "Could not get DJs for contact test")
                return False
            
            djs_data = djs_response.json()
            if not djs_data.get("djs"):
                # Create a test DJ profile first if none exist
                if not self.session_token:
                    self.log_result("Contact Request", False, "No DJs available and no auth session")
                    return False
                
                # Try to create a test DJ profile
                test_dj_created = self.create_test_dj_profile()
                if not test_dj_created:
                    self.log_result("Contact Request", False, "Could not create test DJ for contact")
                    return False
                
                # Get the DJ we just created
                djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
                djs_data = djs_response.json()
                
            if not djs_data.get("djs"):
                self.log_result("Contact Request", False, "Still no DJs available for contact test")
                return False
            
            dj_user_id = djs_data["djs"][0]["user_id"]
            
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
                    self.log_result("Contact Request", True, 
                                  f"Contact request created: {data.get('request_id')}")
                    return True
                else:
                    self.log_result("Contact Request", False, 
                                  f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Contact Request", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Contact Request", False, f"Request failed: {str(e)}")
            return False
    
    def test_review_creation(self):
        """Test POST /api/reviews (create review)"""
        try:
            # First, get a DJ to review
            djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
            if djs_response.status_code != 200:
                self.log_result("Review Creation", False, "Could not get DJs for review test")
                return False
            
            djs_data = djs_response.json()
            if not djs_data.get("djs"):
                self.log_result("Review Creation", False, "No DJs available for review test")
                return False
            
            dj_user_id = djs_data["djs"][0]["user_id"]
            
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
                    self.log_result("Review Creation", True, 
                                  f"Review created: {data.get('review_id')}")
                    return True
                else:
                    self.log_result("Review Creation", False, 
                                  f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Review Creation", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Review Creation", False, f"Request failed: {str(e)}")
            return False
    
    def create_test_dj_profile(self):
        """Create a test DJ profile for testing"""
        if not self.session_token:
            return False
        
        try:
            headers = {**HEADERS, "Authorization": f"Bearer {self.session_token}"}
            
            timestamp = int(time.time())
            dj_data = {
                "email": f"dj.test.{timestamp}@example.com",
                "nom": "Testeur",
                "prenom": "DJ",
                "nom_de_scene": f"DJ Test {timestamp}",
                "telephone": "0123456789",
                "ville": "Paris",
                "zone_intervention": ["Paris", "Île-de-France"],
                "siret": "44306184100047",  # Valid Google France SIRET
                "description": "DJ professionnel pour tous vos événements",
                "annees_experience": 5,
                "types_evenements": ["mariage", "anniversaire", "entreprise"],
                "materiel_son": "Système son professionnel",
                "materiel_lumiere": "Éclairage LED",
                "tarif_indicatif": "500-1000€"
            }
            
            response = requests.post(f"{BASE_URL}/dj/register", json=dj_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Failed to create test DJ: HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Failed to create test DJ: {str(e)}")
            return False
    
    def test_authenticated_endpoints(self):
        """Test authenticated endpoints"""
        if not self.session_token:
            self.log_result("Authenticated Endpoints", False, "No session token available")
            return False
        
        headers = {**HEADERS, "Authorization": f"Bearer {self.session_token}"}
        
        # Test auth/me
        try:
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("user_id"):
                    self.log_result("Auth Me", True, f"User authenticated: {data.get('user_id')}")
                else:
                    self.log_result("Auth Me", False, f"Invalid user data: {data}")
                    return False
            else:
                self.log_result("Auth Me", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Auth Me", False, f"Request failed: {str(e)}")
            return False
        
        # Test DJ registration
        try:
            timestamp = int(time.time())
            dj_data = {
                "email": f"dj.test.{timestamp}@example.com",
                "nom": "Testeur",
                "prenom": "DJ",
                "nom_de_scene": f"DJ Test {timestamp}",
                "telephone": "0123456789",
                "ville": "Paris",
                "zone_intervention": ["Paris", "Île-de-France"],
                "siret": "44306184100047",  # Valid Google France SIRET
                "description": "DJ professionnel pour tous vos événements",
                "annees_experience": 5,
                "types_evenements": ["mariage", "anniversaire", "entreprise"],
                "materiel_son": "Système son professionnel",
                "materiel_lumiere": "Éclairage LED",
                "tarif_indicatif": "500-1000€"
            }
            
            response = requests.post(f"{BASE_URL}/dj/register", json=dj_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") and data.get("profile"):
                    self.log_result("DJ Registration", True, "DJ profile created successfully")
                    
                    # Test DJ profile endpoints
                    self.test_dj_profile_endpoints(headers)
                    return True
                else:
                    self.log_result("DJ Registration", False, f"Invalid response: {data}")
                    return False
            elif response.status_code == 400 and "déjà un profil" in response.text:
                self.log_result("DJ Registration", True, "User already has DJ profile (expected)")
                # Test DJ profile endpoints anyway
                self.test_dj_profile_endpoints(headers)
                return True
            else:
                self.log_result("DJ Registration", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("DJ Registration", False, f"Request failed: {str(e)}")
            return False
    
    def test_dj_profile_endpoints(self, headers):
        """Test DJ profile CRUD endpoints"""
        try:
            # Test get profile
            response = requests.get(f"{BASE_URL}/dj/profile", headers=headers, timeout=10)
            if response.status_code == 200:
                profile = response.json()
                self.log_result("DJ Profile Get", True, f"Retrieved profile for {profile.get('nom_de_scene')}")
                
                # Test update profile
                update_data = {
                    "description": "Updated description for testing",
                    "annees_experience": 10
                }
                
                update_response = requests.put(f"{BASE_URL}/dj/profile", json=update_data, headers=headers, timeout=10)
                if update_response.status_code == 200:
                    self.log_result("DJ Profile Update", True, "Profile updated successfully")
                else:
                    self.log_result("DJ Profile Update", False, f"HTTP {update_response.status_code}: {update_response.text}")
                
                # Test dashboard
                dashboard_response = requests.get(f"{BASE_URL}/dj/dashboard", headers=headers, timeout=10)
                if dashboard_response.status_code == 200:
                    dashboard = dashboard_response.json()
                    self.log_result("DJ Dashboard", True, f"Dashboard loaded with {dashboard.get('nombre_vues', 0)} views")
                else:
                    self.log_result("DJ Dashboard", False, f"HTTP {dashboard_response.status_code}: {dashboard_response.text}")
                
                # Test contacts
                contacts_response = requests.get(f"{BASE_URL}/dj/contacts", headers=headers, timeout=10)
                if contacts_response.status_code == 200:
                    contacts = contacts_response.json()
                    self.log_result("DJ Contacts", True, f"Retrieved {len(contacts)} contact requests")
                else:
                    self.log_result("DJ Contacts", False, f"HTTP {contacts_response.status_code}: {contacts_response.text}")
                
            elif response.status_code == 403:
                self.log_result("DJ Profile Get", False, "User does not have DJ profile (403)")
            else:
                self.log_result("DJ Profile Get", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("DJ Profile Endpoints", False, f"Request failed: {str(e)}")
    
    def test_dj_profile_public(self):
        """Test GET /api/djs/{user_id} (public DJ profile)"""
        try:
            # Get a DJ first
            djs_response = requests.get(f"{BASE_URL}/djs?limit=1", timeout=10)
            if djs_response.status_code != 200:
                self.log_result("DJ Profile Public", False, "Could not get DJs for profile test")
                return False
            
            djs_data = djs_response.json()
            if not djs_data.get("djs"):
                self.log_result("DJ Profile Public", False, "No DJs available for profile test")
                return False
            
            dj_user_id = djs_data["djs"][0]["user_id"]
            
            # Get DJ profile
            response = requests.get(f"{BASE_URL}/djs/{dj_user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("user_id") and data.get("nom_de_scene"):
                    self.log_result("DJ Profile Public", True, 
                                  f"Retrieved profile for {data.get('nom_de_scene')}")
                    return True
                else:
                    self.log_result("DJ Profile Public", False, 
                                  f"Invalid profile data: {data}")
                    return False
            else:
                self.log_result("DJ Profile Public", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("DJ Profile Public", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🎵 Starting DJ Connect France Backend API Tests")
        print("=" * 60)
        
        # Basic API tests (no auth required)
        self.test_health_check()
        self.test_event_types()
        self.test_siret_verification()
        self.test_siret_verification_invalid()
        self.test_dj_search_public()
        self.test_dj_profile_public()
        self.test_contact_request()
        self.test_review_creation()
        
        # Create test session for authenticated tests
        if self.create_test_session():
            self.test_authenticated_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎵 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed, total

if __name__ == "__main__":
    tester = DJConnectTester()
    passed, total = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if passed < total:
        exit(1)
    else:
        print("\n🎉 All tests passed!")
        exit(0)