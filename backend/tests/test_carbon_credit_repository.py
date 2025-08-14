"""
Tests for Carbon Credit Repository

This module contains unit tests for carbon credit repository operations.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.repositories.carbon_credit_repository import (
    CarbonCreditRepository, UserCarbonCreditsRepository,
    CarbonCreditTransactionRepository, CarbonVerificationRuleRepository
)
from app.models.carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonVerificationRule, RateType, TransactionType, VerificationStatus,
    VerificationMethod
)
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError
from tests.factories import (
    UserFactory, CarbonCreditRateFactory, UserCarbonCreditsFactory,
    CarbonCreditTransactionFactory, CarbonVerificationRuleFactory
)


class TestCarbonCreditRepository:
    """Test cases for CarbonCreditRepository"""
    
    @pytest.fixture
    def repository(self, db_session: Session):
        """Create repository instance"""
        return CarbonCreditRepository(db_session)
    
    async def test_get_current_rate(self, repository: CarbonCreditRepository, db_session: Session):
        """Test getting current exchange rate"""
        # Create rates with different effective dates
        old_rate = CarbonCreditRateFactory(
            rate_type=RateType.CO2_TO_KC,
            rate_value=Decimal('0.8'),
            effective_date=datetime.utcnow() - timedelta(days=10)
        )
        current_rate = CarbonCreditRateFactory(
            rate_type=RateType.CO2_TO_KC,
            rate_value=Decimal('1.0'),
            effective_date=datetime.utcnow() - timedelta(days=1)
        )
        future_rate = CarbonCreditRateFactory(
            rate_type=RateType.CO2_TO_KC,
            rate_value=Decimal('1.2'),
            effective_date=datetime.utcnow() + timedelta(days=1)
        )
        
        db_session.add_all([old_rate, current_rate, future_rate])
        db_session.commit()
        
        # Should return the most recent rate that's effective
        result = await repository.get_current_rate(RateType.CO2_TO_KC)
        
        assert result is not None
        assert result.rate_value == Decimal('1.0')
        assert result.id == current_rate.id
    
    async def test_get_current_rate_not_found(self, repository: CarbonCreditRepository):
        """Test getting current rate when none exists"""
        result = await repository.get_current_rate(RateType.KC_TO_USD)
        assert result is None
    
    async def test_get_rate_history(self, repository: CarbonCreditRepository, db_session: Session):
        """Test getting rate history"""
        # Create rates over time
        rates = []
        for i in range(5):
            rate = CarbonCreditRateFactory(
                rate_type=RateType.KC_TO_USD,
                rate_value=Decimal(f'0.0{i+1}'),
                effective_date=datetime.utcnow() - timedelta(days=i*5)
            )
            rates.append(rate)
        
        db_session.add_all(rates)
        db_session.commit()
        
        # Get 20 days of history
        result = await repository.get_rate_history(RateType.KC_TO_USD, days=20)
        
        assert len(result) == 4  # Should exclude the oldest one (25 days ago)
        # Should be ordered by effective_date descending
        assert result[0].rate_value == Decimal('0.01')  # Most recent
    
    async def test_create_rate(self, repository: CarbonCreditRepository, db_session: Session):
        """Test creating a new exchange rate"""
        rate = await repository.create_rate(
            rate_type=RateType.CO2_TO_KC,
            rate_value=Decimal('1.5'),
            source='test_api'
        )
        
        assert rate.id is not None
        assert rate.rate_type == RateType.CO2_TO_KC
        assert rate.rate_value == Decimal('1.5')
        assert rate.source == 'test_api'
        assert rate.effective_date is not None


class TestUserCarbonCreditsRepository:
    """Test cases for UserCarbonCreditsRepository"""
    
    @pytest.fixture
    def repository(self, db_session: Session):
        """Create repository instance"""
        return UserCarbonCreditsRepository(db_session)
    
    async def test_get_by_user_id(self, repository: UserCarbonCreditsRepository, db_session: Session):
        """Test getting user credits by user ID"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        credits = UserCarbonCreditsFactory(user_id=user.id)
        db_session.add(credits)
        db_session.commit()
        
        result = await repository.get_by_user_id(user.id)
        
        assert result is not None
        assert result.user_id == user.id
        assert result.id == credits.id
    
    async def test_get_by_user_id_not_found(self, repository: UserCarbonCreditsRepository):
        """Test getting user credits when none exist"""
        result = await repository.get_by_user_id('nonexistent_user')
        assert result is None
    
    async def test_create_user_credits(self, repository: UserCarbonCreditsRepository, db_session: Session):
        """Test creating carbon credits for new user"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        credits = await repository.create_user_credits(user.id)
        
        assert credits.user_id == user.id
        assert credits.current_balance == Decimal('0')
        assert credits.total_earned == Decimal('0')
        assert credits.total_redeemed == Decimal('0')
    
    async def test_update_balance_earned(self, repository: UserCarbonCreditsRepository, db_session: Session):
        """Test updating balance for earned credits"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create initial credits
        credits = await repository.create_user_credits(user.id)
        
        # Update balance with earned credits
        updated_credits = await repository.update_balance(
            user.id, Decimal('10.0'), TransactionType.EARNED
        )
        
        assert updated_credits.current_balance == Decimal('10.0')
        assert updated_credits.total_earned == Decimal('10.0')
        assert updated_credits.total_redeemed == Decimal('0')
    
    async def test_update_balance_redeemed(self, repository: UserCarbonCreditsRepository, db_session: Session):
        """Test updating balance for redeemed credits"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create credits with initial balance
        credits = UserCarbonCreditsFactory(
            user_id=user.id,
            current_balance=Decimal('20.0'),
            total_earned=Decimal('20.0')
        )
        db_session.add(credits)
        db_session.commit()
        
        # Redeem some credits
        updated_credits = await repository.update_balance(
            user.id, Decimal('5.0'), TransactionType.REDEEMED
        )
        
        assert updated_credits.current_balance == Decimal('15.0')
        assert updated_credits.total_earned == Decimal('20.0')
        assert updated_credits.total_redeemed == Decimal('5.0')
    
    async def test_update_balance_insufficient_funds(self, repository: UserCarbonCreditsRepository, db_session: Session):
        """Test redeeming more credits than available"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create credits with small balance
        credits = UserCarbonCreditsFactory(
            user_id=user.id,
            current_balance=Decimal('5.0')
        )
        db_session.add(credits)
        db_session.commit()
        
        # Try to redeem more than available
        with pytest.raises(ValidationError, match="Insufficient credit balance"):
            await repository.update_balance(
                user.id, Decimal('10.0'), TransactionType.REDEEMED
            )
    
    async def test_get_top_earners(self, repository: UserCarbonCreditsRepository, db_session: Session):
        """Test getting top credit earners"""
        users = UserFactory.create_batch(5)
        db_session.add_all(users)
        db_session.commit()
        
        # Create credits with different earning amounts
        credits_list = []
        for i, user in enumerate(users):
            credits = UserCarbonCreditsFactory(
                user_id=user.id,
                total_earned=Decimal(str((i + 1) * 100))  # 100, 200, 300, 400, 500
            )
            credits_list.append(credits)
        
        db_session.add_all(credits_list)
        db_session.commit()
        
        # Get top 3 earners
        result = await repository.get_top_earners(limit=3)
        
        assert len(result) == 3
        # Should be ordered by total_earned descending
        assert result[0].total_earned == Decimal('500')
        assert result[1].total_earned == Decimal('400')
        assert result[2].total_earned == Decimal('300')


class TestCarbonCreditTransactionRepository:
    """Test cases for CarbonCreditTransactionRepository"""
    
    @pytest.fixture
    def repository(self, db_session: Session):
        """Create repository instance"""
        return CarbonCreditTransactionRepository(db_session)
    
    async def test_create_transaction(self, repository: CarbonCreditTransactionRepository, db_session: Session):
        """Test creating a new transaction"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        transaction = await repository.create_transaction(
            user_id=user.id,
            transaction_type=TransactionType.EARNED,
            amount=Decimal('15.0'),
            co2_saved=Decimal('15.0'),
            activity_reference='habit_123',
            verification_status=VerificationStatus.VERIFIED,
            verification_method=VerificationMethod.AUTOMATIC,
            exchange_rate=Decimal('0.05'),
            usd_value=Decimal('0.75'),
            notes='Test transaction'
        )
        
        assert transaction.id is not None
        assert transaction.user_id == user.id
        assert transaction.transaction_type == TransactionType.EARNED
        assert transaction.amount == Decimal('15.0')
        assert transaction.co2_saved == Decimal('15.0')
        assert transaction.activity_reference == 'habit_123'
        assert transaction.verification_status == VerificationStatus.VERIFIED
        assert transaction.verification_method == VerificationMethod.AUTOMATIC
        assert transaction.exchange_rate == Decimal('0.05')
        assert transaction.usd_value == Decimal('0.75')
        assert transaction.notes == 'Test transaction'
        assert transaction.transaction_hash is not None
    
    async def test_get_user_transactions(self, repository: CarbonCreditTransactionRepository, db_session: Session):
        """Test getting user transaction history"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create transactions for user
        transactions = CarbonCreditTransactionFactory.create_batch(5, user_id=user.id)
        db_session.add_all(transactions)
        db_session.commit()
        
        # Create transactions for another user (should not be returned)
        other_user = UserFactory()
        db_session.add(other_user)
        db_session.commit()
        other_transactions = CarbonCreditTransactionFactory.create_batch(3, user_id=other_user.id)
        db_session.add_all(other_transactions)
        db_session.commit()
        
        result = await repository.get_user_transactions(user.id)
        
        assert len(result) == 5
        for transaction in result:
            assert transaction.user_id == user.id
    
    async def test_get_user_transactions_filtered(self, repository: CarbonCreditTransactionRepository, db_session: Session):
        """Test getting user transactions filtered by type"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create different types of transactions
        earned_transactions = CarbonCreditTransactionFactory.create_batch(
            3, user_id=user.id, transaction_type=TransactionType.EARNED
        )
        redeemed_transactions = CarbonCreditTransactionFactory.create_batch(
            2, user_id=user.id, transaction_type=TransactionType.REDEEMED
        )
        
        db_session.add_all(earned_transactions + redeemed_transactions)
        db_session.commit()
        
        # Get only earned transactions
        result = await repository.get_user_transactions(
            user.id, transaction_type=TransactionType.EARNED
        )
        
        assert len(result) == 3
        for transaction in result:
            assert transaction.transaction_type == TransactionType.EARNED
    
    async def test_get_pending_verifications(self, repository: CarbonCreditTransactionRepository, db_session: Session):
        """Test getting transactions pending verification"""
        users = UserFactory.create_batch(3)
        db_session.add_all(users)
        db_session.commit()
        
        # Create transactions with different verification statuses
        pending_transactions = []
        verified_transactions = []
        
        for user in users:
            pending = CarbonCreditTransactionFactory.create_batch(
                2, user_id=user.id, verification_status=VerificationStatus.PENDING
            )
            verified = CarbonCreditTransactionFactory.create_batch(
                1, user_id=user.id, verification_status=VerificationStatus.VERIFIED
            )
            pending_transactions.extend(pending)
            verified_transactions.extend(verified)
        
        db_session.add_all(pending_transactions + verified_transactions)
        db_session.commit()
        
        result = await repository.get_pending_verifications()
        
        assert len(result) == 6  # 2 pending per user * 3 users
        for transaction in result:
            assert transaction.verification_status == VerificationStatus.PENDING
    
    async def test_verify_transaction(self, repository: CarbonCreditTransactionRepository, db_session: Session):
        """Test verifying a transaction"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        transaction = CarbonCreditTransactionFactory(
            user_id=user.id,
            verification_status=VerificationStatus.PENDING
        )
        db_session.add(transaction)
        db_session.commit()
        
        verification_metadata = {
            "reviewer": "admin_1",
            "notes": "Verified with documentation"
        }
        
        updated_transaction = await repository.verify_transaction(
            transaction.id,
            VerificationStatus.VERIFIED,
            verification_metadata
        )
        
        assert updated_transaction.verification_status == VerificationStatus.VERIFIED
        assert updated_transaction.verification_metadata == verification_metadata
        assert updated_transaction.verified_at is not None
    
    async def test_verify_transaction_not_found(self, repository: CarbonCreditTransactionRepository):
        """Test verifying non-existent transaction"""
        with pytest.raises(NotFoundError, match="Transaction not found"):
            await repository.verify_transaction(
                'nonexistent_id',
                VerificationStatus.VERIFIED
            )


class TestCarbonVerificationRuleRepository:
    """Test cases for CarbonVerificationRuleRepository"""
    
    @pytest.fixture
    def repository(self, db_session: Session):
        """Create repository instance"""
        return CarbonVerificationRuleRepository(db_session)
    
    async def test_get_rule_for_activity(self, repository: CarbonVerificationRuleRepository, db_session: Session):
        """Test getting verification rule for activity"""
        rule = CarbonVerificationRuleFactory(
            activity_type='cycling',
            active=True
        )
        db_session.add(rule)
        db_session.commit()
        
        result = await repository.get_rule_for_activity('cycling')
        
        assert result is not None
        assert result.activity_type == 'cycling'
        assert result.id == rule.id
    
    async def test_get_rule_for_activity_inactive(self, repository: CarbonVerificationRuleRepository, db_session: Session):
        """Test getting rule for activity when rule is inactive"""
        rule = CarbonVerificationRuleFactory(
            activity_type='walking',
            active=False
        )
        db_session.add(rule)
        db_session.commit()
        
        result = await repository.get_rule_for_activity('walking')
        assert result is None
    
    async def test_get_active_rules(self, repository: CarbonVerificationRuleRepository, db_session: Session):
        """Test getting all active verification rules"""
        active_rules = CarbonVerificationRuleFactory.create_batch(3, active=True)
        inactive_rules = CarbonVerificationRuleFactory.create_batch(2, active=False)
        
        db_session.add_all(active_rules + inactive_rules)
        db_session.commit()
        
        result = await repository.get_active_rules()
        
        assert len(result) == 3
        for rule in result:
            assert rule.active is True
    
    async def test_create_rule(self, repository: CarbonVerificationRuleRepository, db_session: Session):
        """Test creating a new verification rule"""
        rule = await repository.create_rule(
            activity_type='solar_installation',
            verification_method=VerificationMethod.MANUAL_REVIEW,
            min_amount=Decimal('100.0'),
            max_amount=Decimal('5000.0'),
            credit_multiplier=Decimal('2.0'),
            requires_evidence=True
        )
        
        assert rule.id is not None
        assert rule.activity_type == 'solar_installation'
        assert rule.verification_method == VerificationMethod.MANUAL_REVIEW
        assert rule.min_amount == Decimal('100.0')
        assert rule.max_amount == Decimal('5000.0')
        assert rule.credit_multiplier == Decimal('2.0')
        assert rule.requires_evidence is True
        assert rule.active is True