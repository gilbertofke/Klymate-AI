"""
Carbon Credits Schemas

This module defines Pydantic schemas for carbon credits API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

from app.models.carbon_credit import (
    RateType, TransactionType, VerificationStatus, VerificationMethod,
    RedemptionType, RedemptionStatus
)


# Request Schemas

class RedemptionRequest(BaseModel):
    """Schema for redemption requests"""
    redemption_type: RedemptionType = Field(..., description="Type of redemption")
    amount_kc: Decimal = Field(..., gt=0, description="Amount of KC to redeem")
    recipient_info: Dict[str, Any] = Field(..., description="Recipient information")
    
    @validator('amount_kc')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > Decimal('10000'):  # Maximum redemption limit
            raise ValueError("Amount exceeds maximum redemption limit")
        return v
    
    @validator('recipient_info')
    def validate_recipient_info(cls, v, values):
        redemption_type = values.get('redemption_type')
        
        if redemption_type == RedemptionType.CASH_OUT:
            required_fields = ['payment_method', 'account_id']
            if redemption_type == RedemptionType.CASH_OUT and v.get('payment_method') == 'paypal':
                required_fields.append('email')
        elif redemption_type == RedemptionType.CARBON_OFFSET:
            required_fields = ['offset_provider', 'project_type']
        elif redemption_type == RedemptionType.DONATION:
            required_fields = ['charity_name', 'charity_id']
        elif redemption_type == RedemptionType.MARKETPLACE:
            required_fields = ['product_category']
        else:
            required_fields = []
        
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field for {redemption_type.value}: {field}")
        
        return v


class VerificationRequest(BaseModel):
    """Schema for transaction verification requests"""
    status: VerificationStatus = Field(..., description="Verification status")
    reviewer_notes: Optional[str] = Field(None, description="Reviewer notes")
    evidence_urls: Optional[List[str]] = Field(None, description="Evidence URLs")
    
    @validator('evidence_urls')
    def validate_evidence_urls(cls, v):
        if v:
            for url in v:
                if not url.startswith(('http://', 'https://')):
                    raise ValueError("Invalid URL format")
        return v


class RateUpdateRequest(BaseModel):
    """Schema for exchange rate update requests"""
    rate_type: RateType = Field(..., description="Type of rate to update")
    rate_value: Decimal = Field(..., gt=0, description="New rate value")
    source: Optional[str] = Field("manual_update", description="Source of rate update")
    
    @validator('rate_value')
    def validate_rate_value(cls, v, values):
        rate_type = values.get('rate_type')
        
        if rate_type == RateType.CO2_TO_KC:
            if v < Decimal('0.1') or v > Decimal('10.0'):
                raise ValueError("CO2 to KC rate must be between 0.1 and 10.0")
        elif rate_type == RateType.KC_TO_USD:
            if v < Decimal('0.001') or v > Decimal('1.0'):
                raise ValueError("KC to USD rate must be between 0.001 and 1.0")
        
        return v


# Response Schemas

class ExchangeRateResponse(BaseModel):
    """Schema for exchange rate information"""
    rate: Optional[float] = Field(None, description="Exchange rate value")
    effective_date: Optional[str] = Field(None, description="When rate becomes effective")
    source: Optional[str] = Field(None, description="Source of the rate")


class UserBalanceResponse(BaseModel):
    """Schema for user balance information"""
    user_id: str = Field(..., description="User ID")
    current_balance: float = Field(..., description="Current credit balance")
    total_earned: float = Field(..., description="Total credits earned")
    total_redeemed: float = Field(..., description="Total credits redeemed")
    usd_value: Optional[float] = Field(None, description="USD value of current balance")
    exchange_rates: Dict[str, Optional[float]] = Field(..., description="Current exchange rates")
    last_updated: str = Field(..., description="Last update timestamp")


class TransactionResponse(BaseModel):
    """Schema for transaction information"""
    id: str = Field(..., description="Transaction ID")
    transaction_type: str = Field(..., description="Type of transaction")
    amount: float = Field(..., description="Credit amount")
    co2_saved: Optional[float] = Field(None, description="CO2 saved in kg")
    verification_status: str = Field(..., description="Verification status")
    verification_method: str = Field(..., description="Verification method")
    usd_value: Optional[float] = Field(None, description="USD value at time of transaction")
    notes: Optional[str] = Field(None, description="Transaction notes")
    created_at: str = Field(..., description="Transaction creation timestamp")
    verified_at: Optional[str] = Field(None, description="Verification timestamp")
    activity_reference: Optional[str] = Field(None, description="Reference to related activity")


class TransactionListResponse(BaseModel):
    """Schema for transaction list response"""
    transactions: List[TransactionResponse] = Field(..., description="List of transactions")
    total_count: Optional[int] = Field(None, description="Total number of transactions")
    has_more: bool = Field(False, description="Whether there are more transactions")


class RedemptionResponse(BaseModel):
    """Schema for redemption information"""
    id: str = Field(..., description="Redemption ID")
    redemption_type: str = Field(..., description="Type of redemption")
    amount_kc: float = Field(..., description="Amount of KC redeemed")
    amount_usd: float = Field(..., description="USD value")
    status: str = Field(..., description="Redemption status")
    external_reference: Optional[str] = Field(None, description="External reference")
    recipient_info: Dict[str, Any] = Field(..., description="Recipient information")
    created_at: str = Field(..., description="Redemption creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")


class CurrentRatesResponse(BaseModel):
    """Schema for current exchange rates"""
    co2_to_kc: ExchangeRateResponse = Field(..., description="CO2 to KC exchange rate")
    kc_to_usd: ExchangeRateResponse = Field(..., description="KC to USD exchange rate")
    last_updated: str = Field(..., description="Last update timestamp")


class PendingVerificationResponse(BaseModel):
    """Schema for pending verification information"""
    id: str = Field(..., description="Transaction ID")
    user_id: str = Field(..., description="User ID")
    amount: float = Field(..., description="Credit amount")
    co2_saved: Optional[float] = Field(None, description="CO2 saved in kg")
    activity_reference: Optional[str] = Field(None, description="Reference to related activity")
    verification_method: str = Field(..., description="Required verification method")
    verification_metadata: Optional[Dict[str, Any]] = Field(None, description="Verification metadata")
    created_at: str = Field(..., description="Transaction creation timestamp")
    notes: Optional[str] = Field(None, description="Transaction notes")


class MarketRateUpdateResponse(BaseModel):
    """Schema for market rate update results"""
    updated_rates: List[Dict[str, Any]] = Field(..., description="Successfully updated rates")
    errors: List[str] = Field(..., description="Update errors")
    timestamp: str = Field(..., description="Update timestamp")


class CreditStatsResponse(BaseModel):
    """Schema for credit statistics"""
    total_users_with_credits: int = Field(..., description="Number of users with credits")
    total_credits_issued: float = Field(..., description="Total credits issued")
    total_credits_redeemed: float = Field(..., description="Total credits redeemed")
    total_co2_offset: float = Field(..., description="Total CO2 offset in kg")
    average_credits_per_user: float = Field(..., description="Average credits per user")
    top_earners: List[Dict[str, Any]] = Field(..., description="Top credit earners")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent credit activity")


# Query Parameter Schemas

class TransactionQueryParams(BaseModel):
    """Schema for transaction query parameters"""
    limit: int = Field(50, ge=1, le=100, description="Maximum number of transactions")
    offset: int = Field(0, ge=0, description="Number of transactions to skip")
    transaction_type: Optional[TransactionType] = Field(None, description="Filter by transaction type")
    verification_status: Optional[VerificationStatus] = Field(None, description="Filter by verification status")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")


class RedemptionQueryParams(BaseModel):
    """Schema for redemption query parameters"""
    limit: int = Field(50, ge=1, le=100, description="Maximum number of redemptions")
    offset: int = Field(0, ge=0, description="Number of redemptions to skip")
    status: Optional[RedemptionStatus] = Field(None, description="Filter by redemption status")
    redemption_type: Optional[RedemptionType] = Field(None, description="Filter by redemption type")


# Error Schemas

class CreditErrorResponse(BaseModel):
    """Schema for credit-related error responses"""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


# Validation Schemas

class ActivityCreditCalculation(BaseModel):
    """Schema for activity credit calculation"""
    activity_type: str = Field(..., description="Type of activity")
    co2_saved: float = Field(..., gt=0, description="CO2 saved in kg")
    verification_method: Optional[VerificationMethod] = Field(None, description="Preferred verification method")
    evidence_urls: Optional[List[str]] = Field(None, description="Evidence URLs")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @validator('co2_saved')
    def validate_co2_saved(cls, v):
        if v <= 0:
            raise ValueError("CO2 saved must be greater than 0")
        if v > 1000:  # Reasonable upper limit
            raise ValueError("CO2 saved amount seems unrealistic")
        return v


class CreditCalculationResponse(BaseModel):
    """Schema for credit calculation response"""
    activity_type: str = Field(..., description="Type of activity")
    co2_saved: float = Field(..., description="CO2 saved in kg")
    base_credits: float = Field(..., description="Base credits before multiplier")
    credit_multiplier: float = Field(..., description="Credit multiplier applied")
    final_credits: float = Field(..., description="Final credits to be awarded")
    verification_required: bool = Field(..., description="Whether verification is required")
    verification_method: str = Field(..., description="Required verification method")
    estimated_usd_value: Optional[float] = Field(None, description="Estimated USD value")
    eligibility_notes: Optional[str] = Field(None, description="Eligibility notes")