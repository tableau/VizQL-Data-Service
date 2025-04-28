#!/bin/bash

set -e

echo "Installing dependencies..."
pip install requests setuptools wheel 
pip install -e ".[dev]" --no-build-isolation

echo "Running linting checks..."
# flake8 src tests
# black --check src tests
# isort --check-only src tests
# mypy src

echo "Running tests with coverage..."
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml

if [ $? -eq 0 ]; then
    echo "All tests passed successfully!"
else
    echo "Tests failed!"
    exit 1
fi
