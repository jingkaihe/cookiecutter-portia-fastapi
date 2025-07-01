# Testing the Portia FastAPI Cookiecutter Template

This directory contains integration tests for the cookiecutter template to ensure it generates working projects.

## Quick Test

Run the bash test script for a quick validation:

```bash
./test_template.sh
```

This script will:
- Generate projects with different configurations
- Check that all expected files are created
- Verify basic functionality

## Comprehensive Testing

For more thorough testing with pytest:

```bash
# Install test dependencies
pip install -r test_requirements.txt

# Run all tests
python test_cookiecutter.py -v
```

## Test Coverage

The integration tests cover:

1. **Project Generation**
   - Default configuration
   - Without example tools
   - With Docker support
   - Different Python versions

2. **File Structure**
   - All required files are created
   - Conditional files (Docker, tools) are handled correctly

3. **Dependency Installation**
   - `uv sync` works correctly
   - Both dev and production dependencies install

4. **Code Quality**
   - Generated code passes linting (ruff)
   - Type checking works (pyright)
   - Unit tests pass

5. **API Functionality**
   - FastAPI application starts
   - All endpoints respond correctly
   - Tools are registered properly

## CI/CD

The `.github/workflows/test.yml` file runs these tests automatically on:
- Push to the template directory
- Pull requests affecting the template

## Manual Testing

After generating a project, you can manually test:

```bash
# Generate a project
cookiecutter . --no-input

# Go to the generated project
cd your_project_name

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Install dependencies
uv sync --group dev

# Run tests
uv run pytest

# Start the API
uv run python main.py

# Test with curl
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/
```

## Troubleshooting

### Tests fail with "uv not installed"
Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### API tests fail with timeout
The API startup test waits 5 seconds for the server to start. On slower systems, you may need to increase this timeout in `test_cookiecutter.py`.

### Docker tests are skipped
Docker tests require Docker to be installed and running. They're optional for local testing but run in CI.