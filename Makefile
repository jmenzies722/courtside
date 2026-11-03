.PHONY: help up down test

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

up: ## Start the local kind cluster (filled in during week 2)
	@echo "coming in week 2"

down: ## Tear everything down so nothing costs money
	@echo "coming in week 2"

test: ## Run all tests
	@echo "no tests yet"
