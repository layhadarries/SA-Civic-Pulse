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
It's the natural hand-off point between Spark and pandas. 
Spark writes it natively -> .write.parquet(...), 
pandas reads it natively -> pd.read_parquet(...)

— no custom format-conversion code needed on either side. 
This is genuinely the standard way these two tools talk to each other in real pipelines


-----------------------
 - EVENT FACTS table -
    global_event_id
    date_key
    location_id
    event_type_id

    actor1_name
    actor1_country
    actor2_name         
    actor2_country      

    goldstein_scale
    avg_tone
    num_mentions        
    num_sources
    num_articles

    source_url          
    date_added          
-----------------------
"""

import os
import pandas
import psycopg2 # communicate to posgresql

# helper method for inserting many rows at once
from psycopg2.extras import execute_values


## --------------------------------------------------------------- ##
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
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "dbname": os.environ.get("POSTGRES_NAME", "sa_civic_pulse"),
    "user": os.environ.get("POSTGRES_USER", "admin"),
    "password": os.environ.get("POSTGRES_PASSWORD", "dev_password"),
}
## --------------------------------------------------------------- ##

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
## --------------------------------------------------------------- ##


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
    print(f"load - EVENT TIME - {len(values)} dates")
## --------------------------------------------------------------- ##


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
    print(f"load - EVENT LOCATION - {len(values)} locations")
## --------------------------------------------------------------- ##


## ---------------------- Load Action Time ----------------------- ##
def load_event_aciton_type(connect, df):
    """
    Load unique CAMEO event combinations 

    event_action_type contains:
      X - event_type_id
        - cameo_root_code
        - cameo_base_code
        - quad_class
      X - UNIQUE NULLS NOT DISTINCT (cameo_root_code, cameo_base_code, quad_class)
    """

    rows = (
        df[["event_root_code", "event_base_code", "quad_class"]]
        .drop_duplicates()
    )

    # turn every tuple in to a list, no index or name because we have that
                # # ("02", "040", 1)
    values = list(rows.itertuples(index=False, name=None))

    sql_query = """
        INSERT INTO event_action_type (cameo_root_code, cameo_base_code, quad_class) 
        VALUES %s ON CONFLICT (cameo_root_code, cameo_base_code, quad_class) DO NOTHING
    """

    execute_sql(connect, sql_query, values)
    print(f"load - EVENT ACTION TYPE - {len(values)} event types")
## --------------------------------------------------------------- ##


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

    returns a dictionary like:
        {   ("02", "040", 1): 5,
            ("03", "030", 2): 6     }
    """

    with conn.cursor() as cur:
        cur.execute("""SELECT event_type_id, cameo_root_code, cameo_base_code, quad_class 
        FROM event_action_type""")

        return {
            (root, base, quad): type_id
            for type_id, root, base, quad in cur.fetchall()
        }

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
    print(f"load - EVENT FACT - {len(values)} rows")
## --------------------------------------------------------------- ##


def main():

    print("--- [1] --- Reading parquet files ---")
    # [1] read parquet files using pandas
    df = pandas.read_parquet(PARQUET_DIR)

    # [2] connect to postgresql using config vars from compose.yml
    pgsql_connect = psycopg2.connect(**DB_CONFIG)

    try:
        # call all the necessary functions
        load_event_time(pgsql_connect, df)
        load_event_location(pgsql_connect, df)
        load_event_aciton_type(pgsql_connect, df)

        location_id = fetch_location_ids(pgsql_connect)
        event_type_id = fetch_event_type_ids(pgsql_connect)

        print(f"Found {len(location_id)} locations.")

        print(f"Found {len(event_type_id)} event types.")

        print("\n--- [5] --- Loading event facts ---")

        load_event_fact(pgsql_connect, df, location_id, event_type_id)

    finally:
        pgsql_connect.close()
        print("\nPostgreSQL connection closed.")

    print("\n--- LOAD COMPLETE ---")


if __name__ == "__main__":
    main()
