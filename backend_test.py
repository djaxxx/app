#!/usr/bin/env python3
"""
Backend Test Suite for Admin CRM Contacts Endpoints
Tests the new Admin CRM Contacts endpoints with admin authentication.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
ADMIN_EMAIL = "adrien.sebert@gmail.com"
TEST_PASSWORD = "test123"
TEST_ADMIN_EMAIL = "test-admin@example.com"  # Use a different email for testing

class AdminContactsTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.admin_session_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    def admin_login(self):
        """Login as admin to get session token"""
        print("🔐 Admin Authentication")
        print("=" * 50)
        
        # First, try to create a test admin user and update the database
        if not self.setup_test_admin():
            return False
        
        # Try to login with admin email
        login_data = {
            "email": ADMIN_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-email", json=login_data)
            
            if response.status_code == 200:
                # Check if session cookie is set
                session_token = None
                for cookie in self.session.cookies:
                    if cookie.name == "session_token":
                        session_token = cookie.value
                        break
                
                if session_token:
                    self.admin_session_token = session_token
                    self.log_test("Admin Login", True, f"Successfully logged in as {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin Login", False, "No session token received")
                    return False
            else:
                self.log_test("Admin Login", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Login error: {str(e)}")
            return False
    
    def setup_test_admin(self):
        """Setup test admin user by updating existing admin user with password"""
        try:
            # Create a test admin user with a different email first
            register_data = {
                "email": TEST_ADMIN_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Test Admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register-email", json=register_data)
            
            if response.status_code == 200:
                # Now update the database to change this user's email to the admin email
                import asyncio
                from backend.database import db
                import bcrypt
                
                async def update_admin():
                    # First, delete any existing admin user
                    await db.users.delete_many({"email": ADMIN_EMAIL})
                    
                    # Create new admin user with password
                    hashed = bcrypt.hashpw(TEST_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    import uuid
                    from datetime import datetime, timezone
                    
                    user_id = f"user_{uuid.uuid4().hex[:12]}"
                    await db.users.insert_one({
                        "user_id": user_id,
                        "email": ADMIN_EMAIL,
                        "name": "Test Admin",
                        "password_hash": hashed,
                        "auth_method": "email",
                        "picture": None,
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    })
                    
                    # Clean up test admin user
                    await db.users.delete_many({"email": TEST_ADMIN_EMAIL})
                    
                    return True
                
                result = asyncio.run(update_admin())
                if result:
                    self.log_test("Admin Setup", True, f"Created admin user with email auth: {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin Setup", False, "Failed to update database")
                    return False
            else:
                self.log_test("Admin Setup", False, f"Failed to create test user: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Setup", False, f"Setup error: {str(e)}")
            return False
    
    def admin_register(self):
        """Register admin account if it doesn't exist"""
        register_data = {
            "email": ADMIN_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Admin User"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register-email", json=register_data)
            
            if response.status_code == 200:
                # Check if session cookie is set
                session_token = None
                for cookie in self.session.cookies:
                    if cookie.name == "session_token":
                        session_token = cookie.value
                        break
                
                if session_token:
                    self.admin_session_token = session_token
                    self.log_test("Admin Registration", True, f"Successfully registered and logged in as {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin Registration", False, "No session token received after registration")
                    return False
            else:
                self.log_test("Admin Registration", False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Registration", False, f"Registration error: {str(e)}")
            return False
    
    def test_admin_contacts_list(self):
        """Test GET /api/admin/contacts - List all contacts"""
        print("📋 Testing Admin Contacts List")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/contacts")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["contacts", "total", "page", "pages"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Admin Contacts List - Structure", False, 
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify contacts array structure
                contacts = data.get("contacts", [])
                if contacts:
                    contact = contacts[0]
                    required_contact_fields = ["contact_type", "id", "nom", "email", "telephone", "ville", "created_at", "source"]
                    missing_contact_fields = [field for field in required_contact_fields if field not in contact]
                    
                    if missing_contact_fields:
                        self.log_test("Admin Contacts List - Contact Structure", False,
                                    f"Missing contact fields: {missing_contact_fields}", contact)
                        return False
                
                self.log_test("Admin Contacts List", True, 
                            f"Found {data['total']} contacts, page {data['page']} of {data['pages']}")
                return True
            else:
                self.log_test("Admin Contacts List", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts List", False, f"Error: {str(e)}")
            return False
    
    def test_admin_contacts_filter_dj(self):
        """Test GET /api/admin/contacts?type=dj - Filter by DJ only"""
        print("🎧 Testing Admin Contacts Filter - DJ Only")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/contacts?type=dj")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", [])
                
                # Verify all contacts are DJs
                non_dj_contacts = [c for c in contacts if c.get("contact_type") != "dj"]
                
                if non_dj_contacts:
                    self.log_test("Admin Contacts Filter DJ", False,
                                f"Found {len(non_dj_contacts)} non-DJ contacts in DJ filter")
                    return False
                
                self.log_test("Admin Contacts Filter DJ", True,
                            f"Found {len(contacts)} DJ contacts only")
                return True
            else:
                self.log_test("Admin Contacts Filter DJ", False,
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts Filter DJ", False, f"Error: {str(e)}")
            return False
    
    def test_admin_contacts_filter_client(self):
        """Test GET /api/admin/contacts?type=client - Filter by client only"""
        print("👥 Testing Admin Contacts Filter - Client Only")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/contacts?type=client")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", [])
                
                # Verify all contacts are clients
                non_client_contacts = [c for c in contacts if c.get("contact_type") != "client"]
                
                if non_client_contacts:
                    self.log_test("Admin Contacts Filter Client", False,
                                f"Found {len(non_client_contacts)} non-client contacts in client filter")
                    return False
                
                self.log_test("Admin Contacts Filter Client", True,
                            f"Found {len(contacts)} client contacts only")
                return True
            else:
                self.log_test("Admin Contacts Filter Client", False,
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts Filter Client", False, f"Error: {str(e)}")
            return False
    
    def test_admin_contacts_filter_active(self):
        """Test GET /api/admin/contacts?status=active - Filter active DJs only"""
        print("🟢 Testing Admin Contacts Filter - Active DJs")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/contacts?status=active")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", [])
                
                # Verify all DJ contacts have active subscription
                dj_contacts = [c for c in contacts if c.get("contact_type") == "dj"]
                inactive_djs = [c for c in dj_contacts if c.get("subscription_status") != "active"]
                
                if inactive_djs:
                    self.log_test("Admin Contacts Filter Active", False,
                                f"Found {len(inactive_djs)} inactive DJs in active filter")
                    return False
                
                self.log_test("Admin Contacts Filter Active", True,
                            f"Found {len(dj_contacts)} active DJ contacts")
                return True
            else:
                self.log_test("Admin Contacts Filter Active", False,
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts Filter Active", False, f"Error: {str(e)}")
            return False
    
    def test_admin_contacts_search(self):
        """Test GET /api/admin/contacts?search=DJ - Search functionality"""
        print("🔍 Testing Admin Contacts Search")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/contacts?search=DJ")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", [])
                
                self.log_test("Admin Contacts Search", True,
                            f"Search for 'DJ' returned {len(contacts)} contacts")
                return True
            else:
                self.log_test("Admin Contacts Search", False,
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts Search", False, f"Error: {str(e)}")
            return False
    
    def test_admin_contacts_stats(self):
        """Test GET /api/admin/contacts/stats - Segmentation stats"""
        print("📊 Testing Admin Contacts Stats")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/contacts/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "djs" not in data or "clients" not in data:
                    self.log_test("Admin Contacts Stats", False,
                                "Missing 'djs' or 'clients' sections", data)
                    return False
                
                # Verify DJs section
                djs = data["djs"]
                required_dj_fields = ["total", "active", "inactive", "boosted", "by_department", "by_region"]
                missing_dj_fields = [field for field in required_dj_fields if field not in djs]
                
                if missing_dj_fields:
                    self.log_test("Admin Contacts Stats - DJs", False,
                                f"Missing DJ fields: {missing_dj_fields}", djs)
                    return False
                
                # Verify Clients section
                clients = data["clients"]
                required_client_fields = ["total_requests", "unread", "unique_clients", "by_event_type"]
                missing_client_fields = [field for field in required_client_fields if field not in clients]
                
                if missing_client_fields:
                    self.log_test("Admin Contacts Stats - Clients", False,
                                f"Missing client fields: {missing_client_fields}", clients)
                    return False
                
                self.log_test("Admin Contacts Stats", True,
                            f"DJs: {djs['total']} total ({djs['active']} active), Clients: {clients['total_requests']} requests ({clients['unique_clients']} unique)")
                return True
            else:
                self.log_test("Admin Contacts Stats", False,
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts Stats", False, f"Error: {str(e)}")
            return False
    
    def test_admin_contacts_export_csv(self):
        """Test GET /api/admin/contacts/export-csv - CSV export"""
        print("📄 Testing Admin Contacts CSV Export")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/contacts/export-csv")
            
            if response.status_code == 200:
                # Verify Content-Type
                content_type = response.headers.get("content-type", "")
                if "text/csv" not in content_type:
                    self.log_test("Admin Contacts CSV Export - Content-Type", False,
                                f"Expected text/csv, got {content_type}")
                    return False
                
                # Verify Content-Disposition
                content_disposition = response.headers.get("content-disposition", "")
                if "attachment" not in content_disposition or "filename" not in content_disposition:
                    self.log_test("Admin Contacts CSV Export - Content-Disposition", False,
                                f"Invalid Content-Disposition: {content_disposition}")
                    return False
                
                # Verify CSV content
                csv_content = response.text
                lines = csv_content.split('\n')
                if len(lines) < 1:
                    self.log_test("Admin Contacts CSV Export - Content", False,
                                "Empty CSV content")
                    return False
                
                # Check header
                header = lines[0]
                if "Type" not in header or "Email" not in header:
                    self.log_test("Admin Contacts CSV Export - Header", False,
                                f"Invalid CSV header: {header}")
                    return False
                
                self.log_test("Admin Contacts CSV Export", True,
                            f"CSV export successful, {len(lines)} lines, filename in headers")
                return True
            else:
                self.log_test("Admin Contacts CSV Export", False,
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts CSV Export", False, f"Error: {str(e)}")
            return False
    
    def test_admin_contacts_security(self):
        """Test security - GET /api/admin/contacts without auth should return 401"""
        print("🔒 Testing Admin Contacts Security")
        print("=" * 50)
        
        try:
            # Create a new session without authentication
            unauthenticated_session = requests.Session()
            response = unauthenticated_session.get(f"{BACKEND_URL}/admin/contacts")
            
            if response.status_code == 401:
                self.log_test("Admin Contacts Security", True,
                            "Correctly returned 401 for unauthenticated request")
                return True
            else:
                self.log_test("Admin Contacts Security", False,
                            f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Contacts Security", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all admin contacts tests"""
        print("🚀 Starting Admin CRM Contacts Endpoint Tests")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        # Step 1: Admin Authentication
        if not self.admin_login():
            print("❌ Admin authentication failed. Cannot proceed with admin tests.")
            return False
        
        # Step 2: Run all admin contacts tests
        tests = [
            self.test_admin_contacts_list,
            self.test_admin_contacts_filter_dj,
            self.test_admin_contacts_filter_client,
            self.test_admin_contacts_filter_active,
            self.test_admin_contacts_search,
            self.test_admin_contacts_stats,
            self.test_admin_contacts_export_csv,
            self.test_admin_contacts_security,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        print("=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    test_suite = AdminContactsTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)