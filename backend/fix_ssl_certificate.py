"""
Fix SSL Certificate for TiDB Connection

This script downloads fresh SSL certificates and tests the database connection.
Run this if you're getting SSL certificate corruption errors.
"""

import os
import subprocess
import sys
from pathlib import Path

def download_fresh_certificates():
    """Download fresh SSL certificates"""
    print("📥 Downloading fresh SSL certificates...")
    
    certificates = [
        ("ca-cert.pem", "https://letsencrypt.org/certs/isrgrootx1.pem"),
        ("tidb-ca.pem", "https://letsencrypt.org/certs/isrgrootx1.pem"),
    ]
    
    for cert_name, cert_url in certificates:
        try:
            # Backup existing certificate
            if Path(cert_name).exists():
                backup_name = f"{cert_name}.backup"
                os.rename(cert_name, backup_name)
                print(f"   Backed up {cert_name} to {backup_name}")
            
            # Download fresh certificate
            result = subprocess.run([
                "curl", "-o", cert_name, cert_url
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Downloaded {cert_name}")
            else:
                print(f"❌ Failed to download {cert_name}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error downloading {cert_name}: {e}")

def test_certificate_format(cert_file):
    """Test if certificate has correct format"""
    try:
        with open(cert_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if content.startswith('-----BEGIN CERTIFICATE-----') and content.strip().endswith('-----END CERTIFICATE-----'):
            print(f"✅ {cert_file}: Valid certificate format")
            return True
        else:
            print(f"❌ {cert_file}: Invalid certificate format")
            return False
            
    except Exception as e:
        print(f"❌ {cert_file}: Error reading - {e}")
        return False

def create_env_file():
    """Create .env file from .env.hackathon if it doesn't exist"""
    env_file = Path(".env")
    hackathon_env = Path(".env.hackathon")
    
    if not env_file.exists() and hackathon_env.exists():
        print("📝 Creating .env file from .env.hackathon...")
        
        # Read hackathon env
        with open(hackathon_env, 'r') as f:
            content = f.read()
        
        # Auto-detect team member based on current directory or ask user
        import getpass
        username = getpass.getuser().lower()
        
        # Map common usernames to team members
        user_mapping = {
            'admin': 'tangus',  # Common Windows admin user
            'tangus': 'tangus',
            'rono': 'rono', 
            'cheptoo': 'cheptoo',
            'victor': 'victor'
        }
        
        # Default to asking user if not found
        team_member = user_mapping.get(username, 'rono')  # Default to rono for this fix
        
        # Replace placeholder database name
        content = content.replace(
            "TIDB_DATABASE=klymate_ai_yourname  # ← CHANGE to: tangus, rono, cheptoo, or victor",
            f"TIDB_DATABASE=klymate_ai_{team_member}  # {team_member.title()}'s database"
        )
        
        # Write to .env
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Created .env file with database: klymate_ai_{team_member}")
    else:
        print("ℹ️  .env file already exists")

def main():
    """Main function to fix SSL certificate issues"""
    print("🔧 TiDB SSL Certificate Fix Tool")
    print("=" * 40)
    
    # Step 1: Create .env file if needed
    create_env_file()
    
    # Step 2: Download fresh certificates
    download_fresh_certificates()
    
    # Step 3: Test certificate formats
    print("\n🔍 Testing certificate formats...")
    ca_cert_ok = test_certificate_format("ca-cert.pem")
    tidb_cert_ok = test_certificate_format("tidb-ca.pem")
    
    # Step 4: Test database connection
    print("\n🔗 Testing database connection...")
    try:
        # Set environment for testing
        os.environ['TIDB_DATABASE'] = 'klymate_ai_rono'
        
        from sqlalchemy import create_engine, text
        
        # Create connection string
        from app.core.config import settings
        connection_string = f"mysql+pymysql://{settings.TIDB_USER}:{settings.TIDB_PASSWORD}@{settings.TIDB_HOST}:{settings.TIDB_PORT}/{settings.TIDB_DATABASE}?charset=utf8mb4&ssl_ca=ca-cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
        
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                success = True
            else:
                print("❌ Database connection failed - unexpected result")
                success = False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        success = False
    
    # Summary
    print("\n" + "=" * 40)
    if ca_cert_ok and tidb_cert_ok and success:
        print("🎉 All fixed! SSL certificates are working correctly.")
        print("\n📋 Next steps for Rono:")
        print("   1. Your .env file is configured with database: klymate_ai_rono")
        print("   2. Fresh SSL certificates have been downloaded")
        print("   3. Database connection is working")
        print("   4. You can now continue with Task 6!")
    else:
        print("⚠️  Some issues remain. Please check the errors above.")
        print("\n💡 Manual steps:")
        print("   1. Ensure TiDB cluster is running")
        print("   2. Check your .env file has correct database name")
        print("   3. Try running: python setup_database.py")

if __name__ == "__main__":
    main()