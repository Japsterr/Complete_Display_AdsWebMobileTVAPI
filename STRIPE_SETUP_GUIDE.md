# Stripe Payment Integration Setup Guide

## 🚀 Complete Implementation Status

✅ **Step 3: Payment Models** - COMPLETED
✅ **Step 4: Frontend Integration** - COMPLETED  
✅ **Step 5: Webhook Handling** - COMPLETED

## 📋 What We've Built

### Backend (Django)
1. **New Models Created:**
   - `StripeCustomer` - Links users to Stripe customer IDs
   - `StripeSubscription` - Tracks subscription status and billing periods
   - `StripePayment` - Records individual payment transactions

2. **API Endpoints Added:**
   - `POST /api/v1/payments/create-checkout-session/` - Initiates Stripe checkout
   - `GET /api/v1/payments/stripe-config/` - Returns Stripe configuration
   - `POST /api/v1/payments/stripe-webhook/` - Handles Stripe webhook events

3. **Webhook Handlers:**
   - ✅ `checkout.session.completed` - Upgrades user to business account
   - ✅ `invoice.payment_succeeded` - Records successful payments
   - ✅ `customer.subscription.updated` - Updates subscription status
   - ✅ `customer.subscription.deleted` - Downgrades cancelled subscriptions

### Frontend (React + TypeScript)
1. **Stripe Service** (`src/services/stripe.ts`)
   - Handles Stripe configuration
   - Creates checkout sessions
   - Formats currency (ZAR support)
   - Manages upgrade eligibility

2. **Enhanced Profile Page**
   - ✅ Upgrade buttons with loading states
   - ✅ Success/error notifications
   - ✅ URL parameter handling for payment results
   - ✅ Business account feature highlights

## 🔧 Setup Instructions for You

### Step 2: Stripe Account Setup

1. **Create Stripe Account:**
   - Go to [https://stripe.com](https://stripe.com)
   - Select **South Africa** as your country
   - Complete account setup

2. **Get Test API Keys:**
   - Go to [https://dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)
   - Copy your **Publishable Key** (starts with `pk_test_`)
   - Copy your **Secret Key** (starts with `sk_test_`)

3. **Create Business Plan Product:**
   - Go to [Products](https://dashboard.stripe.com/test/products) in Stripe Dashboard
   - Click **+ Add Product**
   - Name: "Business Plan"
   - Pricing: R99.00 per month (recurring)
   - Currency: ZAR (South African Rand)
   - Copy the **Price ID** (starts with `price_`)

4. **Set up Webhook Endpoint:**
   - Go to [Webhooks](https://dashboard.stripe.com/test/webhooks) in Stripe Dashboard
   - Click **+ Add endpoint**
   - URL: `https://yourdomain.com/api/v1/payments/stripe-webhook/`
   - Events to send: Select these events:
     - `checkout.session.completed`
     - `invoice.payment_succeeded`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - Copy the **Webhook Secret** (starts with `whsec_`)

### Step 3: Update Configuration Files

1. **Update Django Settings** (`C:\DisplayAdsAPI\signage_project\settings.py`):
```python
# Replace these placeholders with your actual Stripe keys
STRIPE_PUBLISHABLE_KEY = "pk_test_YOUR_ACTUAL_PUBLISHABLE_KEY"
STRIPE_SECRET_KEY = "sk_test_YOUR_ACTUAL_SECRET_KEY"
STRIPE_WEBHOOK_SECRET = "whsec_YOUR_ACTUAL_WEBHOOK_SECRET"
STRIPE_BUSINESS_PLAN_PRICE_ID = "price_YOUR_ACTUAL_PRICE_ID"
```

## 🧪 Testing the Integration

### Test the Payment Flow:
1. **Start both servers:**
   - Django: `python manage.py runserver` (port 8000)
   - React: `npm run dev` (port 5173)

2. **Test upgrade process:**
   - Login as a personal account user
   - Go to Profile page
   - Click "Upgrade to Business" button
   - Should redirect to Stripe Checkout
   - Use test card: `4242 4242 4242 4242`
   - Complete payment
   - Should redirect back with success message
   - User account should be upgraded to 'business'

### Test Cards (Stripe Test Mode):
- **Success:** `4242 4242 4242 4242`
- **Declined:** `4000 0000 0000 0002`
- **3D Secure:** `4000 0025 0000 3155`

## 🔐 Security Features Implemented

✅ **Webhook Signature Verification** - Validates Stripe webhook authenticity
✅ **User Authentication** - Only authenticated users can create checkout sessions  
✅ **Metadata Validation** - User ID validation in webhook handlers
✅ **Error Handling** - Comprehensive error handling and logging
✅ **Currency Localization** - South African Rand (ZAR) support

## 🌍 South Africa Specific Features

✅ **ZAR Currency** - All prices in South African Rand
✅ **Local Payment Methods** - Credit cards supported in SA
✅ **Tax Compliance** - Stripe handles SA tax requirements
✅ **Local Banking** - Supports SA banks and cards

## 📱 User Experience Flow

1. User clicks "Upgrade to Business"
2. Frontend calls `/payments/create-checkout-session/`
3. Django creates Stripe Customer (if needed)
4. Django creates Stripe Checkout Session
5. User redirects to Stripe Checkout page
6. User completes payment with credit card
7. Stripe sends webhook to `/payments/stripe-webhook/`
8. Django processes webhook and upgrades user account
9. User redirects back to dashboard with success message
10. Profile page shows "Business Account" status

## 🚨 Important Notes

- **Test Mode Only** - Currently configured for Stripe test mode
- **HTTPS Required** - Webhooks require HTTPS in production
- **Keep Secret Keys Safe** - Never commit secret keys to git
- **Monitor Webhooks** - Check Stripe Dashboard for webhook delivery status

## 🎯 Next Steps After Setup

1. Add your Stripe keys to the configuration files
2. Test the complete payment flow
3. Set up webhook endpoint (requires HTTPS for production)
4. Test webhook delivery in Stripe Dashboard
5. Add more payment methods if needed
6. Set up live mode when ready for production

## 💡 Troubleshooting

**Common Issues:**
- Webhook signature verification fails → Check webhook secret
- Checkout session creation fails → Check secret key and price ID
- User not upgraded after payment → Check webhook delivery in Stripe Dashboard
- Payment succeeded but no redirect → Check success_url configuration

**Logs to Check:**
- Django server logs for webhook processing
- Browser console for frontend errors  
- Stripe Dashboard webhook logs for delivery status
