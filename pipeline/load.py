"""
load.py — Dimensional Loading Layer for SA Civic Pulse

Ingests cleaned and transformed GDELT events from columnar Parquet storage,
populates dimensional entities (time, location, action types), resolves
surrogate foreign keys, and appends records into the primary fact table.

Input:  data/processed/events/ (Parquet format)
Output: PostgreSQL relational star schema (event_fact, dimensions)
Core Responsibilities:
1. Ingest processed Parquet events into an in-memory Pandas DataFrame.
2. Upsert the time dimension (event_time) indexed by integer date keys (YYYYMMDD).
3. Upsert the geographic dimension (event_location) with GDELT ADM1 codes and fallback values.
4. Upsert the taxonomy dimension (event_action_type) using unique CAMEO code combinations.
5. Query surrogate primary keys from dimensions to map relational foreign key dependencies.
6. Clean, align, and load core event observations into the central fact table (event_fact).
7. Ensure idempotent execution across all load targets via ON CONFLICT DO NOTHING clauses.
"""

import os
import pandas
import psycopg2 # communicate to posgresql

# helper method for inserting many rows at once
from psycopg2.extras import execute_values

from dotenv import load_dotenv



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

load_dotenv()

# Postgres config
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


## ----------------------- helper methods ------------------------ ##
def execute_sql(connect, sql_query, values):
    """
    Execute an INSERT query containing multiple rows.

    connect:
        active PostgreSQL connection

    sql_query:
        SQL statement containing VALUES %s

    values:
        list of rows to insert
    """
    # cursor sends commands
    with connect.cursor() as cursor:
        # execute_values faster than execute, sends may rows
        execute_values(cursor, sql_query, values)

     # makes changes permanent
    connect.commit()


## ----------------------- Load Event Time ----------------------- ##
##  start loading values from parquet files into posgres database  ##
def load_event_time(connect, df):
    """
    Load unique event dates into event_time table in db.

    event_time contains:
        - date_key
        - sql_date
        - year
        - month
    """
    # make sure sql_date is actually a pandas datetime
    df["sql_date"] = pandas.to_datetime(df["sql_date"])

    # we only need one row for each unique date
    rows = ( # create int datekey : 2026-08-31 -> 20260831
        df[["sql_date", "year", "month"]]
        .drop_duplicates()
        .assign(date_key=lambda d: d["sql_date"]
        .dt.strftime("%Y%m%d")
        .astype(int))
    )  

    # convert the DataFrame rows into tuples
    values = list( 
            # (20260831,  2026-08-31, 2026,      8)
        rows[["date_key", "sql_date", "year", "month"]]
        .itertuples(index=False, name=None)
    )

    sql_query = """
        INSERT INTO event_time (date_key, sql_date, year, month) 
        VALUES %s ON CONFLICT (date_key) DO NOTHING
    """

    execute_sql(connect, sql_query, values)


## -------------------- Load Event Location ---------------------- ##
def load_event_location(connect, df):
    """
    Load unique event locations into event_location in db.
    GDELT gives us the ADM1 code.
    eg. SF11 -> Western Cape
    SF is used as our fallback for country-level events.


    event_location contains:
        - location_id
        - adm1_code
        - province_name
        - country_code
    """

    # get every unique ADM1 code from parquet data.
    codes = set(df["adm1_code"].dropna().unique())

    # !! make sure fallback location exists
    # even if this batch has no country-level rows
    codes.add("SF")

    # convert codes into rows for postgres
    values = [
      # ("SF11", "Western Cape",          "SF")
        (code, PROVINCES.get(code, code), "SF") 
        for code in codes
        ]

    sql_query = """
        INSERT INTO event_location (adm1_code, province_name, country_code) 
        VALUES %s ON CONFLICT (adm1_code) DO NOTHING
    """

    execute_sql(connect, sql_query, values)


## ---------------------- Load Action Time ----------------------- ##
def load_event_aciton_type(connect, df):
    """
    Load unique CAMEO event combinations 

    event_action_type contains:
      X - event_type_id
        - cameo_root_code
        - cameo_base_code
        - quad_class
        - category_label
      X - UNIQUE NULLS NOT DISTINCT (cameo_root_code, cameo_base_code, quad_class)
    """

    rows = (
        df[["event_root_code", "event_base_code", "quad_class", "category_label"]]
        .drop_duplicates()
    )

    # turn every tuple in to a list, no index or name because we have that
                # # ("02", "040", 1)
    values = list(rows.itertuples(index=False, name=None))

    sql_query = """
        INSERT INTO event_action_type (cameo_root_code, cameo_base_code, quad_class, category_label) 
        VALUES %s ON CONFLICT (cameo_root_code, cameo_base_code, quad_class) DO NOTHING
    """

    execute_sql(connect, sql_query, values)


## ------------- helper methods for Load Event Time -------------- ##
def fetch_location_ids(conn):
    """
    Get foreign key id from event_location
    returns a dictionary like:
        {   "SF": 1, 
            "SF11": 2, 
            "SF09": 3   }
    """

    with conn.cursor() as cur:
        cur.execute("SELECT location_id, adm1_code FROM event_location")
        return {adm1_code: location_id for location_id, adm1_code in cur.fetchall()}

 
def fetch_event_type_ids(conn):
    """
    Get foreign key id from event_action_type
    """

    with conn.cursor() as cur:
        cur.execute("""SELECT event_type_id, cameo_root_code, cameo_base_code, quad_class 
        FROM event_action_type""")

        return {
            (root, base, quad): type_id
            for type_id, root, base, quad in cur.fetchall()
        }


def fetch_event_time_ids(conn):
    """
    Get the count of total date_key's from event_time table
    """

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(date_key) FROM event_time")
        result = cur.fetchone()
        return result[0] if result else 0


def fetch_event_fact(conn):
    """
    Get the count of total global_event_id's from event_time table
    """

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(global_event_id) FROM event_fact")
        result = cur.fetchone()
        return result[0] if result else 0

 

## ----------------------- Load Event Time ----------------------- ##
def load_event_fact(connect, df, location_id_key, event_type_id_key):
    '''
    Load event observations into event_fact table in db

    event_fact contains:
   > date_key       -> event_time
   > location_id    -> event_location (foreign key = taken from event_location)
   > event_type_id  -> event_action_type (foreign key = taken from event_action_type)
    '''

    # !! make a copy of db incase we accidentally modify the df
    df = df.copy()

    # --- date_key ---
    df["date_key"] = (
        pandas.to_datetime(df["sql_date"])
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    # --- location_id ---
    # convert SF11 into 8 -> represents adm1_code
    df["location_id"] = (
        df["adm1_code"]
        .fillna("SF")
        .map(location_id_key)
    )

    # --- event_type_id ---
    # convert the CAMEO combination into the generated event_type_id
    df["event_type_id"] = df.apply(
        lambda row: event_type_id_key.get(
            (
                row["event_root_code"],
                row["event_base_code"],
                row["quad_class"]
            )
        ),
        axis=1
    )

    # -- fact table columns (taken from transform AFTER loading into db)
    fact_columns = [
        "global_event_id",
        "date_key",
        "location_id",
        "event_type_id",
        "actor1_name",
        "actor1_country",
        "actor2_name",
        "actor2_country",
        "goldstein_scale",
        "avg_tone",
        "num_mentions",
        "num_sources",
        "num_articles",
        "source_url",
        "date_added",
    ]
    # Convert NaN to None so psycopg2 inserts SQL NULL instead of invalid floats
    clean_df = df[fact_columns].astype(object).where(pandas.notnull(df[fact_columns]), None)

    # convert the df into tuples
    values = list(
        clean_df.itertuples(
            index=False,
            name=None
        )
    )

    sql_query = f"""
        INSERT INTO event_fact ({", ".join(fact_columns)})
        VALUES %s ON CONFLICT (global_event_id) DO NOTHING
    """

    execute_sql(connect, sql_query, values)



def main():
    print("\n[3/3] LOAD — writing to Postgres")

    # [1] read parquet files using pandas
    df = pandas.read_parquet(PARQUET_DIR)

    # [2] connect to postgresql using config vars from compose.yml
    pgsql_connect = psycopg2.connect(**DB_CONFIG)

    # [3] Run load process
    try:
        load_event_time(pgsql_connect, df)
        load_event_location(pgsql_connect, df)
        load_event_aciton_type(pgsql_connect, df)

        location_id = fetch_location_ids(pgsql_connect)
        event_type_id = fetch_event_type_ids(pgsql_connect)

        load_event_fact(pgsql_connect, df, location_id, event_type_id)

        event_date_max = fetch_event_time_ids(pgsql_connect)
        event_fact_max = fetch_event_fact(pgsql_connect)
        
        print(f" ✓ Found {event_date_max} event time dates.")
        print(f" ✓ Found {len(location_id)} event locations.")
        print(f" ✓ Found {len(event_type_id)} event types.")
        print(f" ✓ Found {event_fact_max} event fact rows.\n")
        print("======================================")
    finally:
        pgsql_connect.close()


if __name__ == "__main__":
    main()