# backend/payment.py
import stripe

stripe.api_key = "sk_test_..."

def create_checkout_session(user_email: str, plan: str):
    """Create Stripe checkout session"""
    
    prices = {
        'starter': 'price_starter_id',  # $29/month
        'pro': 'price_pro_id',  # $99/month
        'enterprise': 'price_enterprise_id'  # $299/month
    }
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': prices[plan],
            'quantity': 1,
        }],
        mode='subscription',
        success_url='http://localhost:3000/success',
        cancel_url='http://localhost:3000/cancel',
        customer_email=user_email,
    )
    
    return session.url

# Add to main.py
@app.post("/api/create-checkout-session")
async def create_checkout(email: str, plan: str):
    url = create_checkout_session(email, plan)
    return {'checkout_url': url}