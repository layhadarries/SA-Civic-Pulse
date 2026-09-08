"""
take parquet output from transform and load into Postgres.

[1] load -  event_time      (1 row per unique date)
         -  event_location  (1 row per unique prov + fallback for country lvl event)
         -  event_action_type (1 row per unique cameo combination)

* Conflict and Mediation Event Observations

GDELT
  ↓
Extract
  ↓
Transform
  ↓
Parquet
  ↓
Load with Python
  ↓
PostgreSQL
  ↓
Query / API / Dashboard / Analysis


4 main tables in our schema

                 PostgreSQL
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
 event_time   event_location   event_action_type
       │             │             │
       └─────────────┼─────────────┘
                     ↓
                event_fact

We need to first connect to postgres using the config properties!!
Where? -> host + port
Which database? -> dbname
Who are you? -> user
Password? -> password

Why use parquet files?
It remembers data types. 
It's much smaller.
It's fast to read. 
It's the natural hand-off point between Spark and pandas. Spark writes it natively (.write.parquet(...)), pandas reads it natively (pd.read_parquet(...)) — no custom format-conversion code needed on either side. This is genuinely the standard way these two tools talk to each other in real pipelines

"""

import os
import pandas
import psycopg2 # communicate to posgresql

# helpe method for inserting many rows at once
from psycopg2.extras import execute_values


PARQUET_DIR = "data/processed/events"

PROVINCES = {
    "SF": "Unknown / National",
    "SF02": "KwaZulu-Natal",
    "SF03": "Free State",
    "SF04": "Gauteng",
    "SF05": "Eastern Cape",
    "SF06": "Gauteng",
    "SF07": "Mpumalanga",
    "SF08": "Northern Cape",
    "SF09": "Limpopo",
    "SF10": "North West",
    "SF11": "Western Cape",
}

# config from compose
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "sa_civic_pulse_db"),
    "user": os.environ.get("DB_USER", "admin"),
    "password": os.environ.get("DB_PASSWORD", "dev_password"),
}


## ---- start loading values from parquet files into posgres database ---- ##
def load_event_time():
    pass

def load_event_location():
    pass

def load_event_aciton_time():
    pass






def main():

    # [1] connect to postgresql using config vars from compose.yml
    pgsql_connect = psycopg2.connect(**DB_CONFIG)






    pass


if __name__ == "__main__":
    main()