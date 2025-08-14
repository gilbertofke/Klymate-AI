#!/bin/bash

# AWS Deployment Script for Klymate AI Backend
# This script deploys the FastAPI backend to AWS using ECS Fargate

set -e

echo "🚀 AWS Deployment for Klymate AI Backend..."

# Configuration
AWS_REGION=${AWS_REGION:-us-west-2}
ECR_REPOSITORY=${ECR_REPOSITORY:-klymate-ai-backend}
ECS_CLUSTER=${ECS_CLUSTER:-klymate-cluster}
ECS_SERVICE=${ECS_SERVICE:-klymate-backend-service}
TASK_DEFINITION=${TASK_DEFINITION:-klymate-backend-task}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "📝 Using AWS Region: $AWS_REGION"

# Create ECR repository if it doesn't exist
echo "🏗️  Creating ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null || \
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# Get ECR login token
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t $ECR_REPOSITORY:latest .

# Tag image for ECR
ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
docker tag $ECR_REPOSITORY:latest $ECR_URI

# Push image to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_URI

# Create ECS task definition
echo "📋 Creating ECS task definition..."
cat > task-definition.json << EOF
{
  "family": "$TASK_DEFINITION",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "klymate-backend",
      "image": "$ECR_URI",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {"name": "DEBUG", "value": "false"},
        {"name": "LOG_LEVEL", "value": "INFO"},
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "secrets": [
        {"name": "TIDB_HOST", "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:klymate/tidb:host::"},
        {"name": "TIDB_USER", "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:klymate/tidb:user::"},
        {"name": "TIDB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:klymate/tidb:password::"},
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:klymate/openai:api_key::"},
        {"name": "JWT_SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:klymate/jwt:secret_key::"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/klymate-backend",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

# Register task definition
echo "📋 Registering ECS task definition..."
aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION

# Create ECS cluster if it doesn't exist
echo "🏗️  Creating ECS cluster..."
aws ecs describe-clusters --clusters $ECS_CLUSTER --region $AWS_REGION &> /dev/null || \
aws ecs create-cluster --cluster-name $ECS_CLUSTER --capacity-providers FARGATE --region $AWS_REGION

# Create CloudWatch log group
echo "📊 Creating CloudWatch log group..."
aws logs create-log-group --log-group-name /ecs/klymate-backend --region $AWS_REGION &> /dev/null || true

# Create or update ECS service
echo "🚀 Creating/updating ECS service..."
if aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --region $AWS_REGION &> /dev/null; then
    echo "Updating existing service..."
    aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --task-definition $TASK_DEFINITION --region $AWS_REGION
else
    echo "Creating new service..."
    aws ecs create-service \
        --cluster $ECS_CLUSTER \
        --service-name $ECS_SERVICE \
        --task-definition $TASK_DEFINITION \
        --desired-count 2 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
        --region $AWS_REGION
fi

# Wait for service to stabilize
echo "⏳ Waiting for service to stabilize..."
aws ecs wait services-stable --cluster $ECS_CLUSTER --services $ECS_SERVICE --region $AWS_REGION

echo "✅ AWS deployment complete!"
echo "🔗 Check ECS console: https://$AWS_REGION.console.aws.amazon.com/ecs/home?region=$AWS_REGION#/clusters/$ECS_CLUSTER/services"

# Clean up
rm -f task-definition.json

echo "🎉 AWS deployment script complete!"