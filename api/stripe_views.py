import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, StripeCustomer, StripeSubscription, StripePayment
import json

# TODO: Set your Stripe secret key in settings.py
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

class CreateCheckoutSessionView(APIView):
    """Create Stripe Checkout Session for Plan Upgrade"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            plan_type = request.data.get('plan_type')  # 'business' or 'enterprise'
            
            if not plan_type or plan_type not in ['business', 'enterprise']:
                return Response(
                    {'error': 'Invalid plan type. Must be "business" or "enterprise"'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user is already on this plan or higher
            current_plan = user.account_type
            if current_plan == plan_type:
                return Response(
                    {'error': f'User is already on {plan_type} plan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if current_plan == 'enterprise':
                return Response(
                    {'error': 'User is already on the highest tier'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create Stripe customer
            stripe_customer, created = StripeCustomer.objects.get_or_create(
                user=user,
                defaults={'stripe_customer_id': ''}
            )
            
            if created or not stripe_customer.stripe_customer_id:
                # Create customer in Stripe
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.profile.first_name or ''} {user.profile.last_name or ''}".strip() or user.email,
                    metadata={'user_id': user.id}
                )
                stripe_customer.stripe_customer_id = customer.id
                stripe_customer.save()
            
            # Get the correct Stripe price ID
            if plan_type == 'business':
                stripe_price_id = settings.STRIPE_BUSINESS_PLAN_PRICE_ID
            else:  # enterprise
                stripe_price_id = settings.STRIPE_ENTERPRISE_PLAN_PRICE_ID
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=stripe_customer.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri(f'/dashboard?upgrade={plan_type}&status=success'),
                cancel_url=request.build_absolute_uri(f'/profile?upgrade={plan_type}&status=cancelled'),
                metadata={
                    'user_id': user.id,
                    'upgrade_type': plan_type
                }
            )
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            })
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            return Response(
                {'error': 'Failed to create checkout session'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stripe_config(request):
    """Get Stripe publishable key and plan information for frontend"""
    return Response({
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'currency': settings.STRIPE_CURRENCY,
        'plans': settings.PLAN_PRICING
    })

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload in webhook")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature in webhook")
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        handle_checkout_session_completed(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    else:
        logger.info(f"Unhandled event type: {event['type']}")
    
    return HttpResponse(status=200)

def handle_checkout_session_completed(session):
    """Handle successful checkout session completion"""
    try:
        user_id = session['metadata'].get('user_id')
        upgrade_type = session['metadata'].get('upgrade_type')  # 'business' or 'enterprise'
        
        if not user_id or not upgrade_type:
            logger.error("Missing user_id or upgrade_type in checkout session metadata")
            return
        
        user = User.objects.get(id=user_id)
        
        # Upgrade user to the selected plan
        user.account_type = upgrade_type
        user.save()
        
        # Get subscription details from Stripe
        subscription_id = session['subscription']
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Create or update StripeSubscription record
        stripe_customer = StripeCustomer.objects.get(user=user)
        stripe_subscription, created = StripeSubscription.objects.update_or_create(
            stripe_subscription_id=subscription_id,
            defaults={
                'user': user,
                'stripe_customer': stripe_customer,
                'status': subscription['status'],
                'current_period_start': subscription['current_period_start'],
                'current_period_end': subscription['current_period_end'],
                'plan_name': upgrade_type
            }
        )
        
        logger.info(f"Successfully upgraded user {user.email} to {upgrade_type} plan")
        
    except User.DoesNotExist:
        logger.error(f"User not found for checkout session: {user_id}")
    except Exception as e:
        logger.error(f"Error handling checkout session completed: {str(e)}")

def handle_invoice_payment_succeeded(invoice):
    """Handle successful subscription payment"""
    try:
        subscription_id = invoice['subscription']
        if not subscription_id:
            return
        
        stripe_subscription = StripeSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        
        # Record the payment
        StripePayment.objects.create(
            stripe_payment_intent_id=invoice['payment_intent'],
            stripe_subscription=stripe_subscription,
            user=stripe_subscription.user,
            amount=invoice['amount_paid'] / 100,  # Convert from cents
            currency=invoice['currency'].upper(),
            status='succeeded',
            payment_type='subscription'
        )
        
        logger.info(f"Recorded payment for subscription {subscription_id}")
        
    except StripeSubscription.DoesNotExist:
        logger.error(f"StripeSubscription not found: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling invoice payment succeeded: {str(e)}")

def handle_subscription_updated(subscription):
    """Handle subscription status changes"""
    try:
        stripe_subscription = StripeSubscription.objects.get(
            stripe_subscription_id=subscription['id']
        )
        
        # Update subscription status
        stripe_subscription.status = subscription['status']
        stripe_subscription.current_period_start = subscription['current_period_start']
        stripe_subscription.current_period_end = subscription['current_period_end']
        stripe_subscription.save()
        
        # If subscription is canceled or unpaid, downgrade user to free
        if subscription['status'] in ['canceled', 'unpaid', 'past_due']:
            user = stripe_subscription.user
            user.account_type = 'free'  # Downgrade to free tier
            user.save()
            logger.info(f"Downgraded user {user.email} to free due to subscription status: {subscription['status']}")
        
    except StripeSubscription.DoesNotExist:
        logger.error(f"StripeSubscription not found: {subscription['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription updated: {str(e)}")

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        stripe_subscription = StripeSubscription.objects.get(
            stripe_subscription_id=subscription['id']
        )
        
        # Downgrade user to free tier
        user = stripe_subscription.user
        user.account_type = 'free'
        user.save()
        
        # Update subscription status
        stripe_subscription.status = 'canceled'
        stripe_subscription.save()
        
        logger.info(f"Downgraded user {user.email} to free due to subscription cancellation")
        
    except StripeSubscription.DoesNotExist:
        logger.error(f"StripeSubscription not found: {subscription['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")
