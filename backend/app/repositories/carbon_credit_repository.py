"""
Carbon Credits Repository

This module provides data access operations for the carbon credits system,
including credit rates, user balances, transactions, redemptions, and verification rules.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import and_, or_, desc, asc, func, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from app.repositories.base_repository import BaseRepository
from app.models.carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonCreditRedemption, CarbonVerificationRule,
    RateType, TransactionType, VerificationStatus, VerificationMethod,
    RedemptionType, RedemptionStatus
)
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError


class CarbonCreditRepository(BaseRepository[CarbonCreditRate]):
    """Repository for carbon credit rate operations"""
    
    def __init__(self, db: Session):
        super().__init__(CarbonCreditRate, db)
    
    async def get_current_rate(self, rate_type: RateType) -> Optional[CarbonCreditRate]:
        """
        Get the current exchange rate for a specific rate type
        
        Args:
            rate_type: Type of rate to retrieve
            
        Returns:
            Current rate or None if not found
        """
        try:
            query = select(CarbonCreditRate).where(
                and_(
                    CarbonCreditRate.rate_type == rate_type,
                    CarbonCreditRate.effective_date <= datetime.utcnow(),
                    CarbonCreditRate.deleted_at.is_(None)
                )
            ).order_by(desc(CarbonCreditRate.effective_date))
            
            result = await self.db.execute(query)
            return result.scalars().first()
        except Exception as e:
            raise DatabaseError(f"Failed to get current rate: {str(e)}")
    
    async def get_rate_history(
        self, 
        rate_type: RateType, 
        days: int = 30
    ) -> List[CarbonCreditRate]:
        """
        Get rate history for a specific period
        
        Args:
            rate_type: Type of rate to retrieve
            days: Number of days of history to retrieve
            
        Returns:
            List of historical rates
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(CarbonCreditRate).where(
                and_(
                    CarbonCreditRate.rate_type == rate_type,
                    CarbonCreditRate.effective_date >= start_date,
                    CarbonCreditRate.deleted_at.is_(None)
                )
            ).order_by(desc(CarbonCreditRate.effective_date))
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseError(f"Failed to get rate history: {str(e)}")
    
    async def create_rate(
        self, 
        rate_type: RateType, 
        rate_value: Decimal, 
        source: Optional[str] = None,
        effective_date: Optional[datetime] = None
    ) -> CarbonCreditRate:
        """
        Create a new exchange rate
        
        Args:
            rate_type: Type of rate
            rate_value: Rate value
            source: Source of the rate (e.g., market API)
            effective_date: When the rate becomes effective
            
        Returns:
            Created rate record
        """
        try:
            rate = CarbonCreditRate(
                rate_type=rate_type,
                rate_value=rate_value,
                source=source,
                effective_date=effective_date or datetime.utcnow()
            )
            
            return await self.create(rate)
        except Exception as e:
            raise DatabaseError(f"Failed to create rate: {str(e)}")


class UserCarbonCreditsRepository(BaseRepository[UserCarbonCredits]):
    """Repository for user carbon credits operations"""
    
    def __init__(self, db: Session):
        super().__init__(UserCarbonCredits, db)
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserCarbonCredits]:
        """
        Get user carbon credits by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            User carbon credits or None if not found
        """
        try:
            query = select(UserCarbonCredits).where(
                and_(
                    UserCarbonCredits.user_id == user_id,
                    UserCarbonCredits.deleted_at.is_(None)
                )
            )
            
            result = await self.db.execute(query)
            return result.scalars().first()
        except Exception as e:
            raise DatabaseError(f"Failed to get user carbon credits: {str(e)}")
    
    async def create_user_credits(self, user_id: str) -> UserCarbonCredits:
        """
        Create carbon credits record for a new user
        
        Args:
            user_id: User ID
            
        Returns:
            Created user carbon credits record
        """
        try:
            credits = UserCarbonCredits(
                user_id=user_id,
                current_balance=Decimal('0'),
                total_earned=Decimal('0'),
                total_redeemed=Decimal('0')
            )
            
            return await self.create(credits)
        except IntegrityError:
            # User credits already exist
            existing = await self.get_by_user_id(user_id)
            if existing:
                return existing
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to create user credits: {str(e)}")
    
    async def update_balance(
        self, 
        user_id: str, 
        amount_change: Decimal, 
        transaction_type: TransactionType
    ) -> UserCarbonCredits:
        """
        Update user's carbon credit balance
        
        Args:
            user_id: User ID
            amount_change: Amount to add/subtract
            transaction_type: Type of transaction
            
        Returns:
            Updated user carbon credits record
        """
        try:
            credits = await self.get_by_user_id(user_id)
            if not credits:
                credits = await self.create_user_credits(user_id)
            
            # Update balance based on transaction type
            if transaction_type == TransactionType.EARNED:
                credits.current_balance += amount_change
                credits.total_earned += amount_change
            elif transaction_type == TransactionType.REDEEMED:
                if credits.current_balance < amount_change:
                    raise ValidationError("Insufficient credit balance")
                credits.current_balance -= amount_change
                credits.total_redeemed += amount_change
            
            return await self.update(credits.id, credits)
        except Exception as e:
            raise DatabaseError(f"Failed to update balance: {str(e)}")
    
    async def get_top_earners(self, limit: int = 10) -> List[UserCarbonCredits]:
        """
        Get top credit earners
        
        Args:
            limit: Number of top earners to return
            
        Returns:
            List of top earning users
        """
        try:
            query = select(UserCarbonCredits).where(
                UserCarbonCredits.deleted_at.is_(None)
            ).order_by(desc(UserCarbonCredits.total_earned)).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseError(f"Failed to get top earners: {str(e)}")


class CarbonCreditTransactionRepository(BaseRepository[CarbonCreditTransaction]):
    """Repository for carbon credit transaction operations"""
    
    def __init__(self, db: Session):
        super().__init__(CarbonCreditTransaction, db)
    
    async def create_transaction(
        self,
        user_id: str,
        transaction_type: TransactionType,
        amount: Decimal,
        co2_saved: Optional[Decimal] = None,
        activity_reference: Optional[str] = None,
        verification_status: VerificationStatus = VerificationStatus.PENDING,
        verification_method: VerificationMethod = VerificationMethod.AUTOMATIC,
        verification_metadata: Optional[Dict[str, Any]] = None,
        exchange_rate: Optional[Decimal] = None,
        usd_value: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> CarbonCreditTransaction:
        """
        Create a new carbon credit transaction
        
        Args:
            user_id: User ID
            transaction_type: Type of transaction
            amount: Credit amount
            co2_saved: CO2 saved (for earned credits)
            activity_reference: Reference to related activity
            verification_status: Verification status
            verification_method: Verification method
            verification_metadata: Additional verification data
            exchange_rate: Exchange rate at time of transaction
            usd_value: USD value at time of transaction
            notes: Additional notes
            
        Returns:
            Created transaction record
        """
        try:
            # Generate transaction hash for verification
            transaction_hash = self._generate_transaction_hash(
                user_id, transaction_type, amount, datetime.utcnow()
            )
            
            transaction = CarbonCreditTransaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                co2_saved=co2_saved,
                activity_reference=activity_reference,
                verification_status=verification_status,
                verification_method=verification_method,
                verification_metadata=verification_metadata,
                transaction_hash=transaction_hash,
                exchange_rate=exchange_rate,
                usd_value=usd_value,
                notes=notes
            )
            
            return await self.create(transaction)
        except Exception as e:
            raise DatabaseError(f"Failed to create transaction: {str(e)}")
    
    async def get_user_transactions(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0,
        transaction_type: Optional[TransactionType] = None
    ) -> List[CarbonCreditTransaction]:
        """
        Get user's transaction history
        
        Args:
            user_id: User ID
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            transaction_type: Filter by transaction type
            
        Returns:
            List of user transactions
        """
        try:
            conditions = [
                CarbonCreditTransaction.user_id == user_id,
                CarbonCreditTransaction.deleted_at.is_(None)
            ]
            
            if transaction_type:
                conditions.append(CarbonCreditTransaction.transaction_type == transaction_type)
            
            query = select(CarbonCreditTransaction).where(
                and_(*conditions)
            ).order_by(desc(CarbonCreditTransaction.created_at)).limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseError(f"Failed to get user transactions: {str(e)}")
    
    async def get_pending_verifications(
        self, 
        limit: int = 100
    ) -> List[CarbonCreditTransaction]:
        """
        Get transactions pending verification
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of pending transactions
        """
        try:
            query = select(CarbonCreditTransaction).where(
                and_(
                    CarbonCreditTransaction.verification_status == VerificationStatus.PENDING,
                    CarbonCreditTransaction.deleted_at.is_(None)
                )
            ).order_by(asc(CarbonCreditTransaction.created_at)).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseError(f"Failed to get pending verifications: {str(e)}")
    
    async def verify_transaction(
        self, 
        transaction_id: str, 
        status: VerificationStatus,
        verification_metadata: Optional[Dict[str, Any]] = None
    ) -> CarbonCreditTransaction:
        """
        Update transaction verification status
        
        Args:
            transaction_id: Transaction ID
            status: New verification status
            verification_metadata: Additional verification data
            
        Returns:
            Updated transaction record
        """
        try:
            transaction = await self.get_by_id(transaction_id)
            if not transaction:
                raise NotFoundError("Transaction not found")
            
            transaction.verification_status = status
            if verification_metadata:
                transaction.verification_metadata = verification_metadata
            
            if status == VerificationStatus.VERIFIED:
                transaction.verified_at = datetime.utcnow()
            
            return await self.update(transaction_id, transaction)
        except Exception as e:
            raise DatabaseError(f"Failed to verify transaction: {str(e)}")
    
    def _generate_transaction_hash(
        self, 
        user_id: str, 
        transaction_type: TransactionType, 
        amount: Decimal, 
        timestamp: datetime
    ) -> str:
        """
        Generate a hash for transaction verification
        
        Args:
            user_id: User ID
            transaction_type: Transaction type
            amount: Transaction amount
            timestamp: Transaction timestamp
            
        Returns:
            Transaction hash
        """
        import hashlib
        
        data = f"{user_id}:{transaction_type.value}:{amount}:{timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()


class CarbonCreditRedemptionRepository(BaseRepository[CarbonCreditRedemption]):
    """Repository for carbon credit redemption operations"""
    
    def __init__(self, db: Session):
        super().__init__(CarbonCreditRedemption, db)
    
    async def get_user_redemptions(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0,
        status: Optional[RedemptionStatus] = None
    ) -> List[CarbonCreditRedemption]:
        """
        Get user's redemption history
        
        Args:
            user_id: User ID
            limit: Maximum number of redemptions to return
            offset: Number of redemptions to skip
            status: Filter by redemption status
            
        Returns:
            List of user redemptions
        """
        try:
            conditions = [
                CarbonCreditRedemption.user_id == user_id,
                CarbonCreditRedemption.deleted_at.is_(None)
            ]
            
            if status:
                conditions.append(CarbonCreditRedemption.status == status)
            
            query = select(CarbonCreditRedemption).where(
                and_(*conditions)
            ).order_by(desc(CarbonCreditRedemption.created_at)).limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseError(f"Failed to get user redemptions: {str(e)}")
    
    async def update_redemption_status(
        self, 
        redemption_id: str, 
        status: RedemptionStatus,
        external_reference: Optional[str] = None
    ) -> CarbonCreditRedemption:
        """
        Update redemption status
        
        Args:
            redemption_id: Redemption ID
            status: New status
            external_reference: External reference from payment processor
            
        Returns:
            Updated redemption record
        """
        try:
            redemption = await self.get_by_id(redemption_id)
            if not redemption:
                raise NotFoundError("Redemption not found")
            
            redemption.status = status
            if external_reference:
                redemption.external_reference = external_reference
            
            if status == RedemptionStatus.COMPLETED:
                redemption.completed_at = datetime.utcnow()
            
            return await self.update(redemption_id, redemption)
        except Exception as e:
            raise DatabaseError(f"Failed to update redemption status: {str(e)}")


class CarbonVerificationRuleRepository(BaseRepository[CarbonVerificationRule]):
    """Repository for carbon verification rule operations"""
    
    def __init__(self, db: Session):
        super().__init__(CarbonVerificationRule, db)
    
    async def get_rule_for_activity(self, activity_type: str) -> Optional[CarbonVerificationRule]:
        """
        Get verification rule for a specific activity type
        
        Args:
            activity_type: Type of activity
            
        Returns:
            Verification rule or None if not found
        """
        try:
            query = select(CarbonVerificationRule).where(
                and_(
                    CarbonVerificationRule.activity_type == activity_type,
                    CarbonVerificationRule.active == True,
                    CarbonVerificationRule.deleted_at.is_(None)
                )
            )
            
            result = await self.db.execute(query)
            return result.scalars().first()
        except Exception as e:
            raise DatabaseError(f"Failed to get verification rule: {str(e)}")
    
    async def get_active_rules(self) -> List[CarbonVerificationRule]:
        """
        Get all active verification rules
        
        Returns:
            List of active verification rules
        """
        try:
            query = select(CarbonVerificationRule).where(
                and_(
                    CarbonVerificationRule.active == True,
                    CarbonVerificationRule.deleted_at.is_(None)
                )
            ).order_by(CarbonVerificationRule.activity_type)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseError(f"Failed to get active rules: {str(e)}")
    
    async def create_rule(
        self,
        activity_type: str,
        verification_method: VerificationMethod,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        credit_multiplier: Decimal = Decimal('1.0'),
        requires_evidence: bool = False
    ) -> CarbonVerificationRule:
        """
        Create a new verification rule
        
        Args:
            activity_type: Type of activity
            verification_method: Required verification method
            min_amount: Minimum CO2 amount for automatic verification
            max_amount: Maximum CO2 amount for automatic verification
            credit_multiplier: Credit multiplier for this activity
            requires_evidence: Whether evidence is required
            
        Returns:
            Created verification rule
        """
        try:
            rule = CarbonVerificationRule(
                activity_type=activity_type,
                verification_method=verification_method,
                min_amount=min_amount,
                max_amount=max_amount,
                credit_multiplier=credit_multiplier,
                requires_evidence=requires_evidence,
                active=True
            )
            
            return await self.create(rule)
        except Exception as e:
            raise DatabaseError(f"Failed to create verification rule: {str(e)}")