# CI/CD Pipeline Documentation

## Overview

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Klymate AI Backend. The pipeline is implemented using GitHub Actions and supports automated testing, security scanning, building, and deployment to multiple environments.

## Pipeline Components

### 1. Continuous Integration (CI) - `.github/workflows/ci.yml`

The CI pipeline runs on:
- Pull requests to `main` and `dev` branches
- Pushes to `dev` branch
- Changes to backend code or workflow files

#### Jobs:

**Test Job:**
- Sets up Python 3.11 environment
- Installs dependencies with caching
- Creates test environment configuration
- Runs linting (black, isort, flake8)
- Executes tests with coverage reporting
- Uploads coverage reports to Codecov

**Security Scan Job:**
- Runs Bandit for security vulnerability scanning
- Checks for known vulnerabilities with Safety
- Generates security reports

**Build Test Job:**
- Builds Docker image
- Tests container startup and health endpoint
- Validates deployment readiness

**Notify Job:**
- Provides pipeline status notifications
- Fails if any previous job fails

### 2. Continuous Deployment (CD) - `.github/workflows/cd.yml`

The CD pipeline runs on:
- Pushes to `main` branch (automatic staging deployment)
- Manual workflow dispatch for production deployment

#### Jobs:

**Deploy Staging:**
- Builds and pushes Docker image to GitHub Container Registry
- Deploys to staging environment (Railway/Render/AWS)
- Performs health checks and smoke tests
- Runs automatically on main branch updates

**Deploy Production:**
- Requires manual approval via workflow dispatch
- Builds production Docker image
- Deploys to production environment
- Comprehensive health checks and testing
- Creates GitHub release on successful deployment

**Rollback:**
- Automatic rollback on deployment failure
- Manual rollback capability
- Health verification after rollback

### 3. Maintenance - `.github/workflows/maintenance.yml`

Scheduled maintenance tasks:
- Daily dependency updates
- Security audits
- Health checks for deployed environments
- Cleanup of old workflow runs and Docker images

## Environment Configuration

### Staging Environment (`.env.staging`)
- Debug mode disabled
- Staging database and Redis connections
- Firebase staging project
- Reduced rate limiting
- Enhanced logging

### Production Environment (`.env.production`)
- Production-optimized settings
- Production database and Redis
- Firebase production project
- Strict rate limiting
- Warning-level logging only
- Multiple workers for performance

## Deployment Scripts

### Deploy Script (`scripts/deploy.sh`)

Usage: `./deploy.sh [staging|production]`

Features:
- Environment validation
- Docker image building
- Pre-deployment testing
- Database migration handling
- Platform-specific deployment (Railway/Render/AWS)
- Health checks
- Cache warming
- Deployment notifications

### Rollback Script (`scripts/rollback.sh`)

Usage: `./rollback.sh [staging|production] [version]`

Features:
- Production confirmation prompts
- Platform-specific rollback logic
- Health verification
- Critical endpoint testing
- Database rollback warnings
- Rollback notifications

## Security Features

### Code Security
- Bandit static analysis for Python security issues
- Safety checks for known vulnerabilities
- Pre-commit hooks for code quality
- Secret scanning prevention

### Deployment Security
- Non-root Docker containers
- Multi-stage Docker builds
- Environment variable encryption
- SSL/TLS certificate validation
- Rate limiting and CORS protection

### Access Control
- GitHub environment protection rules
- Required reviewers for production deployments
- Secret management via GitHub Secrets
- Audit logging for all deployments

## Monitoring and Observability

### Health Checks
- Application health endpoint (`/health`)
- Database connectivity verification
- Redis cache availability
- External service dependencies

### Metrics and Logging
- Structured JSON logging
- Performance metrics collection
- Error tracking with Sentry integration
- Cache hit rate monitoring

### Alerting
- Deployment failure notifications
- Health check failure alerts
- Security vulnerability warnings
- Performance degradation alerts

## Required GitHub Secrets

### General Secrets
- `GITHUB_TOKEN` - Automatic GitHub token for actions

### Database Secrets
- `TIDB_STAGING_HOST` - Staging database host
- `TIDB_STAGING_USER` - Staging database user
- `TIDB_STAGING_PASSWORD` - Staging database password
- `TIDB_STAGING_DATABASE` - Staging database name
- `TIDB_STAGING_SSL_CA` - Staging SSL certificate
- `TIDB_PRODUCTION_HOST` - Production database host
- `TIDB_PRODUCTION_USER` - Production database user
- `TIDB_PRODUCTION_PASSWORD` - Production database password
- `TIDB_PRODUCTION_DATABASE` - Production database name
- `TIDB_PRODUCTION_SSL_CA` - Production SSL certificate

### Cache Secrets
- `REDIS_STAGING_URL` - Staging Redis connection URL
- `REDIS_PRODUCTION_URL` - Production Redis connection URL

### Firebase Secrets
- `FIREBASE_STAGING_PROJECT_ID` - Staging Firebase project
- `FIREBASE_STAGING_PRIVATE_KEY` - Staging Firebase private key
- `FIREBASE_STAGING_CLIENT_EMAIL` - Staging Firebase client email
- `FIREBASE_PRODUCTION_PROJECT_ID` - Production Firebase project
- `FIREBASE_PRODUCTION_PRIVATE_KEY` - Production Firebase private key
- `FIREBASE_PRODUCTION_CLIENT_EMAIL` - Production Firebase client email

### API Secrets
- `OPENAI_STAGING_API_KEY` - Staging OpenAI API key
- `OPENAI_PRODUCTION_API_KEY` - Production OpenAI API key
- `JWT_STAGING_SECRET_KEY` - Staging JWT secret
- `JWT_PRODUCTION_SECRET_KEY` - Production JWT secret

### Deployment Platform Secrets
- `RAILWAY_TOKEN` - Railway deployment token (if using Railway)
- `RENDER_API_KEY` - Render API key (if using Render)
- `RENDER_STAGING_SERVICE_ID` - Render staging service ID
- `RENDER_PRODUCTION_SERVICE_ID` - Render production service ID
- `AWS_ACCESS_KEY_ID` - AWS access key (if using AWS)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (if using AWS)

### Monitoring Secrets
- `SENTRY_STAGING_DSN` - Staging Sentry DSN
- `SENTRY_PRODUCTION_DSN` - Production Sentry DSN

### Environment URLs
- `STAGING_URL` - Staging application URL
- `PRODUCTION_URL` - Production application URL

## Usage Instructions

### Setting Up CI/CD

1. **Configure GitHub Secrets:**
   - Go to repository Settings > Secrets and variables > Actions
   - Add all required secrets listed above

2. **Set Up Environment Protection:**
   - Go to Settings > Environments
   - Create `staging` and `production` environments
   - Configure protection rules for production (required reviewers)

3. **Configure Branch Protection:**
   - Protect `main` and `dev` branches
   - Require status checks to pass
   - Require pull request reviews

### Deploying to Staging

Staging deployments happen automatically when code is merged to the `main` branch:

1. Create feature branch from `dev`
2. Make changes and commit
3. Create pull request to `dev`
4. After review and approval, merge to `dev`
5. Create pull request from `dev` to `main`
6. After review and approval, merge to `main`
7. CI/CD pipeline automatically deploys to staging

### Deploying to Production

Production deployments require manual approval:

1. Go to Actions tab in GitHub repository
2. Select "CD Pipeline" workflow
3. Click "Run workflow"
4. Select "production" environment
5. Click "Run workflow" button
6. Approve deployment in the production environment

### Rolling Back Deployments

#### Automatic Rollback
- Happens automatically if deployment health checks fail
- Reverts to previous stable version

#### Manual Rollback
1. Use the rollback script: `./scripts/rollback.sh production`
2. Or trigger rollback via platform-specific tools
3. Verify health after rollback

### Monitoring Deployments

1. **GitHub Actions:**
   - Monitor workflow runs in Actions tab
   - Check logs for detailed information

2. **Application Health:**
   - Check health endpoint: `https://your-app.com/health`
   - Monitor application logs

3. **Performance:**
   - Check cache hit rates
   - Monitor response times
   - Review error rates

## Troubleshooting

### Common Issues

**CI Tests Failing:**
- Check test logs in GitHub Actions
- Verify environment configuration
- Ensure all dependencies are installed

**Deployment Failures:**
- Check deployment platform logs
- Verify secrets are configured correctly
- Ensure database connectivity

**Health Check Failures:**
- Verify application is starting correctly
- Check database and Redis connections
- Review application logs

**Rollback Issues:**
- Ensure previous version is available
- Check platform-specific rollback procedures
- Verify health endpoints after rollback

### Getting Help

1. Check GitHub Actions logs for detailed error messages
2. Review application logs in deployment platform
3. Verify all required secrets are configured
4. Check database and external service connectivity
5. Contact DevOps team for platform-specific issues

## Best Practices

### Development
- Write comprehensive tests for all new features
- Follow code quality standards (linting, formatting)
- Use feature branches and pull requests
- Include security considerations in code reviews

### Deployment
- Test thoroughly in staging before production
- Monitor deployments closely
- Have rollback plan ready
- Communicate deployment schedules to team

### Security
- Regularly update dependencies
- Monitor security scan results
- Rotate secrets periodically
- Follow principle of least privilege

### Monitoring
- Set up alerts for critical failures
- Monitor performance metrics
- Review logs regularly
- Track deployment success rates

## Future Enhancements

- Blue-green deployment strategy
- Canary deployments for production
- Automated performance testing
- Integration with monitoring dashboards
- Slack/Teams notifications
- Database migration rollback automation
- Multi-region deployment support