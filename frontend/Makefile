.PHONY: help install dev test lint build generate-api

help: ## List frontend commands
	@grep -hE '^[a-z][a-z0-9-]*:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-12s %s\\n", $$1, $$2}'

install: ## Install frontend dependencies
	npm ci

dev: ## Run the Vite development server
	npm run dev

test: ## Run the frontend test suite
	npm run test

lint: ## Check linting, types and API type drift
	npm run lint

build: ## Build the production static assets
	npm run build

generate-api: ## Generate TypeScript types from the OpenAPI contract
	npm run generate:api
