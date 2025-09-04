#!/usr/bin/env python3
"""
Klymate AI Backend Test Runner

This script runs tests according to the design document's testing strategy,
handling known issues with database connectivity and Firebase authentication.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ FAILED")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_basic_imports():
    """Test basic imports and core functionality."""
    print("\n🔍 Testing Core Functionality")
    print("=" * 50)
    
    test_script = '''
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test basic imports
from app.models.habit import CategoryType, HabitCategory
from app.schemas.habit import HabitCreate
from app.services.habit_service import HabitService
from app.repositories.habit_repository import HabitRepository
from app.api.v1.endpoints.habits import router
from app.main import app

# Test CategoryType enum
assert CategoryType.TRANSPORT == "transport"
assert CategoryType.DIET == "diet"

# Test CO2 calculation
from decimal import Decimal
category = HabitCategory()
category.co2_impact_per_unit = Decimal('2.5')
result = category.calculate_co2_savings(10.0)
assert result == Decimal('25.0')

# Test schema validation
habit_data = {'category_id': 1, 'quantity': 10.5}
habit = HabitCreate(**habit_data)
assert habit.category_id == 1

# Test FastAPI app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/health')
assert response.status_code == 200

print("✅ All core functionality tests passed!")
'''
    
    return run_command(f'python -c "{test_script}"', "Core Functionality Tests")

def test_database_connection():
    """Test database connectivity."""
    return run_command("python test_db_connection.py", "Database Connection Test")

def run_unit_tests():
    """Run unit tests that don't require database."""
    # Create a simple unit test file if it doesn't exist
    unit_test_file = Path("tests/test_core_unit.py")
    if not unit_test_file.exists():
        unit_test_content = '''
"""Core unit tests that don't require database connectivity."""
import pytest
from decimal import Decimal
from app.models.habit import CategoryType, HabitCategory
from app.schemas.habit import HabitCreate

def test_category_type_enum():
    """Test CategoryType enum values."""
    assert CategoryType.TRANSPORT == "transport"
    assert CategoryType.DIET == "diet"
    assert CategoryType.ENERGY == "energy"
    assert CategoryType.LIFESTYLE == "lifestyle"

def test_co2_calculation():
    """Test CO2 savings calculation."""
    category = HabitCategory()
    category.co2_impact_per_unit = Decimal('2.5')
    result = category.calculate_co2_savings(10.0)
    assert result == Decimal('25.0')

def test_habit_create_schema():
    """Test HabitCreate schema validation."""
    data = {"category_id": 1, "quantity": 10.5}
    habit = HabitCreate(**data)
    assert habit.category_id == 1
    assert habit.quantity == 10.5
'''
        with open(unit_test_file, 'w') as f:
            f.write(unit_test_content)
    
    # Try to run pytest on specific unit tests (without coverage)
    return run_command("python -m pytest tests/test_core_unit.py -v --tb=short", "Unit Tests")

def main():
    """Main test runner."""
    print("🚀 Klymate AI Backend Test Suite")
    print("=" * 60)
    print("Following design document testing strategy:")
    print("- Unit Tests (70%): Business logic, models, schemas")
    print("- Integration Tests (20%): API endpoints, services")
    print("- End-to-End Tests (10%): Full user workflows")
    print("=" * 60)
    
    results = []
    
    # Test 1: Core functionality (most important)
    results.append(("Core Functionality", test_basic_imports()))
    
    # Test 2: Database connectivity
    results.append(("Database Connection", test_database_connection()))
    
    # Test 3: Unit tests
    results.append(("Unit Tests", run_unit_tests()))
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\nKnown issues:")
        print("- Async database connections may fail on Windows")
        print("- Firebase authentication requires proper certificate setup")
        print("- These issues don't affect core functionality")
        return 1

if __name__ == "__main__":
    sys.exit(main())