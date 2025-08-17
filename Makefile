# ---- Variables ----
SHELL := /bin/bash

COMPONENTS := api worker
IMAGE_PREFIX ?= opsbox
TAG ?= $(shell git rev-parse --short HEAD)
PYTHON_DIRS := api worker
SCRIPT_DIR := ops/scripts

# Tools (override if needed, e.g., make LINT_RUFF="uv run ruff")
PY := python
PYTEST ?= pytest -q
BLACK ?= black
ISORT ?= isort
RUFF ?= ruff
SHELLCHECK ?= shellcheck
DOCKER ?= docker

# ---- Helpers ----
.DEFAULT_GOAL := help
.PHONY: help build test run fmt lint pipeline-local

help: ## Show this help
	@awk 'BEGIN {FS := ":.*?## "}; /^[a-zA-Z0-9_.-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

fmt: ## Format Python code (black + isort)
	@echo ">> Formatting Python"
	$(BLACK) $(PYTHON_DIRS)
	$(ISORT) $(PYTHON_DIRS)

lint: ## Lint Python (ruff) and bash (shellcheck)
	@echo ">> Lint: ruff"
	$(RUFF) check $(PYTHON_DIRS)
	@echo ">> Lint: black --check"
	$(BLACK) --check $(PYTHON_DIRS)
	@echo ">> Lint: isort --check-only"
	$(ISORT) --check-only $(PYTHON_DIRS)
	@echo ">> Lint: shellcheck"
	@if [ -d $(SCRIPT_DIR) ]; then \
	  $(SHELLCHECK) -x $(SCRIPT_DIR)/*.sh; \
	else \
	  echo "(no $(SCRIPT_DIR) directory; skipping shellcheck)"; \
	fi

test: ## Run pytest for API and worker
	@echo ">> Running tests"
	$(PYTEST)

build: ## Build Docker images for api and worker with tag $(TAG)
	@echo ">> Building images (TAG=$(TAG))"
	@for c in $(COMPONENTS); do \
	  echo "  - $$c"; \
	  $(DOCKER) build --pull -t $(IMAGE_PREFIX)/$$c:$(TAG) -f $$c/Dockerfile $$c ; \
	done

run: ## Bring up local stack via bootstrap script
	@echo ">> Running local stack (kind/helm/bootstrap)"
	@./ops/scripts/bootstrap.sh

pipeline-local: ## Local pipeline: fmt → lint → test → build
	@set -e; \
	  $(MAKE) fmt; \
	  $(MAKE) lint; \
	  $(MAKE) test; \
	  $(MAKE) build
