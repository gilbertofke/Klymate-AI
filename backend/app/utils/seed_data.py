"""
Seed Data Utilities

This module provides utilities for seeding the database with initial data,
including habit categories and other reference data.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.habit import HabitCategory, CategoryType
from app.repositories.habit_repository import HabitCategoryRepository

logger = logging.getLogger(__name__)


class SeedDataService:
    """Service for seeding database with initial data."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize SeedDataService with database session."""
        self.db = db_session
        self.category_repository = HabitCategoryRepository(db_session)
    
    async def seed_habit_categories(self) -> List[HabitCategory]:
        """
        Seed the database with initial habit categories.
        
        Returns:
            List of created HabitCategory instances
        """
        try:
            # Check if categories already exist
            existing_categories = await self.category_repository.get_all_active()
            if existing_categories:
                logger.info(f"Habit categories already exist ({len(existing_categories)} found)")
                return existing_categories
            
            # Define initial habit categories
            categories_data = [
                # Transport Categories
                {
                    "name": "Cycling Instead of Driving",
                    "description": "Cycling to work or for errands instead of driving a car",
                    "category_type": CategoryType.TRANSPORT,
                    "co2_impact_per_unit": Decimal("0.21"),  # kg CO2 saved per km
                    "unit_type": "km"
                },
                {
                    "name": "Public Transport",
                    "description": "Using public transportation instead of private vehicle",
                    "category_type": CategoryType.TRANSPORT,
                    "co2_impact_per_unit": Decimal("0.15"),  # kg CO2 saved per km
                    "unit_type": "km"
                },
                {
                    "name": "Walking Instead of Driving",
                    "description": "Walking for short trips instead of driving",
                    "category_type": CategoryType.TRANSPORT,
                    "co2_impact_per_unit": Decimal("0.21"),  # kg CO2 saved per km
                    "unit_type": "km"
                },
                {
                    "name": "Carpooling",
                    "description": "Sharing rides with others to reduce individual carbon footprint",
                    "category_type": CategoryType.TRANSPORT,
                    "co2_impact_per_unit": Decimal("0.10"),  # kg CO2 saved per km
                    "unit_type": "km"
                },
                
                # Diet Categories
                {
                    "name": "Plant-Based Meal",
                    "description": "Choosing plant-based meals instead of meat-based ones",
                    "category_type": CategoryType.DIET,
                    "co2_impact_per_unit": Decimal("2.5"),  # kg CO2 saved per meal
                    "unit_type": "meal"
                },
                {
                    "name": "Local/Seasonal Food",
                    "description": "Choosing locally sourced and seasonal food items",
                    "category_type": CategoryType.DIET,
                    "co2_impact_per_unit": Decimal("1.2"),  # kg CO2 saved per meal
                    "unit_type": "meal"
                },
                {
                    "name": "Reduced Food Waste",
                    "description": "Avoiding food waste through meal planning and proper storage",
                    "category_type": CategoryType.DIET,
                    "co2_impact_per_unit": Decimal("0.8"),  # kg CO2 saved per kg of food
                    "unit_type": "kg"
                },
                
                # Energy Categories
                {
                    "name": "Energy Conservation",
                    "description": "Reducing electricity consumption through conservation measures",
                    "category_type": CategoryType.ENERGY,
                    "co2_impact_per_unit": Decimal("0.5"),  # kg CO2 saved per kWh
                    "unit_type": "kwh"
                },
                {
                    "name": "LED Light Bulb Usage",
                    "description": "Using LED bulbs instead of incandescent or CFL bulbs",
                    "category_type": CategoryType.ENERGY,
                    "co2_impact_per_unit": Decimal("0.1"),  # kg CO2 saved per hour
                    "unit_type": "hour"
                },
                {
                    "name": "Unplugging Electronics",
                    "description": "Unplugging electronics when not in use to avoid phantom load",
                    "category_type": CategoryType.ENERGY,
                    "co2_impact_per_unit": Decimal("0.05"),  # kg CO2 saved per device per day
                    "unit_type": "device"
                },
                {
                    "name": "Renewable Energy Usage",
                    "description": "Using renewable energy sources like solar or wind",
                    "category_type": CategoryType.ENERGY,
                    "co2_impact_per_unit": Decimal("0.8"),  # kg CO2 saved per kWh
                    "unit_type": "kwh"
                },
                
                # Lifestyle Categories
                {
                    "name": "Recycling",
                    "description": "Recycling materials instead of throwing them away",
                    "category_type": CategoryType.LIFESTYLE,
                    "co2_impact_per_unit": Decimal("1.0"),  # kg CO2 saved per kg recycled
                    "unit_type": "kg"
                },
                {
                    "name": "Composting",
                    "description": "Composting organic waste instead of sending to landfill",
                    "category_type": CategoryType.LIFESTYLE,
                    "co2_impact_per_unit": Decimal("0.6"),  # kg CO2 saved per kg composted
                    "unit_type": "kg"
                },
                {
                    "name": "Reusable Items",
                    "description": "Using reusable bags, bottles, and containers",
                    "category_type": CategoryType.LIFESTYLE,
                    "co2_impact_per_unit": Decimal("0.3"),  # kg CO2 saved per use
                    "unit_type": "use"
                },
                {
                    "name": "Digital Receipts",
                    "description": "Choosing digital receipts instead of paper ones",
                    "category_type": CategoryType.LIFESTYLE,
                    "co2_impact_per_unit": Decimal("0.01"),  # kg CO2 saved per receipt
                    "unit_type": "receipt"
                },
                {
                    "name": "Water Conservation",
                    "description": "Reducing water usage through conservation measures",
                    "category_type": CategoryType.LIFESTYLE,
                    "co2_impact_per_unit": Decimal("0.002"),  # kg CO2 saved per liter
                    "unit_type": "liter"
                }
            ]
            
            # Create categories
            created_categories = []
            for category_data in categories_data:
                try:
                    category = await self.category_repository.create(category_data)
                    created_categories.append(category)
                    logger.debug(f"Created habit category: {category.name}")
                except Exception as e:
                    logger.error(f"Error creating category {category_data['name']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully seeded {len(created_categories)} habit categories")
            return created_categories
            
        except Exception as e:
            logger.error(f"Error seeding habit categories: {str(e)}")
            raise
    
    async def seed_all_data(self) -> Dict[str, Any]:
        """
        Seed all initial data.
        
        Returns:
            Dictionary containing counts of seeded data
        """
        try:
            results = {}
            
            # Seed habit categories
            categories = await self.seed_habit_categories()
            results["habit_categories"] = len(categories)
            
            logger.info(f"Seeding completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error seeding data: {str(e)}")
            raise


async def seed_database(db_session: AsyncSession) -> Dict[str, Any]:
    """
    Convenience function to seed the database.
    
    Args:
        db_session: Async database session
        
    Returns:
        Dictionary containing counts of seeded data
    """
    seed_service = SeedDataService(db_session)
    return await seed_service.seed_all_data()


# CLI script for seeding data
if __name__ == "__main__":
    import asyncio
    from app.core.database import AsyncSessionLocal
    
    async def main():
        """Main function for CLI seeding."""
        async with AsyncSessionLocal() as session:
            try:
                results = await seed_database(session)
                print(f"✅ Database seeding completed: {results}")
            except Exception as e:
                print(f"❌ Database seeding failed: {str(e)}")
                raise
    
    asyncio.run(main())