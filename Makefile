.PHONY: up down logs build api-shell web-shell migrate revision lint format typecheck test pre-commit-install

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

api-shell:
	docker compose exec api bash

web-shell:
	docker compose exec web sh

migrate:
	docker compose exec api uv run alembic upgrade head

revision:
	docker compose exec api uv run alembic revision --autogenerate -m "$(name)"

lint:
	docker compose exec api uv run ruff check src tests
	pnpm lint

format:
	docker compose exec api uv run ruff format src tests
	docker compose exec api uv run black src tests

typecheck:
	docker compose exec api uv run mypy src
	pnpm typecheck

test:
	docker compose exec api uv run pytest
	pnpm test:web

pre-commit-install:
	pre-commit install
