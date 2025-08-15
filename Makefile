# AI Research Framework Makefile
# Provides convenient commands for development and testing using UV

.PHONY: help install test test-unit test-integration test-api test-performance lint format type-check security clean coverage docker-build docker-test

# Default target
help:
	@echo "AI Research Framework - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install all dependencies with UV"
	@echo "  install-dev      Install development dependencies with UV"
	@echo "  sync             Sync all dependencies (UV)"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-api         Run API tests only"
	@echo "  test-performance Run performance tests only"
	@echo "  coverage         Generate coverage report"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code"
	@echo "  type-check       Run type checking"
	@echo "  security         Run security checks"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-test      Test Docker image"
	@echo "  docker-run       Run application in Docker"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean            Clean temporary files"
	@echo "  docs             Generate documentation"
	@echo "  serve            Run development server"

# Check if UV is installed
check-uv:
	@command -v uv >/dev/null 2>&1 || { echo "UV is not installed. Please install UV first: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }

# Setup commands
install: check-uv
	@echo "Installing dependencies with UV..."
	uv sync --all-extras

install-dev: check-uv
	@echo "Installing development dependencies with UV..."
	uv add --dev pytest pytest-asyncio pytest-cov pytest-html pytest-json-report pytest-benchmark
	uv add --dev ruff mypy bandit safety
	uv add --dev httpx

sync: check-uv
	@echo "Syncing dependencies with UV..."
	uv sync --all-extras --dev

# Testing commands
test: clean check-uv
	@echo "Running all tests with UV..."
	@mkdir -p reports htmlcov
	@export PYTHONPATH="$(PWD)/src:$(PYTHONPATH)" && \
	export TESTING=true && \
	export DATABASE_URL="sqlite+aiosqlite:///:memory:" && \
	uv run pytest tests/ -v \
		--cov=src/ai_research_framework \
		--cov-report=html:htmlcov \
		--cov-report=xml:coverage.xml \
		--cov-report=term-missing \
		--html=reports/test_report.html \
		--self-contained-html \
		--json-report \
		--json-report-file=reports/test_report.json

test-unit: check-uv
	@echo "Running unit tests with UV..."
	@mkdir -p reports htmlcov
	@export PYTHONPATH="$(PWD)/src:$(PYTHONPATH)" && \
	export TESTING=true && \
	uv run pytest tests/unit -v \
		--cov=src/ai_research_framework \
		--cov-report=html:htmlcov \
		--cov-report=term-missing \
		--html=reports/unit_test_report.html \
		--self-contained-html

test-integration: check-uv
	@echo "Running integration tests with UV..."
	@mkdir -p reports
	@export PYTHONPATH="$(PWD)/src:$(PYTHONPATH)" && \
	export TESTING=true && \
	uv run pytest tests/integration -v \
		--maxfail=5 \
		--html=reports/integration_test_report.html \
		--self-contained-html

test-api: check-uv
	@echo "Running API tests with UV..."
	@mkdir -p reports
	@export PYTHONPATH="$(PWD)/src:$(PYTHONPATH)" && \
	export TESTING=true && \
	uv run pytest tests/integration/test_api_endpoints.py -v \
		--html=reports/api_test_report.html \
		--self-contained-html

test-performance: check-uv
	@echo "Running performance tests with UV..."
	@mkdir -p reports
	@export PYTHONPATH="$(PWD)/src:$(PYTHONPATH)" && \
	uv run pytest tests/ -m "performance" -v \
		--benchmark-only \
		--benchmark-json=reports/benchmark_report.json

coverage: check-uv
	@echo "Generating coverage report with UV..."
	@mkdir -p htmlcov
	@export PYTHONPATH="$(PWD)/src:$(PYTHONPATH)" && \
	uv run pytest tests/unit \
		--cov=src/ai_research_framework \
		--cov-report=html:htmlcov \
		--cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# Code quality commands
lint: check-uv
	@echo "Running linting checks with UV..."
	uv run ruff check src tests

format: check-uv
	@echo "Formatting code with UV..."
	uv run ruff format src tests

type-check: check-uv
	@echo "Running type checking with UV..."
	uv run mypy src --ignore-missing-imports

security: check-uv
	@echo "Running security checks with UV..."
	@mkdir -p reports
	uv run bandit -r src/ -f json -o reports/bandit_report.json || echo "Security issues found, check reports/bandit_report.json"
	uv run safety check --json --output reports/safety_report.json || echo "Dependency vulnerabilities found, check reports/safety_report.json"

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t ai-research-framework:latest .

docker-test: docker-build
	@echo "Testing Docker image..."
	docker run --rm -d --name test-container -p 8000:8000 ai-research-framework:latest
	@sleep 10
	@curl -f http://localhost:8000/health || (docker stop test-container && exit 1)
	@docker stop test-container
	@echo "Docker image test passed"

docker-run: docker-build
	@echo "Running application in Docker..."
	docker run --rm -p 8000:8000 -v $(PWD)/data:/app/data ai-research-framework:latest

docker-compose-up:
	@echo "Starting application with Docker Compose..."
	docker-compose up --build

docker-compose-down:
	@echo "Stopping application with Docker Compose..."
	docker-compose down

# Utility commands
clean:
	@echo "Cleaning temporary files..."
	@rm -rf __pycache__ .pytest_cache .coverage htmlcov reports .mypy_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -f test.db *.log

docs:
	@echo "Generating documentation..."
	@mkdir -p docs
	@echo "Documentation generation not implemented yet"

serve: check-uv
	@echo "Starting development server with UV..."
	@export PYTHONPATH="$(PWD)/src:$(PYTHONPATH)" && \
	uv run uvicorn ai_research_framework.api.main:app --reload --host 0.0.0.0 --port 8000

# UV-specific commands
uv-lock:
	@echo "Updating UV lock file..."
	uv lock

uv-tree:
	@echo "Showing dependency tree..."
	uv tree

uv-outdated:
	@echo "Checking for outdated packages..."
	uv pip list --outdated

# Quick development workflow
dev: clean lint type-check test-unit
	@echo "Development workflow completed"

# CI/CD workflow
ci: clean lint type-check security test
	@echo "CI/CD workflow completed"

# Show test results
show-results:
	@echo "Opening test results..."
	@if [ -f "reports/test_report.html" ]; then \
		echo "Test report: file://$(PWD)/reports/test_report.html"; \
	fi
	@if [ -f "htmlcov/index.html" ]; then \
		echo "Coverage report: file://$(PWD)/htmlcov/index.html"; \
	fi

# Environment setup
setup-env:
	@echo "Setting up environment..."
	@if [ ! -f ".env" ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

# Full setup for new developers
setup: check-uv setup-env sync
	@echo "Full setup completed!"
	@echo "Next steps:"
	@echo "1. Edit .env file with your configuration"
	@echo "2. Run 'make test' to verify everything works"
	@echo "3. Run 'make serve' to start the development server"

# Windows compatibility note
windows-help:
	@echo "For Windows users:"
	@echo "1. Install UV: https://docs.astral.sh/uv/getting-started/installation/"
	@echo "2. Use scripts/run_tests_windows.bat for testing"
	@echo "3. Use docker-compose up --build for Docker deployment"

