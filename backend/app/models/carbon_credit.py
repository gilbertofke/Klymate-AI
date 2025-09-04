"""
Carbon Credits Models

This module defines the SQLAlchemy models for the carbon credits system,
including credit rates, user balances, transactions, redemptions, and verification rules.
"""

from sqlalchemy import Column, String, DECIMAL, Integer, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Index
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.base import BaseModel


class RateType(PyEnum):
    """Enumeration for carbon credit rate types"""
    CO2_TO_KC = "co2_to_kc"  # CO2 saved to Klymate Credits
    KC_TO_USD = "kc_to_usd"  # Klymate Credits to USD


class TransactionType(PyEnum):
    """Enumeration for carbon credit transaction types"""
    EARNED = "earned"
    REDEEMED = "redeemed"
    TRANSFERRED = "transferred"
    EXPIRED = "expired"


class VerificationStatus(PyEnum):
    """Enumeration for verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class VerificationMethod(PyEnum):
    """Enumeration for verification methods"""
    AUTOMATIC = "automatic"
    AI_VERIFIED = "ai_verified"
    MANUAL_REVIEW = "manual_review"


class RedemptionType(PyEnum):
    """Enumeration for redemption types"""
    CASH_OUT = "cash_out"
    CARBON_OFFSET = "carbon_offset"
    DONATION = "donation"
    MARKETPLACE = "marketplace"


class RedemptionStatus(PyEnum):
    """Enumeration for redemption status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CarbonCreditRate(BaseModel):
    """
    Model for carbon credit exchange rates
    
    Stores current and historical exchange rates for CO2 to Klymate Credits
    and Klymate Credits to USD conversions.
    """
    __tablename__ = "carbon_credit_rates"

    rate_type = Column(Enum(RateType), nullable=False, index=True)
    rate_value = Column(DECIMAL(10, 6), nullable=False)
    effective_date = Column(DateTime, nullable=False, default=func.now())
    source = Column(String(255))  # Market source or manual
    
    __table_args__ = (
        Index('idx_rate_date', 'rate_type', 'effective_date'),
    )

    def __repr__(self):
        return f"<CarbonCreditRate(rate_type={self.rate_type.value}, rate_value={self.rate_value}, effective_date={self.effective_date})>"


class UserCarbonCredits(BaseModel):
    """
    Model for user carbon credit balances
    
    Tracks current balance and lifetime totals for each user.
    """
    __tablename__ = "user_carbon_credits"

    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)
    current_balance = Column(DECIMAL(12, 4), default=0, nullable=False)
    total_earned = Column(DECIMAL(12, 4), default=0, nullable=False)
    total_redeemed = Column(DECIMAL(12, 4), default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="carbon_credits")
    transactions = relationship("CarbonCreditTransaction", foreign_keys="CarbonCreditTransaction.user_id", primaryjoin="UserCarbonCredits.user_id == CarbonCreditTransaction.user_id")

    def __repr__(self):
        return f"<UserCarbonCredits(user_id={self.user_id}, current_balance={self.current_balance})>"


class CarbonCreditTransaction(BaseModel):
    """
    Model for carbon credit transactions
    
    Records all credit transactions including earning, redemption, transfers, and expirations.
    Includes verification status and blockchain-style transaction hashing.
    """
    __tablename__ = "carbon_credit_transactions"

    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(DECIMAL(12, 4), nullable=False)
    co2_saved = Column(DECIMAL(8, 4))  # For earned credits
    activity_reference = Column(CHAR(36))  # Reference to habit log or activity
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    verification_method = Column(Enum(VerificationMethod), default=VerificationMethod.AUTOMATIC)
    verification_metadata = Column(JSON)
    transaction_hash = Column(String(64))  # Blockchain-style verification
    exchange_rate = Column(DECIMAL(10, 6))  # KC to USD rate at time of transaction
    usd_value = Column(DECIMAL(10, 2))  # Monetary value at time of transaction
    notes = Column(Text)
    verified_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    user_credits = relationship("UserCarbonCredits", foreign_keys=[user_id], primaryjoin="CarbonCreditTransaction.user_id == UserCarbonCredits.user_id")
    redemption = relationship("CarbonCreditRedemption", back_populates="transaction", uselist=False)
    
    __table_args__ = (
        Index('idx_user_transactions', 'user_id', 'created_at'),
        Index('idx_verification_status', 'verification_status'),
        Index('idx_transaction_type', 'transaction_type', 'created_at'),
    )

    def __repr__(self):
        return f"<CarbonCreditTransaction(user_id={self.user_id}, type={self.transaction_type.value}, amount={self.amount})>"


class CarbonCreditRedemption(BaseModel):
    """
    Model for carbon credit redemptions
    
    Tracks redemption requests for cash-outs, carbon offsets, donations, and marketplace transactions.
    """
    __tablename__ = "carbon_credit_redemptions"

    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)
    transaction_id = Column(CHAR(36), ForeignKey('carbon_credit_transactions.id'), nullable=False)
    redemption_type = Column(Enum(RedemptionType), nullable=False)
    amount_kc = Column(DECIMAL(12, 4), nullable=False)
    amount_usd = Column(DECIMAL(10, 2), nullable=False)
    recipient_info = Column(JSON)  # Payment details, offset certificate info, etc.
    status = Column(Enum(RedemptionStatus), default=RedemptionStatus.PENDING)
    external_reference = Column(String(255))  # Payment processor reference
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    transaction = relationship("CarbonCreditTransaction", back_populates="redemption")
    
    __table_args__ = (
        Index('idx_user_redemptions', 'user_id', 'created_at'),
        Index('idx_status', 'status'),
    )

    def __repr__(self):
        return f"<CarbonCreditRedemption(user_id={self.user_id}, type={self.redemption_type.value}, amount_kc={self.amount_kc})>"


class CarbonVerificationRule(BaseModel):
    """
    Model for carbon verification rules
    
    Defines verification requirements and credit multipliers for different activity types.
    """
    __tablename__ = "carbon_verification_rules"

    activity_type = Column(String(100), nullable=False, index=True)
    min_amount = Column(DECIMAL(8, 4))  # Minimum CO2 saved for automatic verification
    max_amount = Column(DECIMAL(8, 4))  # Maximum for automatic verification
    verification_method = Column(Enum(VerificationMethod), nullable=False)
    credit_multiplier = Column(DECIMAL(4, 2), default=1.0)  # Bonus/penalty multiplier
    requires_evidence = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_activity_type', 'activity_type'),
    )

    def __repr__(self):
        return f"<CarbonVerificationRule(activity_type={self.activity_type}, verification_method={self.verification_method.value})>"

    def is_automatic_verification_eligible(self, co2_amount: float) -> bool:
        """
        Check if a CO2 amount is eligible for automatic verification
        
        Args:
            co2_amount: Amount of CO2 saved in kg
            
        Returns:
            True if eligible for automatic verification, False otherwise
        """
        if not self.active:
            return False
            
        if self.verification_method != VerificationMethod.AUTOMATIC:
            return False
            
        if self.min_amount and co2_amount < float(self.min_amount):
            return False
            
        if self.max_amount and co2_amount > float(self.max_amount):
            return False
            
        return True

    def calculate_credits(self, co2_amount: float, base_rate: float) -> float:
        """
        Calculate carbon credits for a given CO2 amount
        
        Args:
            co2_amount: Amount of CO2 saved in kg
            base_rate: Base conversion rate from CO2 to credits
            
        Returns:
            Number of credits to award
        """
        base_credits = co2_amount * base_rate
        return base_credits * float(self.credit_multiplier)