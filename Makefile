DOCKER_COMPOSE_FILE ?= docker-compose.yml
DOCKER_PROJECT ?= mega_ai
SERVICE ?=

.PHONY: install test lint typecheck run worker compose-config check
.PHONY: docker-up docker-up-build docker-build docker-down docker-stop docker-logs docker-ps docker-restart docker-exec

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy src

check: test lint typecheck compose-config

run:
	poetry run uvicorn mega_ai.main:app --reload

worker:
	poetry run python -m mega_ai.core.tasks.worker

compose-config:
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) config

docker-up:
	@echo "Starting Mega AI containers in detached mode..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) up -d

docker-up-build:
	@echo "Building and starting Mega AI containers in detached mode..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) up -d --build

docker-build:
	@echo "Building Mega AI images..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) build

docker-down:
	@echo "Stopping and removing Mega AI containers..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) down

docker-stop:
	@echo "Stopping Mega AI containers while preserving volumes..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) stop

docker-logs:
ifeq ($(SERVICE),)
	@echo "Tailing logs for all Mega AI services..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) logs -f --tail=100
else
	@echo "Tailing logs for service $(SERVICE)..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) logs -f --tail=100 $(SERVICE)
endif

docker-ps:
	@echo "Showing Mega AI container status..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) ps

docker-restart:
	@echo "Restarting Mega AI containers..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) restart

docker-exec:
ifndef SERVICE
	$(error Please provide SERVICE. Usage: make docker-exec SERVICE=api)
endif
	@echo "Opening shell in service $(SERVICE)..."
	docker compose -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_PROJECT) exec $(SERVICE) bash
