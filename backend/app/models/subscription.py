"""
Subscription and payment models.
"""
from datetime import datetime, date
from sqlalchemy import (
    Column,
    DateTime,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Subscription(Base):
    """Subscription model for writer support and premium features."""

    __tablename__ = "subscriptions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    subscriber_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    writer_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )  # Null for platform subscriptions

    # Stripe
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Subscription Details
    subscription_type = Column(
        String(30), nullable=False
    )  # premium_reader, premium_writer, writer_support
    status = Column(
        String(20), default="active", nullable=False, index=True
    )  # active, canceled, past_due, incomplete

    # Pricing
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Billing
    billing_interval = Column(
        String(20), default="monthly", nullable=False
    )  # monthly, yearly
    current_period_start = Column(Date, nullable=True)
    current_period_end = Column(Date, nullable=True)
    next_billing_date = Column(Date, nullable=True)

    # Trial
    trial_start = Column(Date, nullable=True)
    trial_end = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    subscriber = relationship(
        "User", foreign_keys=[subscriber_id], back_populates="subscriptions"
    )
    writer = relationship("User", foreign_keys=[writer_id])
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Subscription {self.subscription_type} - {self.status}>"


class Payment(Base):
    """Payment model for tracking all transactions."""

    __tablename__ = "payments"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    subscription_id = Column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True, index=True
    )
    writer_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )  # For direct writer support

    # Stripe
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)

    # Payment Details
    payment_type = Column(
        String(30), nullable=False
    )  # subscription, donation, article_purchase
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, succeeded, failed, refunded

    # Amount
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    platform_fee_cents = Column(Integer, default=0, nullable=False)
    writer_amount_cents = Column(Integer, default=0, nullable=False)

    # Tax
    tax_amount_cents = Column(Integer, default=0, nullable=False)

    # Metadata
    description = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON stored as text

    # Refund
    refunded = Column(Integer, default=0, nullable=False)  # 0 = no, 1 = yes
    refund_amount_cents = Column(Integer, default=0, nullable=False)
    refund_reason = Column(Text, nullable=True)

    # Payout
    payout_status = Column(
        String(20), default="pending", nullable=False
    )  # pending, processing, paid, failed
    payout_date = Column(Date, nullable=True)
    payout_id = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    subscription = relationship("Subscription", back_populates="payments")
    writer = relationship("User", foreign_keys=[writer_id])

    def __repr__(self) -> str:
        return f"<Payment {self.amount_cents} {self.currency} - {self.status}>"
