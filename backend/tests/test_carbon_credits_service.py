"""
Tests for Carbon Credits Service

This module contains unit tests for the CarbonCreditsService class.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session
from unittest.mock import Mock, AsyncMock, patch

from app.services.carbon_credits_service import CarbonCreditsService, CarbonMarketIntegration
from app.models.carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonVerificationRule, RateType, TransactionType, VerificationStatus,
    VerificationMethod, RedemptionType
)
from app.models.user_habit import UserHabit
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from tests.factories import (
    UserFactory, HabitCategoryFactory, UserHabitFactory,
    CarbonCreditRateFactory, UserCarbonCreditsFactory,
    CarbonCreditTransactionFactory, CarbonVerificationRuleFactory
)


class TestCarbonCreditsService:
    """Test cases for CarbonCreditsService"""
    
    @pytest.fixture
    def service(self, db_session: Session):
        """Create service instance"""
        return CarbonCreditsService(db_session)
    
    async def test_get_user_balance_new_user(self, service: CarbonCreditsService, db_session: Session):
        """Test getting balance for new user"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create exchange rates
        co2_rate = CarbonCreditRateFactory(rate_type=RateType.CO2_TO_KC, rate_value=Decimal('1.0'))
        usd_rate = CarbonCreditRateFactory(rate_type=RateType.KC_TO_USD, rate_value=Decimal('0.05'))
        db_session.add_all([co2_rate, usd_rate])
        db_session.commit()
        
        balance = await service.get_user_balance(user.id)
        
        assert balance['user_id'] == user.id
        assert balance['current_balance'] == 0.0
        assert balance['total_earned'] == 0.0
        assert balance['total_redeemed'] == 0.0
        assert balance['usd_value'] == 0.0
        assert balance['exchange_rates']['co2_to_kc'] == 1.0
        assert balance['exchange_rates']['kc_to_usd'] == 0.05
    
    async def test_get_user_balance_existing_user(self, service: CarbonCreditsService, db_session: Session):
        """Test getting balance for existing user with credits"""
        user = UserFactory()
        credits = UserCarbonCreditsFactory(
            user_id=user.id,
            current_balance=Decimal('100.0'),
            total_earned=Decimal('150.0'),
            total_redeemed=Decimal('50.0')
        )
        
        # Create exchange rates
        co2_rate = CarbonCreditRateFactory(rate_type=RateType.CO2_TO_KC, rate_value=Decimal('1.0'))
        usd_rate = CarbonCreditRateFactory(rate_type=RateType.KC_TO_USD, rate_value=Decimal('0.05'))
        
        db_session.add_all([user, credits, co2_rate, usd_rate])
        db_session.commit()
        
        balance = await service.get_user_balance(user.id)
        
        assert balance['current_balance'] == 100.0
        assert balance['total_earned'] == 150.0
        assert balance['total_redeemed'] == 50.0
        assert balance['usd_value'] == 5.0  # 100 * 0.05
    
    async def test_process_habit_for_credits_automatic_verification(
        self, 
        service: CarbonCreditsService, 
        db_session: Session
    ):
        """Test processing habit for credits with automatic verification"""
        # Create test data
        user = UserFactory()
        category = HabitCategoryFactory(name="Cycling to work")
        habit = UserHabitFactory(
            user_id=user.id,
            category_id=category.id,
            co2_saved=Decimal('10.0')
        )
        
        # Create verification rule for cycling (automatic)
        rule = CarbonVerificationRuleFactory(
            activity_type='cycling',
            verification_method=VerificationMethod.AUTOMATIC,
            min_amount=Decimal('0.1'),
            max_amount=Decimal('50.0'),
            credit_multiplier=Decimal('1.2')
        )
        
        # Create exchange rates
        co2_rate = CarbonCreditRateFactory(rate_type=RateType.CO2_TO_KC, rate_value=Decimal('1.0'))
        usd_rate = CarbonCreditRateFactory(rate_type=RateType.KC_TO_USD, rate_value=Decimal('0.05'))
        
        db_session.add_all([user, category, habit, rule, co2_rate, usd_rate])
        db_session.commit()
        
        # Process habit for credits
        transaction = await service.process_habit_for_credits(habit, 'cycling')
        
        assert transaction is not None
        assert transaction.user_id == user.id
        assert transaction.transaction_type == TransactionType.EARNED
        assert transaction.co2_saved == Decimal('10.0')
        assert transaction.verification_status == VerificationStatus.VERIFIED
        assert transaction.verification_method == VerificationMethod.AUTOMATIC
        
        # Verify credits calculation (10 CO2 * 1.0 rate * 1.2 multiplier = 12.0)
        assert transaction.amount == Decimal('12.0')
    
    async def test_process_habit_for_credits_manual_verification(
        self, 
        service: CarbonCreditsService, 
        db_session: Session
    ):
        """Test processing habit for credits requiring manual verification"""
        # Create test data
        user = UserFactory()
        category = HabitCategoryFactory(name="Solar panel installation")
        habit = UserHabitFactory(
            user_id=user.id,
            category_id=category.id,
            co2_saved=Decimal('500.0')  # Large amount requiring manual review
        )
        
        # Create verification rule for solar installation (manual review)
        rule = CarbonVerificationRuleFactory(
            activity_type='solar_installation',
            verification_method=VerificationMethod.MANUAL_REVIEW,
            min_amount=Decimal('100.0'),
            max_amount=Decimal('5000.0'),
            credit_multiplier=Decimal('2.0')
        )
        
        # Create exchange rates
        co2_rate = CarbonCreditRateFactory(rate_type=RateType.CO2_TO_KC, rate_value=Decimal('1.0'))
        
        db_session.add_all([user, category, habit, rule, co2_rate])
        db_session.commit()
        
        # Process habit for credits
        transaction = await service.process_habit_for_credits(habit, 'solar_installation')
        
        assert transaction is not None
        assert transaction.verification_status == VerificationStatus.PENDING
        assert transaction.verification_method == VerificationMethod.MANUAL_REVIEW
        
        # Verify credits calculation (500 CO2 * 1.0 rate * 2.0 multiplier = 1000.0)
        assert transaction.amount == Decimal('1000.0')
    
    async def test_process_habit_no_rule(self, service: CarbonCreditsService, db_session: Session):
        """Test processing habit with no verification rule"""
        user = UserFactory()
        category = HabitCategoryFactory(name="Unknown activity")
        habit = UserHabitFactory(
            user_id=user.id,
            category_id=category.id,
            co2_saved=Decimal('5.0')
        )
        
        db_session.add_all([user, category, habit])
        db_session.commit()
        
        # Process habit for credits (should return None)
        transaction = await service.process_habit_for_credits(habit, 'unknown_activity')
        
        assert transaction is None
    
    async def test_verify_transaction_success(self, service: CarbonCreditsService, db_session: Session):
        """Test successful transaction verification"""
        user = UserFactory()
        transaction = CarbonCreditTransactionFactory(
            user_id=user.id,
            verification_status=VerificationStatus.PENDING,
            amount=Decimal('25.0')
        )
        
        db_session.add_all([user, transaction])
        db_session.commit()
        
        # Verify transaction
        verified_transaction = await service.verify_transaction(
            transaction.id,
            VerificationStatus.VERIFIED,
            reviewer_notes="Verified with documentation",
            evidence_urls=["https://example.com/evidence.jpg"]
        )
        
        assert verified_transaction.verification_status == VerificationStatus.VERIFIED
        assert verified_transaction.verified_at is not None
        assert "Verified with documentation" in verified_transaction.verification_metadata['reviewer_notes']
        assert "https://example.com/evidence.jpg" in verified_transaction.verification_metadata['evidence_urls']
    
    async def test_verify_transaction_not_found(self, service: CarbonCreditsService):
        """Test verifying non-existent transaction"""
        with pytest.raises(NotFoundError, match="Transaction not found"):
            await service.verify_transaction(
                'nonexistent_id',
                VerificationStatus.VERIFIED
            )
    
    async def test_verify_transaction_not_pending(self, service: CarbonCreditsService, db_session: Session):
        """Test verifying already verified transaction"""
        user = UserFactory()
        transaction = CarbonCreditTransactionFactory(
            user_id=user.id,
            verification_status=VerificationStatus.VERIFIED  # Already verified
        )
        
        db_session.add_all([user, transaction])
        db_session.commit()
        
        with pytest.raises(ValidationError, match="Transaction is not pending verification"):
            await service.verify_transaction(
                transaction.id,
                VerificationStatus.VERIFIED
            )
    
    async def test_initiate_redemption_success(self, service: CarbonCreditsService, db_session: Session):
        """Test successful redemption initiation"""
        user = UserFactory()
        credits = UserCarbonCreditsFactory(
            user_id=user.id,
            current_balance=Decimal('100.0')
        )
        
        # Create USD exchange rate
        usd_rate = CarbonCreditRateFactory(rate_type=RateType.KC_TO_USD, rate_value=Decimal('0.05'))
        
        db_session.add_all([user, credits, usd_rate])
        db_session.commit()
        
        recipient_info = {
            "payment_method": "paypal",
            "email": "user@example.com",
            "account_id": "paypal_123"
        }
        
        redemption = await service.initiate_redemption(
            user_id=user.id,
            redemption_type=RedemptionType.CASH_OUT,
            amount_kc=Decimal('50.0'),
            recipient_info=recipient_info
        )
        
        assert redemption.user_id == user.id
        assert redemption.redemption_type == RedemptionType.CASH_OUT
        assert redemption.amount_kc == Decimal('50.0')
        assert redemption.amount_usd == Decimal('2.50')  # 50 * 0.05
        assert redemption.recipient_info == recipient_info
    
    async def test_initiate_redemption_insufficient_balance(
        self, 
        service: CarbonCreditsService, 
        db_session: Session
    ):
        """Test redemption with insufficient balance"""
        user = UserFactory()
        credits = UserCarbonCreditsFactory(
            user_id=user.id,
            current_balance=Decimal('10.0')  # Small balance
        )
        
        db_session.add_all([user, credits])
        db_session.commit()
        
        with pytest.raises(ValidationError, match="Insufficient credit balance"):
            await service.initiate_redemption(
                user_id=user.id,
                redemption_type=RedemptionType.CASH_OUT,
                amount_kc=Decimal('50.0'),  # More than available
                recipient_info={"payment_method": "paypal"}
            )
    
    async def test_get_user_transactions(self, service: CarbonCreditsService, db_session: Session):
        """Test getting user transaction history"""
        user = UserFactory()
        
        # Create transactions
        transactions = CarbonCreditTransactionFactory.create_batch(
            5, user_id=user.id
        )
        
        db_session.add_all([user] + transactions)
        db_session.commit()
        
        # Get transactions
        result = await service.get_user_transactions(user.id, limit=10)
        
        assert len(result) == 5
        for transaction_data in result:
            assert transaction_data['user_id'] == user.id
            assert 'id' in transaction_data
            assert 'transaction_type' in transaction_data
            assert 'amount' in transaction_data
    
    async def test_get_current_rates(self, service: CarbonCreditsService, db_session: Session):
        """Test getting current exchange rates"""
        # Create exchange rates
        co2_rate = CarbonCreditRateFactory(
            rate_type=RateType.CO2_TO_KC,
            rate_value=Decimal('1.0'),
            source='test_source'
        )
        usd_rate = CarbonCreditRateFactory(
            rate_type=RateType.KC_TO_USD,
            rate_value=Decimal('0.05'),
            source='test_source'
        )
        
        db_session.add_all([co2_rate, usd_rate])
        db_session.commit()
        
        rates = await service.get_current_rates()
        
        assert rates['co2_to_kc']['rate'] == 1.0
        assert rates['co2_to_kc']['source'] == 'test_source'
        assert rates['kc_to_usd']['rate'] == 0.05
        assert rates['kc_to_usd']['source'] == 'test_source'
        assert 'last_updated' in rates
    
    async def test_update_exchange_rate(self, service: CarbonCreditsService, db_session: Session):
        """Test updating exchange rate"""
        rate = await service.update_exchange_rate(
            rate_type=RateType.CO2_TO_KC,
            rate_value=Decimal('1.5'),
            source='test_update'
        )
        
        assert rate.rate_type == RateType.CO2_TO_KC
        assert rate.rate_value == Decimal('1.5')
        assert rate.source == 'test_update'
        assert rate.effective_date is not None
    
    async def test_get_pending_verifications(self, service: CarbonCreditsService, db_session: Session):
        """Test getting pending verifications"""
        users = UserFactory.create_batch(3)
        
        # Create pending transactions
        pending_transactions = []
        for user in users:
            transaction = CarbonCreditTransactionFactory(
                user_id=user.id,
                verification_status=VerificationStatus.PENDING
            )
            pending_transactions.append(transaction)
        
        # Create verified transaction (should not be included)
        verified_transaction = CarbonCreditTransactionFactory(
            user_id=users[0].id,
            verification_status=VerificationStatus.VERIFIED
        )
        
        db_session.add_all(users + pending_transactions + [verified_transaction])
        db_session.commit()
        
        pending = await service.get_pending_verifications()
        
        assert len(pending) == 3
        for p in pending:
            assert any(t.id == p['id'] for t in pending_transactions)
    
    def test_map_habit_to_activity_type(self, service: CarbonCreditsService, db_session: Session):
        """Test habit category to activity type mapping"""
        # Create test categories
        cycling_category = HabitCategoryFactory(name="Cycling to work")
        vegan_category = HabitCategoryFactory(name="Eating vegetarian meals")
        recycling_category = HabitCategoryFactory(name="Recycling waste")
        
        db_session.add_all([cycling_category, vegan_category, recycling_category])
        db_session.commit()
        
        # Create habits
        cycling_habit = UserHabitFactory(category_id=cycling_category.id)
        vegan_habit = UserHabitFactory(category_id=vegan_category.id)
        recycling_habit = UserHabitFactory(category_id=recycling_category.id)
        
        cycling_habit.category = cycling_category
        vegan_habit.category = vegan_category
        recycling_habit.category = recycling_category
        
        # Test mappings
        assert service._map_habit_to_activity_type(cycling_habit) == 'cycling'
        assert service._map_habit_to_activity_type(vegan_habit) == 'plant_based_meal'
        assert service._map_habit_to_activity_type(recycling_habit) == 'recycling'


class TestCarbonMarketIntegration:
    """Test cases for CarbonMarketIntegration"""
    
    @pytest.fixture
    def market_integration(self, db_session: Session):
        """Create market integration instance"""
        credits_service = CarbonCreditsService(db_session)
        return CarbonMarketIntegration(credits_service)
    
    async def test_update_rates_from_market(
        self, 
        market_integration: CarbonMarketIntegration,
        db_session: Session
    ):
        """Test updating rates from market APIs"""
        # Mock the random rate generation to be predictable
        with patch('random.uniform') as mock_random:
            mock_random.side_effect = [0.02, 0.001]  # CO2 variation, USD variation
            
            results = await market_integration.update_rates_from_market()
            
            assert 'updated_rates' in results
            assert 'errors' in results
            assert 'timestamp' in results
            assert len(results['updated_rates']) == 2  # CO2 and USD rates
            
            # Verify rate types were updated
            rate_types = [rate['rate_type'] for rate in results['updated_rates']]
            assert 'co2_to_kc' in rate_types
            assert 'kc_to_usd' in rate_types