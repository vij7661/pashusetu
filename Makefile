.PHONY: up down test lint migrate revision

up:
	docker compose up --build

down:
	docker compose down

test:
	docker compose exec api pytest

lint:
	docker compose exec api ruff check app tests

migrate:
	docker compose exec api alembic upgrade head

revision:
	docker compose exec api alembic revision --autogenerate -m "$(m)"


seed:
	docker compose exec api python -m app.db.seed

openapi:
	docker compose exec api python scripts/export_openapi.py

integration:
	docker compose exec api pytest tests/integration -q
