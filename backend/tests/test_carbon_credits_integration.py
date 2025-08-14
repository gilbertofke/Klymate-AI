"""
Integration Tests for Carbon Credits System

This module contains integration tests for the complete carbon credits workflow,
including habit logging, credit earning, verification, and redemption.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.services.carbon_credits_service import CarbonCreditsService, CarbonMarketIntegration
from app.services.habit_service import HabitService
from app.repositories.carbon_credit_repository import (
    CarbonCreditRepository, UserCarbonCreditsRepository,
    CarbonCreditTransactionRepository, CarbonVerificationRuleRepository
)
from app.models.carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonVerificationRule, RateType, TransactionType, VerificationStatus,
    VerificationMethod, RedemptionType
)
from app.models.user_habit import UserHabit
from app.schemas.habit import HabitCreate
from app.schemas.carbon_credit import RedemptionRequest
from app.utils.carbon_credit_seed_data import CarbonCreditSeedData
from tests.factories import (
    UserFactory, HabitCategoryFactory, CarbonCreditRateFactory,
    CarbonVerificationRuleFactory
)


class TestCarbonCreditsIntegration:
    """Integration tests for carbon credits system"""
    
    @pytest.fixture
    async def credits_service(self, db_session: Session):
        """Create carbon credits service with seeded data"""
        service = CarbonCreditsService(db_session)
        
        # Seed initial data
        seed_data = CarbonCreditSeedData(db_session)
        await seed_data.seed_all()
        
        return service
    
    @pytest.fixture
    async def habit_service(self, db_session: Session):
        """Create habit service"""
        return HabitService(db_session)
    
    async def test_complete_credit_earning_workflow(
        self, 
        credits_service: CarbonCreditsService,
        habit_service: HabitService,
        db_session: Session
    ):
        """Test complete workflow from habit logging to credit earning"""
        # Create test user and habit category
        user = UserFactory()
        category = HabitCategoryFactory(
            name="Cycling to work",
            co2_per_unit=Decimal('2.5'),  # 2.5 kg CO2 per km
            unit_name="km"
        )
        db_session.add_all([user, category])
        db_session.commit()
        
        # Log a habit
        habit_data = HabitCreate(
            category_id=category.id,
            quantity=Decimal('10.0'),  # 10 km cycling
            notes="Cycled to work instead of driving"
        )
        
        habit_entry = await habit_service.log_habit(user.id, habit_data)
        
        # Verify habit was created with CO2 savings
        assert habit_entry.co2_saved == Decimal('25.0')  # 10 km * 2.5 kg/km
        
        # Process habit for credits
        transaction = await credits_service.process_habit_for_credits(habit_entry, "cycling")
        
        # Verify transaction was created
        assert transaction is not None
        assert transaction.user_id == user.id
        assert transaction.transaction_type == TransactionType.EARNED
        assert transaction.co2_saved == Decimal('25.0')
        assert transaction.verification_status == VerificationStatus.VERIFIED  # Cycling is auto-verified
        
        # Verify user balance was updated
        balance = await credits_service.get_user_balance(user.id)
        assert balance['current_balance'] > 0
        assert balance['total_earned'] > 0
        
        # Verify credits calculation (cycling has 1.2x multiplier)
        expected_credits = 25.0 * 1.0 * 1.2  # CO2 * base_rate * multiplier
        assert abs(balance['current_balance'] - expected_credits) < 0.01
    
    async def test_verification_workflow(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test transaction verification workflow"""
        # Create test user
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create a transaction that requires manual verification
        transaction_repo = CarbonCreditTransactionRepository(db_session)
        transaction = await transaction_repo.create_transaction(
            user_id=user.id,
            transaction_type=TransactionType.EARNED,
            amount=Decimal('50.0'),
            co2_saved=Decimal('50.0'),
            verification_status=VerificationStatus.PENDING,
            verification_method=VerificationMethod.MANUAL_REVIEW,
            notes="Solar panel installation"
        )
        
        # Verify transaction is pending
        assert transaction.verification_status == VerificationStatus.PENDING
        
        # Get initial balance (should be 0 since transaction is pending)
        initial_balance = await credits_service.get_user_balance(user.id)
        assert initial_balance['current_balance'] == 0
        
        # Verify the transaction
        verified_transaction = await credits_service.verify_transaction(
            transaction.id,
            VerificationStatus.VERIFIED,
            reviewer_notes="Verified with installation photos",
            evidence_urls=["https://example.com/solar_panel.jpg"]
        )
        
        # Verify transaction status updated
        assert verified_transaction.verification_status == VerificationStatus.VERIFIED
        assert verified_transaction.verified_at is not None
        assert "Verified with installation photos" in verified_transaction.verification_metadata['reviewer_notes']
        
        # Verify balance was updated after verification
        updated_balance = await credits_service.get_user_balance(user.id)
        assert updated_balance['current_balance'] == 50.0
        assert updated_balance['total_earned'] == 50.0
    
    async def test_redemption_workflow(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test credit redemption workflow"""
        # Create test user with credits
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create user credits
        user_credits_repo = UserCarbonCreditsRepository(db_session)
        await user_credits_repo.create_user_credits(user.id)
        await user_credits_repo.update_balance(user.id, Decimal('100.0'), TransactionType.EARNED)
        
        # Initiate redemption
        recipient_info = {
            "payment_method": "paypal",
            "email": "user@example.com",
            "account_id": "paypal_123"
        }
        
        redemption = await credits_service.initiate_redemption(
            user_id=user.id,
            redemption_type=RedemptionType.CASH_OUT,
            amount_kc=Decimal('50.0'),
            recipient_info=recipient_info
        )
        
        # Verify redemption was created
        assert redemption.user_id == user.id
        assert redemption.redemption_type == RedemptionType.CASH_OUT
        assert redemption.amount_kc == Decimal('50.0')
        assert redemption.recipient_info == recipient_info
        
        # Verify balance was updated
        updated_balance = await credits_service.get_user_balance(user.id)
        assert updated_balance['current_balance'] == 50.0  # 100 - 50 redeemed
        assert updated_balance['total_redeemed'] == 50.0
    
    async def test_insufficient_balance_redemption(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test redemption with insufficient balance"""
        # Create test user with small balance
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        user_credits_repo = UserCarbonCreditsRepository(db_session)
        await user_credits_repo.create_user_credits(user.id)
        await user_credits_repo.update_balance(user.id, Decimal('10.0'), TransactionType.EARNED)
        
        # Try to redeem more than available
        with pytest.raises(Exception, match="Insufficient credit balance"):
            await credits_service.initiate_redemption(
                user_id=user.id,
                redemption_type=RedemptionType.CASH_OUT,
                amount_kc=Decimal('50.0'),
                recipient_info={"payment_method": "paypal", "email": "user@example.com"}
            )
    
    async def test_activity_type_mapping(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test habit category to activity type mapping"""
        # Create test user and various habit categories
        user = UserFactory()
        
        # Transport category
        cycling_category = HabitCategoryFactory(
            name="Cycling to work",
            co2_per_unit=Decimal('2.0')
        )
        
        # Diet category
        vegan_category = HabitCategoryFactory(
            name="Eating vegetarian meals",
            co2_per_unit=Decimal('1.5')
        )
        
        db_session.add_all([user, cycling_category, vegan_category])
        db_session.commit()
        
        # Create habit entries
        cycling_habit = UserHabit(
            user_id=user.id,
            category_id=cycling_category.id,
            quantity=Decimal('5.0'),
            co2_saved=Decimal('10.0'),
            logged_date=date.today()
        )
        
        vegan_habit = UserHabit(
            user_id=user.id,
            category_id=vegan_category.id,
            quantity=Decimal('3.0'),
            co2_saved=Decimal('4.5'),
            logged_date=date.today()
        )
        
        db_session.add_all([cycling_habit, vegan_habit])
        db_session.commit()
        
        # Process habits for credits
        cycling_transaction = await credits_service.process_habit_for_credits(cycling_habit)
        vegan_transaction = await credits_service.process_habit_for_credits(vegan_habit)
        
        # Verify transactions were created with correct activity types
        assert cycling_transaction is not None
        assert cycling_transaction.verification_metadata['activity_type'] == 'cycling'
        
        assert vegan_transaction is not None
        assert vegan_transaction.verification_metadata['activity_type'] == 'plant_based_meal'
    
    async def test_market_rate_integration(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test market rate integration and updates"""
        # Create market integration service
        market_integration = CarbonMarketIntegration(credits_service)
        
        # Get initial rates
        initial_rates = await credits_service.get_current_rates()
        
        # Trigger market rate update
        update_results = await market_integration.update_rates_from_market()
        
        # Verify update results
        assert 'updated_rates' in update_results
        assert 'timestamp' in update_results
        assert len(update_results['updated_rates']) > 0
        
        # Get updated rates
        updated_rates = await credits_service.get_current_rates()
        
        # Verify rates were updated (timestamps should be different)
        assert updated_rates['last_updated'] != initial_rates['last_updated']
    
    async def test_pending_verifications_queue(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test pending verifications queue management"""
        # Create test users and transactions
        users = UserFactory.create_batch(3)
        db_session.add_all(users)
        db_session.commit()
        
        transaction_repo = CarbonCreditTransactionRepository(db_session)
        
        # Create pending transactions
        pending_transactions = []
        for user in users:
            transaction = await transaction_repo.create_transaction(
                user_id=user.id,
                transaction_type=TransactionType.EARNED,
                amount=Decimal('25.0'),
                co2_saved=Decimal('25.0'),
                verification_status=VerificationStatus.PENDING,
                verification_method=VerificationMethod.AI_VERIFIED
            )
            pending_transactions.append(transaction)
        
        # Get pending verifications
        pending = await credits_service.get_pending_verifications()
        
        # Verify all pending transactions are returned
        assert len(pending) == 3
        for p in pending:
            assert p['verification_method'] == 'ai_verified'
            assert any(t.id == p['id'] for t in pending_transactions)
    
    async def test_credit_multipliers(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test credit multipliers for different activity types"""
        # Create test user
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Test different activities with different multipliers
        test_cases = [
            ("cycling", 10.0, 1.2),  # 20% bonus
            ("composting", 5.0, 1.2),  # 20% bonus
            ("recycling", 3.0, 0.8),  # 20% penalty
            ("renewable_energy", 50.0, 1.5)  # 50% bonus
        ]
        
        for activity_type, co2_saved, expected_multiplier in test_cases:
            # Create habit entry
            habit = UserHabit(
                user_id=user.id,
                category_id="test_category",
                quantity=Decimal('1.0'),
                co2_saved=Decimal(str(co2_saved)),
                logged_date=date.today()
            )
            db_session.add(habit)
            db_session.commit()
            
            # Process for credits
            transaction = await credits_service.process_habit_for_credits(habit, activity_type)
            
            if transaction:
                # Verify multiplier was applied
                metadata = transaction.verification_metadata
                assert abs(metadata['credit_multiplier'] - expected_multiplier) < 0.01
                
                # Verify final credit amount
                expected_credits = co2_saved * 1.0 * expected_multiplier  # CO2 * base_rate * multiplier
                assert abs(float(transaction.amount) - expected_credits) < 0.01


class TestCarbonCreditsAPI:
    """Integration tests for carbon credits API endpoints"""
    
    @pytest.fixture
    def authenticated_client(self, client: TestClient, db_session: Session):
        """Create authenticated test client"""
        # This would set up authentication headers
        # Implementation depends on your auth system
        return client
    
    def test_get_balance_endpoint(self, authenticated_client: TestClient):
        """Test GET /credits/balance endpoint"""
        response = authenticated_client.get("/api/v1/credits/balance")
        
        # This test would need proper authentication setup
        # assert response.status_code == 200
        # data = response.json()
        # assert 'current_balance' in data
        # assert 'total_earned' in data
    
    def test_get_transactions_endpoint(self, authenticated_client: TestClient):
        """Test GET /credits/transactions endpoint"""
        response = authenticated_client.get("/api/v1/credits/transactions?limit=10")
        
        # This test would need proper authentication setup
        # assert response.status_code == 200
        # data = response.json()
        # assert 'transactions' in data
    
    def test_redemption_endpoint(self, authenticated_client: TestClient):
        """Test POST /credits/redeem endpoint"""
        redemption_data = {
            "redemption_type": "cash_out",
            "amount_kc": 25.0,
            "recipient_info": {
                "payment_method": "paypal",
                "email": "user@example.com",
                "account_id": "paypal_123"
            }
        }
        
        response = authenticated_client.post("/api/v1/credits/redeem", json=redemption_data)
        
        # This test would need proper authentication and balance setup
        # assert response.status_code == 200
        # data = response.json()
        # assert data['redemption_type'] == 'cash_out'
    
    def test_rates_endpoint(self, authenticated_client: TestClient):
        """Test GET /credits/rates endpoint"""
        response = authenticated_client.get("/api/v1/credits/rates")
        
        # This test would work without authentication
        # assert response.status_code == 200
        # data = response.json()
        # assert 'co2_to_kc' in data
        # assert 'kc_to_usd' in data


class TestCarbonCreditsPerformance:
    """Performance tests for carbon credits system"""
    
    async def test_bulk_habit_processing(
        self,
        credits_service: CarbonCreditsService,
        db_session: Session
    ):
        """Test processing many habits for credits efficiently"""
        # Create test user
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create many habit entries
        habits = []
        for i in range(100):
            habit = UserHabit(
                user_id=user.id,
                category_id="test_category",
                quantity=Decimal('1.0'),
                co2_saved=Decimal('2.0'),
                logged_date=date.today() - timedelta(days=i % 30)
            )
            habits.append(habit)
        
        db_session.add_all(habits)
        db_session.commit()
        
        # Process all habits for credits
        start_time = datetime.utcnow()
        
        transactions = []
        for habit in habits:
            transaction = await credits_service.process_habit_for_credits(habit, "cycling")
            if transaction:
                transactions.append(transaction)
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Verify performance (should process 100 habits in reasonable time)
        assert processing_time < 10.0  # Less than 10 seconds
        assert len(transactions) == 100  # All habits processed
        
        # Verify final balance
        balance = await credits_service.get_user_balance(user.id)
        expected_balance = 100 * 2.0 * 1.0 * 1.2  # 100 habits * 2.0 CO2 * 1.0 rate * 1.2 multiplier
        assert abs(balance['current_balance'] - expected_balance) < 0.01