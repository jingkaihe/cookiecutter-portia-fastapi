# Portia FastAPI Cookiecutter Template

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for creating production-ready FastAPI services that wrap the Portia SDK for building agentic AI workflows.

## Features

- 🚀 FastAPI web framework with async support
- 🤖 Portia SDK integration for AI agent workflows
- 🔧 Pydantic settings for configuration management
- 🐳 Docker support for containerized deployment
- 📝 Comprehensive API documentation (OpenAPI/Swagger)
- 🛠️ Example tools using Portia's tool decorator pattern
- 📊 Structured logging with Loguru
- 🧪 Test scripts included
- 📦 Modern Python packaging with `uv`

## Prerequisites

- Python 3.11+
- [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/installation.html)
- [uv](https://github.com/astral-sh/uv) (for dependency management)
- An OpenAI API key (or another supported LLM provider)

## Quick Start

### Install Cookiecutter

```bash
# Using pip
pip install cookiecutter

# Or using uv (recommended)
uv tool install cookiecutter
```

### Generate Your Project

```bash
# Directly from GitHub (recommended)
uvx cookiecutter gh:jingkaihe/cookiecutter-portia-fastapi

# Or using cookiecutter with GitHub
cookiecutter https://github.com/jingkaihe/cookiecutter-portia-fastapi

# Or if you've cloned this repository locally
cookiecutter .
```

You'll be prompted for various configuration options:

- `full_name`: Your name (for documentation)
- `email`: Your email address
- `project_name`: Name of your project (e.g., "My Portia Service")
- `project_slug`: URL-friendly version of the project name
- `project_short_description`: Brief description of your service
- `version`: Initial version number
- `python_version`: Python version to use (default: 3.11)
- `use_docker`: Include Docker configuration? (y/n)
- `port`: Port to run the service on
- `include_example_tools`: Include example Portia tools? (y/n)
- `portia_storage_class`: Default storage class for Portia
- `portia_log_level`: Default log level for Portia

### Set Up Your Generated Project

```bash
cd <your-project-slug>

# Install dependencies (for development)
# This automatically creates and manages a virtual environment
uv sync --group dev

# Copy and configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the service
uv run python main.py
# or
uv run uvicorn app.main:app --reload
```

### Access Your API

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Template Structure

After generation, your project will have this structure:

```
your-project-name/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Pydantic settings
│   ├── logging_config.py    # Logging setup
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── schemas/
│   │   ├── request.py       # Request models
│   │   └── response.py      # Response models
│   └── tools/               # Portia tools (if included)
│       └── example_tools.py
├── tests/                   # Test files
├── main.py                  # Entry point
├── Dockerfile              # Docker configuration (if enabled)
├── pyproject.toml          # Project dependencies
├── README.md               # Project documentation
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── test_with_real_api.py   # API testing script
```

## Customization Options

### Adding Your Own Tools

1. Create new tool files in the `app/tools/` directory
2. Use the Portia tool decorator pattern:

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

3. Register your tools in `app/tools/__init__.py`

### Configuration

All configuration is managed through environment variables and Pydantic settings. See the generated `.env.example` file for available options.

### Docker Deployment

If you enabled Docker support:

```bash
# Build the image
docker build -t your-project-name .

# Run the container
docker run -d \
  --name your-service \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-api-key" \
  your-project-name
```

## Example API Usage

### Basic Query

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your task or question here"
  }'
```

### Using Specific Tools

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your task",
    "tools": ["tool_id_1", "tool_id_2"]
  }'
```

## Testing the Template

This template includes comprehensive integration tests. See [TESTING.md](TESTING.md) for details.

Quick test:
```bash
./test_template.sh
```

## Contributing

Feel free to submit issues or pull requests to improve this template! Please ensure all tests pass before submitting.

## License

This template is part of the Portia SDK Python project. See the main project LICENSE for details.