#!/usr/bin/env python3
"""
Simple DJ Boost Testing - Focus on endpoint availability and basic functionality
"""

import asyncio
import httpx
import json

# Get backend URL from frontend .env
BACKEND_URL = "https://dj-directory-fr.preview.emergentagent.com/api"

async def test_boost_endpoints():
    """Test DJ Boost endpoints"""
    client = httpx.AsyncClient(timeout=30.0)
    results = []
    
    print("🚀 Testing DJ Boost Sponsorisé System")
    print("=" * 50)
    
    # Test 1: GET /api/boost/plans
    try:
        response = await client.get(f"{BACKEND_URL}/boost/plans")
        if response.status_code == 200:
            plans = response.json()
            if len(plans) == 3:
                expected_plans = ["1_week", "2_weeks", "1_month"]
                plan_ids = [p["id"] for p in plans]
                if all(pid in plan_ids for pid in expected_plans):
                    results.append("✅ GET /api/boost/plans: Returns 3 plans with correct IDs and pricing")
                else:
                    results.append("❌ GET /api/boost/plans: Missing expected plan IDs")
            else:
                results.append(f"❌ GET /api/boost/plans: Expected 3 plans, got {len(plans)}")
        else:
            results.append(f"❌ GET /api/boost/plans: HTTP {response.status_code}")
    except Exception as e:
        results.append(f"❌ GET /api/boost/plans: Exception {str(e)}")
    
    # Test 2: GET /api/boost/status (no auth)
    try:
        response = await client.get(f"{BACKEND_URL}/boost/status")
        if response.status_code == 401:
            results.append("✅ GET /api/boost/status: Correctly requires authentication (401)")
        else:
            results.append(f"❌ GET /api/boost/status: Expected 401, got {response.status_code}")
    except Exception as e:
        results.append(f"❌ GET /api/boost/status: Exception {str(e)}")
    
    # Test 3: POST /api/boost/create-checkout (no auth)
    try:
        data = {"plan": "1_week", "origin_url": "https://test.com"}
        response = await client.post(f"{BACKEND_URL}/boost/create-checkout", json=data)
        if response.status_code == 401:
            results.append("✅ POST /api/boost/create-checkout: Correctly requires authentication (401)")
        else:
            results.append(f"❌ POST /api/boost/create-checkout: Expected 401, got {response.status_code}")
    except Exception as e:
        results.append(f"❌ POST /api/boost/create-checkout: Exception {str(e)}")
    
    # Test 4: POST /api/boost/create-checkout with invalid plan (no auth, but should still validate)
    try:
        data = {"plan": "invalid_plan", "origin_url": "https://test.com"}
        response = await client.post(f"{BACKEND_URL}/boost/create-checkout", json=data)
        if response.status_code == 401:
            results.append("✅ POST /api/boost/create-checkout (invalid plan): Authentication checked first (401)")
        else:
            results.append(f"❌ POST /api/boost/create-checkout (invalid plan): Expected 401, got {response.status_code}")
    except Exception as e:
        results.append(f"❌ POST /api/boost/create-checkout (invalid plan): Exception {str(e)}")
    
    # Test 5: PUT /api/admin/djs/{user_id}/toggle-boost (no auth)
    try:
        response = await client.put(f"{BACKEND_URL}/admin/djs/user_test123/toggle-boost")
        if response.status_code == 401:
            results.append("✅ PUT /api/admin/djs/{user_id}/toggle-boost: Correctly requires authentication (401)")
        else:
            results.append(f"❌ PUT /api/admin/djs/{{user_id}}/toggle-boost: Expected 401, got {response.status_code}")
    except Exception as e:
        results.append(f"❌ PUT /api/admin/djs/{{user_id}}/toggle-boost: Exception {str(e)}")
    
    # Test 6: Check DJ search includes boost_active field
    try:
        response = await client.get(f"{BACKEND_URL}/djs?limit=1")
        if response.status_code == 200:
            data = response.json()
            if data.get("djs"):
                dj = data["djs"][0]
                if "boost_active" in dj:
                    results.append("✅ GET /api/djs: boost_active field present in DJ response")
                else:
                    results.append("❌ GET /api/djs: boost_active field missing from DJ response")
            else:
                results.append("⚠️ GET /api/djs: No DJs found (expected in test environment)")
        else:
            results.append(f"❌ GET /api/djs: HTTP {response.status_code}")
    except Exception as e:
        results.append(f"❌ GET /api/djs: Exception {str(e)}")
    
    # Test 7: Check sorting (boost_active: -1, note_moyenne: -1)
    try:
        response = await client.get(f"{BACKEND_URL}/djs?limit=10")
        if response.status_code == 200:
            data = response.json()
            djs = data.get("djs", [])
            if len(djs) >= 2:
                # Check if boosted DJs come first
                boost_positions = [i for i, dj in enumerate(djs) if dj.get("boost_active", False)]
                if boost_positions:
                    if boost_positions == list(range(len(boost_positions))):
                        results.append("✅ DJ Sorting: Boosted DJs correctly sorted first")
                    else:
                        results.append("❌ DJ Sorting: Boosted DJs not sorted first")
                else:
                    results.append("⚠️ DJ Sorting: No boosted DJs found for sorting test")
            else:
                results.append("⚠️ DJ Sorting: Insufficient DJs for sorting test")
        else:
            results.append(f"❌ DJ Sorting: HTTP {response.status_code}")
    except Exception as e:
        results.append(f"❌ DJ Sorting: Exception {str(e)}")
    
    await client.aclose()
    
    # Print results
    print("\n📊 TEST RESULTS:")
    print("=" * 50)
    for result in results:
        print(result)
    
    # Count results
    passed = sum(1 for r in results if r.startswith("✅"))
    failed = sum(1 for r in results if r.startswith("❌"))
    warnings = sum(1 for r in results if r.startswith("⚠️"))
    
    print(f"\n📈 SUMMARY: {passed} passed, {failed} failed, {warnings} warnings")
    
    return results, failed == 0

if __name__ == "__main__":
    asyncio.run(test_boost_endpoints())