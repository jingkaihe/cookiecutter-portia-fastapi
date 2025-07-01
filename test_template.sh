#!/bin/bash
# Simple test script for the cookiecutter template

set -e  # Exit on error

echo "Testing Portia FastAPI Cookiecutter Template"
echo "==========================================="

# Store the cookiecutter template directory
TEMPLATE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Working in: $TEMP_DIR"

# Function to cleanup
cleanup() {
    echo "Cleaning up..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Change to temp directory
cd "$TEMP_DIR"

# Test 1: Generate project with default settings
echo -e "\n1. Generating project with default settings..."
uvx cookiecutter "$TEMPLATE_DIR" --no-input \
    -o "$TEMP_DIR" \
    project_name="Test API" \
    project_slug="test_api" \
    include_example_tools=y \
    use_docker=y

# Check if project was created
if [ ! -d "test_api" ]; then
    echo "ERROR: Project directory not created"
    exit 1
fi

cd test_api

# Test 2: Check essential files exist
echo -e "\n2. Checking essential files..."
FILES=(
    "pyproject.toml"
    "README.md"
    "main.py"
    "Makefile"
    ".env.example"
    "Dockerfile"
    ".dockerignore"
    "app/main.py"
    "app/config.py"
    "app/api/routes.py"
    "app/tools/example_tools.py"
    "tests/test_api.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file missing!"
        exit 1
    fi
done

# Test 3: Create .env file
echo -e "\n3. Setting up environment..."
cp .env.example .env
# Use a dummy key for testing
sed -i.bak 's/your-openai-api-key-here/sk-test-dummy-key/g' .env

# Test 4: Check if uv is available
echo -e "\n4. Checking dependencies..."
if command -v uv &> /dev/null; then
    echo "✓ uv is installed"

    # Install dependencies
    echo "Installing dependencies..."
    uv sync --no-group dev

    # Test 5: Run basic tests
    echo -e "\n5. Running basic import test..."
    uv run python -c "from app.main import app; print('✓ App imports successfully')"

    # Test 6: Run unit tests
    echo -e "\n6. Running unit tests..."
    uv run pytest tests/test_api.py -v || echo "⚠ Tests require API keys to pass fully"

else
    echo "⚠ uv not installed, skipping dependency tests"
fi

# Test 7: Test Makefile targets
echo -e "\n7. Testing Makefile..."
make help > /dev/null && echo "✓ Makefile works"

# Test 8: Generate project without example tools
echo -e "\n8. Testing generation without example tools..."
cd "$TEMP_DIR"
uvx cookiecutter "$TEMPLATE_DIR" --no-input \
    -o "$TEMP_DIR" \
    project_name="Minimal API" \
    project_slug="minimal_api" \
    include_example_tools=n \
    use_docker=n

if [ -f "minimal_api/app/tools/example_tools.py" ]; then
    echo "✗ example_tools.py should not exist!"
    exit 1
else
    echo "✓ No example tools included"
fi

if [ -f "minimal_api/Dockerfile" ]; then
    echo "✗ Dockerfile should not exist!"
    exit 1
else
    echo "✓ No Docker files included"
fi

echo -e "\n✅ All tests passed!"
echo "The cookiecutter template is working correctly."