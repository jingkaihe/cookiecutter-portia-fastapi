#!/usr/bin/env python
"""Pre-generation hook to validate user inputs."""

import re
import sys

# Validate project slug
PROJECT_SLUG = "{{ cookiecutter.project_slug }}"
if not re.match(r"^[a-z][a-z0-9_]*$", PROJECT_SLUG):
    print(f"ERROR: The project slug '{PROJECT_SLUG}' is not valid.")
    print(
        "It should start with a lowercase letter and contain only lowercase letters, numbers, and underscores."
    )
    sys.exit(1)

# Validate port number
try:
    port = int("{{ cookiecutter.port }}")
    if not 1 <= port <= 65535:
        print(f"ERROR: Port {port} is not valid. Must be between 1 and 65535.")
        sys.exit(1)
except ValueError:
    print("ERROR: Port must be a number.")
    sys.exit(1)

# Validate Python version
PYTHON_VERSION = "{{ cookiecutter.python_version }}"
try:
    major, minor = PYTHON_VERSION.split(".")
    major, minor = int(major), int(minor)
    if major < 3 or (major == 3 and minor < 11):
        print(f"ERROR: Python {PYTHON_VERSION} is not supported. Minimum version is 3.11.")
        sys.exit(1)
except Exception:
    print(f"ERROR: Invalid Python version format: {PYTHON_VERSION}")
    print("Expected format: X.Y (e.g., 3.11)")
    sys.exit(1)
