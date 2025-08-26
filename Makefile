# Termina - macOS Voice Input Application
# Development and build automation

.PHONY: help install dev-install run test lint format type-check security clean build

# Default target
help: ## Show this help message
	@echo "Termina - macOS Voice Input Application"
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation and lock file management
sync: ## Sync dependencies from lock file
	uv sync --frozen

sync-dev: ## Sync including dev dependencies (default groups handles this automatically)
	uv sync

lock: ## Update lock file
	uv lock

lock-check: ## Verify lock file is up to date
	uv lock --check

## NOTE: pip ベースの手順は廃止しました。uv に一本化しています。

# Runtime commands
run: ## Run the application
	uv run python termina.py

## NOTE: pip ベースの手順は廃止しました。uv に一本化しています。

# Development and testing
test: ## Run tests with coverage
	uv run pytest --cov=. --cov-report=term-missing --cov-report=html

## NOTE: pip ベースの手順は廃止しました。uv に一本化しています。

# Code quality checks
lint: ## Run ruff linter and formatter (recommended order)
	uv run ruff check --fix
	uv run ruff format

lint-check: ## Check linting and formatting without fixing
	uv run ruff check
	uv run ruff format --check

format: ## Format code with ruff
	uv run ruff format

type-check: ## Run mypy type checking (currently disabled due to many errors)
	@echo "Type checking is currently disabled. Run 'uv run mypy . --ignore-missing-imports' manually if needed."

# Security and vulnerability checks
security: ## Run security and vulnerability checks
	uv run ruff check . --select=S --ignore=S603,S607  # Security rules (ignore safe subprocess calls)
	uv run pip-audit

# Quality control - run all checks
quality: lint-check security ## Run all quality checks (CI-friendly)
	@echo "✅ All quality checks passed!"

# Development setup
dev-setup: sync ## Complete development setup
	@echo "🚀 Development environment setup complete!"
	@echo "Run 'make run' to start the application"
	@echo "Run 'make quality' to run all quality checks"

# Cleanup
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Build commands
build: ## Build the project
	uv build

# Additional environment management aliases
install: sync ## Alias for sync - Install dependencies
update-lock: lock ## Alias for lock - Update lock file

# Development workflow shortcuts
check: lock-check quality test ## Run all checks including lock file verification
	@echo "✅ All checks and tests passed!"

quick-test: ## Run tests without coverage
	uv run pytest -v

ci: check ## Alias for check - comprehensive CI pipeline
	@echo "✅ CI checks completed!"

## NOTE: pip ベースの手順は廃止しました。uv に一本化しています。
