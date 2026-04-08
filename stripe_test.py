#!/usr/bin/env python3
"""
Test Stripe subscription endpoints
"""

import requests
import json
import subprocess
import time

BASE_URL = "https://dj-directory-fr.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def get_test_session():
    """Get existing test session"""
    try:
        result = subprocess.run(
            "mongosh --eval \"use('test_database'); var session = db.user_sessions.findOne(); print(session ? session.session_token : 'none');\"",
            shell=True, capture_output=True, text=True
        )
        
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.startswith('test_session_'):
                return line.strip()
        return None
    except:
        return None

def test_stripe_endpoints():
    """Test Stripe subscription endpoints"""
    session_token = get_test_session()
    if not session_token:
        print("❌ No test session available for Stripe testing")
        return False
    
    headers = {**HEADERS, "Authorization": f"Bearer {session_token}"}
    
    try:
        # Test create checkout session
        print("Testing Stripe checkout creation...")
        checkout_data = {
            "origin_url": "https://dj-directory-fr.preview.emergentagent.com"
        }
        
        response = requests.post(f"{BASE_URL}/subscription/create-checkout", 
                               json=checkout_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("checkout_url") and data.get("session_id"):
                print(f"✅ Stripe Checkout: Created successfully - {data.get('session_id')}")
                session_id = data.get('session_id')
                
                # Test get subscription status
                print("Testing subscription status check...")
                status_response = requests.get(f"{BASE_URL}/subscription/status/{session_id}", 
                                             headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Subscription Status: Retrieved status - {status_data.get('status')}")
                    return True
                else:
                    print(f"❌ Subscription Status: HTTP {status_response.status_code}: {status_response.text}")
                    return False
            else:
                print(f"❌ Stripe Checkout: Invalid response format: {data}")
                return False
        else:
            print(f"❌ Stripe Checkout: HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Stripe Endpoints: Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎵 Testing Stripe Subscription APIs")
    print("=" * 40)
    
    result = test_stripe_endpoints()
    
    if result:
        print("🎉 Stripe tests passed!")
    else:
        print("❌ Stripe tests failed")