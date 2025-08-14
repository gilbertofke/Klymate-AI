"""
Tests for Carbon Credit Models

This module contains unit tests for carbon credit models and their methods.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonCreditRedemption, CarbonVerificationRule,
    RateType, TransactionType, VerificationStatus, VerificationMethod,
    RedemptionType, RedemptionStatus
)
from app.models.user import User
from tests.factories import UserFactory


class TestCarbonCreditRate:
    """Test cases for CarbonCreditRate model"""
    
    def test_create_carbon_credit_rate(self, db_session: Session):
        """Test creating a carbon credit rate"""
        rate = CarbonCreditRate(
            rate_type=RateType.CO2_TO_KC,
            rate_value=Decimal('1.0'),
            source='test_source',
            effective_date=datetime.utcnow()
        )
        
        db_session.add(rate)
        db_session.commit()
        
        assert rate.id is not None
        assert rate.rate_type == RateType.CO2_TO_KC
        assert rate.rate_value == Decimal('1.0')
        assert rate.source == 'test_source'
        assert rate.created_at is not None
    
    def test_rate_repr(self, db_session: Session):
        """Test string representation of rate"""
        rate = CarbonCreditRate(
            rate_type=RateType.KC_TO_USD,
            rate_value=Decimal('0.05'),
            effective_date=datetime.utcnow()
        )
        
        repr_str = repr(rate)
        assert 'CarbonCreditRate' in repr_str
        assert 'kc_to_usd' in repr_str
        assert '0.05' in repr_str


class TestUserCarbonCredits:
    """Test cases for UserCarbonCredits model"""
    
    def test_create_user_carbon_credits(self, db_session: Session):
        """Test creating user carbon credits"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        credits = UserCarbonCredits(
            user_id=user.id,
            current_balance=Decimal('100.0'),
            total_earned=Decimal('150.0'),
            total_redeemed=Decimal('50.0')
        )
        
        db_session.add(credits)
        db_session.commit()
        
        assert credits.id is not None
        assert credits.user_id == user.id
        assert credits.current_balance == Decimal('100.0')
        assert credits.total_earned == Decimal('150.0')
        assert credits.total_redeemed == Decimal('50.0')
    
    def test_user_relationship(self, db_session: Session):
        """Test relationship with User model"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        credits = UserCarbonCredits(
            user_id=user.id,
            current_balance=Decimal('50.0')
        )
        
        db_session.add(credits)
        db_session.commit()
        
        # Test relationship
        assert credits.user == user
        assert user.carbon_credits == credits
    
    def test_credits_repr(self, db_session: Session):
        """Test string representation of user credits"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        credits = UserCarbonCredits(
            user_id=user.id,
            current_balance=Decimal('75.5')
        )
        
        repr_str = repr(credits)
        assert 'UserCarbonCredits' in repr_str
        assert user.id in repr_str
        assert '75.5' in repr_str


class TestCarbonCreditTransaction:
    """Test cases for CarbonCreditTransaction model"""
    
    def test_create_transaction(self, db_session: Session):
        """Test creating a carbon credit transaction"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        transaction = CarbonCreditTransaction(
            user_id=user.id,
            transaction_type=TransactionType.EARNED,
            amount=Decimal('10.0'),
            co2_saved=Decimal('10.0'),
            verification_status=VerificationStatus.VERIFIED,
            verification_method=VerificationMethod.AUTOMATIC,
            transaction_hash='test_hash_123',
            exchange_rate=Decimal('0.05'),
            usd_value=Decimal('0.50'),
            notes='Test transaction'
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        assert transaction.id is not None
        assert transaction.user_id == user.id
        assert transaction.transaction_type == TransactionType.EARNED
        assert transaction.amount == Decimal('10.0')
        assert transaction.co2_saved == Decimal('10.0')
        assert transaction.verification_status == VerificationStatus.VERIFIED
        assert transaction.verification_method == VerificationMethod.AUTOMATIC
        assert transaction.transaction_hash == 'test_hash_123'
        assert transaction.exchange_rate == Decimal('0.05')
        assert transaction.usd_value == Decimal('0.50')
        assert transaction.notes == 'Test transaction'
    
    def test_transaction_with_metadata(self, db_session: Session):
        """Test transaction with verification metadata"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        metadata = {
            'verification_source': 'ai_analysis',
            'confidence_score': 0.95,
            'evidence_urls': ['https://example.com/photo1.jpg']
        }
        
        transaction = CarbonCreditTransaction(
            user_id=user.id,
            transaction_type=TransactionType.EARNED,
            amount=Decimal('5.0'),
            verification_metadata=metadata
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        assert transaction.verification_metadata == metadata
        assert transaction.verification_metadata['confidence_score'] == 0.95
    
    def test_transaction_repr(self, db_session: Session):
        """Test string representation of transaction"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        transaction = CarbonCreditTransaction(
            user_id=user.id,
            transaction_type=TransactionType.REDEEMED,
            amount=Decimal('25.0')
        )
        
        repr_str = repr(transaction)
        assert 'CarbonCreditTransaction' in repr_str
        assert user.id in repr_str
        assert 'redeemed' in repr_str
        assert '25.0' in repr_str


class TestCarbonCreditRedemption:
    """Test cases for CarbonCreditRedemption model"""
    
    def test_create_redemption(self, db_session: Session):
        """Test creating a carbon credit redemption"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        transaction = CarbonCreditTransaction(
            user_id=user.id,
            transaction_type=TransactionType.REDEEMED,
            amount=Decimal('20.0')
        )
        db_session.add(transaction)
        db_session.commit()
        
        recipient_info = {
            'payment_method': 'paypal',
            'email': 'user@example.com',
            'account_id': 'paypal_123'
        }
        
        redemption = CarbonCreditRedemption(
            user_id=user.id,
            transaction_id=transaction.id,
            redemption_type=RedemptionType.CASH_OUT,
            amount_kc=Decimal('20.0'),
            amount_usd=Decimal('1.00'),
            recipient_info=recipient_info,
            status=RedemptionStatus.PENDING,
            external_reference='paypal_txn_456'
        )
        
        db_session.add(redemption)
        db_session.commit()
        
        assert redemption.id is not None
        assert redemption.user_id == user.id
        assert redemption.transaction_id == transaction.id
        assert redemption.redemption_type == RedemptionType.CASH_OUT
        assert redemption.amount_kc == Decimal('20.0')
        assert redemption.amount_usd == Decimal('1.00')
        assert redemption.recipient_info == recipient_info
        assert redemption.status == RedemptionStatus.PENDING
        assert redemption.external_reference == 'paypal_txn_456'
    
    def test_redemption_relationships(self, db_session: Session):
        """Test redemption relationships"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        transaction = CarbonCreditTransaction(
            user_id=user.id,
            transaction_type=TransactionType.REDEEMED,
            amount=Decimal('15.0')
        )
        db_session.add(transaction)
        db_session.commit()
        
        redemption = CarbonCreditRedemption(
            user_id=user.id,
            transaction_id=transaction.id,
            redemption_type=RedemptionType.CARBON_OFFSET,
            amount_kc=Decimal('15.0'),
            amount_usd=Decimal('0.75')
        )
        db_session.add(redemption)
        db_session.commit()
        
        # Test relationships
        assert redemption.user == user
        assert redemption.transaction == transaction
        assert transaction.redemption == redemption
    
    def test_redemption_repr(self, db_session: Session):
        """Test string representation of redemption"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        redemption = CarbonCreditRedemption(
            user_id=user.id,
            transaction_id='test_transaction_id',
            redemption_type=RedemptionType.DONATION,
            amount_kc=Decimal('30.0'),
            amount_usd=Decimal('1.50')
        )
        
        repr_str = repr(redemption)
        assert 'CarbonCreditRedemption' in repr_str
        assert user.id in repr_str
        assert 'donation' in repr_str
        assert '30.0' in repr_str


class TestCarbonVerificationRule:
    """Test cases for CarbonVerificationRule model"""
    
    def test_create_verification_rule(self, db_session: Session):
        """Test creating a verification rule"""
        rule = CarbonVerificationRule(
            activity_type='cycling',
            verification_method=VerificationMethod.AUTOMATIC,
            min_amount=Decimal('0.1'),
            max_amount=Decimal('20.0'),
            credit_multiplier=Decimal('1.2'),
            requires_evidence=False,
            active=True
        )
        
        db_session.add(rule)
        db_session.commit()
        
        assert rule.id is not None
        assert rule.activity_type == 'cycling'
        assert rule.verification_method == VerificationMethod.AUTOMATIC
        assert rule.min_amount == Decimal('0.1')
        assert rule.max_amount == Decimal('20.0')
        assert rule.credit_multiplier == Decimal('1.2')
        assert rule.requires_evidence is False
        assert rule.active is True
    
    def test_is_automatic_verification_eligible(self, db_session: Session):
        """Test automatic verification eligibility check"""
        rule = CarbonVerificationRule(
            activity_type='walking',
            verification_method=VerificationMethod.AUTOMATIC,
            min_amount=Decimal('0.5'),
            max_amount=Decimal('10.0'),
            active=True
        )
        
        # Test eligible amount
        assert rule.is_automatic_verification_eligible(5.0) is True
        
        # Test amount too small
        assert rule.is_automatic_verification_eligible(0.1) is False
        
        # Test amount too large
        assert rule.is_automatic_verification_eligible(15.0) is False
        
        # Test inactive rule
        rule.active = False
        assert rule.is_automatic_verification_eligible(5.0) is False
        
        # Test non-automatic method
        rule.active = True
        rule.verification_method = VerificationMethod.MANUAL_REVIEW
        assert rule.is_automatic_verification_eligible(5.0) is False
    
    def test_calculate_credits(self, db_session: Session):
        """Test credit calculation with multiplier"""
        rule = CarbonVerificationRule(
            activity_type='composting',
            verification_method=VerificationMethod.AUTOMATIC,
            credit_multiplier=Decimal('1.5')  # 50% bonus
        )
        
        base_rate = 1.0  # 1 kg CO2 = 1 credit
        co2_amount = 10.0  # 10 kg CO2 saved
        
        credits = rule.calculate_credits(co2_amount, base_rate)
        expected_credits = 10.0 * 1.0 * 1.5  # 15.0 credits
        
        assert credits == expected_credits
    
    def test_calculate_credits_no_multiplier(self, db_session: Session):
        """Test credit calculation without multiplier"""
        rule = CarbonVerificationRule(
            activity_type='recycling',
            verification_method=VerificationMethod.AUTOMATIC,
            credit_multiplier=Decimal('1.0')  # No bonus
        )
        
        base_rate = 1.0
        co2_amount = 5.0
        
        credits = rule.calculate_credits(co2_amount, base_rate)
        expected_credits = 5.0 * 1.0 * 1.0  # 5.0 credits
        
        assert credits == expected_credits
    
    def test_verification_rule_repr(self, db_session: Session):
        """Test string representation of verification rule"""
        rule = CarbonVerificationRule(
            activity_type='solar_installation',
            verification_method=VerificationMethod.MANUAL_REVIEW
        )
        
        repr_str = repr(rule)
        assert 'CarbonVerificationRule' in repr_str
        assert 'solar_installation' in repr_str
        assert 'manual_review' in repr_str


class TestCarbonCreditEnums:
    """Test cases for carbon credit enums"""
    
    def test_rate_type_enum(self):
        """Test RateType enum values"""
        assert RateType.CO2_TO_KC.value == 'co2_to_kc'
        assert RateType.KC_TO_USD.value == 'kc_to_usd'
    
    def test_transaction_type_enum(self):
        """Test TransactionType enum values"""
        assert TransactionType.EARNED.value == 'earned'
        assert TransactionType.REDEEMED.value == 'redeemed'
        assert TransactionType.TRANSFERRED.value == 'transferred'
        assert TransactionType.EXPIRED.value == 'expired'
    
    def test_verification_status_enum(self):
        """Test VerificationStatus enum values"""
        assert VerificationStatus.PENDING.value == 'pending'
        assert VerificationStatus.VERIFIED.value == 'verified'
        assert VerificationStatus.REJECTED.value == 'rejected'
    
    def test_verification_method_enum(self):
        """Test VerificationMethod enum values"""
        assert VerificationMethod.AUTOMATIC.value == 'automatic'
        assert VerificationMethod.AI_VERIFIED.value == 'ai_verified'
        assert VerificationMethod.MANUAL_REVIEW.value == 'manual_review'
    
    def test_redemption_type_enum(self):
        """Test RedemptionType enum values"""
        assert RedemptionType.CASH_OUT.value == 'cash_out'
        assert RedemptionType.CARBON_OFFSET.value == 'carbon_offset'
        assert RedemptionType.DONATION.value == 'donation'
        assert RedemptionType.MARKETPLACE.value == 'marketplace'
    
    def test_redemption_status_enum(self):
        """Test RedemptionStatus enum values"""
        assert RedemptionStatus.PENDING.value == 'pending'
        assert RedemptionStatus.PROCESSING.value == 'processing'
        assert RedemptionStatus.COMPLETED.value == 'completed'
        assert RedemptionStatus.FAILED.value == 'failed'