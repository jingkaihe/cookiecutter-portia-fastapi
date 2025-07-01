# Makefile for {{ cookiecutter.project_name }}
.PHONY: help install install-dev run test test-cov test-unit test-integration lint lint-fix format typecheck clean docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make run          Run the FastAPI application"
	@echo "  make test         Run all tests"
	@echo "  make test-cov     Run tests with coverage report"
	@echo "  make test-unit    Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make lint         Run linter (ruff check)"
	@echo "  make format       Format code (ruff format)"
	@echo "  make typecheck    Run type checker (pyright)"
	@echo "  make clean        Clean up cache files"
{%- if cookiecutter.use_docker == 'y' %}
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"
{%- endif %}

# Install production dependencies
install:
	uv sync --no-group dev

# Install development dependencies
install-dev:
	uv sync --group dev

# Run the application
run:
	uv run python main.py

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov --cov-report=html

# Run unit tests only
test-unit:
	uv run pytest -m "not integration"

# Run integration tests only
test-integration:
	uv run pytest -m integration

# Run linter
lint:
	uv run ruff check .

# Fix linting issues
lint-fix:
	uv run ruff check --fix .

# Format code
format:
	uv run ruff format .

# Run type checker
typecheck:
	uv run pyright

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pyright" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/

{%- if cookiecutter.use_docker == 'y' %}

# Docker commands
docker-build:
	docker build -t {{ cookiecutter.project_slug }} .

docker-run:
	docker run -d \
		--name {{ cookiecutter.project_slug }} \
		-p {{ cookiecutter.port }}:{{ cookiecutter.port }} \
		--env-file .env \
		{{ cookiecutter.project_slug }}

docker-stop:
	docker stop {{ cookiecutter.project_slug }}
	docker rm {{ cookiecutter.project_slug }}
{%- endif %}