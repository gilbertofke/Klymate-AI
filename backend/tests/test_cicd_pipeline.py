"""
Tests for CI/CD pipeline functionality
"""
import pytest
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestCICDPipeline:
    """Test CI/CD pipeline components"""
    
    def test_github_workflows_exist(self):
        """Test that GitHub workflow files exist"""
        workflows_dir = Path(__file__).parent.parent.parent / ".github" / "workflows"
        
        assert workflows_dir.exists(), "GitHub workflows directory should exist"
        
        expected_workflows = ["ci.yml", "cd.yml", "maintenance.yml"]
        for workflow in expected_workflows:
            workflow_path = workflows_dir / workflow
            assert workflow_path.exists(), f"Workflow {workflow} should exist"
            assert workflow_path.stat().st_size > 0, f"Workflow {workflow} should not be empty"
    
    def test_dockerfile_exists_and_valid(self):
        """Test that Dockerfile exists and has required components"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        
        assert dockerfile_path.exists(), "Dockerfile should exist"
        
        dockerfile_content = dockerfile_path.read_text()
        
        # Check for required Dockerfile components
        required_components = [
            "FROM python:3.11-slim",
            "WORKDIR /app",
            "COPY requirements.txt",
            "RUN pip install",
            "EXPOSE 8000",
            "HEALTHCHECK",
            "CMD"
        ]
        
        for component in required_components:
            assert component in dockerfile_content, f"Dockerfile should contain {component}"
    
    def test_environment_files_exist(self):
        """Test that environment configuration files exist"""
        backend_dir = Path(__file__).parent.parent
        
        env_files = [".env.staging", ".env.production"]
        for env_file in env_files:
            env_path = backend_dir / env_file
            assert env_path.exists(), f"Environment file {env_file} should exist"
            
            # Check that file contains required variables
            env_content = env_path.read_text()
            required_vars = [
                "ENVIRONMENT=",
                "TIDB_HOST=",
                "REDIS_URL=",
                "FIREBASE_PROJECT_ID=",
                "OPENAI_API_KEY=",
                "JWT_SECRET_KEY="
            ]
            
            for var in required_vars:
                assert var in env_content, f"{env_file} should contain {var}"
    
    def test_deployment_scripts_exist(self):
        """Test that deployment scripts exist"""
        scripts_dir = Path(__file__).parent.parent / "scripts"
        
        assert scripts_dir.exists(), "Scripts directory should exist"
        
        scripts = ["deploy.sh", "rollback.sh"]
        for script in scripts:
            script_path = scripts_dir / script
            assert script_path.exists(), f"Script {script} should exist"
            assert script_path.stat().st_size > 0, f"Script {script} should not be empty"
    
    @patch('subprocess.run')
    def test_docker_build_simulation(self, mock_subprocess):
        """Test Docker build process simulation"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Simulate docker build command
        result = subprocess.run([
            "docker", "build", "-t", "klymate-backend:test", "."
        ], capture_output=True, text=True)
        
        mock_subprocess.assert_called_once()
        assert result.returncode == 0
    
    def test_ci_workflow_structure(self):
        """Test CI workflow has correct structure"""
        ci_workflow_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "ci.yml"
        
        if not ci_workflow_path.exists():
            pytest.skip("CI workflow file not found")
        
        import yaml
        
        with open(ci_workflow_path, 'r') as f:
            ci_config = yaml.safe_load(f)
        
        # Check workflow structure
        assert 'name' in ci_config
        assert 'on' in ci_config
        assert 'jobs' in ci_config
        
        # Check required jobs
        required_jobs = ['test', 'security-scan', 'build-test']
        for job in required_jobs:
            assert job in ci_config['jobs'], f"CI workflow should have {job} job"
        
        # Check test job has required steps
        test_job = ci_config['jobs']['test']
        step_names = [step.get('name', '') for step in test_job['steps']]
        
        required_steps = [
            'Checkout code',
            'Set up Python',
            'Install dependencies',
            'Run tests with coverage'
        ]
        
        for step in required_steps:
            assert any(step in name for name in step_names), f"Test job should have step: {step}"
    
    def test_cd_workflow_structure(self):
        """Test CD workflow has correct structure"""
        cd_workflow_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "cd.yml"
        
        if not cd_workflow_path.exists():
            pytest.skip("CD workflow file not found")
        
        import yaml
        
        with open(cd_workflow_path, 'r') as f:
            cd_config = yaml.safe_load(f)
        
        # Check workflow structure
        assert 'name' in cd_config
        assert 'on' in cd_config
        assert 'jobs' in cd_config
        
        # Check required jobs
        required_jobs = ['deploy-staging', 'deploy-production']
        for job in required_jobs:
            assert job in cd_config['jobs'], f"CD workflow should have {job} job"
    
    def test_environment_variable_validation(self):
        """Test environment variable validation"""
        # Test staging environment
        staging_vars = self._load_env_file(".env.staging")
        self._validate_env_vars(staging_vars, "staging")
        
        # Test production environment
        production_vars = self._load_env_file(".env.production")
        self._validate_env_vars(production_vars, "production")
    
    def _load_env_file(self, filename):
        """Load environment variables from file"""
        env_path = Path(__file__).parent.parent / filename
        if not env_path.exists():
            return {}
        
        env_vars = {}
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        
        return env_vars
    
    def _validate_env_vars(self, env_vars, environment):
        """Validate environment variables"""
        required_vars = [
            'ENVIRONMENT',
            'TIDB_HOST',
            'TIDB_USER',
            'TIDB_PASSWORD',
            'TIDB_DATABASE',
            'REDIS_URL',
            'FIREBASE_PROJECT_ID',
            'OPENAI_API_KEY',
            'JWT_SECRET_KEY'
        ]
        
        for var in required_vars:
            assert var in env_vars, f"{environment} environment should have {var}"
            assert env_vars[var], f"{environment} environment {var} should not be empty"
        
        # Environment-specific validations
        assert env_vars['ENVIRONMENT'] == environment
        
        if environment == 'production':
            assert env_vars.get('DEBUG', 'true').lower() == 'false'
            assert 'LOG_LEVEL' in env_vars
    
    def test_security_configuration(self):
        """Test security configuration in workflows"""
        ci_workflow_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "ci.yml"
        
        if not ci_workflow_path.exists():
            pytest.skip("CI workflow file not found")
        
        with open(ci_workflow_path, 'r') as f:
            ci_content = f.read()
        
        # Check for security scanning
        assert 'bandit' in ci_content, "CI should include bandit security scanning"
        assert 'safety' in ci_content, "CI should include safety vulnerability checking"
        
        # Check for secret handling
        assert 'secrets.' in ci_content, "CI should use GitHub secrets"
    
    def test_deployment_health_checks(self):
        """Test deployment health check configuration"""
        cd_workflow_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "cd.yml"
        
        if not cd_workflow_path.exists():
            pytest.skip("CD workflow file not found")
        
        with open(cd_workflow_path, 'r') as f:
            cd_content = f.read()
        
        # Check for health checks
        assert 'health check' in cd_content.lower(), "CD should include health checks"
        assert '/health' in cd_content, "CD should check health endpoint"
        
        # Check for rollback capability
        assert 'rollback' in cd_content.lower(), "CD should have rollback capability"
    
    def test_docker_security_best_practices(self):
        """Test Docker security best practices"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        
        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")
        
        dockerfile_content = dockerfile_path.read_text()
        
        # Check for non-root user
        assert 'adduser' in dockerfile_content, "Dockerfile should create non-root user"
        assert 'USER' in dockerfile_content, "Dockerfile should switch to non-root user"
        
        # Check for multi-stage build
        assert 'as builder' in dockerfile_content, "Dockerfile should use multi-stage build"
        assert 'as production' in dockerfile_content, "Dockerfile should have production stage"
        
        # Check for health check
        assert 'HEALTHCHECK' in dockerfile_content, "Dockerfile should include health check"
    
    @pytest.mark.integration
    def test_pipeline_integration(self):
        """Integration test for pipeline components"""
        # This would test the full pipeline in a test environment
        # For now, we'll just verify all components are present
        
        components = [
            Path(__file__).parent.parent.parent / ".github" / "workflows" / "ci.yml",
            Path(__file__).parent.parent.parent / ".github" / "workflows" / "cd.yml",
            Path(__file__).parent.parent / "Dockerfile",
            Path(__file__).parent.parent / ".env.staging",
            Path(__file__).parent.parent / ".env.production",
            Path(__file__).parent.parent / "scripts" / "deploy.sh",
            Path(__file__).parent.parent / "scripts" / "rollback.sh"
        ]
        
        for component in components:
            assert component.exists(), f"Pipeline component {component.name} should exist"
        
        print("✅ All CI/CD pipeline components are present")


class TestDeploymentScripts:
    """Test deployment script functionality"""
    
    def test_deploy_script_validation(self):
        """Test deployment script has proper validation"""
        deploy_script_path = Path(__file__).parent.parent / "scripts" / "deploy.sh"
        
        if not deploy_script_path.exists():
            pytest.skip("Deploy script not found")
        
        script_content = deploy_script_path.read_text()
        
        # Check for environment validation
        assert 'staging' in script_content and 'production' in script_content
        assert 'Invalid environment' in script_content
        
        # Check for safety measures
        assert 'set -e' in script_content, "Script should exit on error"
        assert 'PRODUCTION' in script_content, "Script should have production warnings"
    
    def test_rollback_script_validation(self):
        """Test rollback script has proper validation"""
        rollback_script_path = Path(__file__).parent.parent / "scripts" / "rollback.sh"
        
        if not rollback_script_path.exists():
            pytest.skip("Rollback script not found")
        
        script_content = rollback_script_path.read_text()
        
        # Check for safety measures
        assert 'WARNING' in script_content, "Rollback should have warnings"
        assert 'Are you sure' in script_content, "Rollback should ask for confirmation"
        assert 'health check' in script_content.lower(), "Rollback should verify health"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])