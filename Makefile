.PHONY: help install dev-install test lint format run clean

help:
	@echo "Database Agent - Available commands:"
	@echo ""
	@echo "  make install          Install dependencies"
	@echo "  make dev-install      Install development dependencies"
	@echo "  make test             Run test suite"
	@echo "  make lint             Run code quality checks"
	@echo "  make format           Format code with black and isort"
	@echo "  make run              Run interactive CLI"
	@echo "  make clean            Clean up temporary files"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

test:
	pytest --cov=src --cov-report=term-missing

test-fast:
	pytest -v

lint:
	@echo "Checking formatting..."
	black --check src tests
	@echo "Checking imports..."
	isort --check-only src tests
	@echo "Linting..."
	flake8 src tests
	@echo "Type checking..."
	mypy src

format:
	black src tests
	isort src tests

run:
	python -m cli.main --interactive

run-query:
	python -m cli.main --query "$(QUERY)"

run-schema:
	python -m cli.main --schema

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
