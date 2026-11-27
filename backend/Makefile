# Backend commands for local work without Docker (CONTRIBUTING §10). The root Makefile exposes them
# as backend-<target>. Use a virtual environment with Python 3.11 when running them on your machine.

PYTHON ?= python3
PORT ?= 8000

.PHONY: help install migrate dev worker maintenance test test-models models measure lint format openapi

help: ## List the backend commands
	@grep -hE '^[a-z][a-z0-9-]*:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Install the runtime, test and lint dependencies
	$(PYTHON) -m pip install -r requirements-dev.txt

migrate: ## Apply the database migrations to DATABASE_URL
	$(PYTHON) -m app.db.migrate

dev: migrate ## Apply the migrations and run the API with hot reload
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

worker: ## Run the worker (the API applies the migrations)
	$(PYTHON) -m app.worker

maintenance: ## Run the maintenance cycles
	$(PYTHON) -m app.maintenance

test: ## Run the tests without real models
	$(PYTHON) -m pytest -m "not models"

models: ## Download the fixed revisions of the registered models
	$(PYTHON) -m app.inference.models download

test-models: ## Run the tests that need the downloaded models
	$(PYTHON) -m pytest -m models

measure: ## Print the measurements registered by the adapters
	$(PYTHON) -m app.inference.models measure

lint: ## Check lint and formatting with Ruff
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format: ## Fix lint and formatting with Ruff
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

openapi: ## Export the API contract to openapi.json
	$(PYTHON) -m app.openapi_export
