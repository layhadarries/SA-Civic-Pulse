-include .env
export 


VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
CONTAINER_NAME := sa-civic-pulse-db
SCHEMA := resources/schema.sql

.PHONY: install run-test db-setup add-schema run-pipeline db-stop clean docker-clean db-reset help


install:
	@echo "...Installing dependencies..."
	@$(PIP) install -r requirements.txt

run-test:
	@echo "...Running test files..."
	@$(PYTHON) -m pytest tests/ -v

# -------------- Docker and PostgreSQL --------------
db-setup:
	@echo "...Starting up PostgreSQL container..."
	@docker compose up -d db

add-schema: db-setup
	@echo "...Applying Schema..."
	@docker exec -i $(CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) < $(SCHEMA)
	
	@echo "...Schema applied successfully."

# ETL pipeline
run-pipeline:
	@$(PYTHON) pipeline/extract.py
	@$(PYTHON) pipeline/transform.py
	@$(PYTHON) pipeline/load.py

db-stop:
	@echo "...Stopping PostgreSQL..."
	@docker compose down

db-reset: db-setup
	@echo "...Resetting database..."
	@docker exec -i $(CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	
	@echo ""...Refresh Database"..."
	docker compose up -d --force-recreate

	@echo "...Applying schema..."
	@docker exec -i $(CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) < $(SCHEMA)

# ----------------------- API -----------------------

run-api:
	@echo "...Running API..."
	$(VENV)/bin/uvicorn api.main:app --reload

#----------------------------------------------------

clean:
	@echo "-X Remove v env, data from GDELT, remove schema, recreate db X-"
	rm -rf $(VENV)
	rm -rf data/raw/*.CSV
	rm -rf data/processed/events/*
	docker exec -i $(CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	docker compose up -d --force-recreate

docker-clean:
	@echo "-X Remove sa-sivic-pulse-db X-"
	docker rm -f sa-civic-pulse-db

help:
	@echo "Available commands:"
	@echo "  make install          Install Python dependencies"
	@echo "  make run-test         Run tests"
	@echo "  make postgres-startup Start PostgreSQL"
	@echo "  make postgres-stop    Stop PostgreSQL"
	@echo "  make run-pipeline     Run ETL pipeline"
	@echo "  make clean            Remove generated files"
	@echo "  make docker-clean     Remove database from container"