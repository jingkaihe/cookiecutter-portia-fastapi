# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Cookiecutter template** for creating production-ready FastAPI services that integrate with the Portia SDK for building agentic AI workflows. The template generates FastAPI applications with proper project structure, configuration, testing, and Docker support.

## Key Architecture

### Template Structure
- **`cookiecutter.json`**: Template configuration variables (project name, Python version, Docker support, etc.)
- **`hooks/`**: Pre/post generation validation scripts
- **`{{cookiecutter.project_slug}}/`**: The actual template directory that gets rendered
- **Testing Infrastructure**: `test_template.sh`, `test_cookiecutter.py` for comprehensive template validation

### Generated Project Architecture
When rendered, the template creates a FastAPI service with:
- **App Module** (`app/`): Main FastAPI application with modular structure
  - `main.py`: FastAPI application factory with lifespan management
  - `config.py`: Pydantic settings with environment variable configuration
  - `api/routes.py`: Portia SDK integration endpoints
  - `schemas/`: Request/response Pydantic models
  - `tools/`: Custom Portia tools (optional via cookiecutter config)
- **Entry Point** (`main.py`): Uvicorn server startup
- **Testing** (`tests/`): Unit and integration tests with pytest
- **Configuration**: Docker, Makefile, pyproject.toml with dependency groups

### Portia SDK Integration
The generated projects integrate the Portia SDK with:
- Global Portia instance initialization with tool registry
- API endpoints for executing queries (`/api/v1/run`)
- Tool discovery and filtering capabilities
- Support for clarifications, structured outputs, and end user attribution
- Proper error handling and logging integration

## Development Commands

### Template Testing
```bash
# Quick template validation
./test_template.sh

# Comprehensive testing with pytest
pip install -r test_requirements.txt
python test_cookiecutter.py -v

# Test specific configurations
python test_cookiecutter.py::TestCookiecutterTemplate::test_project_without_example_tools -v
```

### Template Generation
```bash
# Generate from this template locally
cookiecutter . --no-input

# Generate with custom values
cookiecutter . --no-input project_name="My API" use_docker=n

# Generate from GitHub (as documented in README)
uvx cookiecutter gh:jingkaihe/cookiecutter-portia-fastapi
```

### Generated Project Commands (within generated projects)
```bash
# Development setup
uv sync --group dev
cp .env.example .env  # Add your OPENAI_API_KEY

# Run application
make run              # or uv run python main.py
make install-dev      # Install all dependencies

# Testing
make test             # Run all tests
make test-unit        # Unit tests only
make test-integration # Integration tests (require API keys)
make test-cov         # Tests with coverage report

# Code quality
make lint             # Run ruff linting
make format           # Format with ruff
make typecheck        # Run pyright type checking
make lint-fix         # Auto-fix linting issues

# Docker (if enabled)
make docker-build
make docker-run
```

## Configuration Variables

The template supports these cookiecutter variables:
- **`project_name`**: Human-readable project name
- **`project_slug`**: URL-safe project identifier (auto-generated)
- **`python_version`**: Python version (3.11, 3.12)
- **`use_docker`**: Include Docker configuration (y/n)
- **`include_example_tools`**: Include sample Portia tools (y/n)
- **`portia_storage_class`**: MEMORY, DISK, or CLOUD
- **`portia_log_level`**: INFO, DEBUG, WARNING, ERROR
- **`port`**: Application port (default 8000)

## Key Patterns

### Validation Hooks
- **`hooks/pre_gen_project.py`**: Validates project configuration before generation
- **`hooks/post_gen_project.py`**: Cleans up files based on configuration choices
- Validation includes project slug format, port ranges, and Python version compatibility

### Generated Project Patterns
- **Factory Pattern**: `create_app()` function for FastAPI application setup
- **Singleton Pattern**: Global Portia instance with lazy initialization
- **Dependency Injection**: Settings injected via `get_settings()`
- **Lifespan Management**: Proper startup/shutdown with async context managers
- **Tool Registry**: Modular tool system with conditional registration

### Environment Configuration
Generated projects use:
- **Pydantic Settings**: Type-safe environment variable handling
- **`.env` Files**: Local development configuration
- **LLM Provider Support**: OpenAI, Anthropic, Google, Mistral, Azure OpenAI
- **Storage Classes**: Memory (default), Disk, or Portia Cloud

## Testing Strategy

### Template Testing
- **Integration Tests**: Full template generation and project validation
- **Configuration Testing**: Different combinations of cookiecutter variables
- **Dependency Installation**: Validates `uv sync` works in generated projects
- **API Startup**: Tests that generated FastAPI applications start correctly
- **Code Quality**: Ensures generated code passes linting and type checking

### Generated Project Testing
- **Unit Tests**: Fast tests with mocked dependencies
- **Integration Tests**: Real API calls (marked with `@pytest.mark.integration`)
- **Coverage Reports**: HTML coverage reports in `htmlcov/`
- **Test Markers**: `integration` and `slow` for selective test execution

## Dependencies

### Template Dependencies
- **cookiecutter**: Template rendering engine
- **pytest**: Testing framework for template validation
- **httpx**: HTTP client for API testing

### Generated Project Dependencies
- **Core**: FastAPI, Uvicorn, Portia SDK, Pydantic
- **Development**: pytest, ruff, pyright, coverage tools
- **Optional**: Docker support, example tools

## File Organization

### Template Files
- Jinja2 templating with `{{cookiecutter.variable}}` syntax
- Conditional file inclusion based on cookiecutter variables
- Proper `.gitignore`, `.dockerignore`, and environment templates

### Generated Projects
- **Single Responsibility**: Each module has focused functionality
- **API Versioning**: Routes prefixed with `/api/v1`
- **Schema Separation**: Request/response models in separate files
- **Tool Modularity**: Custom tools in dedicated directory
- **Test Structure**: Mirrors application structure in `tests/`