"""
Tests for deployment configuration and containerization.
"""
import os
import pytest
from pathlib import Path
import yaml
import json


class TestDeploymentConfiguration:
    """Test deployment configuration files and setup."""
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists in backend directory."""
        dockerfile_path = Path("backend/Dockerfile")
        assert dockerfile_path.exists(), "Dockerfile should exist in backend directory"
    
    def test_dockerfile_content(self):
        """Test Dockerfile contains required configurations."""
        dockerfile_path = Path("backend/Dockerfile")
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check for Python base image
        assert "FROM python:" in content, "Dockerfile should use Python base image"
        
        # Check for working directory
        assert "WORKDIR" in content, "Dockerfile should set working directory"
        
        # Check for requirements installation
        assert "requirements.txt" in content, "Dockerfile should install requirements"
        
        # Check for FastAPI port exposure
        assert "EXPOSE 8000" in content, "Dockerfile should expose port 8000"
        
        # Check for startup command
        assert "CMD" in content or "ENTRYPOINT" in content, "Dockerfile should have startup command"
    
    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists."""
        compose_path = Path("backend/docker-compose.yml")
        assert compose_path.exists(), "docker-compose.yml should exist"
    
    def test_docker_compose_content(self):
        """Test docker-compose.yml contains required services."""
        compose_path = Path("backend/docker-compose.yml")
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        assert "services" in compose_config, "docker-compose should define services"
        
        # Check for backend service
        services = compose_config["services"]
        assert "backend" in services, "docker-compose should define backend service"
        
        backend_service = services["backend"]
        assert "build" in backend_service, "Backend service should have build configuration"
        assert "ports" in backend_service, "Backend service should expose ports"
        assert "environment" in backend_service, "Backend service should have environment variables"
        
        # Check for Redis service (for caching)
        assert "redis" in services, "docker-compose should define Redis service"
    
    def test_environment_config_files_exist(self):
        """Test that environment-specific configuration files exist."""
        config_files = [
            "backend/.env.development",
            "backend/.env.staging", 
            "backend/.env.production"
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            assert config_path.exists(), f"{config_file} should exist"
    
    def test_deployment_scripts_exist(self):
        """Test that deployment scripts exist."""
        script_files = [
            "backend/deploy/railway.sh",
            "backend/deploy/render.sh",
            "backend/deploy/aws.sh"
        ]
        
        for script_file in script_files:
            script_path = Path(script_file)
            assert script_path.exists(), f"{script_file} should exist"
            
            # Check if script is executable (on Unix systems)
            if os.name != 'nt':  # Not Windows
                assert os.access(script_path, os.X_OK), f"{script_file} should be executable"
    
    def test_production_config_security(self):
        """Test that production configuration follows security best practices."""
        prod_config_path = Path("backend/.env.production")
        with open(prod_config_path, 'r') as f:
            content = f.read()
        
        # Check that debug is disabled
        assert "DEBUG=false" in content or "DEBUG=False" in content, "Debug should be disabled in production"
        
        # Check for secure session configuration
        assert "SECRET_KEY=" in content, "Production should have SECRET_KEY configured"
        
        # Check for TiDB Cloud configuration
        assert "TIDB_HOST=" in content, "Production should have TiDB Cloud host configured"
        assert "TIDB_PORT=" in content, "Production should have TiDB port configured"
    
    def test_health_check_endpoint_configured(self):
        """Test that health check endpoint is properly configured for deployment."""
        from backend.app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200, "Health check endpoint should return 200"
        
        health_data = response.json()
        assert "status" in health_data, "Health check should include status"
        assert health_data["status"] == "healthy", "Health check should report healthy status"


class TestContainerConfiguration:
    """Test container-specific configurations."""
    
    def test_dockerfile_optimization(self):
        """Test that Dockerfile follows optimization best practices."""
        dockerfile_path = Path("backend/Dockerfile")
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check for multi-stage build or layer optimization
        lines = content.split('\n')
        
        # Should copy requirements first for better caching
        req_copy_line = None
        app_copy_line = None
        
        for i, line in enumerate(lines):
            if "COPY requirements.txt" in line:
                req_copy_line = i
            elif "COPY . ." in line or "COPY app" in line:
                app_copy_line = i
        
        if req_copy_line is not None and app_copy_line is not None:
            assert req_copy_line < app_copy_line, "Requirements should be copied before app code for better caching"
    
    def test_container_user_security(self):
        """Test that container runs with non-root user for security."""
        dockerfile_path = Path("backend/Dockerfile")
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Should create and use non-root user
        assert "RUN adduser" in content or "USER " in content, "Container should run with non-root user"


class TestDeploymentEnvironments:
    """Test deployment environment configurations."""
    
    def test_development_environment(self):
        """Test development environment configuration."""
        dev_config_path = Path("backend/.env.development")
        with open(dev_config_path, 'r') as f:
            content = f.read()
        
        assert "DEBUG=true" in content or "DEBUG=True" in content, "Debug should be enabled in development"
        assert "LOG_LEVEL=DEBUG" in content, "Log level should be DEBUG in development"
    
    def test_staging_environment(self):
        """Test staging environment configuration."""
        staging_config_path = Path("backend/.env.staging")
        with open(staging_config_path, 'r') as f:
            content = f.read()
        
        assert "DEBUG=false" in content or "DEBUG=False" in content, "Debug should be disabled in staging"
        assert "LOG_LEVEL=INFO" in content, "Log level should be INFO in staging"
    
    def test_tidb_cloud_configuration(self):
        """Test TiDB Cloud connection configuration for production."""
        prod_config_path = Path("backend/.env.production")
        with open(prod_config_path, 'r') as f:
            content = f.read()
        
        # Check for TiDB Cloud specific configurations
        assert "TIDB_HOST=" in content, "Should have TiDB Cloud host"
        assert "TIDB_PORT=4000" in content, "Should use TiDB Cloud port 4000"
        assert "TIDB_SSL_CA=" in content, "Should have SSL CA configuration"
        assert "TIDB_SSL_VERIFY=true" in content, "Should enable SSL verification"