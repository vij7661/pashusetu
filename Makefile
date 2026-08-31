.PHONY: up down test lint migrate revision seed farmer-qa-seed openapi integration

up:
	docker compose up --build

down:
	docker compose down

test:
	docker compose exec api pytest

lint:
	docker compose exec api ruff check app tests scripts

migrate:
	docker compose exec api alembic upgrade head

revision:
	docker compose exec api alembic revision --autogenerate -m "$(m)"

seed:
	docker compose exec api python -m app.db.seed

farmer-qa-seed:
	docker compose exec api python scripts/seed_farmer_manual_qa.py

openapi:
	docker compose exec api python scripts/export_openapi.py

integration:
	docker compose exec api pytest tests/integration -q
