"""
Test database connection with SSL certificates
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_ssl_certificates():
    """Test if SSL certificates exist and are readable"""
    cert_files = ['ca-cert.pem', 'tidb-ca.pem', 'tidb-ca-root.pem']
    
    print("🔍 Checking SSL certificates...")
    for cert_file in cert_files:
        cert_path = backend_dir / cert_file
        if cert_path.exists():
            try:
                with open(cert_path, 'r') as f:
                    content = f.read()
                    if content.startswith('-----BEGIN CERTIFICATE-----') and content.strip().endswith('-----END CERTIFICATE-----'):
                        print(f"✅ {cert_file}: Valid certificate format")
                    else:
                        print(f"❌ {cert_file}: Invalid certificate format")
            except Exception as e:
                print(f"❌ {cert_file}: Error reading file - {e}")
        else:
            print(f"❌ {cert_file}: File not found")

def test_database_connection():
    """Test database connection"""
    try:
        # Set test database name
        os.environ['TIDB_DATABASE'] = 'klymate_ai_test'
        
        from app.core.config import settings
        print(f"\n🔧 Database Configuration:")
        print(f"   Host: {settings.TIDB_HOST}")
        print(f"   Port: {settings.TIDB_PORT}")
        print(f"   Database: {settings.TIDB_DATABASE}")
        print(f"   User: {settings.TIDB_USER}")
        
        # Test connection string
        from app.core.database import SYNC_DATABASE_URL
        print(f"\n🔗 Connection String: {SYNC_DATABASE_URL[:100]}...")
        
        # Try to create engine
        from sqlalchemy import create_engine, text
        engine = create_engine(SYNC_DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed - unexpected result")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing TiDB Connection and SSL Certificates\n")
    
    # Test certificates
    test_ssl_certificates()
    
    # Test database connection
    success = test_database_connection()
    
    if success:
        print("\n🎉 All tests passed! Database connection is working.")
    else:
        print("\n💡 Troubleshooting suggestions:")
        print("   1. Check if TiDB cluster is running")
        print("   2. Verify credentials in .env file")
        print("   3. Ensure SSL certificate is valid")
        print("   4. Try downloading fresh certificate:")
        print("      curl -o ca-cert.pem https://letsencrypt.org/certs/isrgrootx1.pem")