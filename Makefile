# Cognivest — developer task runner
# Usage: make <target>   |   make help

FRONTEND_DIR ?= frontend
BACKEND_DIR  ?= backend

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---- Docker stack ----------------------------------------------------
.PHONY: up
up: ## Build + start the full local stack (postgres, redis, backend, worker, beat, frontend)
	docker compose up --build -d
	@echo "Backend:  http://localhost:8000/docs   (health: /health)"
	@echo "Frontend: http://localhost:3000"

.PHONY: down
down: ## Stop and remove the local stack containers
	docker compose down

.PHONY: restart
restart: ## Restart the local stack (down + up)
	docker compose down
	docker compose up --build -d

.PHONY: logs
logs: ## Tail logs from the local stack (Ctrl-C to stop)
	docker compose logs -f

.PHONY: ps
ps: ## Show status of the local stack services
	docker compose ps

# ---- Run (native, without Docker) ------------------------------------
.PHONY: backend
backend: ## Run the FastAPI backend locally (uvicorn)
	cd $(BACKEND_DIR) && uvicorn src.main:app --reload

.PHONY: frontend
frontend: ## Run the Next.js frontend locally
	cd $(FRONTEND_DIR) && pnpm dev

# ---- Database --------------------------------------------------------
.PHONY: migrate
migrate: ## Apply Alembic migrations (alembic upgrade head)
	cd $(BACKEND_DIR) && alembic upgrade head

.PHONY: migration
migration: ## Create a new migration: make migration m="message"
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(m)"

.PHONY: seed
seed: ## Seed demo companies + a demo user into the running stack's Postgres
	docker compose exec backend python -m scripts.seed

# ---- Quality ---------------------------------------------------------
.PHONY: lint
lint: ## Lint backend + frontend
	cd $(BACKEND_DIR) && ruff check . && black --check . && mypy src
	cd $(FRONTEND_DIR) && pnpm lint && pnpm exec prettier --check .

.PHONY: fmt
fmt: ## Auto-format backend + frontend
	cd $(BACKEND_DIR) && ruff check --fix . && black .
	cd $(FRONTEND_DIR) && pnpm exec prettier --write .

.PHONY: typecheck
typecheck: ## Type-check backend (mypy) + frontend (tsc)
	cd $(BACKEND_DIR) && mypy src
	cd $(FRONTEND_DIR) && pnpm exec tsc --noEmit

# ---- Workers ---------------------------------------------------------
.PHONY: worker
worker: ## Run a Celery worker locally
	cd $(BACKEND_DIR) && celery -A src.workers.celery_app worker -l info

.PHONY: beat
beat: ## Run Celery Beat scheduler locally
	cd $(BACKEND_DIR) && celery -A src.workers.celery_app beat -l info

# ---- Ops scripts -----------------------------------------------------
.PHONY: backfill
backfill: ## Backfill a ticker into Postgres + cognee: make backfill t=AAPL
	docker compose exec backend python -m scripts.backfill_ticker --ticker $(t)

.PHONY: purge
purge: ## Forget a ticker's Cognee dataset + ledger: make purge t=AAPL [keep=7]
	docker compose exec backend python -m scripts.purge_dataset --ticker $(t) --yes $(if $(strip $(keep)),--older-than-days $(keep))

# ---- Setup -----------------------------------------------------------
.PHONY: install
install: ## Install backend + frontend deps locally
	cd $(BACKEND_DIR) && pip install -e ".[dev]"
	cd $(FRONTEND_DIR) && pnpm install

.PHONY: clean
clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(BACKEND_DIR)/.pytest_cache $(BACKEND_DIR)/.mypy_cache $(BACKEND_DIR)/.ruff_cache
	rm -rf $(FRONTEND_DIR)/.next $(FRONTEND_DIR)/coverage
