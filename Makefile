.PHONY: help dev migrate seed test clean build up down logs

help:
	@echo "DevOps Automation UI - Available commands:"
	@echo "  make dev      - Start development environment"
	@echo "  make migrate  - Run database migrations"
	@echo "  make seed     - Seed database with demo data"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start services"
	@echo "  make down     - Stop services"
	@echo "  make logs     - View logs"

dev:
	docker-compose up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "Running migrations..."
	@cd apps/api && python -m alembic upgrade head || (cd ../..; docker-compose run --rm api alembic upgrade head)
	@echo "Starting services..."
	docker-compose up api

migrate:
	docker-compose run --rm api alembic upgrade head

seed:
	docker-compose run --rm api python apps/api/seed.py

test:
	docker-compose run --rm api pytest apps/api/tests -v --cov=apps/api

clean:
	docker-compose down -v
	rm -rf apps/web/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f
