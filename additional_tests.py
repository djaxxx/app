#!/usr/bin/env python3
"""
Additional tests for non-admin DJ functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"

def test_user_registration_error():
    """Test what's causing user registration to fail"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Try to register a new user
    register_data = {
        "email": f"test-dj-{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password": "test123"
    }
    
    print(f"🔍 Testing user registration with email: {register_data['email']}")
    
    try:
        response = session.post(f"{BASE_URL}/auth/register-email", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Could not parse error JSON")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_existing_user_login():
    """Test login with an existing non-admin user"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Try to login with test-dj@example.com
    login_data = {
        "email": "test-dj@example.com",
        "password": "test123"
    }
    
    print(f"🔍 Testing login with existing test user: {login_data['email']}")
    
    try:
        response = session.post(f"{BASE_URL}/auth/login-email", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            is_admin = data.get("is_admin", False)
            is_dj = data.get("is_dj", False)
            print(f"Login successful: is_admin={is_admin}, is_dj={is_dj}")
            
            if is_dj and not is_admin:
                # Test non-admin boost checkout
                print("\n🔍 Testing non-admin boost checkout...")
                checkout_data = {
                    "plan": "1_week",
                    "origin_url": "https://test.com"
                }
                response = session.post(f"{BASE_URL}/boost/create-checkout", json=checkout_data)
                print(f"Boost checkout status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    checkout_url = data.get("checkout_url")
                    amount = data.get("amount")
                    admin_bypass = data.get("admin_bypass")
                    
                    print(f"Checkout URL present: {bool(checkout_url)}")
                    print(f"Amount: {amount}€")
                    print(f"Admin bypass: {admin_bypass}")
                    
                    if checkout_url and amount == 19.00 and not admin_bypass:
                        print("✅ Non-admin boost checkout working correctly")
                        return True
                    else:
                        print("❌ Non-admin boost checkout not working as expected")
                        return False
                else:
                    print(f"❌ Boost checkout failed: {response.text}")
                    return False
            else:
                print("❌ User is not a non-admin DJ")
                return False
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_non_admin_zone_extension():
    """Test non-admin zone extension pricing"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Login with test user
    login_data = {
        "email": "test-dj@example.com",
        "password": "test123"
    }
    
    response = session.post(f"{BASE_URL}/auth/login-email", json=login_data)
    if response.status_code != 200:
        print("❌ Could not login to test non-admin zone extension")
        return False
    
    data = response.json()
    if data.get("is_admin", False):
        print("❌ Test user is admin, cannot test non-admin functionality")
        return False
    
    print("🔍 Testing non-admin zone extension...")
    
    # Test zone status for non-admin
    response = session.get(f"{BASE_URL}/dj/zone-status")
    if response.status_code == 200:
        data = response.json()
        max_departments = data.get("max_departments")
        extension_price = data.get("extension_price")
        is_admin = data.get("is_admin")
        
        print(f"Zone status - max_departments: {max_departments}, extension_price: {extension_price}€, is_admin: {is_admin}")
        
        if max_departments == 4 and extension_price == 20.00 and not is_admin:
            print("✅ Non-admin zone status correct")
            
            # Test zone extension checkout
            zone_data = {
                "department_code": "69",  # Rhône
                "origin_url": "https://test.com"
            }
            response = session.post(f"{BASE_URL}/dj/zone/add-department", json=zone_data)
            print(f"Zone extension status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                checkout_url = data.get("checkout_url")
                amount = data.get("amount")
                admin_bypass = data.get("admin_bypass")
                
                print(f"Checkout URL present: {bool(checkout_url)}")
                print(f"Amount: {amount}€")
                print(f"Admin bypass: {admin_bypass}")
                
                if checkout_url and amount == 20.00 and not admin_bypass:
                    print("✅ Non-admin zone extension working correctly")
                    return True
                else:
                    print("❌ Non-admin zone extension not working as expected")
                    return False
            else:
                print(f"❌ Zone extension failed: {response.text}")
                return False
        else:
            print("❌ Non-admin zone status incorrect")
            return False
    else:
        print(f"❌ Zone status failed: {response.status_code}")
        return False

def main():
    print("🎯 Additional DJ Match France Backend Tests")
    print("=" * 50)
    
    # Test user registration error
    print("\n1. Testing user registration...")
    test_user_registration_error()
    
    # Test existing user functionality
    print("\n2. Testing existing non-admin user...")
    test_existing_user_login()
    
    # Test non-admin zone extension
    print("\n3. Testing non-admin zone extension...")
    test_non_admin_zone_extension()

if __name__ == "__main__":
    main()