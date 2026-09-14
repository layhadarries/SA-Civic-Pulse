# DB_CONFIG = {
#     "host": os.environ.get("DB_HOST", "localhost"),
#     "port": os.environ.get("DB_PORT", "5432"),
#     "dbname": os.environ.get("DB_NAME", "sa_civic_pulse"),
#     "user": os.environ.get("DB_USER", "admin"),
#     "password": os.environ.get("DB_PASSWORD", "dev_password"),
# }


"""
main.py

The API layer. currently 1 endpoint, just a Python function that runs a
SQL query and returns the result -- FastAPI handles turning that into JSON.

endpoints:
    1) /docs
    2) [GET] :
        3.1) -> /
        3.2) -> /docs *** Fast Api automatically creates this
        3.3) -> /events         	A list of individual events

        3.4) -> /event-types/top	Which CAMEO categories occur most
        3.5) -> /sentiment/trend	Average tone per month, optionally per-province

How to run:
    uvicorn api.main:app --reload
Then visit http://localhost:8000/docs for interactive docs (auto-generated, free).

"""

import os
from datetime import date
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, Query

app = FastAPI(title="SA Civic Pulse API")

# TODO: create documentation for api !!
# TODO: http code response failure handlers !!S

# TODO: Make this reusable. infact make this as posgres start up reusable (aka turn into a class)
## CONFIG
# config from compose
DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "dbname": os.environ.get("POSTGRES_NAME", "sa_civic_pulse"),
    "user": os.environ.get("POSTGRES_USER", "admin"),
    "password": os.environ.get("POSTGRES_PASSWORD", "dev_password"),
}


## ----------------------- helper methods ------------------------ ##
def run_query(sql, params=None):
    """Run a SELECT and return a list of plain dictionaries -- one per row."""

    # POSGRES CONNECT start up
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()
## --------------------------------------------------------------- ##

# -> http://localhost:8000/
@app.get("/")
def root():
    return {"message": "SA Civic Pulse API -- see /docs for available endpoints"}


# -> http://localhost:8000/events
@app.get("/events")
def get_events(
    province: Optional[str] = Query(None, description="Province name, e.g. 'Western Cape'"),
    start_date: Optional[date] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(50, le=500, description="Max rows to return"),
):
    """Events filtered by province and/or date range."""
    conditions = []
    params = []

    if province:
        conditions.append("loc.province_name = %s")
        params.append(province)
    if start_date:
        conditions.append("t.sql_date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("t.sql_date <= %s")
        params.append(end_date)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql = f"""
        SELECT f.global_event_id, t.sql_date, loc.province_name,
               et.category_label, f.actor1_name, f.actor2_name,
               f.avg_tone, f.goldstein_scale, f.source_url
        FROM event_fact f
        JOIN event_time t ON f.date_key = t.date_key
        JOIN event_location loc ON f.location_id = loc.location_id
        JOIN event_action_type et ON f.event_type_id = et.event_type_id
        {where_clause}
        ORDER BY t.sql_date DESC
        LIMIT %s
    """
    params.append(limit)

    return run_query(sql, params)

# @app.get("??") 