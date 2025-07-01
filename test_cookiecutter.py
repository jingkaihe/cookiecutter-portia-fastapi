#!/usr/bin/env python
"""Integration tests for the Portia FastAPI cookiecutter template.

This script tests the cookiecutter template by:
1. Generating a project with various configurations
2. Installing dependencies
3. Running basic tests
4. Checking that the API starts correctly
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
import pytest


def run_command(
    cmd: list[str], cwd: str | None = None, env: dict | None = None
) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env or os.environ.copy(),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class TestCookiecutterTemplate:
    """Test the cookiecutter template generation and functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def generate_project(
        self,
        output_dir: str,
        extra_context: dict | None = None,
    ) -> Path:
        """Generate a project using cookiecutter."""
        # Default context
        context = {
            "full_name": "Test User",
            "email": "test@example.com",
            "project_name": "Test Portia API",
            "project_slug": "test_portia_api",
            "project_short_description": "Test project for Portia FastAPI",
            "version": "0.1.0",
            "python_version": "3.11",
            "use_docker": "n",  # Skip Docker for faster tests
            "port": "8000",
            "include_example_tools": "y",
            "portia_storage_class": "MEMORY",
            "portia_log_level": "INFO",
        }

        if extra_context:
            context.update(extra_context)

        # Create cookiecutter config
        config_file = Path(output_dir) / "cookiecutter_config.json"
        with open(config_file, "w") as f:
            json.dump({"default_context": context}, f)

        # Run cookiecutter
        template_dir = Path(__file__).parent
        cmd = [
            "uvx",
            "cookiecutter",
            str(template_dir),
            "--no-input",
            "--output-dir",
            output_dir,
            "--config-file",
            str(config_file),
        ]

        returncode, stdout, stderr = run_command(cmd)
        if returncode != 0:
            # For validation tests, we expect failures
            raise subprocess.CalledProcessError(returncode, cmd, output=stdout, stderr=stderr)

        return Path(output_dir) / context["project_slug"]

    def test_project_generation(self, temp_dir):
        """Test that project generates successfully with default settings."""
        project_dir = self.generate_project(temp_dir)

        # Check that key files exist
        assert project_dir.exists()
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / ".env.example").exists()
        assert (project_dir / "main.py").exists()
        assert (project_dir / "Makefile").exists()

        # Check app structure
        assert (project_dir / "app" / "__init__.py").exists()
        assert (project_dir / "app" / "main.py").exists()
        assert (project_dir / "app" / "config.py").exists()
        assert (project_dir / "app" / "api" / "routes.py").exists()
        assert (project_dir / "app" / "schemas" / "request.py").exists()
        assert (project_dir / "app" / "tools" / "example_tools.py").exists()

        # Check test files
        assert (project_dir / "tests" / "__init__.py").exists()
        assert (project_dir / "tests" / "test_api.py").exists()

    def test_project_without_example_tools(self, temp_dir):
        """Test project generation without example tools."""
        project_dir = self.generate_project(
            temp_dir,
            extra_context={"include_example_tools": "n"},
        )

        # Check that example_tools.py doesn't exist
        assert not (project_dir / "app" / "tools" / "example_tools.py").exists()

        # But tools/__init__.py should still exist with empty registry
        tools_init = project_dir / "app" / "tools" / "__init__.py"
        assert tools_init.exists()
        content = tools_init.read_text()
        assert "custom_tools = ToolRegistry([])" in content

    def test_project_with_docker(self, temp_dir):
        """Test project generation with Docker support."""
        project_dir = self.generate_project(
            temp_dir,
            extra_context={"use_docker": "y"},
        )

        # Check Docker files
        assert (project_dir / "Dockerfile").exists()
        assert (project_dir / ".dockerignore").exists()

        # Check Makefile has Docker commands
        makefile_content = (project_dir / "Makefile").read_text()
        assert "docker-build:" in makefile_content
        assert "docker-run:" in makefile_content

    def test_dependency_installation(self, temp_dir):
        """Test that dependencies can be installed."""
        project_dir = self.generate_project(temp_dir)

        # Create .env file with dummy API key
        env_example = (project_dir / ".env.example").read_text()
        env_content = env_example.replace("your-openai-api-key-here", "sk-dummy-key-for-testing")
        (project_dir / ".env").write_text(env_content)

        # Check if uv is available
        returncode, _, _ = run_command(["uv", "--version"])
        if returncode != 0:
            pytest.skip("uv is not installed")

        # Install dependencies
        returncode, stdout, stderr = run_command(
            ["uv", "sync", "--no-group", "dev"],
            cwd=str(project_dir),
        )
        assert returncode == 0, f"Dependency installation failed: {stderr}"

    def test_unit_tests(self, temp_dir):
        """Test that the generated project's tests pass."""
        project_dir = self.generate_project(temp_dir)

        # Create .env file
        env_example = (project_dir / ".env.example").read_text()
        env_content = env_example.replace("your-openai-api-key-here", "sk-dummy-key-for-testing")
        (project_dir / ".env").write_text(env_content)

        # Check if uv is available
        returncode, _, _ = run_command(["uv", "--version"])
        if returncode != 0:
            pytest.skip("uv is not installed")

        # Install dependencies including dev
        returncode, stdout, stderr = run_command(
            ["uv", "sync", "--group", "dev"],
            cwd=str(project_dir),
        )
        assert returncode == 0, f"Dependency installation failed: {stderr}"

        # Run tests
        returncode, stdout, stderr = run_command(
            ["uv", "run", "pytest", "tests/test_api.py", "-v"],
            cwd=str(project_dir),
        )
        assert returncode == 0, f"Tests failed: {stdout}\n{stderr}"

    @pytest.mark.skip(reason="Requires running server setup")
    def test_api_startup(self, temp_dir):
        """Test that the API starts and responds correctly."""
        project_dir = self.generate_project(temp_dir)

        # Create .env file
        env_example = (project_dir / ".env.example").read_text()
        env_content = env_example.replace("your-openai-api-key-here", "sk-dummy-key-for-testing")
        (project_dir / ".env").write_text(env_content)

        # Check if uv is available
        returncode, _, _ = run_command(["uv", "--version"])
        if returncode != 0:
            pytest.skip("uv is not installed")

        # Install dependencies
        returncode, stdout, stderr = run_command(
            ["uv", "sync", "--no-group", "dev"],
            cwd=str(project_dir),
        )
        assert returncode == 0, f"Dependency installation failed: {stderr}"

        # Start the API in a subprocess
        env = os.environ.copy()
        env["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"

        process = subprocess.Popen(
            ["uv", "run", "python", "main.py"],
            cwd=str(project_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Wait for API to start
            time.sleep(5)

            # Test endpoints
            base_url = "http://localhost:8000"

            # Test root endpoint
            response = httpx.get(f"{base_url}/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "version" in data

            # Test health endpoint
            response = httpx.get(f"{base_url}/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}

            # Test API status endpoint
            response = httpx.get(f"{base_url}/api/v1/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "available_tools" in data
            assert len(data["available_tools"]) == 6  # We have 6 example tools

            # Test tools endpoint
            response = httpx.get(f"{base_url}/api/v1/tools")
            assert response.status_code == 200
            tools = response.json()
            assert len(tools) == 6
            tool_ids = [tool["id"] for tool in tools]
            assert "reverse_text" in tool_ids
            assert "add_numbers" in tool_ids

        finally:
            # Clean up
            process.terminate()
            process.wait(timeout=5)

    def test_different_python_versions(self, temp_dir):
        """Test generation with different Python versions."""
        for py_version in ["3.11", "3.12"]:
            project_dir = self.generate_project(
                temp_dir,
                extra_context={
                    "project_slug": f"test_py{py_version.replace('.', '')}",
                    "python_version": py_version,
                },
            )

            # Check pyproject.toml has correct Python version
            pyproject = (project_dir / "pyproject.toml").read_text()
            assert f'requires-python = ">={py_version}"' in pyproject
            assert f'target-version = "py{py_version.replace(".", "")}"' in pyproject

    def test_validation_hooks(self, temp_dir):
        """Test that validation hooks work correctly."""
        # Test invalid project slug
        with pytest.raises(subprocess.CalledProcessError):
            self.generate_project(
                temp_dir,
                extra_context={"project_slug": "invalid-slug-with-dashes"},
            )

        # Test invalid port
        with pytest.raises(subprocess.CalledProcessError):
            self.generate_project(
                temp_dir,
                extra_context={"port": "99999"},
            )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
