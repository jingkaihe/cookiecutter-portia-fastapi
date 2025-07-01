# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}

Generated from the Portia FastAPI cookiecutter template.

## Features

- ✅ RESTful API with automatic OpenAPI documentation
- ✅ Pydantic settings for environment-based configuration
{%- if cookiecutter.include_example_tools == 'y' %}
- ✅ Example tools using the Portia tool decorator pattern
{%- endif %}
- ✅ Comprehensive error handling and logging
{%- if cookiecutter.use_docker == 'y' %}
- ✅ Docker support for easy deployment
{%- endif %}
- ✅ Type safety throughout the codebase
- ✅ Health check and status endpoints

## Quick Start

### Prerequisites

- Python {{ cookiecutter.python_version }}+
- An OpenAI API key (or another supported LLM provider)
{%- if cookiecutter.use_docker == 'y' %}
- Docker (optional, for containerized deployment)
{%- endif %}

### Local Development

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. **Install dependencies using uv:**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # For development (includes test tools, linters, etc.)
   uv sync --group dev

   # For production (core dependencies only)
   uv sync --no-group dev
   ```

3. **Run the application:**
   ```bash
   # Using uv run (recommended - automatic environment management)
   uv run uvicorn app.main:app --reload

   # Or using the main script
   uv run python main.py
   ```

4. **Access the API:**
   - API documentation: http://localhost:{{ cookiecutter.port }}/docs
   - Alternative docs: http://localhost:{{ cookiecutter.port }}/redoc
   - Health check: http://localhost:{{ cookiecutter.port }}/health

{%- if cookiecutter.use_docker == 'y' %}

### Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t {{ cookiecutter.project_slug }} .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name {{ cookiecutter.project_slug }} \
     -p {{ cookiecutter.port }}:{{ cookiecutter.port }} \
     -e OPENAI_API_KEY="your-api-key" \
     {{ cookiecutter.project_slug }}
   ```

3. **Check logs:**
   ```bash
   docker logs {{ cookiecutter.project_slug }}
   ```
{%- endif %}

## Testing

This project includes comprehensive unit tests and integration tests.

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only (no API key required)
make test-unit

# Run tests with coverage
make test-cov

# Run integration tests (requires API key)
make test-integration
```

### Test Structure

- `tests/test_api.py` - API endpoint tests
- `tests/test_config.py` - Configuration tests  
- `tests/test_schemas.py` - Pydantic schema tests
- `tests/conftest.py` - Shared test fixtures

### Test Categories

- **Unit Tests**: Fast tests that don't require external APIs
- **Integration Tests**: Tests that require real LLM API keys (marked with `@pytest.mark.integration`)

### Coverage

Generate coverage reports:
```bash
make test-cov
# Open htmlcov/index.html to view detailed coverage
```

## API Endpoints

### `GET /`
Root endpoint with welcome message and API information.

### `GET /health`
Health check endpoint for monitoring.

### `GET /api/v1/`
Get API status and list of available tools.

**Response:**
```json
{
  "status": "healthy",
  "version": "{{ cookiecutter.version }}",
  "portia_version": "0.4.3",
  "available_tools": [{% if cookiecutter.include_example_tools == 'y' %}"reverse_text", "roll_dice", "add_numbers", "get_random_fact", "uppercase_text", "count_letters"{% endif %}],
  "timestamp": "2024-03-20T10:30:00"
}
```

### `POST /api/v1/run`
Execute a query using the Portia SDK.

**Request:**
```json
{
  "query": "Your task or question here",
  "tools": ["tool_id"],
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "status": "COMPLETE",
  "result": "The result of your query",
  "clarifications": [],
  "plan_run_id": "run_abc123",
  "error": null,
  "metadata": {
    "execution_time": 1.2,
    "tools_used": ["tool_id"],
    "tools_available": 1
  }
}
```

### Example Requests
{%- if cookiecutter.include_example_tools == 'y' %}

**Simple text manipulation:**
```bash
curl -X POST http://localhost:{{ cookiecutter.port }}/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Reverse the text hello world"
  }'
```

**Math calculation:**
```bash
curl -X POST http://localhost:{{ cookiecutter.port }}/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Add 42 and 58"
  }'
```

**Get a random fact:**
```bash
curl -X POST http://localhost:{{ cookiecutter.port }}/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me a random fun fact"
  }'
```

**Using specific tools:**
```bash
curl -X POST http://localhost:{{ cookiecutter.port }}/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Roll a 20-sided die",
    "tools": ["roll_dice"]
  }'
```
{%- endif %}

### `GET /api/v1/tools`
Get detailed information about available tools.

## Configuration

The application uses Pydantic settings for configuration management. All settings can be overridden using environment variables.

### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | None |
| `APP_NAME` | Application name | "{{ cookiecutter.project_name }}" |
| `APP_VERSION` | Application version | "{{ cookiecutter.version }}" |
| `DEBUG` | Debug mode | false |
| `LOG_LEVEL` | Logging level | "info" |
| `HOST` | Server host | "0.0.0.0" |
| `PORT` | Server port | {{ cookiecutter.port }} |

### Portia Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `PORTIA_LOG_LEVEL` | Portia SDK log level | "{{ cookiecutter.portia_log_level }}" |
| `PORTIA_STORAGE_CLASS` | Storage class (MEMORY/DISK/CLOUD) | "{{ cookiecutter.portia_storage_class }}" |
| `PORTIA_API_KEY` | Portia Cloud API key (optional) | None |

{%- if cookiecutter.include_example_tools != 'y' %}

## Adding Custom Tools

Create your tools in the `app/tools/` directory using the Portia tool decorator:

```python
from typing import Annotated
from portia import tool

@tool
def my_custom_tool(
    param: Annotated[str, "Description of parameter"]
) -> str:
    """Tool description."""
    return f"Result: {param}"
```

Then register them in `app/tools/__init__.py`:

```python
from portia import ToolRegistry
from .my_tools import my_custom_tool

custom_tools = ToolRegistry([
    my_custom_tool(),
])
```
{%- endif %}

## Development

### Using Make (Optional)

A Makefile is provided for common tasks:

```bash
make help         # Show available commands
make install-dev  # Install with dev dependencies
make run          # Run the application
make test         # Run tests
make lint         # Check code style
make format       # Format code
```

### Running Tests

```bash
# Run tests with uv
uv run pytest

# Run with coverage
uv run pytest --cov --cov-report=html
```

### Code Quality

```bash
# Run linter and formatter
uv run ruff check --fix .
uv run ruff format .

# Type checking
uv run pyright
```

## License

{{ cookiecutter.project_name }} - {{ cookiecutter.project_short_description }}

Created by {{ cookiecutter.full_name }} ({{ cookiecutter.email }})