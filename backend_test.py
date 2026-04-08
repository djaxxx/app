#!/usr/bin/env python3
"""
Backend API Testing Script for DJ Connect France
Tests new backend features: DJ Visibility Filter, Dashboard Lock Screen, Geographic Lookup API
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class DJMatchNewFeaturesTester:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.session_token = None
        self.user_id = None
        self.inactive_dj_user_id = None
        self.active_dj_user_id = None
        
    async def cleanup_test_data(self):
        """Clean up any existing test data"""
        try:
            # Remove test users and related data
            await self.db.users.delete_many({"email": {"$regex": "djtest.*@example.com"}})
            await self.db.user_sessions.delete_many({"session_token": {"$regex": "test_session_.*"}})
            await self.db.dj_profiles.delete_many({"email": {"$regex": "djtest.*@example.com"}})
            await self.db.contact_requests.delete_many({"nom_client": {"$regex": "Test Client.*"}})
            print("✅ Cleaned up existing test data")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def create_test_user_session(self):
        """Create test user session for authentication"""
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            self.user_id = f"test-user-{timestamp}"
            self.session_token = f"test_session_{timestamp}"
            email = f"djtest.{timestamp}@example.com"
            
            # Create user
            user_doc = {
                "user_id": self.user_id,
                "email": email,
                "name": "Test User",
                "picture": "",
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.users.insert_one(user_doc)
            
            # Create user session
            session_doc = {
                "user_id": self.user_id,
                "session_token": self.session_token,
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.user_sessions.insert_one(session_doc)
            
            print(f"✅ Created test user session: {self.user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create test user session: {e}")
            return False
    
    async def create_test_dj_profiles(self):
        """Create test DJ profiles - one active, one inactive"""
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            
            # Create INACTIVE DJ profile
            self.inactive_dj_user_id = f"inactive-dj-{timestamp}"
            inactive_email = f"djtest.inactive.{timestamp}@example.com"
            
            inactive_user_doc = {
                "user_id": self.inactive_dj_user_id,
                "email": inactive_email,
                "name": "Inactive DJ User",
                "picture": "",
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.users.insert_one(inactive_user_doc)
            
            inactive_dj_doc = {
                "user_id": self.inactive_dj_user_id,
                "email": inactive_email,
                "nom": "Inactive",
                "prenom": "DJ",
                "nom_de_scene": "DJ Inactive Test",
                "telephone": "0612345678",
                "ville": "Paris",
                "zone_intervention": ["Paris"],
                "siret": "44306184100047",
                "siret_verified": True,
                "company_name": "GOOGLE FRANCE",
                "description": "Inactive DJ for testing",
                "subscription_status": "inactive",  # INACTIVE
                "is_active": False,
                "note_moyenne": 4.5,
                "nombre_avis": 10,
                "nombre_vues": 50,
                "nombre_demandes": 5,
                "badge_verifie": True,
                "profil_complete_percent": 85,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await self.db.dj_profiles.insert_one(inactive_dj_doc)
            
            # Create ACTIVE DJ profile
            self.active_dj_user_id = f"active-dj-{timestamp}"
            active_email = f"djtest.active.{timestamp}@example.com"
            
            active_user_doc = {
                "user_id": self.active_dj_user_id,
                "email": active_email,
                "name": "Active DJ User",
                "picture": "",
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.users.insert_one(active_user_doc)
            
            active_dj_doc = {
                "user_id": self.active_dj_user_id,
                "email": active_email,
                "nom": "Active",
                "prenom": "DJ",
                "nom_de_scene": "DJ Active Test",
                "telephone": "0612345679",
                "ville": "Lyon",
                "zone_intervention": ["Lyon"],
                "siret": "44306184100047",
                "siret_verified": True,
                "company_name": "GOOGLE FRANCE",
                "description": "Active DJ for testing",
                "subscription_status": "active",  # ACTIVE
                "is_active": True,
                "note_moyenne": 4.8,
                "nombre_avis": 15,
                "nombre_vues": 100,
                "nombre_demandes": 10,
                "badge_verifie": True,
                "profil_complete_percent": 95,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await self.db.dj_profiles.insert_one(active_dj_doc)
            
            print(f"✅ Created inactive DJ profile: {self.inactive_dj_user_id}")
            print(f"✅ Created active DJ profile: {self.active_dj_user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create test DJ profiles: {e}")
            return False
    
    async def create_authenticated_dj_session(self):
        """Create authenticated DJ session for dashboard testing"""
        try:
            # Create session for inactive DJ
            inactive_session_token = f"inactive_dj_session_{int(datetime.now().timestamp() * 1000)}"
            inactive_session_doc = {
                "user_id": self.inactive_dj_user_id,
                "session_token": inactive_session_token,
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.user_sessions.insert_one(inactive_session_doc)
            
            # Create session for active DJ
            active_session_token = f"active_dj_session_{int(datetime.now().timestamp() * 1000)}"
            active_session_doc = {
                "user_id": self.active_dj_user_id,
                "session_token": active_session_token,
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.user_sessions.insert_one(active_session_doc)
            
            self.inactive_dj_session = inactive_session_token
            self.active_dj_session = active_session_token
            
            print(f"✅ Created DJ session tokens")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create DJ sessions: {e}")
            return False
    
    # ===================
    # TEST 1: DJ VISIBILITY FILTER (Active Subscription Only)
    # ===================
    
    async def test_dj_visibility_get_dj_profile(self):
        """Test GET /api/djs/{user_id} - should return 404 for inactive DJs"""
        print("\n🧪 Testing DJ Visibility Filter - GET /api/djs/{user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test 1: Try to get INACTIVE DJ profile - should return 404
                print(f"  Testing inactive DJ: {self.inactive_dj_user_id}")
                response = await client.get(f"{BACKEND_URL}/djs/{self.inactive_dj_user_id}")
                
                if response.status_code == 404:
                    print("  ✅ INACTIVE DJ correctly returns 404 (not visible)")
                    inactive_test_passed = True
                else:
                    print(f"  ❌ INACTIVE DJ should return 404, got {response.status_code}")
                    print(f"  Response: {response.text}")
                    inactive_test_passed = False
                
                # Test 2: Try to get ACTIVE DJ profile - should return 200
                print(f"  Testing active DJ: {self.active_dj_user_id}")
                response = await client.get(f"{BACKEND_URL}/djs/{self.active_dj_user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("subscription_status") == "active":
                        print("  ✅ ACTIVE DJ correctly returns 200 with profile data")
                        active_test_passed = True
                    else:
                        print(f"  ❌ ACTIVE DJ has wrong subscription status: {data.get('subscription_status')}")
                        active_test_passed = False
                else:
                    print(f"  ❌ ACTIVE DJ should return 200, got {response.status_code}")
                    print(f"  Response: {response.text}")
                    active_test_passed = False
                
                return inactive_test_passed and active_test_passed
                
        except Exception as e:
            print(f"  ❌ Exception during DJ visibility test: {e}")
            return False
    
    async def test_dj_visibility_contact_request(self):
        """Test POST /api/contact - should reject contact requests for inactive DJs"""
        print("\n🧪 Testing DJ Visibility Filter - POST /api/contact")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test 1: Try to contact INACTIVE DJ - should return 404
                contact_data = {
                    "dj_user_id": self.inactive_dj_user_id,
                    "client_nom": "Test Client Inactive",
                    "client_email": "testclient@example.com",
                    "client_telephone": "0612345678",
                    "type_evenement": "mariage",
                    "date_evenement": "2024-06-15",
                    "lieu_evenement": "Paris",
                    "message": "Test contact for inactive DJ"
                }
                
                print(f"  Testing contact to inactive DJ: {self.inactive_dj_user_id}")
                response = await client.post(f"{BACKEND_URL}/contact", json=contact_data)
                
                if response.status_code == 404:
                    print("  ✅ Contact to INACTIVE DJ correctly rejected (404)")
                    inactive_contact_passed = True
                else:
                    print(f"  ❌ Contact to INACTIVE DJ should return 404, got {response.status_code}")
                    print(f"  Response: {response.text}")
                    inactive_contact_passed = False
                
                # Test 2: Try to contact ACTIVE DJ - should return 200
                contact_data["dj_user_id"] = self.active_dj_user_id
                contact_data["client_nom"] = "Test Client Active"
                contact_data["message"] = "Test contact for active DJ"
                
                print(f"  Testing contact to active DJ: {self.active_dj_user_id}")
                response = await client.post(f"{BACKEND_URL}/contact", json=contact_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "request_id" in data:
                        print("  ✅ Contact to ACTIVE DJ correctly accepted (200)")
                        active_contact_passed = True
                    else:
                        print("  ❌ Contact response missing request_id")
                        active_contact_passed = False
                else:
                    print(f"  ❌ Contact to ACTIVE DJ should return 200, got {response.status_code}")
                    print(f"  Response: {response.text}")
                    active_contact_passed = False
                
                return inactive_contact_passed and active_contact_passed
                
        except Exception as e:
            print(f"  ❌ Exception during contact visibility test: {e}")
            return False
    
    async def test_dj_visibility_list_djs(self):
        """Test GET /api/djs - should only return DJs with subscription_status='active'"""
        print("\n🧪 Testing DJ Visibility Filter - GET /api/djs")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{BACKEND_URL}/djs?page=1&limit=50")
                
                if response.status_code == 200:
                    data = response.json()
                    djs = data.get("djs", [])
                    
                    # Check that all returned DJs have active subscription
                    all_active = True
                    inactive_found = False
                    active_found = False
                    
                    for dj in djs:
                        if dj.get("subscription_status") != "active":
                            all_active = False
                            print(f"  ❌ Found DJ with non-active subscription: {dj.get('user_id')} - {dj.get('subscription_status')}")
                        
                        if dj.get("user_id") == self.inactive_dj_user_id:
                            inactive_found = True
                        if dj.get("user_id") == self.active_dj_user_id:
                            active_found = True
                    
                    if not inactive_found and active_found and all_active:
                        print(f"  ✅ DJ list correctly shows only active DJs ({len(djs)} total)")
                        print("  ✅ Inactive test DJ not in list, active test DJ in list")
                        return True
                    else:
                        print(f"  ❌ DJ list filtering failed:")
                        print(f"    - Inactive DJ found: {inactive_found} (should be False)")
                        print(f"    - Active DJ found: {active_found} (should be True)")
                        print(f"    - All DJs active: {all_active} (should be True)")
                        return False
                else:
                    print(f"  ❌ DJ list should return 200, got {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Exception during DJ list visibility test: {e}")
            return False
    
    async def test_dj_visibility_map_djs(self):
        """Test GET /api/geo/djs-map - should only return DJs with active subscription"""
        print("\n🧪 Testing DJ Visibility Filter - GET /api/geo/djs-map")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{BACKEND_URL}/geo/djs-map")
                
                if response.status_code == 200:
                    data = response.json()
                    djs = data.get("djs", [])
                    
                    # Check that all returned DJs have active subscription
                    all_active = True
                    inactive_found = False
                    active_found = False
                    
                    for dj in djs:
                        # Note: map endpoint doesn't return subscription_status in response
                        # but should only include active DJs based on query filter
                        if dj.get("user_id") == self.inactive_dj_user_id:
                            inactive_found = True
                        if dj.get("user_id") == self.active_dj_user_id:
                            active_found = True
                    
                    if not inactive_found:
                        print(f"  ✅ DJ map correctly excludes inactive DJs ({len(djs)} total)")
                        return True
                    else:
                        print(f"  ❌ DJ map includes inactive DJ: {self.inactive_dj_user_id}")
                        return False
                else:
                    print(f"  ❌ DJ map should return 200, got {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Exception during DJ map visibility test: {e}")
            return False
    
    # ===================
    # TEST 2: DJ DASHBOARD LOCK SCREEN (Backend)
    # ===================
    
    async def test_dashboard_lock_screen(self):
        """Test GET /api/dj/dashboard - should return is_locked: true when DJ has no active subscription"""
        print("\n🧪 Testing DJ Dashboard Lock Screen - GET /api/dj/dashboard")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test 1: INACTIVE DJ dashboard - should be locked
                headers = {"Authorization": f"Bearer {self.inactive_dj_session}"}
                print(f"  Testing inactive DJ dashboard: {self.inactive_dj_user_id}")
                
                response = await client.get(f"{BACKEND_URL}/dj/dashboard", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    is_locked = data.get("is_locked")
                    lock_message = data.get("lock_message")
                    subscription_status = data.get("subscription_status")
                    
                    # Check locked status
                    if is_locked is True and subscription_status == "inactive":
                        print("  ✅ INACTIVE DJ dashboard correctly locked (is_locked: true)")
                        inactive_locked = True
                    else:
                        print(f"  ❌ INACTIVE DJ dashboard should be locked, got is_locked: {is_locked}, status: {subscription_status}")
                        inactive_locked = False
                    
                    # Check lock message
                    if lock_message and "abonnement" in lock_message.lower():
                        print("  ✅ Lock message present and mentions subscription")
                        lock_msg_ok = True
                    else:
                        print(f"  ❌ Lock message missing or invalid: {lock_message}")
                        lock_msg_ok = False
                    
                    # Check limited stats (should be 0 for locked)
                    limited_stats = (
                        data.get("nombre_vues") == 0 and
                        data.get("nombre_demandes") == 0 and
                        data.get("demandes_non_lues") == 0 and
                        data.get("note_moyenne") == 0 and
                        data.get("nombre_avis") == 0
                    )
                    
                    if limited_stats:
                        print("  ✅ Limited stats correctly returned (all zeros)")
                        stats_ok = True
                    else:
                        print(f"  ❌ Stats should be limited for locked dashboard:")
                        print(f"    - Views: {data.get('nombre_vues')} (should be 0)")
                        print(f"    - Requests: {data.get('nombre_demandes')} (should be 0)")
                        print(f"    - Rating: {data.get('note_moyenne')} (should be 0)")
                        stats_ok = False
                    
                    inactive_test_passed = inactive_locked and lock_msg_ok and stats_ok
                else:
                    print(f"  ❌ INACTIVE DJ dashboard should return 200, got {response.status_code}")
                    inactive_test_passed = False
                
                # Test 2: ACTIVE DJ dashboard - should NOT be locked
                headers = {"Authorization": f"Bearer {self.active_dj_session}"}
                print(f"  Testing active DJ dashboard: {self.active_dj_user_id}")
                
                response = await client.get(f"{BACKEND_URL}/dj/dashboard", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    is_locked = data.get("is_locked")
                    subscription_status = data.get("subscription_status")
                    
                    if is_locked is False and subscription_status == "active":
                        print("  ✅ ACTIVE DJ dashboard correctly unlocked (is_locked: false)")
                        
                        # Check that real stats are returned (not limited)
                        real_stats = (
                            data.get("nombre_vues", 0) > 0 or
                            data.get("nombre_demandes", 0) > 0 or
                            data.get("note_moyenne", 0) > 0
                        )
                        
                        if real_stats:
                            print("  ✅ Real stats returned for active DJ")
                            active_test_passed = True
                        else:
                            print("  ⚠️ Active DJ has no stats, but dashboard is unlocked (acceptable)")
                            active_test_passed = True
                    else:
                        print(f"  ❌ ACTIVE DJ dashboard should be unlocked, got is_locked: {is_locked}, status: {subscription_status}")
                        active_test_passed = False
                else:
                    print(f"  ❌ ACTIVE DJ dashboard should return 200, got {response.status_code}")
                    active_test_passed = False
                
                return inactive_test_passed and active_test_passed
                
        except Exception as e:
            print(f"  ❌ Exception during dashboard lock test: {e}")
            return False
    
    # ===================
    # TEST 3: GEOGRAPHIC LOOKUP API
    # ===================
    
    async def test_geographic_lookup_cities(self):
        """Test GET /api/geo/lookup-city for various French cities"""
        print("\n🧪 Testing Geographic Lookup API - Cities")
        
        test_cities = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"]
        all_passed = True
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for city in test_cities:
                    print(f"  Testing city lookup: {city}")
                    response = await client.get(f"{BACKEND_URL}/geo/lookup-city?city={city}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check required fields
                        required_fields = ["department_name", "region_name"]
                        missing_fields = [field for field in required_fields if not data.get(field)]
                        
                        if not missing_fields:
                            print(f"    ✅ {city}: {data.get('department_name')}, {data.get('region_name')}")
                        else:
                            print(f"    ❌ {city}: Missing fields {missing_fields}")
                            all_passed = False
                    else:
                        print(f"    ❌ {city}: HTTP {response.status_code}")
                        all_passed = False
                
                return all_passed
                
        except Exception as e:
            print(f"  ❌ Exception during city lookup test: {e}")
            return False
    
    async def test_geographic_regions(self):
        """Test GET /api/geo/regions"""
        print("\n🧪 Testing Geographic Lookup API - Regions")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{BACKEND_URL}/geo/regions")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        # Check for some expected French regions
                        region_names = [region.get("name", "") for region in data]
                        expected_regions = ["Île-de-France", "Provence-Alpes-Côte d'Azur", "Auvergne-Rhône-Alpes"]
                        
                        found_regions = [region for region in expected_regions if any(region in name for name in region_names)]
                        
                        if len(found_regions) >= 2:
                            print(f"  ✅ Regions endpoint returned {len(data)} regions")
                            print(f"    Found expected regions: {found_regions}")
                            return True
                        else:
                            print(f"  ❌ Expected French regions not found. Got: {region_names[:5]}")
                            return False
                    else:
                        print(f"  ❌ Regions should return a non-empty list, got: {type(data)}")
                        return False
                else:
                    print(f"  ❌ Regions endpoint should return 200, got {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Exception during regions test: {e}")
            return False
    
    async def test_geographic_departments(self):
        """Test GET /api/geo/departments and filtered by region"""
        print("\n🧪 Testing Geographic Lookup API - Departments")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test 1: All departments
                print("  Testing all departments")
                response = await client.get(f"{BACKEND_URL}/geo/departments")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 90:  # France has 101 departments
                        print(f"    ✅ All departments returned ({len(data)} departments)")
                        all_deps_ok = True
                    else:
                        print(f"    ❌ Expected 90+ departments, got {len(data) if isinstance(data, list) else 'non-list'}")
                        all_deps_ok = False
                else:
                    print(f"    ❌ All departments should return 200, got {response.status_code}")
                    all_deps_ok = False
                
                # Test 2: Departments filtered by region (Île-de-France)
                print("  Testing departments for Île-de-France (IDF)")
                response = await client.get(f"{BACKEND_URL}/geo/departments?region_code=IDF")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) == 8:  # IDF has 8 departments
                        # Check for Paris (75)
                        dept_codes = [dept.get("code") for dept in data]
                        if "75" in dept_codes:
                            print(f"    ✅ IDF departments returned ({len(data)} departments, includes Paris)")
                            idf_deps_ok = True
                        else:
                            print(f"    ❌ IDF departments missing Paris (75). Got codes: {dept_codes}")
                            idf_deps_ok = False
                    else:
                        print(f"    ❌ Expected 8 IDF departments, got {len(data) if isinstance(data, list) else 'non-list'}")
                        idf_deps_ok = False
                else:
                    print(f"    ❌ IDF departments should return 200, got {response.status_code}")
                    idf_deps_ok = False
                
                return all_deps_ok and idf_deps_ok
                
        except Exception as e:
            print(f"  ❌ Exception during departments test: {e}")
            return False
    
    async def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{BACKEND_URL}/health")
                
                if response.status_code == 200:
                    print("✅ Backend health check passed")
                    return True
                else:
                    print(f"❌ Backend health check failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Backend health check error: {e}")
            return False
    
    async def run_tests(self):
        """Run all new feature tests"""
        print("🧪 Starting DJ Match New Features Backend Tests")
        print("=" * 60)
        
        # Test backend health first
        print("\n1. Testing Backend Health...")
        health_ok = await self.test_backend_health()
        if not health_ok:
            print("❌ Backend is not healthy, aborting tests")
            return False
        
        # Clean up any existing test data
        print("\n2. Cleaning up existing test data...")
        await self.cleanup_test_data()
        
        # Create test data
        print("\n3. Creating test user session...")
        user_created = await self.create_test_user_session()
        if not user_created:
            print("❌ Failed to create test user session")
            return False
        
        print("\n4. Creating test DJ profiles...")
        djs_created = await self.create_test_dj_profiles()
        if not djs_created:
            print("❌ Failed to create test DJ profiles")
            return False
        
        print("\n5. Creating authenticated DJ sessions...")
        sessions_created = await self.create_authenticated_dj_session()
        if not sessions_created:
            print("❌ Failed to create DJ sessions")
            return False
        
        # Run the 3 main feature tests
        print("\n" + "=" * 60)
        print("TESTING NEW FEATURES")
        print("=" * 60)
        
        # Test 1: DJ Visibility Filter (HIGH PRIORITY)
        print("\n🎯 TEST 1: DJ VISIBILITY FILTER (Active Subscription Only)")
        visibility_tests = []
        visibility_tests.append(await self.test_dj_visibility_get_dj_profile())
        visibility_tests.append(await self.test_dj_visibility_contact_request())
        visibility_tests.append(await self.test_dj_visibility_list_djs())
        visibility_tests.append(await self.test_dj_visibility_map_djs())
        
        visibility_passed = all(visibility_tests)
        
        # Test 2: DJ Dashboard Lock Screen (HIGH PRIORITY)
        print("\n🎯 TEST 2: DJ DASHBOARD LOCK SCREEN (Backend)")
        dashboard_passed = await self.test_dashboard_lock_screen()
        
        # Test 3: Geographic Lookup API (MEDIUM PRIORITY)
        print("\n🎯 TEST 3: GEOGRAPHIC LOOKUP API")
        geo_tests = []
        geo_tests.append(await self.test_geographic_lookup_cities())
        geo_tests.append(await self.test_geographic_regions())
        geo_tests.append(await self.test_geographic_departments())
        
        geo_passed = all(geo_tests)
        
        # Final cleanup
        print("\n6. Cleaning up test data...")
        await self.cleanup_test_data()
        
        # Results summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"1. DJ Visibility Filter (Active Subscription Only): {'✅ PASSED' if visibility_passed else '❌ FAILED'}")
        print(f"2. DJ Dashboard Lock Screen (Backend): {'✅ PASSED' if dashboard_passed else '❌ FAILED'}")
        print(f"3. Geographic Lookup API: {'✅ PASSED' if geo_passed else '❌ FAILED'}")
        
        all_passed = visibility_passed and dashboard_passed and geo_passed
        
        if all_passed:
            print("\n🎉 ALL NEW BACKEND FEATURES TESTS PASSED!")
            return True
        else:
            print("\n💥 SOME BACKEND FEATURES TESTS FAILED!")
            return False
    
    async def close(self):
        """Close database connection"""
        self.client.close()

async def main():
    """Main test function"""
    tester = DJMatchNewFeaturesTester()
    try:
        success = await tester.run_tests()
        return success
    finally:
        await tester.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)