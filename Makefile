.PHONY: help install dev test lint format clean build publish

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install DevSafe in production mode
	pip install .

dev: ## Install DevSafe in development mode
	pip install -e .
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=devsafe --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 devsafe/ tests/
	mypy devsafe/

format: ## Format code
	black devsafe/ tests/
	isort devsafe/ tests/

format-check: ## Check code formatting without making changes
	black --check devsafe/ tests/
	isort --check-only devsafe/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	python -m build

publish-test: build ## Publish to Test PyPI
	python -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	python -m twine upload dist/*

docker-build: ## Build Docker image
	docker build -t devsafe:latest .

docker-run: ## Run DevSafe in Docker
	docker run --rm -it devsafe:latest

setup-hooks: ## Set up git hooks for development
	cp devsafe/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

demo: ## Run a quick demo
	@echo "🚀 DevSafe Demo"
	@echo "================"
	devsafe status
	@echo ""
	@echo "For more commands, run: devsafe --help"