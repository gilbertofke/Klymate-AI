"""
Carbon Credits Seed Data

This module provides seed data for carbon credit rates and verification rules.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.carbon_credit import (
    CarbonCreditRate, CarbonVerificationRule,
    RateType, VerificationMethod
)
from app.repositories.carbon_credit_repository import (
    CarbonCreditRepository, CarbonVerificationRuleRepository
)


class CarbonCreditSeedData:
    """Seed data manager for carbon credits system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rate_repo = CarbonCreditRepository(db)
        self.rule_repo = CarbonVerificationRuleRepository(db)
    
    async def seed_initial_rates(self) -> List[CarbonCreditRate]:
        """
        Seed initial carbon credit exchange rates
        
        Returns:
            List of created rate records
        """
        rates_data = [
            {
                'rate_type': RateType.CO2_TO_KC,
                'rate_value': Decimal('1.0'),  # 1 kg CO2 = 1 Klymate Credit
                'source': 'initial_seed',
                'effective_date': datetime.utcnow()
            },
            {
                'rate_type': RateType.KC_TO_USD,
                'rate_value': Decimal('0.05'),  # 1 KC = $0.05 USD
                'source': 'initial_seed',
                'effective_date': datetime.utcnow()
            }
        ]
        
        created_rates = []
        for rate_data in rates_data:
            # Check if rate already exists
            existing_rate = await self.rate_repo.get_current_rate(rate_data['rate_type'])
            if not existing_rate:
                rate = await self.rate_repo.create_rate(**rate_data)
                created_rates.append(rate)
        
        return created_rates
    
    async def seed_verification_rules(self) -> List[CarbonVerificationRule]:
        """
        Seed initial verification rules for different activity types
        
        Returns:
            List of created verification rule records
        """
        rules_data = [
            # Transport activities
            {
                'activity_type': 'public_transport',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.1'),
                'max_amount': Decimal('50.0'),
                'credit_multiplier': Decimal('1.0'),
                'requires_evidence': False
            },
            {
                'activity_type': 'cycling',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.1'),
                'max_amount': Decimal('20.0'),
                'credit_multiplier': Decimal('1.2'),  # 20% bonus for cycling
                'requires_evidence': False
            },
            {
                'activity_type': 'walking',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.1'),
                'max_amount': Decimal('10.0'),
                'credit_multiplier': Decimal('1.1'),  # 10% bonus for walking
                'requires_evidence': False
            },
            {
                'activity_type': 'carpooling',
                'verification_method': VerificationMethod.AI_VERIFIED,
                'min_amount': Decimal('1.0'),
                'max_amount': Decimal('100.0'),
                'credit_multiplier': Decimal('1.0'),
                'requires_evidence': True
            },
            
            # Diet activities
            {
                'activity_type': 'plant_based_meal',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.5'),
                'max_amount': Decimal('5.0'),
                'credit_multiplier': Decimal('1.0'),
                'requires_evidence': False
            },
            {
                'activity_type': 'local_food',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.2'),
                'max_amount': Decimal('3.0'),
                'credit_multiplier': Decimal('1.1'),  # 10% bonus for local food
                'requires_evidence': False
            },
            {
                'activity_type': 'reduced_meat',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('1.0'),
                'max_amount': Decimal('10.0'),
                'credit_multiplier': Decimal('1.0'),
                'requires_evidence': False
            },
            
            # Energy activities
            {
                'activity_type': 'renewable_energy',
                'verification_method': VerificationMethod.MANUAL_REVIEW,
                'min_amount': Decimal('10.0'),
                'max_amount': Decimal('1000.0'),
                'credit_multiplier': Decimal('1.5'),  # 50% bonus for renewable energy
                'requires_evidence': True
            },
            {
                'activity_type': 'energy_conservation',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.5'),
                'max_amount': Decimal('50.0'),
                'credit_multiplier': Decimal('1.0'),
                'requires_evidence': False
            },
            {
                'activity_type': 'led_lighting',
                'verification_method': VerificationMethod.AI_VERIFIED,
                'min_amount': Decimal('2.0'),
                'max_amount': Decimal('20.0'),
                'credit_multiplier': Decimal('1.0'),
                'requires_evidence': True
            },
            
            # Lifestyle activities
            {
                'activity_type': 'recycling',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.1'),
                'max_amount': Decimal('5.0'),
                'credit_multiplier': Decimal('0.8'),  # Lower multiplier for basic recycling
                'requires_evidence': False
            },
            {
                'activity_type': 'composting',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.5'),
                'max_amount': Decimal('10.0'),
                'credit_multiplier': Decimal('1.2'),  # 20% bonus for composting
                'requires_evidence': False
            },
            {
                'activity_type': 'water_conservation',
                'verification_method': VerificationMethod.AUTOMATIC,
                'min_amount': Decimal('0.2'),
                'max_amount': Decimal('15.0'),
                'credit_multiplier': Decimal('1.0'),
                'requires_evidence': False
            },
            {
                'activity_type': 'sustainable_shopping',
                'verification_method': VerificationMethod.AI_VERIFIED,
                'min_amount': Decimal('1.0'),
                'max_amount': Decimal('25.0'),
                'credit_multiplier': Decimal('1.1'),  # 10% bonus for sustainable shopping
                'requires_evidence': True
            },
            
            # High-impact activities requiring manual review
            {
                'activity_type': 'solar_installation',
                'verification_method': VerificationMethod.MANUAL_REVIEW,
                'min_amount': Decimal('100.0'),
                'max_amount': Decimal('5000.0'),
                'credit_multiplier': Decimal('2.0'),  # 100% bonus for major installations
                'requires_evidence': True
            },
            {
                'activity_type': 'electric_vehicle',
                'verification_method': VerificationMethod.MANUAL_REVIEW,
                'min_amount': Decimal('500.0'),
                'max_amount': Decimal('3000.0'),
                'credit_multiplier': Decimal('1.8'),  # 80% bonus for EV adoption
                'requires_evidence': True
            },
            {
                'activity_type': 'home_insulation',
                'verification_method': VerificationMethod.MANUAL_REVIEW,
                'min_amount': Decimal('200.0'),
                'max_amount': Decimal('2000.0'),
                'credit_multiplier': Decimal('1.5'),  # 50% bonus for home improvements
                'requires_evidence': True
            }
        ]
        
        created_rules = []
        for rule_data in rules_data:
            # Check if rule already exists
            existing_rule = await self.rule_repo.get_rule_for_activity(rule_data['activity_type'])
            if not existing_rule:
                rule = await self.rule_repo.create_rule(**rule_data)
                created_rules.append(rule)
        
        return created_rules
    
    async def seed_all(self) -> Dict[str, Any]:
        """
        Seed all carbon credit data
        
        Returns:
            Dictionary with counts of created records
        """
        rates = await self.seed_initial_rates()
        rules = await self.seed_verification_rules()
        
        return {
            'rates_created': len(rates),
            'rules_created': len(rules),
            'total_records': len(rates) + len(rules)
        }
    
    @staticmethod
    def get_activity_descriptions() -> Dict[str, str]:
        """
        Get descriptions for all activity types
        
        Returns:
            Dictionary mapping activity types to descriptions
        """
        return {
            # Transport
            'public_transport': 'Using public transportation instead of private vehicle',
            'cycling': 'Cycling instead of driving or using motorized transport',
            'walking': 'Walking instead of using motorized transport',
            'carpooling': 'Sharing rides with others to reduce individual emissions',
            
            # Diet
            'plant_based_meal': 'Choosing plant-based meals over meat-based options',
            'local_food': 'Purchasing locally sourced food to reduce transport emissions',
            'reduced_meat': 'Reducing meat consumption compared to typical diet',
            
            # Energy
            'renewable_energy': 'Using renewable energy sources (solar, wind, etc.)',
            'energy_conservation': 'Reducing energy consumption through behavioral changes',
            'led_lighting': 'Switching to LED lighting from incandescent bulbs',
            
            # Lifestyle
            'recycling': 'Properly recycling materials instead of throwing away',
            'composting': 'Composting organic waste instead of sending to landfill',
            'water_conservation': 'Reducing water usage through conservation practices',
            'sustainable_shopping': 'Choosing sustainable and eco-friendly products',
            
            # High-impact
            'solar_installation': 'Installing solar panels or renewable energy systems',
            'electric_vehicle': 'Purchasing or using electric vehicles',
            'home_insulation': 'Improving home insulation to reduce energy usage'
        }
    
    @staticmethod
    def get_verification_requirements() -> Dict[str, Dict[str, Any]]:
        """
        Get verification requirements for each activity type
        
        Returns:
            Dictionary with verification requirements
        """
        return {
            'automatic': {
                'description': 'Automatically verified based on user input',
                'requirements': ['Valid activity log entry', 'Reasonable CO2 savings amount'],
                'processing_time': 'Immediate'
            },
            'ai_verified': {
                'description': 'AI-assisted verification with optional evidence',
                'requirements': ['Activity log entry', 'Optional photo evidence', 'AI pattern analysis'],
                'processing_time': '1-24 hours'
            },
            'manual_review': {
                'description': 'Manual review by verification team',
                'requirements': ['Detailed activity description', 'Photo evidence', 'Documentation'],
                'processing_time': '1-7 business days'
            }
        }