# -- EXPECTED ORDER --
# make db-reset
#      ↓
# Empty database
#      ↓
# Apply schema
#      ↓
# make run-pipeline
#      ↓
# Extract → Transform → Load

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: $(VENV) install run-test db-startup run-pipeline clean db-stop run-api clean db-reset help

# Create the venv only if the folder doesn't already exist
$(VENV):
	@echo "[1]...Creating virtual environment..."
	@python3.12 -m venv $(VENV)
	@$(PIP) install --upgrade pip setuptools wheel

install: $(VENV)
	@echo "[2]...Installing dependencies..."
	@$(PIP) install -r requirements.txt

run-test:
	@echo "[2]...Running test files..."
	@$(PYTHON) -m pytest tests/ -v

db-setup:
	@echo "[5]...Strating up PostgreSQL..."
	docker compose up -d

	@echo "...Applying Schema..."
	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse < sql/schema.sql

run-pipeline:
	@echo "[6]...Load Raw GDELT files..."
	@$(PYTHON) pipeline/extract.py
	
	@echo "[7]...Clean and Filter Data..."
	@$(PYTHON) pipeline/transform.py
	
	@echo "[8]...Load data into PostgreSQL Database..."
	@$(PYTHON) pipeline/load.py

# db-stop:
# 	@echo "...Stopping PostgreSQL..."
# 	@docker compose down

# run-api:
# 	@echo "[9]...Running API..."


# DO NOT USE
clean:
	@echo "-X Remove whatever files created or downloaded - for a clean repo X-"
# 	rm -rf $(VENV)
	rm -rf data/raw/*.CSV
	rm -rf data/processed/events/*

db-reset:
	@echo "...Resetting database..."
	@docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@echo "...Applying schema..."
	@docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse < sql/schema.sql


help:
	@echo "Available commands:"
	@echo "  make install          Install Python dependencies"
	@echo "  make run-test         Run tests"
	@echo "  make postgres-startup Start PostgreSQL"
	@echo "  make postgres-stop    Stop PostgreSQL"
	@echo "  make run-pipeline     Run ETL pipeline"
	@echo "  make clean            Remove generated files"