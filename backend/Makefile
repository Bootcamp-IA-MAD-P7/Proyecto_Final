# Backend commands for local work without Docker (CONTRIBUTING §10). The root Makefile exposes them
# as backend-<target>. Use a virtual environment with Python 3.11 when running them on your machine.

PYTHON ?= python3
PORT ?= 8000

.PHONY: help install dev test lint format openapi

help: ## List the backend commands
	@grep -hE '^[a-z][a-z0-9-]*:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Install the runtime, test and lint dependencies
	$(PYTHON) -m pip install -r requirements-dev.txt

dev: ## Run the API with hot reload
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

test: ## Run the tests
	$(PYTHON) -m pytest

lint: ## Check lint and formatting with Ruff
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format: ## Fix lint and formatting with Ruff
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

openapi: ## Export the API contract to openapi.json
	$(PYTHON) -m app.openapi_export
