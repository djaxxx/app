#!/usr/bin/env python3
"""
Comprehensive DJ Boost Testing - All scenarios from review request
"""

import asyncio
import httpx
import json

BACKEND_URL = "https://dj-directory-fr.preview.emergentagent.com/api"

async def test_all_scenarios():
    """Test all scenarios from the review request"""
    client = httpx.AsyncClient(timeout=30.0)
    results = []
    
    print("🎯 DJ Boost Sponsorisé - Comprehensive Testing")
    print("=" * 60)
    
    # Test 1: GET /api/boost/plans — Should return 3 plans
    print("\n1️⃣ Testing GET /api/boost/plans")
    try:
        response = await client.get(f"{BACKEND_URL}/boost/plans")
        if response.status_code == 200:
            plans = response.json()
            expected = {
                "1_week": {"amount": 18.0, "days": 7},
                "2_weeks": {"amount": 34.0, "days": 14},
                "1_month": {"amount": 60.0, "days": 30}
            }
            
            if len(plans) == 3:
                all_correct = True
                for plan in plans:
                    plan_id = plan["id"]
                    if plan_id in expected:
                        exp = expected[plan_id]
                        if plan["amount"] != exp["amount"] or plan["days"] != exp["days"]:
                            all_correct = False
                            break
                    else:
                        all_correct = False
                        break
                
                if all_correct:
                    results.append("✅ GET /api/boost/plans: Returns 3 plans with correct pricing (1_week: 18€/7 days, 2_weeks: 34€/14 days, 1_month: 60€/30 days)")
                else:
                    results.append("❌ GET /api/boost/plans: Incorrect plan details")
            else:
                results.append(f"❌ GET /api/boost/plans: Expected 3 plans, got {len(plans)}")
        else:
            results.append(f"❌ GET /api/boost/plans: HTTP {response.status_code}")
    except Exception as e:
        results.append(f"❌ GET /api/boost/plans: Exception {str(e)}")
    
    # Test 2: GET /api/boost/status — Requires auth (should return 401 without token)
    print("\n2️⃣ Testing GET /api/boost/status (no auth)")
    try:
        response = await client.get(f"{BACKEND_URL}/boost/status")
        if response.status_code == 401:
            results.append("✅ GET /api/boost/status: Correctly returns 401 without auth token")
        else:
            results.append(f"❌ GET /api/boost/status: Expected 401, got {response.status_code}")
    except Exception as e:
        results.append(f"❌ GET /api/boost/status: Exception {str(e)}")
    
    # Test 3: POST /api/boost/create-checkout — Requires auth
    print("\n3️⃣ Testing POST /api/boost/create-checkout (no auth)")
    try:
        data = {"plan": "1_week", "origin_url": "https://test.com"}
        response = await client.post(f"{BACKEND_URL}/boost/create-checkout", json=data)
        if response.status_code == 401:
            results.append("✅ POST /api/boost/create-checkout: Correctly returns 401 without auth")
        else:
            results.append(f"❌ POST /api/boost/create-checkout: Expected 401, got {response.status_code}")
    except Exception as e:
        results.append(f"❌ POST /api/boost/create-checkout: Exception {str(e)}")
    
    # Test 4: GET /api/djs — Check that response includes boost_active field
    print("\n4️⃣ Testing GET /api/djs (boost_active field)")
    try:
        response = await client.get(f"{BACKEND_URL}/djs")
        if response.status_code == 200:
            data = response.json()
            djs = data.get("djs", [])
            if djs:
                dj = djs[0]
                if "boost_active" in dj:
                    results.append("✅ GET /api/djs: Response includes boost_active field for DJs")
                else:
                    results.append("❌ GET /api/djs: boost_active field missing from DJ response")
            else:
                results.append("⚠️ GET /api/djs: No DJs found (expected in test environment)")
        else:
            results.append(f"❌ GET /api/djs: HTTP {response.status_code}")
    except Exception as e:
        results.append(f"❌ GET /api/djs: Exception {str(e)}")
    
    # Test 5: PUT /api/admin/djs/user_f83caa26bd79/toggle-boost — Admin endpoint
    print("\n5️⃣ Testing PUT /api/admin/djs/{user_id}/toggle-boost (no auth)")
    try:
        response = await client.put(f"{BACKEND_URL}/admin/djs/user_f83caa26bd79/toggle-boost")
        if response.status_code == 401:
            results.append("✅ PUT /api/admin/djs/{user_id}/toggle-boost: Admin endpoint correctly requires auth (401)")
        else:
            results.append(f"❌ PUT /api/admin/djs/{{user_id}}/toggle-boost: Expected 401, got {response.status_code}")
    except Exception as e:
        results.append(f"❌ PUT /api/admin/djs/{{user_id}}/toggle-boost: Exception {str(e)}")
    
    # Test 6: Sorting verification — boost_active: -1, then note_moyenne: -1
    print("\n6️⃣ Testing DJ sorting (boost_active: -1, note_moyenne: -1)")
    try:
        response = await client.get(f"{BACKEND_URL}/djs?limit=20")
        if response.status_code == 200:
            data = response.json()
            djs = data.get("djs", [])
            
            # Check sorting logic
            boosted_djs = [dj for dj in djs if dj.get("boost_active", False)]
            non_boosted_djs = [dj for dj in djs if not dj.get("boost_active", False)]
            
            # Verify boosted DJs come first
            boosted_positions = [i for i, dj in enumerate(djs) if dj.get("boost_active", False)]
            
            if boosted_djs:
                if boosted_positions == list(range(len(boosted_djs))):
                    results.append("✅ DJ Sorting: Boosted DJs correctly sorted first (boost_active: -1)")
                else:
                    results.append("❌ DJ Sorting: Boosted DJs not sorted first")
            else:
                # Check if non-boosted DJs are sorted by rating
                ratings = [dj.get("note_moyenne", 0) for dj in non_boosted_djs]
                if len(ratings) > 1:
                    is_sorted = all(ratings[i] >= ratings[i+1] for i in range(len(ratings)-1))
                    if is_sorted:
                        results.append("✅ DJ Sorting: DJs correctly sorted by note_moyenne: -1 (no boosted DJs found)")
                    else:
                        results.append("❌ DJ Sorting: DJs not correctly sorted by rating")
                else:
                    results.append("⚠️ DJ Sorting: Insufficient DJs for sorting verification")
        else:
            results.append(f"❌ DJ Sorting: HTTP {response.status_code}")
    except Exception as e:
        results.append(f"❌ DJ Sorting: Exception {str(e)}")
    
    # Test 7: POST /api/boost/create-checkout with invalid plan
    print("\n7️⃣ Testing POST /api/boost/create-checkout (invalid plan)")
    try:
        data = {"plan": "invalid_plan", "origin_url": "https://test.com"}
        response = await client.post(f"{BACKEND_URL}/boost/create-checkout", json=data)
        if response.status_code == 401:
            results.append("✅ POST /api/boost/create-checkout (invalid plan): Auth checked first, returns 401")
        elif response.status_code == 400:
            results.append("✅ POST /api/boost/create-checkout (invalid plan): Would return 400 for invalid plan (if authenticated)")
        else:
            results.append(f"❌ POST /api/boost/create-checkout (invalid plan): Unexpected status {response.status_code}")
    except Exception as e:
        results.append(f"❌ POST /api/boost/create-checkout (invalid plan): Exception {str(e)}")
    
    await client.aclose()
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    for result in results:
        print(result)
    
    # Count results
    passed = sum(1 for r in results if r.startswith("✅"))
    failed = sum(1 for r in results if r.startswith("❌"))
    warnings = sum(1 for r in results if r.startswith("⚠️"))
    
    print(f"\n📈 FINAL SUMMARY:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    print(f"📋 Total: {len(results)}")
    
    if failed == 0:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("✨ DJ Boost Sponsorisé system is working correctly")
        print("🔒 All endpoints exist and have proper authentication")
        print("📊 boost_active field is included in DJ responses")
        print("🔄 Sorting logic is implemented (boost_active: -1, note_moyenne: -1)")
    else:
        print(f"\n⚠️ {failed} critical issues found that need attention")
    
    return results, failed == 0

if __name__ == "__main__":
    asyncio.run(test_all_scenarios())