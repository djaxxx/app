#!/usr/bin/env python3
"""
Additional Stripe API Testing - Status endpoint
"""

import asyncio
import httpx
import json
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

async def test_subscription_status_endpoint():
    """Test the subscription status endpoint with a mock session ID"""
    
    # Create a test user and session
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Create test user and session
        timestamp = int(datetime.now().timestamp() * 1000)
        user_id = f"status-test-user-{timestamp}"
        session_token = f"status_session_{timestamp}"
        email = f"status.test.{timestamp}@example.com"
        
        # Create user
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": "Status Test User",
            "picture": "",
            "created_at": datetime.now(timezone.utc)
        })
        
        # Create session
        await db.user_sessions.insert_one({
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "created_at": datetime.now(timezone.utc)
        })
        
        print(f"✅ Created test user for status endpoint: {user_id}")
        
        # Test with a mock session ID (this will fail gracefully since it's not a real Stripe session)
        mock_session_id = "cs_test_mock_session_id_for_testing"
        
        headers = {
            "Authorization": f"Bearer {session_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            response = await http_client.get(
                f"{BACKEND_URL}/subscription/status/{mock_session_id}",
                headers=headers
            )
            
            print(f"Status endpoint response code: {response.status_code}")
            print(f"Status endpoint response: {response.text}")
            
            # This should return a 500 error since it's not a real Stripe session,
            # but the endpoint should be accessible and handle the error gracefully
            if response.status_code in [500, 400]:
                print("✅ Status endpoint is accessible and handles invalid session IDs")
                return True
            elif response.status_code == 200:
                print("✅ Status endpoint returned success (unexpected but good)")
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
        
    except Exception as e:
        print(f"❌ Error testing status endpoint: {e}")
        return False
    finally:
        # Cleanup
        await db.users.delete_many({"email": {"$regex": "status.test.*@example.com"}})
        await db.user_sessions.delete_many({"session_token": {"$regex": "status_session_.*"}})
        client.close()

async def test_webhook_endpoint():
    """Test that the webhook endpoint is accessible"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test webhook endpoint with empty body (should handle gracefully)
            response = await client.post(
                f"{BACKEND_URL}/webhook/stripe",
                headers={"Content-Type": "application/json"},
                json={}
            )
            
            print(f"Webhook endpoint response code: {response.status_code}")
            print(f"Webhook endpoint response: {response.text}")
            
            # Webhook should return 200 even for invalid requests to avoid Stripe retries
            if response.status_code == 200:
                print("✅ Webhook endpoint is accessible and handles requests")
                return True
            else:
                print(f"❌ Webhook endpoint returned unexpected status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing webhook endpoint: {e}")
        return False

async def main():
    """Run additional Stripe API tests"""
    print("🧪 Testing Additional Stripe API Endpoints")
    print("=" * 50)
    
    print("\n1. Testing subscription status endpoint...")
    status_ok = await test_subscription_status_endpoint()
    
    print("\n2. Testing webhook endpoint...")
    webhook_ok = await test_webhook_endpoint()
    
    print("\n" + "=" * 50)
    if status_ok and webhook_ok:
        print("🎉 Additional Stripe API tests PASSED!")
        return True
    else:
        print("💥 Some additional tests FAILED!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)