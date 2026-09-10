VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Create the venv only if the folder doesn't already exist
$(VENV):
	@echo "[1]...Creating virtual environment..."
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip

install: $(VENV)
	@echo "[2]...Installing dependencies..."
	@$(PIP) install -r requirements.txt

test:
	@echo "[2]...Running test files..."

postgres-startup:
	@echo "[5]...Strating up PostgreSQL..."
	docker compose up -d

	@echo "...Applying Schema..."
	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse < pipeline/schema.sql

run-pipeline:
	@echo "[6]...Load Raw GDELT files..."
	# python windows || python3 linux
	python3 pipeline/extract.py
	
	@echo "[7]...Clean and Filter Data..."
	python3 pipeline/transform.py
	
	@echo "[8]...Load data into PostgreSQL Database..."
	python3 pipeline/load.py

# run-api:
# 	@echo "[9]...Running API..."

run_docker_test_db:
	@echo "[1] ...Start Database..."
	docker compose up -d

	@echo "---Confirm if running---"
	docker ps

	@echo "---Resetting Schema---"
	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

	@echo "---Apply Schema DDL---"
	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse < pipeline/schema.sql

	@echo "---Load Parquet into Postgres---"
	venv/bin/python pipeline/load.py

	@echo "---Row Counts Across Tables---"
	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "\
		SELECT 'event_time' AS tbl, COUNT(*) FROM event_time \
		UNION ALL \
		SELECT 'event_location', COUNT(*) FROM event_location \
		UNION ALL \
		SELECT 'event_action_type', COUNT(*) FROM event_action_type \
		UNION ALL \
		SELECT 'event_fact', COUNT(*) FROM event_fact;"

	@echo "---Verify Foreign Key Joins---"
	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "\
		SELECT \
			f.global_event_id, \
			t.sql_date, \
			l.province_name, \
			a.cameo_root_code, \
			f.actor1_name, \
			f.goldstein_scale \
		FROM event_fact f \
		JOIN event_time t ON f.date_key = t.date_key \
		JOIN event_location l ON f.location_id = l.location_id \
		JOIN event_action_type a ON f.event_type_id = a.event_type_id \
		LIMIT 5;"