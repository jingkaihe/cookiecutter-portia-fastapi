# Contributing to Cookiecutter Portia FastAPI

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## How to Contribute

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cookiecutter-portia-fastapi.git
   cd cookiecutter-portia-fastapi
   ```

3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes** and test them thoroughly

5. **Run the tests**:
   ```bash
   # Install test dependencies
   pip install -r test_requirements.txt
   
   # Run tests
   pytest test_cookiecutter.py
   
   # Or use the test script
   ./test_template.sh
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

## Development Guidelines

- Follow PEP 8 style guidelines
- Use `ruff` for linting and formatting
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

## Testing

Before submitting a PR, ensure:
- All existing tests pass
- New features have appropriate tests
- The generated projects work correctly
- Documentation is updated

## Questions?

Feel free to open an issue for any questions or concerns!