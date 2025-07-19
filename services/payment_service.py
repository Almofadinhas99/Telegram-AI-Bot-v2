import logging
import stripe
from typing import Dict, Any, Optional
from config.settings import settings
from models.user import UserPlan

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        stripe.api_key = settings.stripe_secret_key
        self.webhook_secret = settings.stripe_webhook_secret

    async def create_checkout_session(
        self,
        user_id: int,
        plan: UserPlan,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """Create Stripe checkout session for subscription"""
        
        try:
            # Plan pricing mapping
            plan_prices = {
                UserPlan.FREE: None,  # Free plan
                UserPlan.STARTER: "price_starter_999",  # $9.99/month
                UserPlan.PRO: "price_pro_1999",        # $19.99/month
                UserPlan.PREMIUM: "price_premium_5999", # $59.99/month
                UserPlan.ULTIMATE: "price_ultimate_14999" # $149.99/month
            }
            
            if plan == UserPlan.FREE:
                return {
                    "success": False,
                    "error": "Cannot create checkout for free plan"
                }
            
            price_id = plan_prices.get(plan)
            if not price_id:
                return {
                    "success": False,
                    "error": f"Price not found for plan: {plan}"
                }
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user_id),
                metadata={
                    'user_id': user_id,
                    'plan': plan.value
                }
            )
            
            return {
                "success": True,
                "checkout_url": session.url,
                "session_id": session.id
            }
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_products_and_prices(self) -> Dict[str, Any]:
        """Create Stripe products and prices (run once during setup)"""
        
        try:
            plans = [
                {
                    "name": "Starter Plan",
                    "description": "50 GPT-4o msgs/day, 15 images/month, 3 music/month",
                    "price": 999,  # $9.99 in cents
                    "price_id": "price_starter_999"
                },
                {
                    "name": "Pro Plan", 
                    "description": "100 GPT-4o msgs/day, 50 images/month, 10 music/month, 5 videos/month",
                    "price": 1999,  # $19.99 in cents
                    "price_id": "price_pro_1999"
                },
                {
                    "name": "Premium Plan",
                    "description": "100 GPT-4 msgs/day, 100 images/month, 20 music/month, 10 videos/month",
                    "price": 5999,  # $59.99 in cents
                    "price_id": "price_premium_5999"
                },
                {
                    "name": "Ultimate Plan",
                    "description": "200 GPT-4 msgs/day, 200 images/month, 30 music/month, 20 videos/month, Claude 1M tokens",
                    "price": 14999,  # $149.99 in cents
                    "price_id": "price_ultimate_14999"
                }
            ]
            
            created_products = []
            
            for plan in plans:
                # Create product
                product = stripe.Product.create(
                    name=plan["name"],
                    description=plan["description"],
                    metadata={
                        "plan_type": plan["price_id"]
                    }
                )
                
                # Create price
                price = stripe.Price.create(
                    unit_amount=plan["price"],
                    currency='usd',
                    recurring={'interval': 'month'},
                    product=product.id,
                    lookup_key=plan["price_id"]
                )
                
                created_products.append({
                    "product_id": product.id,
                    "price_id": price.id,
                    "lookup_key": plan["price_id"],
                    "amount": plan["price"]
                })
            
            return {
                "success": True,
                "products": created_products
            }
            
        except Exception as e:
            logger.error(f"Error creating products and prices: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_webhook(self, payload: str, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                
                # Get user info from session
                user_id = int(session['client_reference_id'])
                plan_name = session['metadata']['plan']
                
                return {
                    "success": True,
                    "event_type": "subscription_created",
                    "user_id": user_id,
                    "plan": plan_name,
                    "subscription_id": session.get('subscription')
                }
                
            elif event['type'] == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                
                return {
                    "success": True,
                    "event_type": "payment_succeeded",
                    "subscription_id": invoice['subscription'],
                    "amount_paid": invoice['amount_paid']
                }
                
            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                
                return {
                    "success": True,
                    "event_type": "payment_failed",
                    "subscription_id": invoice['subscription']
                }
                
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                
                return {
                    "success": True,
                    "event_type": "subscription_cancelled",
                    "subscription_id": subscription['id']
                }
            
            return {
                "success": True,
                "event_type": "unhandled",
                "type": event['type']
            }
            
        except ValueError as e:
            logger.error(f"Invalid payload in webhook: {e}")
            return {
                "success": False,
                "error": "Invalid payload"
            }
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature in webhook: {e}")
            return {
                "success": False,
                "error": "Invalid signature"
            }
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_subscription_status(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription status from Stripe"""
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "success": True,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription status: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel subscription at period end"""
        
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            return {
                "success": True,
                "cancelled_at": subscription.canceled_at,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_plan_features(self, plan: UserPlan) -> Dict[str, Any]:
        """Get plan features and limits"""
        
        features = {
            UserPlan.FREE: {
                "name": "🆓 Free",
                "price": "$0/mês",
                "daily_gpt4o_messages": 5,
                "daily_gpt4_messages": 0,
                "monthly_images": 3,
                "monthly_music": 1,
                "monthly_videos": 0,
                "monthly_claude_tokens": 0,
                "features": [
                    "✅ 5 mensagens GPT-4o por dia",
                    "✅ 3 imagens por mês (FLUX Schnell)",
                    "✅ 1 música por mês",
                    "❌ Sem vídeos",
                    "❌ Sem Claude",
                    "❌ Sem GPT-4"
                ]
            },
            UserPlan.STARTER: {
                "name": "🚀 Starter",
                "price": "$9.99/mês",
                "daily_gpt4o_messages": 50,
                "daily_gpt4_messages": 0,
                "monthly_images": 15,
                "monthly_music": 3,
                "monthly_videos": 0,
                "monthly_claude_tokens": 0,
                "features": [
                    "✅ 50 mensagens GPT-4o por dia",
                    "✅ 15 imagens por mês (FLUX Schnell)",
                    "✅ 3 músicas por mês",
                    "❌ Sem vídeos",
                    "❌ Sem Claude",
                    "❌ Sem GPT-4"
                ]
            },
            UserPlan.PRO: {
                "name": "💼 Pro",
                "price": "$19.99/mês",
                "daily_gpt4o_messages": 100,
                "daily_gpt4_messages": 0,
                "monthly_images": 50,
                "monthly_music": 10,
                "monthly_videos": 5,
                "monthly_claude_tokens": 0,
                "features": [
                    "✅ 100 mensagens GPT-4o por dia",
                    "✅ 50 imagens por mês (FLUX Dev)",
                    "✅ 10 músicas por mês",
                    "✅ 5 vídeos por mês",
                    "❌ Sem Claude",
                    "❌ Sem GPT-4"
                ]
            },
            UserPlan.PREMIUM: {
                "name": "⭐ Premium",
                "price": "$59.99/mês",
                "daily_gpt4o_messages": 50,
                "daily_gpt4_messages": 100,
                "monthly_images": 100,
                "monthly_music": 20,
                "monthly_videos": 10,
                "monthly_claude_tokens": 0,
                "features": [
                    "✅ 50 mensagens GPT-4o por dia",
                    "✅ 100 mensagens GPT-4 por dia",
                    "✅ 100 imagens por mês (FLUX Pro)",
                    "✅ 20 músicas por mês",
                    "✅ 10 vídeos por mês",
                    "❌ Sem Claude"
                ]
            },
            UserPlan.ULTIMATE: {
                "name": "👑 Ultimate",
                "price": "$149.99/mês",
                "daily_gpt4o_messages": 100,
                "daily_gpt4_messages": 200,
                "monthly_images": 200,
                "monthly_music": 30,
                "monthly_videos": 20,
                "monthly_claude_tokens": 1000000,
                "features": [
                    "✅ 100 mensagens GPT-4o por dia",
                    "✅ 200 mensagens GPT-4 por dia",
                    "✅ 200 imagens por mês (FLUX Pro)",
                    "✅ 30 músicas por mês",
                    "✅ 20 vídeos por mês",
                    "✅ Claude 1M tokens por mês"
                ]
            }
        }
        
        return features.get(plan, features[UserPlan.FREE])

