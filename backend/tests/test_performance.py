"""
Performance Testing

This module contains performance tests for the Klymate AI backend system,
testing response times, throughput, and system behavior under load.
"""

import pytest
import asyncio
import time
from decimal import Decimal
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import statistics

from app.services.carbon_credits_service import CarbonCreditsService
from app.services.habit_service import HabitService
from app.services.gamification_service import GamificationService
from app.services.analytics_service import AnalyticsService
from app.utils.carbon_credit_seed_data import CarbonCreditSeedData
from app.schemas.habit import HabitCreate
from tests.factories import UserFactory, HabitCategoryFactory


class TestPerformanceBenchmarks:
    """Performance benchmarks for core system operations"""
    
    @pytest.fixture
    async def setup_performance_test(self, db_session: Session):
        """Set up performance test environment"""
        # Seed carbon credits data
        seed_data = CarbonCreditSeedData(db_session)
        await seed_data.seed_all()
        
        # Create test users and categories
        users = UserFactory.create_batch(100)
        categories = HabitCategoryFactory.create_batch(10)
        
        db_session.add_all(users + categories)
        db_session.commit()
        
        return {
            'users': users,
            'categories': categories
        }
    
    async def test_habit_logging_performance(self, setup_performance_test, db_session: Session):
        """Test habit logging performance under load"""
        test_data = setup_performance_test
        habit_service = HabitService(db_session)
        
        # Test single habit logging performance
        user = test_data['users'][0]
        category = test_data['categories'][0]
        
        # Measure single operation time
        start_time = time.time()
        
        habit_data = HabitCreate(
            category_id=category.id,
            quantity=Decimal('5.0'),
            notes="Performance test habit"
        )
        
        habit_entry = await habit_service.log_habit(user.id, habit_data)
        
        single_operation_time = time.time() - start_time
        
        # Single habit logging should be fast
        assert single_operation_time < 0.5  # Less than 500ms
        assert habit_entry is not None
        
        # Test bulk operations
        start_time = time.time()
        
        tasks = []
        for i in range(50):  # 50 concurrent habit logs
            habit_data = HabitCreate(
                category_id=category.id,
                quantity=Decimal(str(i + 1)),
                notes=f"Bulk test habit {i+1}"
            )
            tasks.append(habit_service.log_habit(user.id, habit_data))
        
        results = await asyncio.gather(*tasks)
        bulk_operation_time = time.time() - start_time
        
        # Bulk operations should complete in reasonable time
        assert bulk_operation_time < 10.0  # Less than 10 seconds for 50 operations
        assert len(results) == 50
        assert all(result is not None for result in results)
        
        # Calculate throughput
        throughput = len(results) / bulk_operation_time
        print(f"Habit logging throughput: {throughput:.2f} operations/second")
        
        # Should achieve reasonable throughput
        assert throughput > 5.0  # At least 5 operations per second
    
    async def test_carbon_credits_performance(self, setup_performance_test, db_session: Session):
        """Test carbon credits system performance"""
        test_data = setup_performance_test
        credits_service = CarbonCreditsService(db_session)
        
        # Test balance retrieval performance
        user = test_data['users'][0]
        
        # Measure balance retrieval time
        start_time = time.time()
        balance = await credits_service.get_user_balance(user.id)
        balance_time = time.time() - start_time
        
        assert balance_time < 0.2  # Less than 200ms
        assert balance is not None
        
        # Test concurrent balance retrievals
        start_time = time.time()
        
        tasks = []
        for user in test_data['users'][:20]:  # Test with 20 users
            tasks.append(credits_service.get_user_balance(user.id))
        
        results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        assert concurrent_time < 2.0  # Less than 2 seconds for 20 users
        assert len(results) == 20
        
        # Calculate concurrent throughput
        concurrent_throughput = len(results) / concurrent_time
        print(f"Balance retrieval throughput: {concurrent_throughput:.2f} operations/second")
        
        assert concurrent_throughput > 10.0  # At least 10 operations per second
    
    async def test_analytics_performance(self, setup_performance_test, db_session: Session):
        """Test analytics system performance with large datasets"""
        test_data = setup_performance_test
        analytics_service = AnalyticsService(db_session)
        habit_service = HabitService(db_session)
        
        # Create substantial dataset
        category = test_data['categories'][0]
        
        # Log habits for multiple users over time
        for user in test_data['users'][:10]:  # Use first 10 users
            for day in range(30):  # 30 days of data
                habit_data = HabitCreate(
                    category_id=category.id,
                    quantity=Decimal(str((day % 5) + 1)),
                    logged_date=date.today() - timedelta(days=day),
                    notes=f"Analytics test day {day}"
                )
                await habit_service.log_habit(user.id, habit_data)
        
        # Test dashboard data generation performance
        start_time = time.time()
        dashboard_data = await analytics_service.get_dashboard_data()
        dashboard_time = time.time() - start_time
        
        assert dashboard_time < 2.0  # Less than 2 seconds
        assert dashboard_data is not None
        assert 'total_users' in dashboard_data
        
        print(f"Dashboard generation time: {dashboard_time:.3f} seconds")
        
        # Test trends calculation performance
        start_time = time.time()
        trends_data = await analytics_service.get_trends_data("week")
        trends_time = time.time() - start_time
        
        assert trends_time < 1.0  # Less than 1 second
        assert trends_data is not None
        
        print(f"Trends calculation time: {trends_time:.3f} seconds")
    
    async def test_database_query_performance(self, setup_performance_test, db_session: Session):
        """Test database query performance"""
        test_data = setup_performance_test
        
        # Test user lookup performance
        start_time = time.time()
        
        # Simulate multiple user lookups
        for user in test_data['users'][:50]:
            db_session.get(type(user), user.id)
        
        lookup_time = time.time() - start_time
        
        assert lookup_time < 1.0  # Less than 1 second for 50 lookups
        
        print(f"Database lookup time for 50 users: {lookup_time:.3f} seconds")
        
        # Test complex query performance
        from app.models.user_habit import UserHabit
        
        start_time = time.time()
        
        # Complex query with joins and aggregations
        query = db_session.query(UserHabit).join(UserHabit.category).limit(100)
        results = query.all()
        
        complex_query_time = time.time() - start_time
        
        assert complex_query_time < 0.5  # Less than 500ms
        
        print(f"Complex query time: {complex_query_time:.3f} seconds")


class TestMemoryUsage:
    """Test memory usage patterns"""
    
    async def test_memory_usage_under_load(self, db_session: Session):
        """Test memory usage during high-load operations"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        users = UserFactory.create_batch(500)
        categories = HabitCategoryFactory.create_batch(20)
        
        db_session.add_all(users + categories)
        db_session.commit()
        
        # Perform memory-intensive operations
        habit_service = HabitService(db_session)
        
        for user in users[:100]:  # Process 100 users
            for category in categories[:5]:  # 5 habits each
                habit_data = HabitCreate(
                    category_id=category.id,
                    quantity=Decimal('3.0'),
                    notes="Memory test habit"
                )
                await habit_service.log_habit(user.id, habit_data)
        
        # Check memory usage after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        # Memory increase should be reasonable
        assert memory_increase < 100  # Less than 100MB increase


class TestScalabilityLimits:
    """Test system scalability limits"""
    
    async def test_concurrent_user_limit(self, db_session: Session):
        """Test system behavior with many concurrent users"""
        # Create many users
        users = UserFactory.create_batch(200)
        category = HabitCategoryFactory()
        
        db_session.add_all(users + [category])
        db_session.commit()
        
        habit_service = HabitService(db_session)
        
        # Test concurrent operations from many users
        start_time = time.time()
        
        tasks = []
        for user in users:
            habit_data = HabitCreate(
                category_id=category.id,
                quantity=Decimal('2.0'),
                notes=f"Concurrent test for user {user.id}"
            )
            tasks.append(habit_service.log_habit(user.id, habit_data))
        
        # Execute in batches to avoid overwhelming the system
        batch_size = 50
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)
        
        total_time = time.time() - start_time
        
        assert len(results) == 200
        assert all(result is not None for result in results)
        
        throughput = len(results) / total_time
        print(f"Concurrent user throughput: {throughput:.2f} operations/second")
        
        # Should handle concurrent users efficiently
        assert throughput > 10.0  # At least 10 operations per second
    
    async def test_data_volume_limits(self, db_session: Session):
        """Test system behavior with large data volumes"""
        # Create user with many habits
        user = UserFactory()
        categories = HabitCategoryFactory.create_batch(5)
        
        db_session.add_all([user] + categories)
        db_session.commit()
        
        habit_service = HabitService(db_session)
        
        # Create large number of habits
        start_time = time.time()
        
        for i in range(1000):  # 1000 habits
            category = categories[i % len(categories)]
            habit_data = HabitCreate(
                category_id=category.id,
                quantity=Decimal(str((i % 10) + 1)),
                logged_date=date.today() - timedelta(days=i % 365),
                notes=f"Volume test habit {i+1}"
            )
            await habit_service.log_habit(user.id, habit_data)
        
        creation_time = time.time() - start_time
        
        print(f"Created 1000 habits in {creation_time:.2f} seconds")
        
        # Test retrieval performance with large dataset
        start_time = time.time()
        
        user_habits = await habit_service.get_user_habit_history(
            user.id, 
            limit=1000
        )
        
        retrieval_time = time.time() - start_time
        
        assert len(user_habits) == 1000
        assert retrieval_time < 2.0  # Should retrieve quickly even with large dataset
        
        print(f"Retrieved 1000 habits in {retrieval_time:.3f} seconds")


class TestResponseTimeDistribution:
    """Test response time distribution and consistency"""
    
    async def test_response_time_consistency(self, db_session: Session):
        """Test that response times are consistent"""
        # Setup
        seed_data = CarbonCreditSeedData(db_session)
        await seed_data.seed_all()
        
        user = UserFactory()
        category = HabitCategoryFactory()
        
        db_session.add_all([user, category])
        db_session.commit()
        
        habit_service = HabitService(db_session)
        credits_service = CarbonCreditsService(db_session)
        
        # Measure response times for multiple operations
        habit_times = []
        balance_times = []
        
        for i in range(50):  # 50 measurements
            # Measure habit logging time
            start_time = time.time()
            
            habit_data = HabitCreate(
                category_id=category.id,
                quantity=Decimal('3.0'),
                notes=f"Consistency test {i+1}"
            )
            
            await habit_service.log_habit(user.id, habit_data)
            habit_time = time.time() - start_time
            habit_times.append(habit_time)
            
            # Measure balance retrieval time
            start_time = time.time()
            await credits_service.get_user_balance(user.id)
            balance_time = time.time() - start_time
            balance_times.append(balance_time)
        
        # Analyze response time distribution
        habit_avg = statistics.mean(habit_times)
        habit_median = statistics.median(habit_times)
        habit_stdev = statistics.stdev(habit_times)
        
        balance_avg = statistics.mean(balance_times)
        balance_median = statistics.median(balance_times)
        balance_stdev = statistics.stdev(balance_times)
        
        print(f"Habit logging - Avg: {habit_avg:.3f}s, Median: {habit_median:.3f}s, StdDev: {habit_stdev:.3f}s")
        print(f"Balance retrieval - Avg: {balance_avg:.3f}s, Median: {balance_median:.3f}s, StdDev: {balance_stdev:.3f}s")
        
        # Response times should be consistent (low standard deviation)
        assert habit_stdev < habit_avg * 0.5  # StdDev should be less than 50% of average
        assert balance_stdev < balance_avg * 0.5
        
        # Average response times should be reasonable
        assert habit_avg < 1.0  # Less than 1 second average
        assert balance_avg < 0.5  # Less than 500ms average


class TestLoadTestingScenarios:
    """Realistic load testing scenarios"""
    
    async def test_typical_user_session(self, db_session: Session):
        """Test performance of typical user session"""
        # Setup
        seed_data = CarbonCreditSeedData(db_session)
        await seed_data.seed_all()
        
        user = UserFactory()
        categories = HabitCategoryFactory.create_batch(3)
        
        db_session.add_all([user] + categories)
        db_session.commit()
        
        # Services
        habit_service = HabitService(db_session)
        credits_service = CarbonCreditsService(db_session)
        analytics_service = AnalyticsService(db_session)
        
        # Simulate typical user session
        session_start = time.time()
        
        # 1. User checks their balance
        await credits_service.get_user_balance(user.id)
        
        # 2. User logs 2-3 habits
        for i, category in enumerate(categories):
            habit_data = HabitCreate(
                category_id=category.id,
                quantity=Decimal(str(i + 2)),
                notes=f"Session habit {i+1}"
            )
            await habit_service.log_habit(user.id, habit_data)
        
        # 3. User checks updated balance
        await credits_service.get_user_balance(user.id)
        
        # 4. User views their statistics
        await habit_service.get_user_statistics(user.id)
        
        # 5. User checks recent habits
        await habit_service.get_recent_habits(user.id)
        
        session_time = time.time() - session_start
        
        print(f"Typical user session completed in {session_time:.3f} seconds")
        
        # Typical session should complete quickly
        assert session_time < 3.0  # Less than 3 seconds for complete session
    
    async def test_peak_usage_simulation(self, db_session: Session):
        """Simulate peak usage with many concurrent users"""
        # Setup for peak usage
        users = UserFactory.create_batch(50)  # 50 concurrent users
        categories = HabitCategoryFactory.create_batch(5)
        
        db_session.add_all(users + categories)
        db_session.commit()
        
        # Seed data
        seed_data = CarbonCreditSeedData(db_session)
        await seed_data.seed_all()
        
        # Services
        habit_service = HabitService(db_session)
        credits_service = CarbonCreditsService(db_session)
        
        # Simulate peak usage
        peak_start = time.time()
        
        # Create tasks for concurrent user activities
        tasks = []
        
        for user in users:
            # Each user performs multiple actions
            category = categories[hash(user.id) % len(categories)]
            
            # Log habit
            habit_data = HabitCreate(
                category_id=category.id,
                quantity=Decimal('4.0'),
                notes=f"Peak usage test for {user.id}"
            )
            tasks.append(habit_service.log_habit(user.id, habit_data))
            
            # Check balance
            tasks.append(credits_service.get_user_balance(user.id))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        peak_time = time.time() - peak_start
        
        print(f"Peak usage simulation: {len(tasks)} operations in {peak_time:.3f} seconds")
        print(f"Peak throughput: {len(tasks) / peak_time:.2f} operations/second")
        
        # System should handle peak load
        assert len(results) == len(tasks)
        assert peak_time < 10.0  # Should complete within 10 seconds
        
        throughput = len(tasks) / peak_time
        assert throughput > 10.0  # At least 10 operations per second during peak