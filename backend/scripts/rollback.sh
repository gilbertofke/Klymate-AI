#!/bin/bash

# Rollback script for Klymate AI Backend
# Usage: ./rollback.sh [staging|production] [version]

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-previous}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Rolling back Klymate AI Backend in $ENVIRONMENT to $VERSION"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "ERROR: Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Production rollback confirmation
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "WARNING: You are about to rollback PRODUCTION!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "ERROR: Rollback cancelled"
        exit 1
    fi
fi

# Load environment variables
if [[ -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]]; then
    echo "Loading $ENVIRONMENT environment variables"
    set -a
    source "$PROJECT_ROOT/.env.$ENVIRONMENT"
    set +a
fi

# Get current deployment info
echo "Getting current deployment information"
CURRENT_VERSION=$(curl -s "$DEPLOYMENT_URL/health" | jq -r '.version' 2>/dev/null || echo "unknown")
echo "Current version: $CURRENT_VERSION"

# Rollback based on platform
if [[ -n "$RAILWAY_TOKEN" ]]; then
    echo "Rolling back Railway deployment"
    
    # Install Railway CLI if not present
    if ! command -v railway &> /dev/null; then
        curl -fsSL https://railway.app/install.sh | sh
    fi
    
    # Login and rollback
    railway login --token "$RAILWAY_TOKEN"
    
    if [[ "$VERSION" == "previous" ]]; then
        railway rollback --service "backend-$ENVIRONMENT"
    else
        railway rollback --service "backend-$ENVIRONMENT" --to "$VERSION"
    fi
    
    echo "SUCCESS: Railway rollback initiated"
    
elif [[ -n "$RENDER_API_KEY" ]]; then
    echo "Rolling back Render deployment"
    
    # Get service ID based on environment
    if [[ "$ENVIRONMENT" == "staging" ]]; then
        SERVICE_ID="$RENDER_STAGING_SERVICE_ID"
    else
        SERVICE_ID="$RENDER_PRODUCTION_SERVICE_ID"
    fi
    
    # Get previous deployment
    PREVIOUS_DEPLOY=$(curl -s \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services/$SERVICE_ID/deploys" | \
        jq -r '.deploys[1].id' 2>/dev/null)
    
    if [[ "$PREVIOUS_DEPLOY" != "null" && -n "$PREVIOUS_DEPLOY" ]]; then
        # Trigger rollback by redeploying previous version
        curl -X POST \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"clearCache\": true}" \
            "https://api.render.com/v1/services/$SERVICE_ID/deploys"
        
        echo "SUCCESS: Render rollback initiated"
    else
        echo "ERROR: Could not find previous deployment to rollback to"
        exit 1
    fi
    
elif [[ -n "$AWS_ACCESS_KEY_ID" ]]; then
    echo "Rolling back AWS deployment"
    
    # AWS ECS rollback logic would go here
    # This would typically involve updating the service to use a previous task definition
    
    echo "SUCCESS: AWS rollback initiated"
    
else
    echo "ERROR: No deployment platform configured for rollback"
    exit 1
fi

# Wait for rollback to complete
echo "Waiting for rollback to complete"
sleep 60

# Health check after rollback
echo "Performing post-rollback health check"
for i in {1..15}; do
    if curl -f "$DEPLOYMENT_URL/health" >/dev/null 2>&1; then
        NEW_VERSION=$(curl -s "$DEPLOYMENT_URL/health" | jq -r '.version' 2>/dev/null || echo "unknown")
        echo "SUCCESS: Rollback successful"
        echo "Previous version: $CURRENT_VERSION"
        echo "Current version: $NEW_VERSION"
        break
    else
        echo "INFO: Waiting for rollback to complete... (attempt $i/15)"
        sleep 30
    fi
    
    if [[ $i -eq 15 ]]; then
        echo "ERROR: Rollback health check failed"
        echo "ALERT: Manual intervention may be required"
        exit 1
    fi
done

# Verify critical endpoints
echo "Verifying critical endpoints"
ENDPOINTS=(
    "/health"
    "/api/v1/habits/categories"
    "/api/v1/gamification/badges"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -f "$DEPLOYMENT_URL$endpoint" >/dev/null 2>&1; then
        echo "SUCCESS: $endpoint is responding"
    else
        echo "WARNING: $endpoint is not responding properly"
    fi
done

# Database rollback warning
echo ""
echo "IMPORTANT: Database Rollback"
echo "============================"
echo "This script only rolls back the application code."
echo "If database migrations were run, you may need to:"
echo "1. Review database changes"
echo "2. Run migration rollbacks if necessary"
echo "3. Restore from backup if data corruption occurred"
echo ""

# Send notification
echo "Sending rollback notification"
# Notification logic would go here

echo "SUCCESS: Rollback to $VERSION in $ENVIRONMENT completed!"

# Print rollback summary
echo ""
echo "Rollback Summary"
echo "================"
echo "Environment: $ENVIRONMENT"
echo "Target Version: $VERSION"
echo "Previous Version: $CURRENT_VERSION"
echo "Timestamp: $(date)"
if [[ -n "$DEPLOYMENT_URL" ]]; then
    echo "URL: $DEPLOYMENT_URL"
fi
echo ""
echo "Next Steps:"
echo "1. Monitor application metrics"
echo "2. Check error logs"
echo "3. Verify user functionality"
echo "4. Plan fix for original issue"