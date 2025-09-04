#!/usr/bin/env python3
"""
Firebase Credentials Setup Helper

This script helps you set up Firebase credentials for Klymate AI.
Run this after downloading your service account JSON file.
"""

import json
import os
import sys

def setup_firebase_credentials():
    print("🔥 Firebase Credentials Setup for Klymate AI")
    print("=" * 50)
    
    # Check if service account file exists
    json_file = input("Enter path to your service account JSON file: ").strip()
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return
    
    try:
        # Load the JSON file
        with open(json_file, 'r') as f:
            creds = json.load(f)
        
        print("\n📋 Extracted credentials:")
        print(f"Project ID: {creds['project_id']}")
        print(f"Client Email: {creds['client_email']}")
        
        # Generate backend .env content
        backend_env = f"""# Klymate AI Backend Development Environment

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./klymate_dev.db

# JWT Configuration
SECRET_KEY=development-secret-key-change-in-production
JWT_SECRET_KEY=development-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Firebase Configuration - Auto-generated from service account
FIREBASE_PROJECT_ID={creds['project_id']}
FIREBASE_PRIVATE_KEY_ID={creds['private_key_id']}
FIREBASE_PRIVATE_KEY={creds['private_key']}
FIREBASE_CLIENT_EMAIL={creds['client_email']}
FIREBASE_CLIENT_ID={creds['client_id']}
FIREBASE_AUTH_URI={creds['auth_uri']}
FIREBASE_TOKEN_URI={creds['token_uri']}

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_METHODS=*
ALLOWED_HEADERS=*

# Testing Configuration
TESTING_MODE=false
MOCK_EXTERNAL_APIS=true

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
"""
        
        # Write backend .env file
        with open('backend/.env', 'w') as f:
            f.write(backend_env)
        
        print("\n✅ Backend credentials configured!")
        print("📁 Updated: backend/.env")
        
        # Prompt for frontend config
        print("\n🌐 Frontend Configuration")
        print("Now you need to get your Firebase web app config from:")
        print("https://console.firebase.google.com → Project Settings → Your apps")
        
        api_key = input("Enter your Firebase API Key: ").strip()
        if api_key:
            frontend_env = f"""# Klymate AI Frontend Development Environment

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Development Mode
NODE_ENV=development

# Firebase Configuration - From Firebase Console
NEXT_PUBLIC_FIREBASE_API_KEY={api_key}
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN={creds['project_id']}.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID={creds['project_id']}
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET={creds['project_id']}.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=YOUR_MESSAGING_SENDER_ID
NEXT_PUBLIC_FIREBASE_APP_ID=YOUR_APP_ID
"""
            
            with open('frontend/.env.local', 'w') as f:
                f.write(frontend_env)
            
            print("✅ Frontend credentials partially configured!")
            print("📁 Updated: frontend/.env.local")
            print("⚠️  You still need to add MESSAGING_SENDER_ID and APP_ID from Firebase Console")
        
        print("\n🚀 Next Steps:")
        print("1. Complete frontend config with MESSAGING_SENDER_ID and APP_ID")
        print("2. Restart your backend: cd backend && python -m uvicorn app.main:app --reload")
        print("3. Restart your frontend: cd frontend && npm run dev")
        print("4. Test registration at http://localhost:3000")
        
    except Exception as e:
        print(f"❌ Error processing JSON file: {e}")

if __name__ == "__main__":
    setup_firebase_credentials()