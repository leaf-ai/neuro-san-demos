venv: ## Set up a virtual environment in project
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment in ./venv..."; \
		python3 -m venv venv; \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

install: venv ## Install all dependencies in the virtual environment
	@echo "Installing all dependencies including test dependencies in virtual environment..."
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt -r requirements-build.txt
	@echo "All dependencies including test dependencies installed successfully."

activate: ## Activate the venv
	@if [ ! -d "venv" ]; then \
		echo "No virtual environment detected..."; \
		echo "To create a virtual environment and install dependencies, run:"; \
		echo "    make install"; \
		echo ""; \
	else \
		echo "To activate the environment in your current shell, run:"; \
		echo "    source venv/bin/activate"; \
		echo ""; \
	fi

lint: ## Run code formatting and linting tools on source
	isort run.py apps/ coded_tools/ --force-single-line
	black run.py apps/ coded_tools/
	flake8 run.py apps/ coded_tools/
	pylint run.py apps/ coded_tools/

lint-tests: ## Run code formatting and linting tools on tests
	isort tests/ --force-single-line
	black tests/
	flake8 tests/
	pylint tests/

test: lint lint-tests ## Run tests with coverage
	python -m pytest tests/ -v --cov=coded_tools --cov=apps

.PHONY: help venv install activate lint lint-tests test
.DEFAULT_GOAL := help

help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[m %s\n", $$1, $$2}'
