"""
Carbon Credits Service

This module provides business logic for the carbon credits system,
including credit calculations, verification, earning, and redemption.
"""

from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import hashlib
import logging
from sqlalchemy.orm import Session

from app.repositories.carbon_credit_repository import (
    CarbonCreditRepository, UserCarbonCreditsRepository,
    CarbonCreditTransactionRepository, CarbonVerificationRuleRepository
)
from app.repositories.user_repository import UserRepository
from app.repositories.habit_repository import HabitRepository
from app.models.carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonCreditRedemption, CarbonVerificationRule,
    RateType, TransactionType, VerificationStatus, VerificationMethod,
    RedemptionType, RedemptionStatus
)
from app.models.user_habit import UserHabit
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.utils.cache import cache_manager

logger = logging.getLogger(__name__)


class CarbonCreditsService:
    """Service for managing carbon credits system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rate_repo = CarbonCreditRepository(db)
        self.user_credits_repo = UserCarbonCreditsRepository(db)
        self.transaction_repo = CarbonCreditTransactionRepository(db)
        self.rule_repo = CarbonVerificationRuleRepository(db)
        self.user_repo = UserRepository(db)
        self.habit_repo = HabitRepository(db)
    
    async def get_user_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current carbon credit balance and statistics
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with balance information
        """
        try:
            # Get or create user credits
            credits = await self.user_credits_repo.get_by_user_id(user_id)
            if not credits:
                credits = await self.user_credits_repo.create_user_credits(user_id)
            
            # Get current exchange rates
            co2_rate = await self.rate_repo.get_current_rate(RateType.CO2_TO_KC)
            usd_rate = await self.rate_repo.get_current_rate(RateType.KC_TO_USD)
            
            # Calculate USD value
            usd_value = None
            if usd_rate:
                usd_value = float(credits.current_balance * usd_rate.rate_value)
            
            return {
                'user_id': user_id,
                'current_balance': float(credits.current_balance),
                'total_earned': float(credits.total_earned),
                'total_redeemed': float(credits.total_redeemed),
                'usd_value': usd_value,
                'exchange_rates': {
                    'co2_to_kc': float(co2_rate.rate_value) if co2_rate else None,
                    'kc_to_usd': float(usd_rate.rate_value) if usd_rate else None
                },
                'last_updated': credits.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get user balance for {user_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve balance: {str(e)}")
    
    async def process_habit_for_credits(
        self, 
        user_habit: UserHabit,
        activity_type: Optional[str] = None
    ) -> Optional[CarbonCreditTransaction]:
        """
        Process a user habit for carbon credit earning
        
        Args:
            user_habit: The habit log entry
            activity_type: Override activity type for verification rules
            
        Returns:
            Created transaction or None if not eligible
        """
        try:
            # Determine activity type
            if not activity_type:
                # Map habit category to activity type
                activity_type = self._map_habit_to_activity_type(user_habit)
            
            if not activity_type:
                logger.info(f"No activity type mapping for habit {user_habit.id}")
                return None
            
            # Get verification rule for activity
            rule = await self.rule_repo.get_rule_for_activity(activity_type)
            if not rule:
                logger.info(f"No verification rule for activity type: {activity_type}")
                return None
            
            # Calculate CO2 savings
            co2_saved = float(user_habit.co2_saved) if user_habit.co2_saved else 0.0
            if co2_saved <= 0:
                logger.info(f"No CO2 savings for habit {user_habit.id}")
                return None
            
            # Get current CO2 to KC rate
            co2_rate = await self.rate_repo.get_current_rate(RateType.CO2_TO_KC)
            if not co2_rate:
                logger.error("No CO2 to KC exchange rate available")
                return None
            
            # Calculate credits with multiplier
            base_credits = rule.calculate_credits(co2_saved, float(co2_rate.rate_value))
            
            # Determine verification method and status
            verification_method = rule.verification_method
            verification_status = VerificationStatus.PENDING
            
            if rule.is_automatic_verification_eligible(co2_saved):
                verification_status = VerificationStatus.VERIFIED
            
            # Get USD exchange rate for value calculation
            usd_rate = await self.rate_repo.get_current_rate(RateType.KC_TO_USD)
            usd_value = None
            if usd_rate:
                usd_value = Decimal(str(base_credits)) * usd_rate.rate_value
            
            # Create transaction
            transaction = await self.transaction_repo.create_transaction(
                user_id=user_habit.user_id,
                transaction_type=TransactionType.EARNED,
                amount=Decimal(str(base_credits)),
                co2_saved=Decimal(str(co2_saved)),
                activity_reference=user_habit.id,
                verification_status=verification_status,
                verification_method=verification_method,
                verification_metadata={
                    'activity_type': activity_type,
                    'habit_category': user_habit.category.name if user_habit.category else None,
                    'credit_multiplier': float(rule.credit_multiplier),
                    'base_co2_rate': float(co2_rate.rate_value),
                    'processed_at': datetime.utcnow().isoformat()
                },
                exchange_rate=usd_rate.rate_value if usd_rate else None,
                usd_value=usd_value,
                notes=f"Credits earned from {activity_type} activity"
            )
            
            # If automatically verified, update user balance
            if verification_status == VerificationStatus.VERIFIED:
                await self.user_credits_repo.update_balance(
                    user_habit.user_id,
                    Decimal(str(base_credits)),
                    TransactionType.EARNED
                )
                
                # Clear cache for user balance
                await self._clear_user_cache(user_habit.user_id)
            
            logger.info(f"Created credit transaction {transaction.id} for user {user_habit.user_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to process habit for credits: {str(e)}")
            raise BusinessLogicError(f"Failed to process credits: {str(e)}")
    
    async def verify_transaction(
        self, 
        transaction_id: str, 
        status: VerificationStatus,
        reviewer_notes: Optional[str] = None,
        evidence_urls: Optional[List[str]] = None
    ) -> CarbonCreditTransaction:
        """
        Verify a pending transaction
        
        Args:
            transaction_id: Transaction ID
            status: New verification status
            reviewer_notes: Optional reviewer notes
            evidence_urls: Optional evidence URLs
            
        Returns:
            Updated transaction
        """
        try:
            transaction = await self.transaction_repo.get_by_id(transaction_id)
            if not transaction:
                raise NotFoundError("Transaction not found")
            
            if transaction.verification_status != VerificationStatus.PENDING:
                raise ValidationError("Transaction is not pending verification")
            
            # Prepare verification metadata
            verification_metadata = transaction.verification_metadata or {}
            verification_metadata.update({
                'verified_at': datetime.utcnow().isoformat(),
                'reviewer_notes': reviewer_notes,
                'evidence_urls': evidence_urls or []
            })
            
            # Update transaction
            updated_transaction = await self.transaction_repo.verify_transaction(
                transaction_id, status, verification_metadata
            )
            
            # If verified, update user balance
            if status == VerificationStatus.VERIFIED:
                await self.user_credits_repo.update_balance(
                    transaction.user_id,
                    transaction.amount,
                    TransactionType.EARNED
                )
                
                # Clear cache for user balance
                await self._clear_user_cache(transaction.user_id)
                
                logger.info(f"Verified transaction {transaction_id} and updated user balance")
            
            return updated_transaction
            
        except Exception as e:
            logger.error(f"Failed to verify transaction {transaction_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to verify transaction: {str(e)}")
    
    async def initiate_redemption(
        self,
        user_id: str,
        redemption_type: RedemptionType,
        amount_kc: Decimal,
        recipient_info: Dict[str, Any]
    ) -> CarbonCreditRedemption:
        """
        Initiate a credit redemption request
        
        Args:
            user_id: User ID
            redemption_type: Type of redemption
            amount_kc: Amount of KC to redeem
            recipient_info: Recipient information
            
        Returns:
            Created redemption record
        """
        try:
            # Validate user has sufficient balance
            credits = await self.user_credits_repo.get_by_user_id(user_id)
            if not credits or credits.current_balance < amount_kc:
                raise ValidationError("Insufficient credit balance")
            
            # Get current USD exchange rate
            usd_rate = await self.rate_repo.get_current_rate(RateType.KC_TO_USD)
            if not usd_rate:
                raise BusinessLogicError("USD exchange rate not available")
            
            amount_usd = amount_kc * usd_rate.rate_value
            
            # Create redemption transaction
            transaction = await self.transaction_repo.create_transaction(
                user_id=user_id,
                transaction_type=TransactionType.REDEEMED,
                amount=amount_kc,
                verification_status=VerificationStatus.VERIFIED,
                verification_method=VerificationMethod.AUTOMATIC,
                exchange_rate=usd_rate.rate_value,
                usd_value=amount_usd,
                notes=f"Redemption for {redemption_type.value}"
            )
            
            # Create redemption record
            from app.repositories.carbon_credit_repository import CarbonCreditRedemptionRepository
            redemption_repo = CarbonCreditRedemptionRepository(self.db)
            
            redemption = await redemption_repo.create(
                user_id=user_id,
                transaction_id=transaction.id,
                redemption_type=redemption_type,
                amount_kc=amount_kc,
                amount_usd=amount_usd,
                recipient_info=recipient_info,
                status=RedemptionStatus.PENDING,
                external_reference=self._generate_external_reference(redemption_type)
            )
            
            # Update user balance
            await self.user_credits_repo.update_balance(
                user_id, amount_kc, TransactionType.REDEEMED
            )
            
            # Clear cache for user balance
            await self._clear_user_cache(user_id)
            
            logger.info(f"Created redemption {redemption.id} for user {user_id}")
            return redemption
            
        except Exception as e:
            logger.error(f"Failed to initiate redemption for user {user_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to initiate redemption: {str(e)}")
    
    async def get_user_transactions(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's transaction history
        
        Args:
            user_id: User ID
            limit: Maximum number of transactions
            offset: Number of transactions to skip
            transaction_type: Filter by transaction type
            
        Returns:
            List of transaction dictionaries
        """
        try:
            transactions = await self.transaction_repo.get_user_transactions(
                user_id, limit, offset, transaction_type
            )
            
            return [
                {
                    'id': t.id,
                    'transaction_type': t.transaction_type.value,
                    'amount': float(t.amount),
                    'co2_saved': float(t.co2_saved) if t.co2_saved else None,
                    'verification_status': t.verification_status.value,
                    'verification_method': t.verification_method.value,
                    'usd_value': float(t.usd_value) if t.usd_value else None,
                    'notes': t.notes,
                    'created_at': t.created_at.isoformat(),
                    'verified_at': t.verified_at.isoformat() if t.verified_at else None,
                    'activity_reference': t.activity_reference
                }
                for t in transactions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get transactions for user {user_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve transactions: {str(e)}")
    
    async def get_current_rates(self) -> Dict[str, Any]:
        """
        Get current exchange rates
        
        Returns:
            Dictionary with current rates
        """
        try:
            co2_rate = await self.rate_repo.get_current_rate(RateType.CO2_TO_KC)
            usd_rate = await self.rate_repo.get_current_rate(RateType.KC_TO_USD)
            
            return {
                'co2_to_kc': {
                    'rate': float(co2_rate.rate_value) if co2_rate else None,
                    'effective_date': co2_rate.effective_date.isoformat() if co2_rate else None,
                    'source': co2_rate.source if co2_rate else None
                },
                'kc_to_usd': {
                    'rate': float(usd_rate.rate_value) if usd_rate else None,
                    'effective_date': usd_rate.effective_date.isoformat() if usd_rate else None,
                    'source': usd_rate.source if usd_rate else None
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get current rates: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve rates: {str(e)}")
    
    async def update_exchange_rate(
        self,
        rate_type: RateType,
        rate_value: Decimal,
        source: str = "manual_update"
    ) -> CarbonCreditRate:
        """
        Update exchange rate
        
        Args:
            rate_type: Type of rate to update
            rate_value: New rate value
            source: Source of the rate update
            
        Returns:
            Created rate record
        """
        try:
            rate = await self.rate_repo.create_rate(
                rate_type=rate_type,
                rate_value=rate_value,
                source=source
            )
            
            # Clear cached rates
            cache_key = f"carbon_credits:rates:{rate_type.value}"
            await cache_manager.delete(cache_key)
            
            logger.info(f"Updated {rate_type.value} rate to {rate_value} from {source}")
            return rate
            
        except Exception as e:
            logger.error(f"Failed to update exchange rate: {str(e)}")
            raise BusinessLogicError(f"Failed to update rate: {str(e)}")
    
    async def get_pending_verifications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get transactions pending verification
        
        Args:
            limit: Maximum number of transactions
            
        Returns:
            List of pending transactions
        """
        try:
            transactions = await self.transaction_repo.get_pending_verifications(limit)
            
            return [
                {
                    'id': t.id,
                    'user_id': t.user_id,
                    'amount': float(t.amount),
                    'co2_saved': float(t.co2_saved) if t.co2_saved else None,
                    'activity_reference': t.activity_reference,
                    'verification_method': t.verification_method.value,
                    'verification_metadata': t.verification_metadata,
                    'created_at': t.created_at.isoformat(),
                    'notes': t.notes
                }
                for t in transactions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get pending verifications: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve pending verifications: {str(e)}")
    
    def _map_habit_to_activity_type(self, user_habit: UserHabit) -> Optional[str]:
        """
        Map a user habit to an activity type for verification rules
        
        Args:
            user_habit: The habit log entry
            
        Returns:
            Activity type string or None
        """
        if not user_habit.category:
            return None
        
        # Mapping based on habit category names
        category_name = user_habit.category.name.lower()
        
        # Transport mappings
        if 'public transport' in category_name or 'bus' in category_name or 'train' in category_name:
            return 'public_transport'
        elif 'cycling' in category_name or 'bike' in category_name:
            return 'cycling'
        elif 'walking' in category_name or 'walk' in category_name:
            return 'walking'
        elif 'carpool' in category_name or 'rideshare' in category_name:
            return 'carpooling'
        
        # Diet mappings
        elif 'vegetarian' in category_name or 'plant' in category_name or 'vegan' in category_name:
            return 'plant_based_meal'
        elif 'local' in category_name or 'organic' in category_name:
            return 'local_food'
        elif 'meat' in category_name and 'reduc' in category_name:
            return 'reduced_meat'
        
        # Energy mappings
        elif 'renewable' in category_name or 'solar' in category_name or 'wind' in category_name:
            return 'renewable_energy'
        elif 'energy' in category_name and ('conserv' in category_name or 'saving' in category_name):
            return 'energy_conservation'
        elif 'led' in category_name or 'light' in category_name:
            return 'led_lighting'
        
        # Lifestyle mappings
        elif 'recycl' in category_name:
            return 'recycling'
        elif 'compost' in category_name:
            return 'composting'
        elif 'water' in category_name:
            return 'water_conservation'
        elif 'sustainable' in category_name or 'eco' in category_name:
            return 'sustainable_shopping'
        
        # Default fallback based on category type
        category_type = user_habit.category.category_type.value if user_habit.category.category_type else None
        if category_type == 'transport':
            return 'public_transport'  # Default transport activity
        elif category_type == 'diet':
            return 'plant_based_meal'  # Default diet activity
        elif category_type == 'energy':
            return 'energy_conservation'  # Default energy activity
        elif category_type == 'lifestyle':
            return 'recycling'  # Default lifestyle activity
        
        return None
    
    def _generate_external_reference(self, redemption_type: RedemptionType) -> str:
        """
        Generate external reference for redemption
        
        Args:
            redemption_type: Type of redemption
            
        Returns:
            External reference string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_input = f"{redemption_type.value}:{timestamp}:{datetime.utcnow().microsecond}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        return f"{redemption_type.value}_{timestamp}_{hash_suffix}"
    
    async def _clear_user_cache(self, user_id: str) -> None:
        """
        Clear cached data for a user
        
        Args:
            user_id: User ID
        """
        try:
            cache_keys = [
                f"carbon_credits:balance:{user_id}",
                f"carbon_credits:transactions:{user_id}",
                f"user:stats:{user_id}"
            ]
            
            for key in cache_keys:
                await cache_manager.delete(key)
                
        except Exception as e:
            logger.warning(f"Failed to clear cache for user {user_id}: {str(e)}")


class CarbonMarketIntegration:
    """Service for integrating with carbon market APIs for real-time rates"""
    
    def __init__(self, credits_service: CarbonCreditsService):
        self.credits_service = credits_service
    
    async def update_rates_from_market(self) -> Dict[str, Any]:
        """
        Update exchange rates from carbon market APIs
        
        Returns:
            Dictionary with update results
        """
        try:
            # This would integrate with real carbon market APIs
            # For now, we'll simulate rate updates
            
            results = {
                'updated_rates': [],
                'errors': [],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Simulate CO2 to KC rate update (this would come from carbon market API)
            try:
                # In production, this would fetch from carbon market APIs
                # For now, we'll use a simulated rate with small variations
                import random
                base_rate = 1.0
                variation = random.uniform(-0.05, 0.05)  # ±5% variation
                new_co2_rate = Decimal(str(base_rate + variation))
                
                rate = await self.credits_service.update_exchange_rate(
                    RateType.CO2_TO_KC,
                    new_co2_rate,
                    "carbon_market_api"
                )
                
                results['updated_rates'].append({
                    'rate_type': 'co2_to_kc',
                    'new_rate': float(new_co2_rate),
                    'effective_date': rate.effective_date.isoformat()
                })
                
            except Exception as e:
                results['errors'].append(f"Failed to update CO2 rate: {str(e)}")
            
            # Simulate KC to USD rate update
            try:
                # In production, this would fetch from financial APIs
                base_usd_rate = 0.05
                usd_variation = random.uniform(-0.002, 0.002)  # ±$0.002 variation
                new_usd_rate = Decimal(str(base_usd_rate + usd_variation))
                
                rate = await self.credits_service.update_exchange_rate(
                    RateType.KC_TO_USD,
                    new_usd_rate,
                    "financial_market_api"
                )
                
                results['updated_rates'].append({
                    'rate_type': 'kc_to_usd',
                    'new_rate': float(new_usd_rate),
                    'effective_date': rate.effective_date.isoformat()
                })
                
            except Exception as e:
                results['errors'].append(f"Failed to update USD rate: {str(e)}")
            
            logger.info(f"Market rate update completed: {len(results['updated_rates'])} rates updated")
            return results
            
        except Exception as e:
            logger.error(f"Failed to update rates from market: {str(e)}")
            raise BusinessLogicError(f"Market rate update failed: {str(e)}")
    
    async def schedule_rate_updates(self) -> None:
        """
        Schedule periodic rate updates from market APIs
        This would typically be called by a background task scheduler
        """
        try:
            # Update rates every hour during market hours
            # This is a simplified implementation - in production you'd use
            # a proper task scheduler like Celery or APScheduler
            
            await self.update_rates_from_market()
            logger.info("Scheduled rate update completed")
            
        except Exception as e:
            logger.error(f"Scheduled rate update failed: {str(e)}")
            # Don't raise exception for scheduled tasks to avoid breaking the scheduler