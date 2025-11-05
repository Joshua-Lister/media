"""
Payment service using Stripe.

**IMPORTANT: UPDATE STRIPE KEYS**
Before using this service, update your .env file with:
- STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key (get from https://dashboard.stripe.com/apikeys)
- STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
- STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret (create webhook endpoint)

Test mode keys start with sk_test_ and pk_test_
Live mode keys start with sk_live_ and pk_live_
"""
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, date
import stripe

from app.core.config import settings
from app.models.subscription import Subscription, Payment
from app.models.user import User

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Service for payment operations using Stripe."""

    @staticmethod
    async def create_customer(user: User) -> str:
        """
        Create a Stripe customer for a user.

        **REQUIRES: STRIPE_SECRET_KEY in .env**

        Args:
            user: User to create customer for

        Returns:
            str: Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name or user.username,
                metadata={"user_id": str(user.id)},
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    async def create_subscription(
        db: AsyncSession,
        user: User,
        price_id: str,
        writer_id: Optional[UUID] = None,
    ) -> Subscription:
        """
        Create a subscription.

        **REQUIRES: STRIPE_SECRET_KEY in .env**

        Args:
            db: Database session
            user: Subscriber user
            price_id: Stripe price ID
            writer_id: Optional writer to subscribe to

        Returns:
            Subscription: Created subscription
        """
        try:
            # Create or get customer
            if not hasattr(user, "stripe_customer_id"):
                customer_id = await PaymentService.create_customer(user)
            else:
                customer_id = user.stripe_customer_id

            # Create subscription in Stripe
            stripe_sub = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )

            # Determine subscription type and amount
            price = stripe.Price.retrieve(price_id)
            amount_cents = price.unit_amount
            subscription_type = "premium_reader"  # Default

            if writer_id:
                subscription_type = "writer_support"

            # Create subscription in database
            subscription = Subscription(
                subscriber_id=user.id,
                writer_id=writer_id,
                stripe_subscription_id=stripe_sub.id,
                stripe_customer_id=customer_id,
                subscription_type=subscription_type,
                status=stripe_sub.status,
                amount_cents=amount_cents,
                currency=price.currency.upper(),
                billing_interval="monthly" if price.recurring.interval == "month" else "yearly",
                current_period_start=date.fromtimestamp(stripe_sub.current_period_start),
                current_period_end=date.fromtimestamp(stripe_sub.current_period_end),
            )

            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)

            return subscription

        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    async def create_payment_intent(
        db: AsyncSession,
        user: User,
        amount_cents: int,
        currency: str = "usd",
        writer_id: Optional[UUID] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Create a one-time payment intent (for donations).

        **REQUIRES: STRIPE_SECRET_KEY in .env**

        Args:
            db: Database session
            user: User making payment
            amount_cents: Amount in cents
            currency: Currency code
            writer_id: Optional writer receiving payment
            description: Payment description

        Returns:
            Dict with payment intent details
        """
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    "user_id": str(user.id),
                    "writer_id": str(writer_id) if writer_id else None,
                },
                description=description or "One-time payment",
            )

            # Calculate platform fee and writer amount
            platform_fee_cents = int(amount_cents * settings.PLATFORM_FEE_PERCENTAGE / 100)
            writer_amount_cents = amount_cents - platform_fee_cents

            # Create payment record
            payment = Payment(
                user_id=user.id,
                writer_id=writer_id,
                stripe_payment_intent_id=intent.id,
                payment_type="donation",
                status="pending",
                amount_cents=amount_cents,
                currency=currency.upper(),
                platform_fee_cents=platform_fee_cents,
                writer_amount_cents=writer_amount_cents,
                description=description,
            )

            db.add(payment)
            await db.commit()

            return {
                "client_secret": intent.client_secret,
                "payment_id": str(payment.id),
            }

        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    async def cancel_subscription(
        db: AsyncSession, subscription: Subscription
    ) -> Subscription:
        """
        Cancel a subscription.

        **REQUIRES: STRIPE_SECRET_KEY in .env**

        Args:
            db: Database session
            subscription: Subscription to cancel

        Returns:
            Subscription: Canceled subscription
        """
        try:
            # Cancel in Stripe
            stripe.Subscription.delete(subscription.stripe_subscription_id)

            # Update in database
            subscription.status = "canceled"
            subscription.canceled_at = datetime.utcnow()
            await db.commit()
            await db.refresh(subscription)

            return subscription

        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    async def handle_webhook(
        db: AsyncSession, payload: bytes, sig_header: str
    ) -> Dict:
        """
        Handle Stripe webhook events.

        **REQUIRES: STRIPE_WEBHOOK_SECRET in .env**

        Args:
            db: Database session
            payload: Webhook payload
            sig_header: Stripe signature header

        Returns:
            Dict with processing result
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )

            # Handle different event types
            if event.type == "payment_intent.succeeded":
                payment_intent = event.data.object
                await PaymentService._handle_successful_payment(db, payment_intent)

            elif event.type == "payment_intent.payment_failed":
                payment_intent = event.data.object
                await PaymentService._handle_failed_payment(db, payment_intent)

            elif event.type == "customer.subscription.updated":
                subscription = event.data.object
                await PaymentService._handle_subscription_update(db, subscription)

            elif event.type == "customer.subscription.deleted":
                subscription = event.data.object
                await PaymentService._handle_subscription_deletion(db, subscription)

            return {"status": "success", "event": event.type}

        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid webhook signature")

    @staticmethod
    async def _handle_successful_payment(db: AsyncSession, payment_intent: Dict):
        """Handle successful payment."""
        from sqlalchemy import select

        result = await db.execute(
            select(Payment).where(
                Payment.stripe_payment_intent_id == payment_intent.id
            )
        )
        payment = result.scalar_one_or_none()

        if payment:
            payment.status = "succeeded"
            payment.stripe_charge_id = payment_intent.charges.data[0].id
            await db.commit()

    @staticmethod
    async def _handle_failed_payment(db: AsyncSession, payment_intent: Dict):
        """Handle failed payment."""
        from sqlalchemy import select

        result = await db.execute(
            select(Payment).where(
                Payment.stripe_payment_intent_id == payment_intent.id
            )
        )
        payment = result.scalar_one_or_none()

        if payment:
            payment.status = "failed"
            await db.commit()

    @staticmethod
    async def _handle_subscription_update(db: AsyncSession, stripe_sub: Dict):
        """Handle subscription update."""
        from sqlalchemy import select

        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub.id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = stripe_sub.status
            subscription.current_period_start = date.fromtimestamp(
                stripe_sub.current_period_start
            )
            subscription.current_period_end = date.fromtimestamp(
                stripe_sub.current_period_end
            )
            await db.commit()

    @staticmethod
    async def _handle_subscription_deletion(db: AsyncSession, stripe_sub: Dict):
        """Handle subscription deletion."""
        from sqlalchemy import select

        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub.id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = "canceled"
            subscription.canceled_at = datetime.utcnow()
            await db.commit()

    @staticmethod
    def get_publishable_key() -> str:
        """
        Get Stripe publishable key for frontend.

        Returns:
            str: Stripe publishable key
        """
        return settings.STRIPE_PUBLISHABLE_KEY
