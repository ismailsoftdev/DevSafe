.PHONY: help install dev test test-cov lint format format-check clean build setup-hooks demo

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the devsafe command from this checkout (editable)
	uv tool install --editable . --force

dev: ## Create the development environment
	uv sync

test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ --cov=devsafe --cov-report=html --cov-report=term

lint: ## Run linting checks
	uv run flake8 devsafe/ tests/
	uv run mypy devsafe/

format: ## Format code
	uv run black devsafe/ tests/
	uv run isort devsafe/ tests/

format-check: ## Check code formatting without making changes
	uv run black --check devsafe/ tests/
	uv run isort --check-only devsafe/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	uv build

setup-hooks: ## Set up git hooks for development
	cp devsafe/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

demo: ## Run a quick demo
	@echo "🚀 DevSafe Demo"
	@echo "================"
	uv run devsafe status
	@echo ""
	@echo "For more commands, run: devsafe --help"
