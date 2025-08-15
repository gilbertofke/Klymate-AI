#!/bin/bash

# Render Deployment Script for Klymate AI Backend
# This script helps configure deployment to Render

set -e

echo "🚀 Render Deployment Configuration for Klymate AI Backend..."

# Check if render.yaml exists, create if not
if [ ! -f "render.yaml" ]; then
    echo "📝 Creating render.yaml configuration..."
    cat > render.yaml << EOF
services:
  - type: web
    name: klymate-ai-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port \$PORT --workers 2
    healthCheckPath: /health
    envVars:
      - key: DEBUG
        value: false
      - key: LOG_LEVEL
        value: INFO
      - key: ENVIRONMENT
        value: production
      - key: TIDB_HOST
        fromDatabase:
          name: tidb-cloud
          property: host
      - key: TIDB_PORT
        value: 4000
      - key: TIDB_USER
        fromDatabase:
          name: tidb-cloud
          property: user
      - key: TIDB_PASSWORD
        fromDatabase:
          name: tidb-cloud
          property: password
      - key: TIDB_DATABASE
        fromDatabase:
          name: tidb-cloud
          property: database
      - key: TIDB_SSL_CA
        value: ./private-docs/tidb-ca.pem
      - key: TIDB_SSL_VERIFY
        value: true
      - key: REDIS_URL
        fromService:
          type: redis
          name: klymate-redis
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: FIREBASE_CREDENTIALS
        value: ./firebase-credentials-production.json
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: SECRET_KEY
        generateValue: true
      - key: CORS_ORIGINS
        value: '["https://klymate.ai", "https://app.klymate.ai"]'

  - type: redis
    name: klymate-redis
    ipAllowList: []

databases:
  - name: tidb-cloud
    databaseName: klymate_production
    user: production_user
EOF
    echo "✅ render.yaml created!"
fi

# Create Render-specific requirements if needed
if [ ! -f "requirements-render.txt" ]; then
    echo "📝 Creating Render-specific requirements..."
    cp requirements.txt requirements-render.txt
    echo "gunicorn==21.2.0" >> requirements-render.txt
    echo "✅ requirements-render.txt created!"
fi

# Create Render build script
cat > build.sh << 'EOF'
#!/bin/bash
# Render build script

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "🔧 Setting up SSL certificates..."
# Copy TiDB CA certificate if it exists
if [ -f "private-docs/tidb-ca.pem" ]; then
    echo "✅ TiDB CA certificate found"
else
    echo "⚠️  TiDB CA certificate not found - download from TiDB Cloud"
fi

echo "🔧 Running database migrations..."
# Run Alembic migrations
alembic upgrade head

echo "✅ Build complete!"
EOF

chmod +x build.sh

echo "📋 Render Deployment Instructions:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Render"
echo "3. Use the render.yaml file for configuration"
echo "4. Set the following environment variables in Render dashboard:"
echo "   - OPENAI_API_KEY (your OpenAI API key)"
echo "   - TIDB_HOST (your TiDB Cloud host)"
echo "   - TIDB_USER (your TiDB Cloud user)"
echo "   - TIDB_PASSWORD (your TiDB Cloud password)"
echo "   - TIDB_DATABASE (your TiDB Cloud database name)"
echo "5. Upload your TiDB CA certificate and Firebase credentials"
echo "6. Deploy!"

echo "🔗 Render Dashboard: https://dashboard.render.com/"
echo "📚 Render Docs: https://render.com/docs"

echo "✅ Render configuration complete!"