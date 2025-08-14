"""
Carbon Credits API Endpoints

This module provides REST API endpoints for the carbon credits system,
including balance management, transactions, redemptions, and verification.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.core.middleware import get_current_user
from app.services.carbon_credits_service import CarbonCreditsService, CarbonMarketIntegration
from app.schemas.carbon_credit import (
    UserBalanceResponse, TransactionResponse, TransactionListResponse,
    RedemptionRequest, RedemptionResponse, VerificationRequest,
    RateUpdateRequest, CurrentRatesResponse, PendingVerificationResponse,
    MarketRateUpdateResponse, CreditStatsResponse, TransactionQueryParams,
    RedemptionQueryParams, ActivityCreditCalculation, CreditCalculationResponse,
    CreditErrorResponse
)
from app.models.carbon_credit import (
    TransactionType, VerificationStatus, RedemptionStatus, RateType
)
from app.models.user import User
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.utils.cache import cache_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credits", tags=["Carbon Credits"])


@router.get("/balance", response_model=UserBalanceResponse)
async def get_user_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's carbon credit balance and statistics
    """
    try:
        service = CarbonCreditsService(db)
        balance = await service.get_user_balance(current_user.id)
        return UserBalanceResponse(**balance)
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get balance for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve balance")


@router.get("/transactions", response_model=TransactionListResponse)
async def get_user_transactions(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of transactions"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's transaction history with pagination and filtering
    """
    try:
        service = CarbonCreditsService(db)
        transactions = await service.get_user_transactions(
            current_user.id, limit, offset, transaction_type
        )
        
        return TransactionListResponse(
            transactions=[TransactionResponse(**t) for t in transactions],
            total_count=None,  # Could be implemented with a separate count query
            has_more=len(transactions) == limit
        )
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get transactions for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transactions")


@router.post("/redeem", response_model=RedemptionResponse)
async def initiate_redemption(
    redemption_request: RedemptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate a carbon credit redemption request
    """
    try:
        service = CarbonCreditsService(db)
        redemption = await service.initiate_redemption(
            user_id=current_user.id,
            redemption_type=redemption_request.redemption_type,
            amount_kc=redemption_request.amount_kc,
            recipient_info=redemption_request.recipient_info
        )
        
        return RedemptionResponse(
            id=redemption.id,
            redemption_type=redemption.redemption_type.value,
            amount_kc=float(redemption.amount_kc),
            amount_usd=float(redemption.amount_usd),
            status=redemption.status.value,
            external_reference=redemption.external_reference,
            recipient_info=redemption.recipient_info,
            created_at=redemption.created_at.isoformat(),
            completed_at=redemption.completed_at.isoformat() if redemption.completed_at else None
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to initiate redemption for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process redemption")


@router.get("/rates", response_model=CurrentRatesResponse)
async def get_current_rates(db: Session = Depends(get_db)):
    """
    Get current carbon credit exchange rates
    """
    try:
        # Try to get from cache first
        cache_key = "carbon_credits:current_rates"
        cached_rates = await cache_manager.get(cache_key)
        
        if cached_rates:
            return CurrentRatesResponse(**cached_rates)
        
        service = CarbonCreditsService(db)
        rates = await service.get_current_rates()
        
        # Cache for 5 minutes
        await cache_manager.set(cache_key, rates, ttl=300)
        
        return CurrentRatesResponse(
            co2_to_kc=rates['co2_to_kc'],
            kc_to_usd=rates['kc_to_usd'],
            last_updated=rates['last_updated']
        )
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get current rates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve rates")


@router.post("/calculate", response_model=CreditCalculationResponse)
async def calculate_credits_for_activity(
    calculation_request: ActivityCreditCalculation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate credits for a potential activity (preview calculation)
    """
    try:
        service = CarbonCreditsService(db)
        
        # Get verification rule for activity
        rule = await service.rule_repo.get_rule_for_activity(calculation_request.activity_type)
        if not rule:
            raise HTTPException(
                status_code=404, 
                detail=f"No verification rule found for activity type: {calculation_request.activity_type}"
            )
        
        # Get current CO2 to KC rate
        co2_rate = await service.rate_repo.get_current_rate(RateType.CO2_TO_KC)
        if not co2_rate:
            raise HTTPException(status_code=400, detail="CO2 exchange rate not available")
        
        # Calculate credits
        base_rate = float(co2_rate.rate_value)
        base_credits = calculation_request.co2_saved * base_rate
        final_credits = rule.calculate_credits(calculation_request.co2_saved, base_rate)
        
        # Get USD rate for value estimation
        usd_rate = await service.rate_repo.get_current_rate(RateType.KC_TO_USD)
        estimated_usd_value = None
        if usd_rate:
            estimated_usd_value = final_credits * float(usd_rate.rate_value)
        
        # Check verification requirements
        verification_required = not rule.is_automatic_verification_eligible(calculation_request.co2_saved)
        
        return CreditCalculationResponse(
            activity_type=calculation_request.activity_type,
            co2_saved=calculation_request.co2_saved,
            base_credits=base_credits,
            credit_multiplier=float(rule.credit_multiplier),
            final_credits=final_credits,
            verification_required=verification_required,
            verification_method=rule.verification_method.value,
            estimated_usd_value=estimated_usd_value,
            eligibility_notes=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate credits: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate credits")


# Admin endpoints (require admin privileges)

@router.get("/admin/pending-verifications", response_model=List[PendingVerificationResponse])
async def get_pending_verifications(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transactions pending verification (admin only)
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = CarbonCreditsService(db)
        pending = await service.get_pending_verifications(limit)
        
        return [PendingVerificationResponse(**p) for p in pending]
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get pending verifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pending verifications")


@router.post("/admin/verify/{transaction_id}")
async def verify_transaction(
    transaction_id: str,
    verification_request: VerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify a pending transaction (admin only)
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = CarbonCreditsService(db)
        transaction = await service.verify_transaction(
            transaction_id=transaction_id,
            status=verification_request.status,
            reviewer_notes=verification_request.reviewer_notes,
            evidence_urls=verification_request.evidence_urls
        )
        
        return {
            "transaction_id": transaction.id,
            "status": transaction.verification_status.value,
            "verified_at": transaction.verified_at.isoformat() if transaction.verified_at else None,
            "message": f"Transaction {verification_request.status.value} successfully"
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to verify transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify transaction")


@router.post("/admin/update-rates", response_model=dict)
async def update_exchange_rates(
    rate_update: RateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update exchange rates (admin only)
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = CarbonCreditsService(db)
        rate = await service.update_exchange_rate(
            rate_type=rate_update.rate_type,
            rate_value=rate_update.rate_value,
            source=rate_update.source
        )
        
        return {
            "rate_type": rate.rate_type.value,
            "new_rate": float(rate.rate_value),
            "effective_date": rate.effective_date.isoformat(),
            "source": rate.source,
            "message": "Exchange rate updated successfully"
        }
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update exchange rate: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update rate")


@router.post("/admin/market-update", response_model=MarketRateUpdateResponse)
async def trigger_market_rate_update(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger market rate update (admin only)
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = CarbonCreditsService(db)
        market_integration = CarbonMarketIntegration(service)
        
        # Run market update in background
        background_tasks.add_task(market_integration.update_rates_from_market)
        
        return MarketRateUpdateResponse(
            updated_rates=[],
            errors=[],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to trigger market rate update: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger market update")


@router.get("/admin/stats", response_model=CreditStatsResponse)
async def get_credit_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get carbon credits system statistics (admin only)
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = CarbonCreditsService(db)
        
        # Get top earners
        top_earners_data = await service.user_credits_repo.get_top_earners(limit=10)
        top_earners = [
            {
                "user_id": credits.user_id,
                "total_earned": float(credits.total_earned),
                "current_balance": float(credits.current_balance)
            }
            for credits in top_earners_data
        ]
        
        # Get recent transactions (simplified)
        recent_transactions = await service.transaction_repo.get_user_transactions(
            user_id="", limit=10  # This would need to be modified to get all recent transactions
        )
        
        # Calculate basic stats (this would be more sophisticated in production)
        total_users_with_credits = len(top_earners_data)
        total_credits_issued = sum(float(credits.total_earned) for credits in top_earners_data)
        total_credits_redeemed = sum(float(credits.total_redeemed) for credits in top_earners_data)
        
        return CreditStatsResponse(
            total_users_with_credits=total_users_with_credits,
            total_credits_issued=total_credits_issued,
            total_credits_redeemed=total_credits_redeemed,
            total_co2_offset=total_credits_issued,  # Assuming 1:1 ratio for simplicity
            average_credits_per_user=total_credits_issued / max(total_users_with_credits, 1),
            top_earners=top_earners,
            recent_activity=[]  # Would be populated with recent transaction data
        )
    except Exception as e:
        logger.error(f"Failed to get credit statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


# Webhook endpoints for external integrations

@router.post("/webhooks/payment-processor")
async def payment_processor_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """
    Handle webhooks from payment processors for redemption status updates
    """
    try:
        # This would handle webhooks from payment processors like PayPal, Stripe, etc.
        # to update redemption statuses
        
        external_reference = webhook_data.get('external_reference')
        status = webhook_data.get('status')
        
        if not external_reference or not status:
            raise HTTPException(status_code=400, detail="Missing required webhook data")
        
        # Update redemption status based on webhook
        # This is a simplified implementation
        logger.info(f"Received payment webhook for {external_reference}: {status}")
        
        return {"status": "processed", "message": "Webhook processed successfully"}
        
    except Exception as e:
        logger.error(f"Failed to process payment webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.post("/webhooks/carbon-market")
async def carbon_market_webhook(
    webhook_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle webhooks from carbon market APIs for rate updates
    """
    try:
        # This would handle webhooks from carbon market APIs
        # to automatically update exchange rates
        
        rate_type = webhook_data.get('rate_type')
        new_rate = webhook_data.get('rate')
        
        if not rate_type or not new_rate:
            raise HTTPException(status_code=400, detail="Missing required webhook data")
        
        # Trigger rate update in background
        service = CarbonCreditsService(db)
        background_tasks.add_task(
            service.update_exchange_rate,
            RateType(rate_type),
            Decimal(str(new_rate)),
            "carbon_market_webhook"
        )
        
        return {"status": "processed", "message": "Rate update triggered"}
        
    except Exception as e:
        logger.error(f"Failed to process carbon market webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")