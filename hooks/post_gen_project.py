#!/usr/bin/env python
"""Post-generation hook to clean up files based on user choices."""

import os
import shutil

# Get cookiecutter context
REMOVE_PATHS = []

# Remove Docker files if not needed
if "{{ cookiecutter.use_docker }}" != "y":
    REMOVE_PATHS.append("Dockerfile")
    REMOVE_PATHS.append(".dockerignore")

# Remove example tools if not needed
if "{{ cookiecutter.include_example_tools }}" != "y":
    REMOVE_PATHS.append("app/tools/example_tools.py")

# Remove files
for path in REMOVE_PATHS:
    path = path.strip()
    if not path:
        continue

    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

# Create empty test directory
os.makedirs("tests", exist_ok=True)
with open("tests/__init__.py", "w") as f:
    f.write('"""Tests for {{ cookiecutter.project_name }}."""\n')

# Create a simple test file
with open("tests/test_api.py", "w") as f:
    f.write('''"""Basic API tests for {{ cookiecutter.project_name }}."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_status():
    """Test API status endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "available_tools" in data
''')

# Create .dockerignore if Docker is enabled
if "{{ cookiecutter.use_docker }}" == "y":
    with open(".dockerignore", "w") as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.pytest_cache/
.coverage
.mypy_cache/
.ruff_cache/

# Environment
.env
.env.*

# IDE
.vscode/
.idea/

# Git
.git/
.gitignore

# Documentation
*.md
docs/

# Tests
tests/
test_*.py

# Development files
*.log
.DS_Store
""")

print("\nProject '{{ cookiecutter.project_name }}' created successfully!")
print("\nNext steps:")
print("1. cd {{ cookiecutter.project_slug }}")
print("2. cp .env.example .env")
print("3. Edit .env and add your OPENAI_API_KEY")
print("4. uv sync --group dev  # For development")
print("   OR")
print("   uv sync --no-group dev  # For production")
print("5. uv run python main.py")
print("\nVisit http://localhost:{{ cookiecutter.port }}/docs for API documentation.")
