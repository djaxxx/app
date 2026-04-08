#!/usr/bin/env python3
"""
Backend API Testing Script for DJ Connect France
Tests Stripe subscription API with valid API key
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

class StripeSubscriptionTester:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.session_token = None
        self.user_id = None
        
    async def cleanup_test_data(self):
        """Clean up any existing test data"""
        try:
            # Remove test users and related data
            await self.db.users.delete_many({"email": {"$regex": "stripe.test.*@example.com"}})
            await self.db.user_sessions.delete_many({"session_token": {"$regex": "stripe_session_.*"}})
            await self.db.dj_profiles.delete_many({"email": {"$regex": "stripe.test.*@example.com"}})
            await self.db.payment_transactions.delete_many({"user_id": {"$regex": "stripe-test-user-.*"}})
            print("✅ Cleaned up existing test data")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def create_test_user_and_dj(self):
        """Create test user and DJ profile in MongoDB"""
        try:
            # Generate unique identifiers
            timestamp = int(datetime.now().timestamp() * 1000)
            self.user_id = f"stripe-test-user-{timestamp}"
            self.session_token = f"stripe_session_{timestamp}"
            email = f"stripe.test.{timestamp}@example.com"
            
            # Create user
            user_doc = {
                "user_id": self.user_id,
                "email": email,
                "name": "Stripe Test User",
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
            
            # Create DJ profile
            dj_doc = {
                "user_id": self.user_id,
                "email": email,
                "nom": "Test",
                "prenom": "Stripe",
                "nom_de_scene": "DJ Stripe Test",
                "telephone": "0612345678",
                "ville": "Paris",
                "zone_intervention": ["Paris", "Île-de-France"],
                "siret": "44306184100047",  # Google France SIRET (valid)
                "siret_verified": True,
                "company_name": "GOOGLE FRANCE",
                "description": "DJ de test pour Stripe",
                "annees_experience": 5,
                "types_evenements": ["mariage", "anniversaire"],
                "materiel_son": "Système professionnel",
                "materiel_lumiere": "Éclairage LED",
                "tarif_indicatif": "500-800€",
                "subscription_status": "inactive",
                "is_active": False,
                "note_moyenne": 0.0,
                "nombre_avis": 0,
                "nombre_vues": 0,
                "nombre_demandes": 0,
                "badge_verifie": True,
                "profil_complete_percent": 85,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await self.db.dj_profiles.insert_one(dj_doc)
            
            print(f"✅ Created test user: {self.user_id}")
            print(f"✅ Created session token: {self.session_token}")
            print(f"✅ Created DJ profile for: {email}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create test data: {e}")
            return False
    
    async def test_stripe_checkout_creation(self):
        """Test POST /api/subscription/create-checkout"""
        try:
            headers = {
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "origin_url": "https://dj-directory-fr.preview.emergentagent.com"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/subscription/create-checkout",
                    headers=headers,
                    json=payload
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Stripe checkout created successfully!")
                    print(f"Checkout URL: {data.get('checkout_url', 'N/A')}")
                    print(f"Session ID: {data.get('session_id', 'N/A')}")
                    
                    # Validate response structure
                    if 'checkout_url' in data and 'session_id' in data:
                        if data['checkout_url'].startswith('https://checkout.stripe.com'):
                            print("✅ Valid Stripe checkout URL format")
                            return True, data
                        else:
                            print(f"❌ Invalid checkout URL format: {data['checkout_url']}")
                            return False, data
                    else:
                        print("❌ Missing required fields in response")
                        return False, data
                else:
                    error_text = response.text
                    print(f"❌ Stripe checkout failed: {response.status_code}")
                    print(f"Error response: {error_text}")
                    
                    try:
                        error_data = response.json()
                        print(f"Error detail: {error_data.get('detail', 'No detail provided')}")
                    except:
                        pass
                    
                    return False, {"error": error_text}
                    
        except Exception as e:
            print(f"❌ Exception during Stripe checkout test: {e}")
            return False, {"error": str(e)}
    
    async def verify_payment_transaction_record(self, session_id):
        """Verify that payment transaction was recorded in database"""
        try:
            transaction = await self.db.payment_transactions.find_one(
                {"session_id": session_id}, 
                {"_id": 0}
            )
            
            if transaction:
                print("✅ Payment transaction recorded in database:")
                print(f"  - Transaction ID: {transaction.get('transaction_id')}")
                print(f"  - User ID: {transaction.get('user_id')}")
                print(f"  - Amount: {transaction.get('amount')} {transaction.get('currency')}")
                print(f"  - Status: {transaction.get('status')}")
                print(f"  - Payment Status: {transaction.get('payment_status')}")
                return True
            else:
                print("❌ No payment transaction found in database")
                return False
                
        except Exception as e:
            print(f"❌ Error checking payment transaction: {e}")
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
        """Run all Stripe subscription tests"""
        print("🧪 Starting Stripe Subscription API Tests")
        print("=" * 50)
        
        # Test backend health first
        print("\n1. Testing Backend Health...")
        health_ok = await self.test_backend_health()
        if not health_ok:
            print("❌ Backend is not healthy, aborting tests")
            return False
        
        # Clean up any existing test data
        print("\n2. Cleaning up existing test data...")
        await self.cleanup_test_data()
        
        # Create test user and DJ profile
        print("\n3. Creating test user and DJ profile...")
        user_created = await self.create_test_user_and_dj()
        if not user_created:
            print("❌ Failed to create test data, aborting tests")
            return False
        
        # Test Stripe checkout creation
        print("\n4. Testing Stripe checkout creation...")
        checkout_success, checkout_data = await self.test_stripe_checkout_creation()
        
        if checkout_success:
            session_id = checkout_data.get('session_id')
            if session_id:
                print("\n5. Verifying payment transaction record...")
                await self.verify_payment_transaction_record(session_id)
        
        # Final cleanup
        print("\n6. Cleaning up test data...")
        await self.cleanup_test_data()
        
        print("\n" + "=" * 50)
        if checkout_success:
            print("🎉 All Stripe subscription tests PASSED!")
            return True
        else:
            print("💥 Stripe subscription tests FAILED!")
            return False
    
    async def close(self):
        """Close database connection"""
        self.client.close()

async def main():
    """Main test function"""
    tester = StripeSubscriptionTester()
    try:
        success = await tester.run_tests()
        return success
    finally:
        await tester.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)