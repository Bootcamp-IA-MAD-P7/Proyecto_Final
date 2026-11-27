# Single entry point for every project command (CONTRIBUTING §10). Run `make help` to list them.
#
# Every service lives in its own folder with a Makefile that defines, for local work without Docker:
#   install  install dependencies
#   dev      run the service locally
#   test     run its tests
#   lint     run its linters and format checks
# This Makefile finds those folders automatically and adds <service>-<target> commands for each one.

SHELL := bash
.DEFAULT_GOAL := help

SERVICES := $(patsubst %/Makefile,%,$(wildcard */Makefile))
# Ports of the root .env (the same ones Compose publishes), for make e2e. Only these two are read,
# and the shell wins: `FRONTEND_PORT=8080 make e2e`.
BACKEND_PORT ?= $(shell sed -n 's/^BACKEND_PORT=//p' .env 2>/dev/null)
FRONTEND_PORT ?= $(shell sed -n 's/^FRONTEND_PORT=//p' .env 2>/dev/null)
export BACKEND_PORT FRONTEND_PORT

COMPOSE := docker compose
COMPOSE_PROD := docker compose -f compose.yaml -f compose.production.yaml

.PHONY: help setup env hooks install dev test lint ci ci-production-build ci-auth-secret-regression e2e e2e-install models up down logs ps up-prod down-prod labels github-setup github-protect claude-skills

help: ## List every available command
	@echo "Usage: make <command>"
	@echo
	@grep -hE '^[a-z][a-z0-9-]*:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'
	@echo
	@if [ -n "$(SERVICES)" ]; then \
		echo "Per service ($(SERVICES)):"; \
		echo "  <service>-install  Install the service dependencies locally"; \
		echo "  <service>-dev      Run the service locally, without Docker"; \
		echo "  <service>-test     Run the service tests"; \
		echo "  <service>-lint     Run the service linters"; \
		echo "  <service>-up       Run only this service with Docker"; \
		echo "  <service>-down     Stop this service in Docker"; \
		echo "  <service>-logs     Follow this service logs in Docker"; \
	else \
		echo "No services yet: the walking skeleton adds them (WORKFLOW §5)."; \
	fi

# --- Setup ---

setup: hooks env install ## Prepare a fresh clone: git hooks, .env files and dependencies

hooks: ## Enable the repository git hooks (commit message check)
	@git config core.hooksPath .githooks
	@echo "Git hooks enabled (.githooks)."

env: ## Create every missing .env from its .env.example
	@find . -name .env.example -not -path './.git/*' -not -path '*/node_modules/*' | while read -r example; do \
		target="$${example%.example}"; \
		if [ ! -f "$$target" ]; then cp "$$example" "$$target"; echo "Created $$target"; fi; \
	done

install: $(addsuffix -install,$(SERVICES)) ## Install every service locally

# --- Local, without Docker ---

dev: ## Run every service locally, without Docker
	@if [ -z "$(SERVICES)" ]; then echo "No services yet."; else $(MAKE) -j$(words $(SERVICES)) $(addsuffix -dev,$(SERVICES)); fi

test: $(addsuffix -test,$(SERVICES)) ## Run every service test suite

lint: $(addsuffix -lint,$(SERVICES)) ## Run every service linter

# --- CI: the same checks as the Servicios job, in Docker ---

ci: env ci-auth-secret-regression ## Run every service lint and tests in its dev image, then build the production images
	@if [ -z "$(SERVICES)" ]; then echo "No services yet."; exit 0; fi; \
	for service in $(SERVICES); do \
		$(COMPOSE) --progress quiet run --rm --build $$service make lint test || exit 1; \
	done; \
	$(MAKE) ci-production-build COMPOSE_PROD='$(COMPOSE_PROD)'

ci-production-build: ## Build production images with an ephemeral Compose authentication secret
	@# AUTH_SECRET exists only while Compose interpolates this build; make up-prod still requires one.
	@AUTH_SECRET="$$(openssl rand -hex 32)" $(COMPOSE_PROD) --progress quiet build

ci-auth-secret-regression: ## Verify the CI-only authentication secret is ephemeral and generated per build
	@bash .github/scripts/test-ci-auth-secret.sh

# --- End-to-end: Playwright on this machine against the running stack ---

e2e-install: ## Install the browser of the end-to-end tests (once per machine)
	$(MAKE) -C frontend e2e-install

e2e: ## Run the end-to-end tests against `make up` with the models (first time: make e2e-install)
	@curl -fsS -o /dev/null "http://localhost:$${BACKEND_PORT:-8000}/ready" || { echo "The API is not ready: run make up first."; exit 1; }
	@curl -fsS -o /dev/null "http://localhost:$${FRONTEND_PORT:-5173}/" || { echo "The web is not up: run make up first."; exit 1; }
	@$(COMPOSE) run --rm --no-deps -T worker python -m app.inference.models check \
		|| { echo "The worker needs INFERENCE_PIPELINE=models and the models: run make models (README, Modelos de inferencia)."; exit 1; }
	@mkdir -p frontend/e2e/generated
	$(COMPOSE) run --rm --no-deps -T worker sh scripts/two-voices.sh > frontend/e2e/generated/two-voices.ogg
	$(MAKE) -C frontend e2e

# --- Models: download once into the private volume of the worker ---

models: env ## Download the fixed model revisions into the worker volume (needs HF_TOKEN in backend/.env)
	$(COMPOSE) run --rm --no-deps --build -e HF_HUB_OFFLINE=0 worker python -m app.inference.models download

# --- Docker: development ---

up: ## Run everything with Docker (compose.yaml + compose.override.yaml)
	$(COMPOSE) up -d --build

down: ## Stop everything in Docker
	$(COMPOSE) down

logs: ## Follow every service log in Docker
	$(COMPOSE) logs -f

ps: ## List the running containers
	$(COMPOSE) ps

# --- Docker: production configuration ---

up-prod: ## Run everything with the production configuration
	$(COMPOSE_PROD) up -d --build

down-prod: ## Stop the production configuration
	$(COMPOSE_PROD) down

# --- GitHub (gh with admin rights on the repository) ---

labels: ## Create or update the GitHub labels of docs/ISSUE_LABELS.md
	@bash .github/scripts/labels.sh

github-setup: ## Configure GitHub: dev as default branch, rebase and merge commits only, and the labels
	gh repo edit --default-branch dev --enable-rebase-merge --enable-merge-commit --enable-squash-merge=false
	@bash .github/scripts/labels.sh

github-protect: ## Protect dev and main with the rulesets of .github/rulesets/
	@bash .github/scripts/rulesets.sh

# --- AI tools ---

claude-skills: ## Copy the skills of .agents/skills/ to .claude/skills/ for Claude Code
	@mkdir -p .claude/skills
	@for skill in .agents/skills/*/; do \
		name=$$(basename "$$skill"); \
		if [ ! -L ".claude/skills/$$name" ]; then mkdir -p ".claude/skills/$$name" && cp -R "$$skill." ".claude/skills/$$name/"; fi; \
	done
	@echo "Skills copied to .claude/skills/. Run it again when they change."

# --- Per service (each <service>/Makefile defines install, dev, test and lint) ---

%-install:
	$(MAKE) -C $* install

%-dev:
	$(MAKE) -C $* dev

%-test:
	$(MAKE) -C $* test

%-lint:
	$(MAKE) -C $* lint

%-up:
	$(COMPOSE) up -d --build $*

%-down:
	$(COMPOSE) stop $*

%-logs:
	$(COMPOSE) logs -f $*
