"""
Test Data Factories - Task 10 Implementation

This module provides factory classes for generating test data using
the Factory Boy library. Follows best practices for test data generation
with realistic and consistent data.
"""

import factory
import factory.fuzzy
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Any, List
import random
import string

from app.models.user import User
from app.models.habit import HabitCategory, CategoryType
from app.models.user_habit import UserHabit
from app.models.badge import Badge, BadgeCategory, BadgeTrigger, UserBadge
from app.models.ai_conversation import AIConversation
from app.models.carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonCreditRedemption, CarbonVerificationRule,
    RateType, TransactionType, VerificationStatus, VerificationMethod,
    RedemptionType, RedemptionStatus
)


class UserFactory(factory.Factory):
    """Factory for creating User test instances."""
    
    class Meta:
        model = User
    
    # Basic user information
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker('name')
    display_name = factory.LazyAttribute(lambda obj: obj.name.split()[0])
    
    # Firebase integration
    firebase_uid = factory.LazyAttribute(lambda obj: f"firebase_{obj.email.split('@')[0]}")
    
    # User status
    is_active = True
    is_verified = factory.Faker('boolean', chance_of_getting_true=80)
    is_deleted = False
    
    # Onboarding
    onboarding_completed = factory.Faker('boolean', chance_of_getting_true=70)
    
    # Carbon footprint data
    baseline_footprint = factory.fuzzy.FuzzyDecimal(8000.0, 20000.0, 2)  # kg CO2/year
    current_footprint = factory.LazyAttribute(
        lambda obj: obj.baseline_footprint - Decimal(random.uniform(500, 2000))
    )
    total_co2_saved = factory.fuzzy.FuzzyDecimal(0.0, 1000.0, 2)
    
    # Gamification
    eco_score = factory.fuzzy.FuzzyInteger(0, 1000)
    current_streak = factory.fuzzy.FuzzyInteger(0, 100)
    longest_streak = factory.LazyAttribute(
        lambda obj: max(obj.current_streak, random.randint(obj.current_streak, obj.current_streak + 50))
    )
    
    # Activity tracking
    login_count = factory.fuzzy.FuzzyInteger(1, 100)
    last_login_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(days=random.randint(1, 30)))
    
    @factory.post_generation
    def set_preferences(self, create, extracted, **kwargs):
        """Set user preferences as JSON."""
        if create:
            preferences = {
                "notifications": {
                    "email": True,
                    "push": True,
                    "weekly_summary": True
                },
                "privacy": {
                    "share_progress": False,
                    "public_profile": False
                },
                "goals": {
                    "weekly_co2_target": float(random.uniform(10, 50)),
                    "monthly_co2_target": float(random.uniform(50, 200))
                }
            }
            import json
            self.preferences = json.dumps(preferences)


class HabitCategoryFactory(factory.Factory):
    """Factory for creating HabitCategory test instances."""
    
    class Meta:
        model = HabitCategory
    
    name = factory.Iterator([
        "Walking instead of driving",
        "Using public transport",
        "Cycling to work",
        "Eating vegetarian meals",
        "Reducing meat consumption",
        "Using LED bulbs",
        "Adjusting thermostat",
        "Unplugging devices",
        "Recycling waste",
        "Reducing plastic use"
    ])
    
    description = factory.LazyAttribute(
        lambda obj: f"Reduce your carbon footprint by {obj.name.lower()}"
    )
    
    category_type = factory.Iterator([
        CategoryType.TRANSPORT,
        CategoryType.DIET,
        CategoryType.ENERGY,
        CategoryType.LIFESTYLE
    ])
    
    # CO2 impact calculations
    co2_per_unit = factory.fuzzy.FuzzyDecimal(0.5, 10.0, 2)  # kg CO2 per unit
    unit_name = factory.Iterator(["km", "meal", "hour", "item", "day"])
    
    # Category metadata
    icon_name = factory.LazyAttribute(lambda obj: f"icon_{obj.category_type.value}")
    color_code = factory.Iterator(["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"])
    
    # Status
    is_active = True
    is_deleted = False
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-1y', end_date='-6m')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(days=random.randint(1, 30)))


class UserHabitFactory(factory.Factory):
    """Factory for creating UserHabit test instances."""
    
    class Meta:
        model = UserHabit
    
    # Foreign keys (will be set by test setup)
    user_id = factory.SubFactory(UserFactory)
    category_id = factory.SubFactory(HabitCategoryFactory)
    
    # Habit logging data
    quantity = factory.fuzzy.FuzzyDecimal(1.0, 10.0, 1)
    co2_saved = factory.LazyAttribute(
        lambda obj: obj.quantity * Decimal(random.uniform(1.0, 5.0))
    )
    
    # Logging details
    logged_date = factory.Faker('date_between', start_date='-30d', end_date='today')
    notes = factory.Faker('sentence', nb_words=8)
    
    # Verification
    is_verified = factory.Faker('boolean', chance_of_getting_true=90)
    verified_at = factory.LazyAttribute(
        lambda obj: obj.created_at + timedelta(hours=random.randint(1, 24)) if obj.is_verified else None
    )
    
    # Status
    is_deleted = False
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(minutes=random.randint(1, 60)))


class BadgeFactory(factory.Factory):
    """Factory for creating Badge test instances."""
    
    class Meta:
        model = Badge
    
    name = factory.Iterator([
        "First Steps",
        "Eco Warrior",
        "Green Commuter",
        "Energy Saver",
        "Streak Master",
        "Carbon Crusher",
        "Habit Hero",
        "Sustainability Star",
        "Planet Protector",
        "Green Guardian"
    ])
    
    description = factory.LazyAttribute(
        lambda obj: f"Earned by demonstrating commitment to {obj.name.lower().replace(' ', '_')} activities"
    )
    
    category = factory.Iterator([
        BadgeCategory.MILESTONE,
        BadgeCategory.ACHIEVEMENT,
        BadgeCategory.STREAK,
        BadgeCategory.SOCIAL,
        BadgeCategory.SPECIAL
    ])
    
    points_value = factory.fuzzy.FuzzyInteger(10, 100)
    icon_url = factory.LazyAttribute(lambda obj: f"/icons/badges/{obj.name.lower().replace(' ', '_')}.svg")
    
    # Badge criteria (JSON)
    @factory.lazy_attribute
    def criteria(self):
        criteria_options = [
            {
                "trigger": "habit_logged",
                "count": random.randint(5, 50),
                "category": "any"
            },
            {
                "trigger": "co2_saved",
                "threshold": random.uniform(10.0, 100.0),
                "timeframe": "total"
            },
            {
                "trigger": "streak_achieved",
                "days": random.randint(7, 30)
            },
            {
                "trigger": "milestone_reached",
                "conditions": {
                    "and": [
                        {"field": "total_habits", "operator": ">=", "value": random.randint(10, 50)},
                        {"field": "total_co2_saved", "operator": ">=", "value": random.uniform(50.0, 200.0)}
                    ]
                }
            }
        ]
        return random.choice(criteria_options)
    
    # Status
    is_active = True
    sort_order = factory.Sequence(lambda n: n)
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-1y', end_date='-6m')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(days=random.randint(1, 30)))


class UserBadgeFactory(factory.Factory):
    """Factory for creating UserBadge test instances."""
    
    class Meta:
        model = UserBadge
    
    # Foreign keys
    user_id = factory.SubFactory(UserFactory)
    badge_id = factory.SubFactory(BadgeFactory)
    
    # Badge earning
    earned_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    
    # Progress tracking
    @factory.lazy_attribute
    def progress_data(self):
        if random.choice([True, False]):  # 50% chance of having progress data
            return {
                "current": random.randint(80, 100),
                "target": 100,
                "percentage": random.uniform(80.0, 100.0)
            }
        return None
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(minutes=random.randint(1, 60)))


class AIConversationFactory(factory.Factory):
    """Factory for creating AIConversation test instances."""
    
    class Meta:
        model = AIConversation
    
    # Foreign key
    user_id = factory.SubFactory(UserFactory)
    
    # Message details
    message_type = factory.Iterator(["user", "assistant", "system"])
    content = factory.LazyAttribute(
        lambda obj: _generate_conversation_content(obj.message_type)
    )
    
    # Session tracking
    session_id = factory.LazyAttribute(lambda obj: f"session_{random.randint(1000, 9999)}")
    
    # AI metadata
    model_used = factory.Iterator(["gpt-3.5-turbo", "gpt-4", "claude-3"])
    tokens_used = factory.fuzzy.FuzzyInteger(50, 500)
    processing_time_ms = factory.fuzzy.FuzzyInteger(100, 2000)
    
    # Response quality
    response_rating = factory.fuzzy.FuzzyInteger(1, 5)
    response_feedback = factory.Faker('sentence', nb_words=6)
    
    # Vector embedding (mock)
    @factory.lazy_attribute
    def embedding(self):
        # Generate mock embedding vector
        import json
        return json.dumps([random.uniform(-1, 1) for _ in range(1536)])
    
    # Context metadata
    @factory.lazy_attribute
    def context_metadata(self):
        return {
            "user_context": {
                "total_habits": random.randint(0, 50),
                "current_streak": random.randint(0, 30),
                "eco_score": random.randint(0, 1000)
            },
            "conversation_context": {
                "topic": random.choice(["habits", "goals", "progress", "tips"]),
                "sentiment": random.choice(["positive", "neutral", "negative"])
            }
        }
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-7d', end_date='now')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(seconds=random.randint(1, 300)))


def _generate_conversation_content(message_type: str) -> str:
    """Generate realistic conversation content based on message type."""
    if message_type == "user":
        user_messages = [
            "How can I reduce my carbon footprint?",
            "What are some easy habits to start with?",
            "I've been walking to work for a week now!",
            "Can you help me set a goal for this month?",
            "What's the impact of eating less meat?",
            "I'm struggling to maintain my streak",
            "How do I track my energy usage?",
            "What are the best transportation alternatives?"
        ]
        return random.choice(user_messages)
    
    elif message_type == "assistant":
        assistant_messages = [
            "Great question! Here are some effective ways to reduce your carbon footprint...",
            "Congratulations on your progress! Walking to work is an excellent habit.",
            "I'd recommend starting with transportation and energy habits as they have high impact.",
            "Based on your current habits, here's a personalized goal suggestion...",
            "Reducing meat consumption can save approximately 0.8kg CO2 per meal.",
            "Don't worry about streak breaks - consistency matters more than perfection.",
            "You can track energy usage by monitoring your monthly bills and using smart meters.",
            "Public transport, cycling, and walking are the most sustainable options."
        ]
        return random.choice(assistant_messages)
    
    else:  # system
        system_messages = [
            "User session started",
            "Conversation context updated",
            "User preferences loaded",
            "Habit data synchronized",
            "Goal progress calculated",
            "Badge criteria evaluated"
        ]
        return random.choice(system_messages)


# Utility functions for creating related test data

def create_user_with_habits(habit_count: int = 5) -> Dict[str, Any]:
    """Create a user with associated habits."""
    user = UserFactory.create()
    habits = []
    
    for _ in range(habit_count):
        habit = UserHabitFactory.create(user_id=user.id)
        habits.append(habit)
    
    return {
        "user": user,
        "habits": habits
    }


def create_user_with_badges(badge_count: int = 3) -> Dict[str, Any]:
    """Create a user with earned badges."""
    user = UserFactory.create()
    badges = []
    user_badges = []
    
    for _ in range(badge_count):
        badge = BadgeFactory.create()
        user_badge = UserBadgeFactory.create(user_id=user.id, badge_id=badge.id)
        badges.append(badge)
        user_badges.append(user_badge)
    
    return {
        "user": user,
        "badges": badges,
        "user_badges": user_badges
    }


def create_conversation_thread(user_id: int, message_count: int = 6):
    """Create a conversation thread with alternating user/assistant messages."""
    conversations = []
    session_id = f"session_{random.randint(1000, 9999)}"
    
    for i in range(message_count):
        message_type = "user" if i % 2 == 0 else "assistant"
        conversation = AIConversationFactory.create(
            user_id=user_id,
            message_type=message_type,
            session_id=session_id
        )
        conversations.append(conversation)
    
    return conversations


def create_test_dataset() -> Dict[str, Any]:
    """Create a comprehensive test dataset with related entities."""
    # Create users
    users = UserFactory.create_batch(10)
    
    # Create habit categories
    categories = HabitCategoryFactory.create_batch(8)
    
    # Create badges
    badges = BadgeFactory.create_batch(12)
    
    # Create habits for users
    habits = []
    for user in users[:5]:  # First 5 users get habits
        user_habits = UserHabitFactory.create_batch(
            random.randint(3, 8),
            user_id=user.id,
            category_id=factory.Iterator([cat.id for cat in categories])
        )
        habits.extend(user_habits)
    
    # Create user badges
    user_badges = []
    for user in users[:3]:  # First 3 users get badges
        earned_badges = UserBadgeFactory.create_batch(
            random.randint(2, 5),
            user_id=user.id,
            badge_id=factory.Iterator([badge.id for badge in badges])
        )
        user_badges.extend(earned_badges)
    
    # Create AI conversations
    conversations = []
    for user in users[:4]:  # First 4 users have conversations
        user_conversations = create_conversation_thread(user.id, random.randint(4, 10))
        conversations.extend(user_conversations)
    
    return {
        "users": users,
        "categories": categories,
        "badges": badges,
        "habits": habits,
        "user_badges": user_badges,
        "conversations": conversations
    }


class CarbonCreditRateFactory(factory.Factory):
    """Factory for creating CarbonCreditRate test instances."""
    
    class Meta:
        model = CarbonCreditRate
    
    rate_type = factory.Iterator([RateType.CO2_TO_KC, RateType.KC_TO_USD])
    rate_value = factory.LazyAttribute(
        lambda obj: Decimal('1.0') if obj.rate_type == RateType.CO2_TO_KC else Decimal('0.05')
    )
    effective_date = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    source = factory.Iterator(['market_api', 'manual_update', 'initial_seed'])
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(minutes=random.randint(1, 60)))


class UserCarbonCreditsFactory(factory.Factory):
    """Factory for creating UserCarbonCredits test instances."""
    
    class Meta:
        model = UserCarbonCredits
    
    user_id = factory.SubFactory(UserFactory)
    current_balance = factory.fuzzy.FuzzyDecimal(0.0, 500.0, 2)
    total_earned = factory.LazyAttribute(
        lambda obj: obj.current_balance + Decimal(random.uniform(0, 200))
    )
    total_redeemed = factory.LazyAttribute(
        lambda obj: obj.total_earned - obj.current_balance
    )
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-90d', end_date='-30d')
    updated_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')


class CarbonCreditTransactionFactory(factory.Factory):
    """Factory for creating CarbonCreditTransaction test instances."""
    
    class Meta:
        model = CarbonCreditTransaction
    
    user_id = factory.SubFactory(UserFactory)
    transaction_type = factory.Iterator([
        TransactionType.EARNED,
        TransactionType.REDEEMED,
        TransactionType.TRANSFERRED
    ])
    amount = factory.fuzzy.FuzzyDecimal(1.0, 50.0, 2)
    
    # CO2 data for earned credits
    co2_saved = factory.LazyAttribute(
        lambda obj: obj.amount if obj.transaction_type == TransactionType.EARNED else None
    )
    activity_reference = factory.LazyAttribute(
        lambda obj: f"habit_{random.randint(1000, 9999)}" if obj.transaction_type == TransactionType.EARNED else None
    )
    
    # Verification
    verification_status = factory.Iterator([
        VerificationStatus.PENDING,
        VerificationStatus.VERIFIED,
        VerificationStatus.REJECTED
    ])
    verification_method = factory.Iterator([
        VerificationMethod.AUTOMATIC,
        VerificationMethod.AI_VERIFIED,
        VerificationMethod.MANUAL_REVIEW
    ])
    
    # Transaction hash
    transaction_hash = factory.LazyAttribute(
        lambda obj: f"hash_{random.randint(100000, 999999)}"
    )
    
    # Exchange rates
    exchange_rate = factory.fuzzy.FuzzyDecimal(0.04, 0.06, 4)  # KC to USD rate
    usd_value = factory.LazyAttribute(
        lambda obj: obj.amount * obj.exchange_rate
    )
    
    notes = factory.Faker('sentence', nb_words=8)
    
    # Verification timestamp
    verified_at = factory.LazyAttribute(
        lambda obj: obj.created_at + timedelta(hours=random.randint(1, 48)) 
        if obj.verification_status == VerificationStatus.VERIFIED else None
    )
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(minutes=random.randint(1, 60)))
    
    @factory.lazy_attribute
    def verification_metadata(self):
        """Generate verification metadata based on method."""
        if self.verification_method == VerificationMethod.AI_VERIFIED:
            return {
                "confidence_score": random.uniform(0.7, 0.99),
                "analysis_method": "image_recognition",
                "evidence_urls": [f"https://example.com/evidence_{random.randint(1000, 9999)}.jpg"]
            }
        elif self.verification_method == VerificationMethod.MANUAL_REVIEW:
            return {
                "reviewer_id": f"admin_{random.randint(1, 10)}",
                "review_notes": "Manually verified with supporting documentation",
                "evidence_count": random.randint(1, 3)
            }
        return None


class CarbonCreditRedemptionFactory(factory.Factory):
    """Factory for creating CarbonCreditRedemption test instances."""
    
    class Meta:
        model = CarbonCreditRedemption
    
    user_id = factory.SubFactory(UserFactory)
    transaction_id = factory.SubFactory(CarbonCreditTransactionFactory)
    redemption_type = factory.Iterator([
        RedemptionType.CASH_OUT,
        RedemptionType.CARBON_OFFSET,
        RedemptionType.DONATION,
        RedemptionType.MARKETPLACE
    ])
    
    amount_kc = factory.fuzzy.FuzzyDecimal(10.0, 100.0, 2)
    amount_usd = factory.LazyAttribute(
        lambda obj: obj.amount_kc * Decimal('0.05')  # Standard rate
    )
    
    status = factory.Iterator([
        RedemptionStatus.PENDING,
        RedemptionStatus.PROCESSING,
        RedemptionStatus.COMPLETED,
        RedemptionStatus.FAILED
    ])
    
    external_reference = factory.LazyAttribute(
        lambda obj: f"{obj.redemption_type.value}_{random.randint(10000, 99999)}"
    )
    
    # Completion timestamp
    completed_at = factory.LazyAttribute(
        lambda obj: obj.created_at + timedelta(days=random.randint(1, 7))
        if obj.status == RedemptionStatus.COMPLETED else None
    )
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(hours=random.randint(1, 24)))
    
    @factory.lazy_attribute
    def recipient_info(self):
        """Generate recipient info based on redemption type."""
        if self.redemption_type == RedemptionType.CASH_OUT:
            return {
                "payment_method": random.choice(["paypal", "bank_transfer", "stripe"]),
                "account_id": f"account_{random.randint(1000, 9999)}",
                "email": f"user{random.randint(1, 100)}@example.com"
            }
        elif self.redemption_type == RedemptionType.CARBON_OFFSET:
            return {
                "offset_provider": random.choice(["CarbonFund", "Atmosfair", "Gold Standard"]),
                "project_type": random.choice(["reforestation", "renewable_energy", "methane_capture"]),
                "certificate_id": f"cert_{random.randint(10000, 99999)}"
            }
        elif self.redemption_type == RedemptionType.DONATION:
            return {
                "charity_name": random.choice(["WWF", "Greenpeace", "Sierra Club"]),
                "charity_id": f"charity_{random.randint(100, 999)}",
                "tax_receipt": True
            }
        else:  # MARKETPLACE
            return {
                "marketplace": "Klymate Marketplace",
                "product_category": random.choice(["eco_products", "renewable_energy", "carbon_offsets"]),
                "order_id": f"order_{random.randint(10000, 99999)}"
            }


class CarbonVerificationRuleFactory(factory.Factory):
    """Factory for creating CarbonVerificationRule test instances."""
    
    class Meta:
        model = CarbonVerificationRule
    
    activity_type = factory.Iterator([
        'public_transport', 'cycling', 'walking', 'carpooling',
        'plant_based_meal', 'local_food', 'reduced_meat',
        'renewable_energy', 'energy_conservation', 'led_lighting',
        'recycling', 'composting', 'water_conservation',
        'solar_installation', 'electric_vehicle', 'home_insulation'
    ])
    
    verification_method = factory.Iterator([
        VerificationMethod.AUTOMATIC,
        VerificationMethod.AI_VERIFIED,
        VerificationMethod.MANUAL_REVIEW
    ])
    
    min_amount = factory.fuzzy.FuzzyDecimal(0.1, 5.0, 2)
    max_amount = factory.LazyAttribute(
        lambda obj: obj.min_amount + Decimal(random.uniform(10, 100))
    )
    
    credit_multiplier = factory.fuzzy.FuzzyDecimal(0.8, 2.0, 2)
    requires_evidence = factory.LazyAttribute(
        lambda obj: obj.verification_method != VerificationMethod.AUTOMATIC
    )
    active = factory.Faker('boolean', chance_of_getting_true=90)
    
    # Timestamps
    created_at = factory.Faker('date_time_between', start_date='-1y', end_date='-6m')
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(days=random.randint(1, 30)))


def create_user_with_carbon_credits(transaction_count: int = 5) -> Dict[str, Any]:
    """Create a user with carbon credits and transaction history."""
    user = UserFactory.create()
    
    # Create user carbon credits record
    credits = UserCarbonCreditsFactory.create(user_id=user.id)
    
    # Create transaction history
    transactions = []
    for _ in range(transaction_count):
        transaction = CarbonCreditTransactionFactory.create(user_id=user.id)
        transactions.append(transaction)
    
    # Create some redemptions
    redemptions = []
    redeemed_transactions = [t for t in transactions if t.transaction_type == TransactionType.REDEEMED]
    for transaction in redeemed_transactions[:2]:  # Create redemptions for first 2 redeemed transactions
        redemption = CarbonCreditRedemptionFactory.create(
            user_id=user.id,
            transaction_id=transaction.id
        )
        redemptions.append(redemption)
    
    return {
        "user": user,
        "credits": credits,
        "transactions": transactions,
        "redemptions": redemptions
    }