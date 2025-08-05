# Stripe Integration Guide for AI Marketing System

**Complete Setup for Subscription Tiers, Individual Packages, and Webhook Integration**

---

## Overview

This guide provides step-by-step instructions for setting up all Stripe products, pricing plans, and webhook integrations for the AI Marketing System. By following this guide, you'll have a complete billing system that automatically manages subscriptions, upgrades, downgrades, and access control.

---

## Part 1: Stripe Dashboard Setup

### Initial Stripe Configuration

1. **Create Stripe Account**
   - Go to https://stripe.com and create an account
   - Complete business verification
   - Enable live payments when ready for production

2. **Get API Keys**
   - Navigate to Developers → API Keys
   - Copy your **Publishable Key** and **Secret Key**
   - Store these securely (you'll need them for integration)

3. **Configure Webhooks Endpoint**
   - Go to Developers → Webhooks
   - Click "Add endpoint"
   - URL: `https://your-domain.com/webhooks/stripe`
   - Select events (detailed list below)

---

## Part 2: Creating Subscription Tier Products

### Tier 1: Startup Accelerator ($497/month)

**Step 1: Create Product**
```
Stripe Dashboard → Products → Create Product

Product Information:
- Name: "AI Marketing System - Startup Accelerator"
- Description: "4 core AI agents for growing businesses"
- Statement Descriptor: "AI Marketing Startup"
- Unit Label: "subscription"
```

**Step 2: Create Pricing**
```
Pricing Information:
- Price: $497.00
- Billing Period: Monthly
- Currency: USD
- Price ID: price_startup_monthly (save this ID)

Advanced Options:
- Usage Type: Licensed
- Aggregate Usage: Sum
- Billing Scheme: Per unit
```

**Step 3: Add Metadata**
```
Metadata (Key-Value Pairs):
- tier: "startup"
- agents_included: "content_strategist,social_media_orchestrator,email_marketing_maestro,analytics_intelligence"
- max_contacts: "10000"
- max_social_posts: "50"
- max_emails: "5000"
- support_level: "community"
- api_access: "false"
```

### Tier 2: Growth Engine ($1,497/month)

**Step 1: Create Product**
```
Product Information:
- Name: "AI Marketing System - Growth Engine"
- Description: "7 AI agents for scaling businesses"
- Statement Descriptor: "AI Marketing Growth"
- Unit Label: "subscription"
```

**Step 2: Create Pricing**
```
Pricing Information:
- Price: $1,497.00
- Billing Period: Monthly
- Currency: USD
- Price ID: price_growth_monthly

Advanced Options:
- Usage Type: Licensed
- Aggregate Usage: Sum
- Billing Scheme: Per unit
```

**Step 3: Add Metadata**
```
Metadata:
- tier: "growth"
- agents_included: "content_strategist,social_media_orchestrator,email_marketing_maestro,analytics_intelligence,seo_domination,lead_generation_specialist,brand_guardian"
- max_contacts: "50000"
- max_social_posts: "unlimited"
- max_emails: "25000"
- support_level: "priority_email"
- api_access: "basic"
```

### Tier 3: Enterprise Dominator ($4,997/month)

**Step 1: Create Product**
```
Product Information:
- Name: "AI Marketing System - Enterprise Dominator"
- Description: "All 9 AI agents for large enterprises"
- Statement Descriptor: "AI Marketing Enterprise"
- Unit Label: "subscription"
```

**Step 2: Create Pricing**
```
Pricing Information:
- Price: $4,997.00
- Billing Period: Monthly
- Currency: USD
- Price ID: price_enterprise_monthly
```

**Step 3: Add Metadata**
```
Metadata:
- tier: "enterprise"
- agents_included: "all"
- max_contacts: "unlimited"
- max_social_posts: "unlimited"
- max_emails: "unlimited"
- support_level: "priority_phone_video"
- api_access: "full"
- white_label: "basic"
- custom_integrations: "true"
```

### Tier 4: Fortune 500 Command Center ($14,997/month)

**Step 1: Create Product**
```
Product Information:
- Name: "AI Marketing System - Fortune 500 Command Center"
- Description: "Enterprise solution with on-premise deployment"
- Statement Descriptor: "AI Marketing F500"
- Unit Label: "subscription"
```

**Step 2: Create Pricing**
```
Pricing Information:
- Price: $14,997.00
- Billing Period: Monthly
- Currency: USD
- Price ID: price_fortune500_monthly
```

**Step 3: Add Metadata**
```
Metadata:
- tier: "fortune500"
- agents_included: "all"
- max_contacts: "unlimited"
- max_social_posts: "unlimited"
- max_emails: "unlimited"
- support_level: "dedicated_24_7"
- api_access: "full"
- white_label: "complete"
- on_premise: "true"
- custom_development: "true"
- dedicated_infrastructure: "true"
```

---

## Part 3: Individual Agent Packages

### Content Intelligence Suite ($197/month)

**Create Product:**
```
Product Information:
- Name: "Content Intelligence Suite"
- Description: "Content Strategist Agent with predictive intelligence"
- Statement Descriptor: "AI Content Suite"

Pricing:
- Price: $197.00
- Billing Period: Monthly
- Price ID: price_content_suite_monthly

Metadata:
- package_type: "individual_agent"
- agent: "content_strategist"
- features: "predictive_content_intelligence,competitor_analysis,seo_optimization"
- max_content_pieces: "100"
```

### Social Media Mastery ($297/month)

**Create Product:**
```
Product Information:
- Name: "Social Media Mastery"
- Description: "Social Media Orchestrator with emotional intelligence"
- Statement Descriptor: "AI Social Mastery"

Pricing:
- Price: $297.00
- Billing Period: Monthly
- Price ID: price_social_mastery_monthly

Metadata:
- package_type: "individual_agent"
- agent: "social_media_orchestrator"
- features: "emotional_intelligence,crisis_management,influencer_relations"
- max_social_accounts: "10"
```

### SEO Domination Package ($397/month)

**Create Product:**
```
Product Information:
- Name: "SEO Domination Package"
- Description: "SEO Agent with future keyword prediction"
- Statement Descriptor: "AI SEO Domination"

Pricing:
- Price: $397.00
- Billing Period: Monthly
- Price ID: price_seo_domination_monthly

Metadata:
- package_type: "individual_agent"
- agent: "seo_domination"
- features: "future_keyword_prediction,technical_seo,competitor_intelligence"
- max_keywords_tracked: "500"
```

### Email Marketing Excellence ($247/month)

**Create Product:**
```
Product Information:
- Name: "Email Marketing Excellence"
- Description: "Email Marketing Maestro with behavioral prediction"
- Statement Descriptor: "AI Email Excellence"

Pricing:
- Price: $247.00
- Billing Period: Monthly
- Price ID: price_email_excellence_monthly

Metadata:
- package_type: "individual_agent"
- agent: "email_marketing_maestro"
- features: "behavioral_prediction,personalization,deliverability_optimization"
- max_email_contacts: "25000"
```

### Paid Advertising Optimizer ($697/month)

**Create Product:**
```
Product Information:
- Name: "Paid Advertising Optimizer"
- Description: "Advertising Agent with 96% ROI prediction accuracy"
- Statement Descriptor: "AI Ad Optimizer"

Pricing:
- Price: $697.00
- Billing Period: Monthly
- Price ID: price_ad_optimizer_monthly

Metadata:
- package_type: "individual_agent"
- agent: "paid_advertising_optimizer"
- features: "roi_prediction,creative_dna_analysis,cross_platform_optimization"
- max_ad_spend_managed: "50000"
```

### Analytics Intelligence Pro ($447/month)

**Create Product:**
```
Product Information:
- Name: "Analytics Intelligence Pro"
- Description: "Analytics Agent with causal intelligence"
- Statement Descriptor: "AI Analytics Pro"

Pricing:
- Price: $447.00
- Billing Period: Monthly
- Price ID: price_analytics_pro_monthly

Metadata:
- package_type: "individual_agent"
- agent: "analytics_intelligence"
- features: "causal_intelligence,predictive_modeling,custom_dashboards"
- max_data_sources: "20"
```

### Lead Generation Machine ($497/month)

**Create Product:**
```
Product Information:
- Name: "Lead Generation Machine"
- Description: "Lead Generation Agent with intent signal aggregation"
- Statement Descriptor: "AI Lead Machine"

Pricing:
- Price: $497.00
- Billing Period: Monthly
- Price ID: price_lead_machine_monthly

Metadata:
- package_type: "individual_agent"
- agent: "lead_generation_specialist"
- features: "intent_signal_aggregation,predictive_scoring,automated_research"
- max_leads_processed: "1000"
```

### Brand Protection Suite ($347/month)

**Create Product:**
```
Product Information:
- Name: "Brand Protection Suite"
- Description: "Brand Guardian Agent with predictive crisis detection"
- Statement Descriptor: "AI Brand Protection"

Pricing:
- Price: $347.00
- Billing Period: Monthly
- Price ID: price_brand_protection_monthly

Metadata:
- package_type: "individual_agent"
- agent: "brand_guardian"
- features: "predictive_crisis_detection,reputation_management,competitive_intelligence"
- max_mentions_monitored: "10000"
```

### Customer Journey Optimizer ($597/month)

**Create Product:**
```
Product Information:
- Name: "Customer Journey Optimizer"
- Description: "Journey Architect Agent with real-time personalization"
- Statement Descriptor: "AI Journey Optimizer"

Pricing:
- Price: $597.00
- Billing Period: Monthly
- Price ID: price_journey_optimizer_monthly

Metadata:
- package_type: "individual_agent"
- agent: "customer_journey_architect"
- features: "journey_prediction,real_time_personalization,conversion_optimization"
- max_customer_journeys: "5000"
```

---

## Part 4: White Label Licensing Products

### Agency Partner Program ($2,997/month + 20% revenue share)

**Create Product:**
```
Product Information:
- Name: "Agency Partner Program"
- Description: "White-label solution for marketing agencies"
- Statement Descriptor: "AI Agency Partner"

Pricing:
- Price: $2,997.00
- Billing Period: Monthly
- Price ID: price_agency_partner_monthly

Metadata:
- license_type: "agency_partner"
- revenue_share: "20"
- white_label: "complete"
- reseller_pricing: "true"
- training_included: "true"
- co_marketing: "true"
```

### Technology Partner Program ($9,997/month + 15% revenue share)

**Create Product:**
```
Product Information:
- Name: "Technology Partner Program"
- Description: "API integration licensing for software companies"
- Statement Descriptor: "AI Tech Partner"

Pricing:
- Price: $9,997.00
- Billing Period: Monthly
- Price ID: price_tech_partner_monthly

Metadata:
- license_type: "technology_partner"
- revenue_share: "15"
- api_integration: "full"
- embedded_capabilities: "true"
- joint_go_to_market: "true"
```

### Enterprise Licensing (Custom pricing starting at $50,000/year)

**Create Product:**
```
Product Information:
- Name: "Enterprise Licensing"
- Description: "Source code licensing for large corporations"
- Statement Descriptor: "AI Enterprise License"

Pricing:
- Price: $50,000.00
- Billing Period: Yearly
- Price ID: price_enterprise_license_yearly

Metadata:
- license_type: "enterprise_source"
- source_code_access: "true"
- unlimited_internal_usage: "true"
- custom_development_rights: "true"
- ongoing_updates: "true"
```

---

## Part 5: Webhook Configuration

### Required Webhook Events

**In Stripe Dashboard → Developers → Webhooks, select these events:**

```
Customer Events:
- customer.created
- customer.updated
- customer.deleted
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted

Payment Events:
- invoice.payment_succeeded
- invoice.payment_failed
- invoice.upcoming
- payment_intent.succeeded
- payment_intent.payment_failed

Subscription Events:
- subscription.created
- subscription.updated
- subscription.deleted
- subscription.trial_will_end

Product Events:
- product.created
- product.updated
- price.created
- price.updated
```

### Webhook Endpoint Implementation

**Create webhook handler in your AI Marketing System:**

```python
# File: /api/webhooks/stripe.py

from fastapi import APIRouter, Request, HTTPException
import stripe
import json
import logging
from config.settings import settings

router = APIRouter()
logger = logging.getLogger("stripe_webhooks")

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/webhooks/stripe")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'customer.subscription.created':
        await handle_subscription_created(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        await handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        await handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        await handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        await handle_payment_failed(event['data']['object'])
    else:
        logger.info(f"Unhandled event type: {event['type']}")
    
    return {"status": "success"}

async def handle_subscription_created(subscription):
    """Handle new subscription creation"""
    customer_id = subscription['customer']
    price_id = subscription['items']['data'][0]['price']['id']
    
    # Get customer details
    customer = stripe.Customer.retrieve(customer_id)
    
    # Determine subscription tier/package from price_id
    tier_mapping = {
        'price_startup_monthly': 'startup',
        'price_growth_monthly': 'growth',
        'price_enterprise_monthly': 'enterprise',
        'price_fortune500_monthly': 'fortune500',
        'price_content_suite_monthly': 'content_suite',
        'price_social_mastery_monthly': 'social_mastery',
        # Add all other price IDs
    }
    
    subscription_type = tier_mapping.get(price_id, 'unknown')
    
    # Create user account in AI Marketing System
    await create_user_account(
        email=customer['email'],
        customer_id=customer_id,
        subscription_id=subscription['id'],
        subscription_type=subscription_type,
        metadata=subscription.get('metadata', {})
    )
    
    # Activate appropriate agents
    await activate_agents_for_subscription(subscription_type, customer_id)
    
    # Send welcome email
    await send_welcome_email(customer['email'], subscription_type)

async def handle_subscription_updated(subscription):
    """Handle subscription changes (upgrades/downgrades)"""
    customer_id = subscription['customer']
    price_id = subscription['items']['data'][0]['price']['id']
    
    # Update user permissions
    await update_user_subscription(customer_id, price_id)
    
    # Adjust agent access
    await adjust_agent_access(customer_id, price_id)

async def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    customer_id = subscription['customer']
    
    # Deactivate user account
    await deactivate_user_account(customer_id)
    
    # Stop all agents
    await deactivate_all_agents(customer_id)
    
    # Send cancellation email
    await send_cancellation_email(customer_id)

async def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    customer_id = invoice['customer']
    
    # Ensure account is active
    await ensure_account_active(customer_id)
    
    # Send payment confirmation
    await send_payment_confirmation(customer_id, invoice['amount_paid'])

async def handle_payment_failed(invoice):
    """Handle failed payment"""
    customer_id = invoice['customer']
    
    # Suspend account after grace period
    await handle_payment_failure(customer_id, invoice)
    
    # Send payment failure notification
    await send_payment_failure_notification(customer_id)
```

### Environment Variables for Stripe

**Add to your .env file:**

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# For production, use live keys:
# STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
# STRIPE_SECRET_KEY=sk_live_your_live_secret_key
```

---

## Part 6: Frontend Integration

### Stripe Checkout Integration

**Create checkout sessions for each product:**

```javascript
// Frontend JavaScript for subscription checkout

async function createCheckoutSession(priceId, customerEmail = null) {
    const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            price_id: priceId,
            customer_email: customerEmail,
            success_url: window.location.origin + '/success',
            cancel_url: window.location.origin + '/pricing'
        })
    });
    
    const session = await response.json();
    
    // Redirect to Stripe Checkout
    const stripe = Stripe('pk_test_your_publishable_key_here');
    const { error } = await stripe.redirectToCheckout({
        sessionId: session.id
    });
    
    if (error) {
        console.error('Error:', error);
    }
}

// Subscription tier buttons
document.getElementById('startup-tier-btn').addEventListener('click', () => {
    createCheckoutSession('price_startup_monthly');
});

document.getElementById('growth-tier-btn').addEventListener('click', () => {
    createCheckoutSession('price_growth_monthly');
});

document.getElementById('enterprise-tier-btn').addEventListener('click', () => {
    createCheckoutSession('price_enterprise_monthly');
});

// Individual agent package buttons
document.getElementById('content-suite-btn').addEventListener('click', () => {
    createCheckoutSession('price_content_suite_monthly');
});

document.getElementById('social-mastery-btn').addEventListener('click', () => {
    createCheckoutSession('price_social_mastery_monthly');
});

// Add buttons for all other packages...
```

### Backend Checkout Session Creation

```python
# File: /api/stripe_checkout.py

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest):
    """Create Stripe checkout session"""
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': request.price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.cancel_url,
            customer_email=request.customer_email,
            metadata={
                'product_type': 'ai_marketing_subscription'
            }
        )
        
        return {"id": checkout_session.id}
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Part 7: Customer Portal Integration

### Enable Customer Portal

**In Stripe Dashboard:**

1. Go to Settings → Billing → Customer Portal
2. Enable the customer portal
3. Configure allowed actions:
   - ✅ Update payment method
   - ✅ Download invoices
   - ✅ Cancel subscription
   - ✅ Update subscription (for upgrades/downgrades)

### Portal Integration Code

```python
@router.post("/create-portal-session")
async def create_portal_session(customer_id: str):
    """Create customer portal session"""
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url='https://your-domain.com/dashboard'
        )
        
        return {"url": portal_session.url}
        
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Part 8: Testing and Validation

### Test Mode Setup

**Use Stripe test mode for development:**

1. Use test API keys (pk_test_ and sk_test_)
2. Test with these card numbers:
   - Success: 4242424242424242
   - Decline: 4000000000000002
   - Requires authentication: 4000002500003155

### Webhook Testing

**Test webhooks locally:**

1. Install Stripe CLI: `stripe login`
2. Forward events: `stripe listen --forward-to localhost:8000/webhooks/stripe`
3. Trigger test events: `stripe trigger customer.subscription.created`

### Production Checklist

**Before going live:**

- [ ] Replace test API keys with live keys
- [ ] Update webhook endpoint to production URL
- [ ] Test all subscription flows
- [ ] Verify webhook handling
- [ ] Test customer portal functionality
- [ ] Validate email notifications
- [ ] Check agent activation/deactivation
- [ ] Test upgrade/downgrade flows
- [ ] Verify cancellation handling

---

## Part 9: Monitoring and Analytics

### Stripe Dashboard Monitoring

**Key metrics to monitor:**

- Monthly Recurring Revenue (MRR)
- Customer churn rate
- Failed payment rates
- Subscription upgrade/downgrade rates
- Revenue by product/tier

### Custom Analytics Integration

```python
# Track subscription metrics in your system
async def track_subscription_metrics():
    """Track key subscription metrics"""
    
    # Get all active subscriptions
    subscriptions = stripe.Subscription.list(status='active', limit=100)
    
    metrics = {
        'total_active_subscriptions': len(subscriptions.data),
        'mrr_by_tier': {},
        'customer_count_by_tier': {}
    }
    
    for subscription in subscriptions.data:
        price_id = subscription['items']['data'][0]['price']['id']
        amount = subscription['items']['data'][0]['price']['unit_amount'] / 100
        
        # Categorize by tier
        tier = get_tier_from_price_id(price_id)
        
        if tier not in metrics['mrr_by_tier']:
            metrics['mrr_by_tier'][tier] = 0
            metrics['customer_count_by_tier'][tier] = 0
        
        metrics['mrr_by_tier'][tier] += amount
        metrics['customer_count_by_tier'][tier] += 1
    
    # Store metrics in your database
    await store_subscription_metrics(metrics)
    
    return metrics
```

---

## Part 10: Troubleshooting Common Issues

### Failed Webhook Delivery

**If webhooks aren't being received:**

1. Check webhook endpoint URL is correct
2. Verify SSL certificate is valid
3. Ensure endpoint returns 200 status
4. Check Stripe webhook logs for errors
5. Verify webhook secret is correct

### Subscription Not Activating

**If user subscription doesn't activate agents:**

1. Check webhook event was received
2. Verify price_id mapping is correct
3. Check user account creation logic
4. Verify agent activation function
5. Check for any error logs

### Payment Failures

**Handle payment failures gracefully:**

1. Implement retry logic for failed payments
2. Send clear communication to customers
3. Provide grace period before service suspension
4. Offer payment method update options

---

**This completes the comprehensive Stripe integration setup for your AI Marketing System. All subscription tiers, individual packages, and white-label options are now configured with proper webhook handling and customer management.**

**For additional support or custom configurations, refer to the Stripe documentation or contact the development team.**

