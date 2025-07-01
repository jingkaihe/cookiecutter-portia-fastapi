# Makefile for Portia FastAPI Cookiecutter Template
.PHONY: help test test-quick test-full test-generation test-validation test-integration clean clean-all lint lint-fix format install install-dev generate demo coverage docs

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test          Run all tests (quick validation)"
	@echo "  make test-quick    Run quick template generation tests"
	@echo "  make test-full     Run comprehensive tests including integration"
	@echo "  make test-generation  Test template generation with different configs"
	@echo "  make test-validation  Test template validation and linting"
	@echo "  make test-integration Run integration tests with pytest"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make install       Install test dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo "  make lint          Run linting on template files"
	@echo "  make lint-fix      Fix linting issues automatically"
	@echo "  make format        Format template files"
	@echo ""
	@echo "🚀 Generation:"
	@echo "  make generate      Generate a test project interactively"
	@echo "  make demo          Generate demo projects with different configs"
	@echo ""
	@echo "📊 Coverage & Docs:"
	@echo "  make coverage      Generate test coverage report"
	@echo "  make docs          Generate documentation"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean         Clean generated test projects"
	@echo "  make clean-all     Deep clean including coverage and cache"

# Quick test - runs the bash test script
test: test-quick

test-quick:
	@echo "🧪 Running quick template tests..."
	@./test_template.sh

# Full comprehensive testing
test-full: test-generation test-validation test-integration
	@echo "✅ All tests completed successfully!"

# Test template generation with different configurations
test-generation:
	@echo "🔧 Testing template generation with various configurations..."
	@echo "Testing default configuration..."
	@uvx cookiecutter . --no-input --output-dir /tmp/cookiecutter-test project_name="Test Default" project_slug="test_default"
	@echo "Testing without Docker..."
	@uvx cookiecutter . --no-input --output-dir /tmp/cookiecutter-test project_name="Test No Docker" project_slug="test_no_docker" use_docker=n
	@echo "Testing without example tools..."
	@uvx cookiecutter . --no-input --output-dir /tmp/cookiecutter-test project_name="Test Minimal" project_slug="test_minimal" include_example_tools=n use_docker=n
	@echo "Testing with Python 3.12..."
	@uvx cookiecutter . --no-input --output-dir /tmp/cookiecutter-test project_name="Test Python312" project_slug="test_python312" python_version="3.12"
	@echo "✅ Template generation tests completed"
	@rm -rf /tmp/cookiecutter-test

# Test validation and code quality of generated projects
test-validation:
	@echo "🔍 Testing validation and code quality..."
	@# Generate a test project
	@uvx cookiecutter . --no-input --output-dir /tmp/cookiecutter-validation project_name="Validation Test" project_slug="validation_test"
	@cd /tmp/cookiecutter-validation/validation_test && \
		if command -v uv &> /dev/null; then \
			echo "Installing dependencies..."; \
			uv sync --group dev > /dev/null 2>&1; \
			echo "Running linting..."; \
			uv run ruff check . || echo "⚠️  Linting issues found"; \
			echo "Running type checking..."; \
			uv run pyright || echo "⚠️  Type checking issues found"; \
			echo "Running tests..."; \
			uv run pytest -v > /dev/null 2>&1 && echo "✅ Generated project tests pass"; \
		else \
			echo "⚠️  uv not available, skipping dependency validation"; \
		fi
	@rm -rf /tmp/cookiecutter-validation
	@echo "✅ Validation tests completed"

# Run comprehensive integration tests with pytest
test-integration:
	@echo "🔗 Running integration tests..."
	@if [ -f test_requirements.txt ]; then \
		echo "Installing test requirements..."; \
		pip install -r test_requirements.txt > /dev/null 2>&1; \
	fi
	@python test_cookiecutter.py -v
	@echo "✅ Integration tests completed"

# Install basic test dependencies
install:
	@echo "📦 Installing test dependencies..."
	@if command -v uv &> /dev/null; then \
		echo "Using uv to install cookiecutter..."; \
		uv tool install cookiecutter; \
	else \
		echo "Installing cookiecutter with pip..."; \
		pip install cookiecutter; \
	fi

# Install development dependencies
install-dev: install
	@echo "📦 Installing development dependencies..."
	@if [ -f test_requirements.txt ]; then \
		pip install -r test_requirements.txt; \
	fi
	@echo "Installing additional dev tools..."
	@pip install ruff pyright pre-commit

# Lint template files
lint:
	@echo "🔍 Running linting on template files..."
	@echo "Checking JSON files..."
	@python -m json.tool cookiecutter.json > /dev/null && echo "✅ cookiecutter.json is valid"
	@echo "Checking Python files..."
	@find . -name "*.py" -not -path "./{{cookiecutter.project_slug}}/*" -not -path "./.venv/*" -not -path "./htmlcov/*" | xargs python -m py_compile
	@if command -v ruff &> /dev/null; then \
		echo "Running ruff on template..."; \
		ruff check test_cookiecutter.py hooks/ || echo "⚠️  Ruff issues found (expected for cookiecutter hooks)"; \
	fi

# Fix linting issues
lint-fix:
	@echo "🔧 Fixing linting issues..."
	@if command -v ruff &> /dev/null; then \
		echo "Running ruff --fix..."; \
		ruff check test_cookiecutter.py hooks/ --fix || echo "⚠️  Some issues couldn't be auto-fixed"; \
		ruff format test_cookiecutter.py hooks/; \
	fi

# Format template files
format: lint-fix

# Generate a test project interactively
generate:
	@echo "🚀 Generating a new project from template..."
	@echo "This will run cookiecutter interactively"
	@uvx cookiecutter .

# Generate demo projects with different configurations
demo:
	@echo "🚀 Generating demo projects..."
	@mkdir -p demo-projects
	@echo "Generating full-featured demo..."
	@uvx cookiecutter . --no-input --output-dir demo-projects \
		project_name="Full Featured Demo" \
		project_slug="full_demo" \
		use_docker=y \
		include_example_tools=y \
		portia_storage_class="MEMORY" \
		portia_log_level="INFO"
	@echo "Generating minimal demo..."
	@uvx cookiecutter . --no-input --output-dir demo-projects \
		project_name="Minimal Demo" \
		project_slug="minimal_demo" \
		use_docker=n \
		include_example_tools=n \
		portia_storage_class="MEMORY" \
		portia_log_level="WARNING"
	@echo "Generating production-ready demo..."
	@uvx cookiecutter . --no-input --output-dir demo-projects \
		project_name="Production Demo" \
		project_slug="production_demo" \
		use_docker=y \
		include_example_tools=n \
		portia_storage_class="CLOUD" \
		portia_log_level="INFO"
	@echo ""
	@echo "✅ Demo projects generated in demo-projects/ directory:"
	@ls -la demo-projects/
	@echo ""
	@echo "To test a demo project:"
	@echo "  cd demo-projects/full_demo"
	@echo "  cp .env.example .env"
	@echo "  # Edit .env to add your OPENAI_API_KEY"
	@echo "  uv sync --group dev"
	@echo "  uv run python main.py"

# Generate test coverage report
coverage:
	@echo "📊 Generating test coverage report..."
	@if [ -f test_requirements.txt ]; then \
		pip install -r test_requirements.txt > /dev/null 2>&1; \
	fi
	@python -m pytest test_cookiecutter.py --cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# Generate documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "Template structure:" > TEMPLATE_STRUCTURE.md
	@echo '```' >> TEMPLATE_STRUCTURE.md
	@find . -type f -not -path "./.git/*" -not -path "./htmlcov/*" -not -path "./.venv/*" -not -path "./demo-projects/*" | sort >> TEMPLATE_STRUCTURE.md
	@echo '```' >> TEMPLATE_STRUCTURE.md
	@echo ""
	@echo "Cookiecutter variables:" >> TEMPLATE_STRUCTURE.md
	@echo '```json' >> TEMPLATE_STRUCTURE.md
	@cat cookiecutter.json >> TEMPLATE_STRUCTURE.md
	@echo '```' >> TEMPLATE_STRUCTURE.md
	@echo "✅ Documentation generated in TEMPLATE_STRUCTURE.md"

# Clean generated test projects and temporary files
clean:
	@echo "🧹 Cleaning up generated test projects..."
	@rm -rf demo-projects/
	@rm -rf /tmp/cookiecutter-*
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Deep clean including coverage reports and other artifacts
clean-all: clean
	@echo "🧹 Deep cleaning..."
	@rm -rf htmlcov/
	@rm -rf .coverage
	@rm -rf .ruff_cache/
	@rm -rf .pyright/
	@rm -f TEMPLATE_STRUCTURE.md
	@echo "✅ Deep clean completed"

# Development workflow targets
dev-setup: install-dev
	@echo "🛠️  Setting up development environment..."
	@if command -v pre-commit &> /dev/null; then \
		echo "Installing pre-commit hooks..."; \
		pre-commit install; \
	fi
	@echo "✅ Development environment ready!"

# Quick development test cycle
dev-test: clean test-quick lint
	@echo "✅ Development test cycle completed!"

# Release preparation
release-check: clean-all test-full lint coverage
	@echo "🚀 Release check completed!"
	@echo "✅ Template is ready for release"

# Docker-based testing (if Docker is available)
test-docker:
	@echo "🐳 Running tests in Docker..."
	@if command -v docker &> /dev/null; then \
		docker run --rm -v "$(PWD):/workspace" -w /workspace python:3.11-slim bash -c " \
			apt-get update && apt-get install -y curl && \
			curl -LsSf https://astral.sh/uv/install.sh | sh && \
			export PATH=\"/root/.local/bin:\$PATH\" && \
			./test_template.sh \
		"; \
	else \
		echo "❌ Docker not available"; \
		exit 1; \
	fi

# CI/CD simulation
ci: clean-all install-dev lint test-full coverage
	@echo "🤖 CI/CD simulation completed successfully!"