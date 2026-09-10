venv:
	@echo "[1]...Creating virtual environment..."
	@python3 -m venv venv
# 	@echo "[2]...Activating virtual environment..."
	@source venv/bin/activate
	@echo "[3]...Virtual environment created and activated."

install-dep:
	@echo "[4]...Installing dependencies..."
	@pip install -r requirements.txt

postgres-startup:
	@echo "[5]...Strating Up PostgreSQL..."
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
# 	@echo "[5]...Running API..."




# run_docker_test_db:
# 	@echo "[5] ...Start Database..."
# 	docker compose up -d

# 	@echo "-Confirm if running-"
# 	docker ps

# 	@echo "-Deleting schema-"
# 	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 	@echo "-Refresh Database-"
# 	docker compose up -d --force-recreate



# 	@echo "-Apply Schema-"
# 	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse < pipeline/schema.sql
	
# 	@echo "-Populating test dimensions and fact-"
# 	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "\
# 		INSERT INTO event_time (date_key, sql_date, year, month) \
# 		VALUES (20260831, '2026-08-31', 2026, 8) \
# 		ON CONFLICT (date_key) DO NOTHING;"

# 	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "\
# 		INSERT INTO event_action_type (cameo_root_code, cameo_base_code, quad_class) \
# 		VALUES ('14', '141', 3) \
# 		ON CONFLICT (cameo_root_code, cameo_base_code, quad_class) DO NOTHING;"
	
# 	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "\
# 		INSERT INTO event_location (adm1_code, province_name, country_code) \
# 		VALUES ('SF11', 'Western Cape', 'SF') \
# 		ON CONFLICT (adm1_code) DO NOTHING;"
	
# 	docker exec -i sa-civic-pulse-db psql -U admin -d sa_civic_pulse -c "\
# 		INSERT INTO event_fact (global_event_id, date_key, location_id, event_type_id, actor1_name, avg_tone) \
# 		VALUES (1320689300, 20260831, 1, 1, 'SOUTH AFRICA', -3.737259) \
# 		ON CONFLICT (global_event_id) DO NOTHING;"