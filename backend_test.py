#!/usr/bin/env python3
"""
Backend Testing Script for DJ Match France - Smart Geographic Search
Tests the geographic search functionality for DJs
"""

import requests
import json
import sys
from urllib.parse import quote

# Configuration
BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"

def test_api_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test an API endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🧪 Testing: {description}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                result = response.json()
                print(f"   ✅ SUCCESS")
                return result
            except:
                print(f"   ✅ SUCCESS (no JSON response)")
                return {"status": "success"}
        else:
            print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ REQUEST FAILED: {str(e)}")
        return None

def test_smart_geographic_search():
    """Test the Smart Geographic Search functionality"""
    
    print("=" * 80)
    print("🎯 TESTING SMART GEOGRAPHIC SEARCH FEATURE")
    print("=" * 80)
    
    # Test 1: Search by Region "Normandie" - should return DJ AS'
    print("\n📍 TEST 1: Search by Region 'Normandie'")
    result = test_api_endpoint(
        "GET", 
        f"/djs?ville={quote('Normandie')}", 
        description="Search DJs in Normandie region"
    )
    
    if result:
        total = result.get("total", 0)
        djs = result.get("djs", [])
        print(f"   Found {total} DJs")
        
        # Check if DJ AS' is in results
        dj_as_found = False
        for dj in djs:
            if dj.get("nom_de_scene") == "DJ AS'":
                dj_as_found = True
                print(f"   ✅ DJ AS' found in Normandie search")
                print(f"      - Ville: {dj.get('ville')}")
                print(f"      - Region: {dj.get('region_name')}")
                print(f"      - Department: {dj.get('department_name')}")
                break
        
        if not dj_as_found and total > 0:
            print(f"   ⚠️  DJ AS' not found, but {total} other DJs found")
            for dj in djs[:3]:  # Show first 3 DJs
                print(f"      - {dj.get('nom_de_scene')} in {dj.get('ville')} ({dj.get('region_name')})")
        elif not dj_as_found:
            print(f"   ❌ No DJs found for Normandie search")
    
    # Test 2: Search by Department "Orne" - should return DJ AS'
    print("\n📍 TEST 2: Search by Department 'Orne'")
    result = test_api_endpoint(
        "GET", 
        f"/djs?ville={quote('Orne')}", 
        description="Search DJs in Orne department"
    )
    
    if result:
        total = result.get("total", 0)
        djs = result.get("djs", [])
        print(f"   Found {total} DJs")
        
        # Check if DJ AS' is in results
        dj_as_found = False
        for dj in djs:
            if dj.get("nom_de_scene") == "DJ AS'":
                dj_as_found = True
                print(f"   ✅ DJ AS' found in Orne search")
                print(f"      - Ville: {dj.get('ville')}")
                print(f"      - Department: {dj.get('department_name')}")
                break
        
        if not dj_as_found and total > 0:
            print(f"   ⚠️  DJ AS' not found, but {total} other DJs found")
        elif not dj_as_found:
            print(f"   ❌ No DJs found for Orne search")
    
    # Test 3: Search by small city "La Chapelle" - should return DJ AS'
    print("\n📍 TEST 3: Search by small city 'La Chapelle'")
    result = test_api_endpoint(
        "GET", 
        f"/djs?ville={quote('La Chapelle')}", 
        description="Search DJs in La Chapelle (partial city name)"
    )
    
    if result:
        total = result.get("total", 0)
        djs = result.get("djs", [])
        print(f"   Found {total} DJs")
        
        # Check if DJ AS' is in results
        dj_as_found = False
        for dj in djs:
            if dj.get("nom_de_scene") == "DJ AS'":
                dj_as_found = True
                print(f"   ✅ DJ AS' found in La Chapelle search")
                print(f"      - Ville: {dj.get('ville')}")
                break
        
        if not dj_as_found and total > 0:
            print(f"   ⚠️  DJ AS' not found, but {total} other DJs found")
        elif not dj_as_found:
            print(f"   ❌ No DJs found for La Chapelle search")
    
    # Test 4: Search by "Sarthe" (in zone_intervention) - should return DJ AS'
    print("\n📍 TEST 4: Search by 'Sarthe' (zone_intervention)")
    result = test_api_endpoint(
        "GET", 
        f"/djs?ville={quote('Sarthe')}", 
        description="Search DJs with Sarthe in zone_intervention"
    )
    
    if result:
        total = result.get("total", 0)
        djs = result.get("djs", [])
        print(f"   Found {total} DJs")
        
        # Check if DJ AS' is in results
        dj_as_found = False
        for dj in djs:
            if dj.get("nom_de_scene") == "DJ AS'":
                dj_as_found = True
                print(f"   ✅ DJ AS' found in Sarthe search")
                print(f"      - Zone intervention: {dj.get('zone_intervention')}")
                break
        
        if not dj_as_found and total > 0:
            print(f"   ⚠️  DJ AS' not found, but {total} other DJs found")
        elif not dj_as_found:
            print(f"   ❌ No DJs found for Sarthe search")
    
    # Test 5: Search unrelated region "Bretagne" - should return 0 results
    print("\n📍 TEST 5: Search by unrelated region 'Bretagne'")
    result = test_api_endpoint(
        "GET", 
        f"/djs?ville={quote('Bretagne')}", 
        description="Search DJs in Bretagne (should not find DJ AS')"
    )
    
    if result:
        total = result.get("total", 0)
        djs = result.get("djs", [])
        print(f"   Found {total} DJs")
        
        # Check if DJ AS' is in results (should NOT be)
        dj_as_found = False
        for dj in djs:
            if dj.get("nom_de_scene") == "DJ AS'":
                dj_as_found = True
                print(f"   ❌ DJ AS' unexpectedly found in Bretagne search")
                break
        
        if not dj_as_found:
            print(f"   ✅ DJ AS' correctly NOT found in Bretagne search")
            if total > 0:
                print(f"      Found {total} other DJs in Bretagne")
    
    # Test 6: All DJs without filter - should return DJ AS'
    print("\n📍 TEST 6: All DJs without filter")
    result = test_api_endpoint(
        "GET", 
        "/djs", 
        description="Get all active DJs (should include DJ AS')"
    )
    
    if result:
        total = result.get("total", 0)
        djs = result.get("djs", [])
        print(f"   Found {total} total DJs")
        
        # Check if DJ AS' is in results
        dj_as_found = False
        for dj in djs:
            if dj.get("nom_de_scene") == "DJ AS'":
                dj_as_found = True
                print(f"   ✅ DJ AS' found in all DJs list")
                print(f"      - Subscription status: {dj.get('subscription_status')}")
                print(f"      - Is active: {dj.get('is_active')}")
                break
        
        if not dj_as_found:
            print(f"   ❌ DJ AS' not found in all DJs list")
            print(f"      This suggests DJ AS' may not have active subscription")

def test_geo_lookup_apis():
    """Test the Geographic Lookup APIs"""
    
    print("\n" + "=" * 80)
    print("🌍 TESTING GEOGRAPHIC LOOKUP APIs")
    print("=" * 80)
    
    # Test 7: Geo Lookup API for La Chapelle-près-Sées
    print("\n📍 TEST 7: Geo Lookup for 'La Chapelle-près-Sées'")
    result = test_api_endpoint(
        "GET", 
        f"/geo/lookup-city?city={quote('La Chapelle-près-Sées')}", 
        description="Lookup city information for La Chapelle-près-Sées"
    )
    
    if result and "error" not in result:
        print(f"   ✅ City lookup successful")
        print(f"      - Region: {result.get('region_name')}")
        print(f"      - Department: {result.get('department_name')}")
        print(f"      - Department code: {result.get('department_code')}")
        print(f"      - Region code: {result.get('region_code')}")
        
        # Verify expected values
        if result.get('region_name') == 'Normandie':
            print(f"   ✅ Correct region: Normandie")
        else:
            print(f"   ❌ Wrong region: expected 'Normandie', got '{result.get('region_name')}'")
            
        if result.get('department_name') == 'Orne':
            print(f"   ✅ Correct department: Orne")
        else:
            print(f"   ❌ Wrong department: expected 'Orne', got '{result.get('department_name')}'")
    elif result and "error" in result:
        print(f"   ❌ City lookup failed: {result.get('error')}")
    
    # Test 8: Geo Lookup for small city "Sées"
    print("\n📍 TEST 8: Geo Lookup for 'Sées'")
    result = test_api_endpoint(
        "GET", 
        f"/geo/lookup-city?city={quote('Sées')}", 
        description="Lookup city information for Sées"
    )
    
    if result and "error" not in result:
        print(f"   ✅ City lookup successful")
        print(f"      - Region: {result.get('region_name')}")
        print(f"      - Department: {result.get('department_name')}")
    elif result and "error" in result:
        print(f"   ⚠️  City lookup returned error: {result.get('error')}")
        print(f"      This is acceptable for small cities not in the database")
    
    # Test 9: Get all regions
    print("\n📍 TEST 9: Get all French regions")
    result = test_api_endpoint(
        "GET", 
        "/geo/regions", 
        description="Get all French regions"
    )
    
    if result and isinstance(result, list):
        print(f"   ✅ Found {len(result)} regions")
        # Check if Normandie is in the list
        normandie_found = False
        for region in result:
            if region.get('name') == 'Normandie':
                normandie_found = True
                print(f"   ✅ Normandie region found with code: {region.get('code')}")
                break
        
        if not normandie_found:
            print(f"   ❌ Normandie region not found in regions list")
    
    # Test 10: Get all departments
    print("\n📍 TEST 10: Get all French departments")
    result = test_api_endpoint(
        "GET", 
        "/geo/departments", 
        description="Get all French departments"
    )
    
    if result and isinstance(result, list):
        print(f"   ✅ Found {len(result)} departments")
        # Check if Orne is in the list
        orne_found = False
        for dept in result:
            if dept.get('name') == 'Orne':
                orne_found = True
                print(f"   ✅ Orne department found with code: {dept.get('code')}")
                break
        
        if not orne_found:
            print(f"   ❌ Orne department not found in departments list")

def main():
    """Main test function"""
    print("🚀 Starting Backend Tests for Smart Geographic Search")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # Test the Smart Geographic Search functionality
    test_smart_geographic_search()
    
    # Test the Geographic Lookup APIs
    test_geo_lookup_apis()
    
    print("\n" + "=" * 80)
    print("🏁 TESTING COMPLETE")
    print("=" * 80)
    
    print("\n📋 SUMMARY:")
    print("   - Tested DJ search by region (Normandie)")
    print("   - Tested DJ search by department (Orne)")
    print("   - Tested DJ search by partial city name (La Chapelle)")
    print("   - Tested DJ search by zone_intervention (Sarthe)")
    print("   - Tested negative case (Bretagne)")
    print("   - Tested all DJs endpoint")
    print("   - Tested geo lookup APIs")
    print("   - Tested regions and departments endpoints")

if __name__ == "__main__":
    main()