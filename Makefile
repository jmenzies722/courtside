.PHONY: help sqs ingest record api web down test

# espn = live games tonight, replay = a real past night played back
SOURCE ?= replay
DATE ?= 20261104
SPEED ?= 1
LOCAL_SQS = QUEUE_NAME=game-events SQS_ENDPOINT_URL=http://localhost:9324

help: ## List commands
	@\grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

sqs: ## Start the local queue (ElasticMQ). UI: http://localhost:9325
	docker compose up -d

ingest: ## Run ingest into the local queue (SOURCE=replay|espn, DATE=YYYYMMDD, SPEED=1)
	cd services/ingest && $(LOCAL_SQS) SOURCE=$(SOURCE) REPLAY_DATE=$(DATE) REPLAY_SPEED=$(SPEED) POLL_SECONDS=3 uv run python worker.py

record: ## Save a real night of games for replay (make record DATE=YYYYMMDD)
	cd services/ingest && uv run python replay.py record $(DATE)

api: ## Run the API at http://localhost:8000
	cd services/api && $(LOCAL_SQS) uv run uvicorn app:app --port 8000 --timeout-graceful-shutdown 5

web: ## Run the Next.js scoreboard at http://localhost:3000
	cd web && API_URL=http://localhost:8000 npm run dev

test: ## Run every service's tests
	cd services/ingest && uv run python -m pytest -q tests
	cd services/api && uv run python -m pytest -q tests

down: ## Stop local services
	docker compose down
