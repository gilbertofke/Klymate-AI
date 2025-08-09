#!/usr/bin/env python3
"""
Database Setup Script for Klymate AI

This script helps team members set up their database connection
and verify everything is working correctly.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = backend_dir / ".env"
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("📋 Please copy .env.template to .env and fill in your details:")
        print(f"   cp {backend_dir}/.env.template {backend_dir}/.env")
        return False
    
    # Load environment variables
    load_dotenv(env_path)
    
    required_vars = [
        "TIDB_HOST",
        "TIDB_PORT", 
        "TIDB_USER",
        "TIDB_PASSWORD",
        "TIDB_DATABASE"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) in ["your_username.root", "your_generated_password", "your-project-id"]:
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or placeholder values in .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📋 Please update your .env file with real values")
        return False
    
    print("✅ .env file looks good!")
    return True

async def test_database_connection():
    """Test database connection."""
    try:
        from app.core.database import check_database_connection
        print("🔍 Testing database connection...")
        
        result = await check_database_connection()
        if result:
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

async def initialize_database():
    """Initialize database tables."""
    try:
        from app.core.database_init import DatabaseInitializer
        print("🏗️  Initializing database...")
        
        await DatabaseInitializer.initialize_for_development()
        print("✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

async def check_database_health():
    """Check database health and show status."""
    try:
        from app.core.database_init import DatabaseInitializer
        print("🏥 Checking database health...")
        
        health = await DatabaseInitializer.check_database_health()
        
        if health["status"] == "healthy":
            print("✅ Database is healthy!")
            print(f"   📊 Database: {health['database']}")
            print(f"   🌐 Host: {health['host']}")
            print(f"   📋 Tables: {health['tables_count']}")
            if health.get('tables'):
                print(f"   📝 Table list: {', '.join(health['tables'])}")
        else:
            print("❌ Database is unhealthy!")
            print(f"   ❗ Error: {health.get('error', 'Unknown error')}")
        
        return health["status"] == "healthy"
        
    except Exception as e:
        print(f"❌ Database health check failed: {str(e)}")
        return False

def show_next_steps():
    """Show next steps after successful setup."""
    print("\n🎉 Database setup complete!")
    print("\n📋 Next steps:")
    print("   1. Run tests: python run_tests.py")
    print("   2. Start development server: python app/main.py")
    print("   3. Check API docs: http://localhost:8000/docs")
    print("\n🔧 Useful commands:")
    print("   - Check database: python app/core/database_init.py check")
    print("   - Reset database: python app/core/database_init.py reset")
    print("   - Create migration: python -m alembic revision --autogenerate -m 'description'")
    print("   - Apply migrations: python -m alembic upgrade head")

async def main():
    """Main setup function."""
    print("🚀 Klymate AI Database Setup (Hackathon Mode)")
    print("=" * 50)
    
    # Step 1: Check .env file
    if not check_env_file():
        print("\n🆘 QUICK FIX:")
        print("   1. Copy: cp .env.template .env")
        print("   2. Edit .env with your TiDB credentials")
        print("   3. Ask team lead for shared credentials if needed")
        return 1
    
    # Step 2: Test connection
    if not await test_database_connection():
        print("\n🆘 CONNECTION FAILED - QUICK FIXES:")
        print("   1. Double-check credentials in .env file")
        print("   2. Ask team lead if TiDB cluster is running")
        print("   3. Try a different database name (add your name)")
        print("   4. If still failing, continue with local development")
        
        # For hackathon, don't block on database issues
        response = input("\n❓ Continue anyway? (y/n): ").lower()
        if response != 'y':
            return 1
        print("⚠️  Continuing without database connection...")
    
    # Step 3: Initialize database (only if connection works)
    try:
        if not await initialize_database():
            print("⚠️  Database initialization failed, but continuing...")
    except:
        print("⚠️  Skipping database initialization...")
    
    # Step 4: Check health (optional for hackathon)
    try:
        await check_database_health()
    except:
        print("⚠️  Skipping health check...")
    
    # Step 5: Show next steps
    show_next_steps()
    
    print("\n🏃‍♂️ HACKATHON TIP: If database isn't working, focus on other features first!")
    print("   You can always come back to database setup later.")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)