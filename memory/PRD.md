# DJ Connect France - Product Requirements Document

## Overview
Premium DJ directory platform for France connecting professional DJs with clients.

## Core Features

### DJ Registration (Mandatory filters)
- Email + password (via Google OAuth)
- Name, stage name, phone
- City + intervention zone
- **SIRET NUMBER (MANDATORY)** - Auto-verified via INSEE API
- Reject registration if SIRET invalid

### DJ Profile
- Profile photo + gallery (photos/videos)
- Description, experience years
- Event types (wedding, birthday, corporate, etc.)
- Equipment (sound, lighting, options)
- Indicative pricing
- Client reviews/ratings
- Social media links
- Location + intervention radius
- **"DJ Vérifié" badge** if: SIRET valid + profile >80% complete

### Monetization
- Monthly subscription: 5€
- Payment via Stripe
- Auto-suspend profile if non-payment

### DJ Dashboard
- Profile views count
- Requests received count
- Performance stats
- New message notifications

### Client Side
- Search by city/department/region
- Filter by event type, budget, rating
- "Verified DJ only" filter
- Modern card display (Airbnb style)
- Quick contact form
- Direct call/WhatsApp option

## Technical Stack
- Frontend: Expo React Native (mobile-first)
- Backend: FastAPI
- Database: MongoDB
- Auth: Google OAuth via Emergent
- Payments: Stripe
- SIRET Verification: INSEE Sirene API

## API Keys Used
- INSEE API: For SIRET verification
- Stripe: For subscriptions
- Emergent Auth: For Google OAuth
