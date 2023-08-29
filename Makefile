# Makefile for setting up PostgreSQL container and starting Django app

activate:
	pipenv shell
	
run:
	python app/manage.py runserver 0.0.0.0:8000

make_migrations:
	python app/manage.py makemigrations

migrate:
	python app/manage.py migrate

createsuperuser:
	python app/manage.py createsuperuser

db_configure:
	@echo "Configuring database..."
	@echo "DATABASE_URL=postgres://postgres:postgres@localhost:5432/dividitto" > .env

db_start:
	@echo "Setting up Django app..."
	docker compose docker-compose-dev.yml up -d

db_purge:
	@echo "Deleting Django DB..."
	docker compose docker-compose-dev.yml stop db
	docker compose docker-compose-dev.yml rm -f db
	sudo rm -rf pg_data
	docker compose docker-compose-dev.yml up -d

db_ps:
	@echo "Setting up Django app..."
	docker compose docker-compose-dev.yml ps

db_logs:
	@echo "Setting up Django app..."
	docker compose docker-compose-dev.yml logs --tail=100 -f db

help:
	@echo "Available targets:"
	@echo "  - run: start Django app"
	@echo "  - db_configure: configure database"
	@echo "  - db_start: start PostgreSQL container"
	@echo "  - db_ps: check db status"
	@echo "  - db_logs: check db logs"

# Default target
.DEFAULT_GOAL := help
