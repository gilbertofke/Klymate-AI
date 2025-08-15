#!/bin/bash

# Railway Deployment Script for Klymate AI Backend
# This script deploys the FastAPI backend to Railway

set -e

echo "🚀 Starting Railway deployment for Klymate AI Backend..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please run 'railway login' first."
    exit 1
fi

# Set environment variables
echo "📝 Setting environment variables..."

# Database configuration
railway variables set TIDB_HOST="$TIDB_HOST"
railway variables set TIDB_PORT="$TIDB_PORT"
railway variables set TIDB_USER="$TIDB_USER"
railway variables set TIDB_PASSWORD="$TIDB_PASSWORD"
railway variables set TIDB_DATABASE="$TIDB_DATABASE"
railway variables set TIDB_SSL_CA="./private-docs/tidb-ca.pem"
railway variables set TIDB_SSL_VERIFY="true"

# Redis configuration (Railway provides Redis addon)
railway variables set REDIS_URL="$REDIS_URL"

# API Keys
railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
railway variables set FIREBASE_CREDENTIALS="./firebase-credentials-production.json"

# Security
railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
railway variables set SECRET_KEY="$SECRET_KEY"

# Application configuration
railway variables set DEBUG="false"
railway variables set LOG_LEVEL="INFO"
railway variables set ENVIRONMENT="production"

# CORS origins
railway variables set CORS_ORIGINS='["https://klymate.ai", "https://app.klymate.ai"]'

echo "📦 Building and deploying to Railway..."

# Deploy to Railway
railway up --detach

echo "✅ Deployment initiated! Check Railway dashboard for status."
echo "🔗 Your app will be available at: https://your-app.railway.app"

# Wait for deployment to complete
echo "⏳ Waiting for deployment to complete..."
sleep 30

# Check health endpoint
echo "🏥 Checking application health..."
RAILWAY_URL=$(railway status --json | jq -r '.deployments[0].url')

if [ "$RAILWAY_URL" != "null" ]; then
    if curl -f "$RAILWAY_URL/health" > /dev/null 2>&1; then
        echo "✅ Application is healthy and running!"
        echo "🔗 Application URL: $RAILWAY_URL"
    else
        echo "⚠️  Application deployed but health check failed. Check logs."
        railway logs
    fi
else
    echo "⚠️  Could not determine application URL. Check Railway dashboard."
fi

echo "🎉 Railway deployment complete!"