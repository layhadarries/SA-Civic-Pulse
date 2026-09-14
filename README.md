# SA Civic Pulse

A data pipeline that tracks event and sentiment trends across South African provinces,
built from the [GDELT Project](https://www.gdeltproject.org/)'s global event database.

Built as a Data Engineering elective project to demonstrate ETL pipeline design, star
schema modelling, containerization, and CI/CD automation — using free tools and a
dataset with real South African relevance.

## What it does

GDELT scans global news coverage every 15 minutes and extracts structured "events"
(who did what to whom, where, and how the coverage read). This project filters that
firehose down to events located in South Africa, cleans and categorizes them, and
serves them through a REST API — letting you ask questions like "how is sentiment
trending in Gauteng this year?" or "what are the most common event types reported
in the Western Cape?"

## Tech stack

| Tool | Role |
|---|---|
| **GDELT** | Raw data source (free, updated every 15 minutes) |
| **PySpark** | Filters and cleans millions of global rows down to South African events |
| **Docker + Postgres** | Local data warehouse (star schema) |
| **FastAPI** | REST API serving the cleaned data |
| **GitHub Actions** | CI (tests on every push) + scheduled pipeline runs |

## Architecture

```
GDELT files (raw, HTTP)
   ↓ extract.py
data/raw/ (local, gitignored)
   ↓ transform.py (PySpark)
data/processed/ (parquet, cleaned + filtered to South Africa)
   ↓ load.py
Postgres (Docker) — star schema warehouse
   ↓ serve
FastAPI — REST endpoints
   ↑ orchestrated/scheduled by
GitHub Actions (CI on push + scheduled pipeline runs)
```

## Database schema

One row per GDELT event mention, linked to three dimension tables:

```mermaid
ER Diagram
    event_fact }o--|| event_time : occurs_on
    event_fact }o--|| event_location : happens_in
    event_fact }o--|| event_action_type : classified_as
    event_fact {
        bigint global_event_id PK
        int date_key FK
        int location_id FK
        int event_type_id FK
        text actor1_name
        text actor2_name
        double avg_tone
        double goldstein_scale
    }
    event_time {
        int date_key PK
        date sql_date
        int year
        int month
    }
    event_location {
        int location_id PK
        text adm1_code
        text province_name
        text country_code
    }
    event_action_type {
        int event_type_id PK
        text cameo_root_code
        text cameo_base_code
        int quad_class
        text category_label
    }
```

## Environment variables

The project reads its database credentials from a `.env` file at the project root
(used by both `compose.yml` and the Python scripts). Copy the template and
adjust if needed:

```bash
cp .env.example .env
```

.env should contain:

POSTGRES_HOST=localhost
POSTGRES_PORT=5050
POSTGRES_DB=sa_civic_pulse
POSTGRES_USER=admin
POSTGRES_PASSWORD=db_password

## Getting masterfilelist.txt

`extract.py` reads from a file called `masterfilelist.txt`, which is GDELT's own
index of every 15-minute data file it has ever published. This must be downloaded manually due to how large the file is, it's a one-time manual step:

1. Go to [gdeltproject.org/data.html#rawdatafiles](https://www.gdeltproject.org/data.html#rawdatafiles)
2. Under the GDELT 2.0 section, click **"Master CSV Data File List – English"**
3. Save the file as `masterfilelist.txt` in the **project root** (same folder as this README)

Or, directly from a terminal:
```bash
curl -o masterfilelist.txt http://data.gdeltproject.org/gdeltv2/masterfilelist.txt
```

This file is large (tens of MB) and updates every 15 minutes on GDELT's side, so
it's gitignored rather than committed — re-download it if it's ever missing or you
want the most current file listing.

## How to run it

**Prerequisites:** Docker, Python 3.10+, Java 17 (required by PySpark).

# 1. Set up and activate your environment file
```bash
cp .env.example .env
source venv/bin/activate
```

# 2. Create the virtual environment and install dependencies
```bash
make install
```

# 3. Start Postgres and apply the schema
```bash
make db-setup
make add-schema
```

# 4. Run the pipeline (extract -> transform -> load)
```bash
make run-pipeline
```

# 5. Run the API
```bash
venv/bin/uvicorn api.main:app --reload
```

Then visit `http://localhost:8000/docs` for interactive API documentation.

Other useful commands:
```bash
make run-test    # run the test suite
make db-reset    # wipe and reapply the schema (careful -- deletes all loaded data)
make db-stop     # stop the Postgres container
make clean       # remove downloaded/processed data files
make help        # list all available commands
```

## Why these choices

**Why Spark, not pandas.** Several free South African datasets were considered first
(Municipal Money, SAPS crime stats, EskomSePush). Municipal Money in particular is a
clean, current, real API — but at tens of thousands of rows, using Spark on it would
be over-engineering for the sake of it. GDELT is different: a single week of raw
files here totals ~740,000 global rows, of which South Africa makes up roughly
0.5–0.9%. Scaled to a full year, that's tens of millions of global rows Spark has to
filter through to extract a South Africa-specific dataset — genuine justification
for a distributed processing tool, not just a checkbox technology.

**Why a star schema over a single flat table.** Event type (CAMEO codes) and location
(province) are both repeated heavily across events — storing them as lookup tables
instead of repeating text on every row keeps the fact table lean and makes filtering
by province or category a straightforward join rather than a text match.

**Why the location dimension uses FIPS codes, not ISO.** GDELT encodes country and
province using FIPS 10-4 codes, not ISO — South Africa is `SF`, not `ZA`. Verified
directly against the GDELT Event Database Codebook and confirmed against real
downloaded data before building the schema around it.

## Known limitations

- **Duplicate event mentions.** GDELT records one row per article, not one row per
  real-world event — multiple articles covering the same incident produce multiple
  rows with near-identical fields. This project does not attempt to deduplicate
  these (see the project's GitLab issue tracker for the full reasoning); the schema
  keys on the raw `global_event_id`, so a "number of events" count reflects article
  volume, not necessarily distinct real-world incidents. Sentiment/tone trends are
  less affected by this, since duplicate rows for the same event carry similar tone.

- **Geocoding granularity varies.** Roughly 20% of South African rows only resolve
  to country level (no specific province), rather than city or province level. These
  are represented in `event_location` as a fallback `'SF'` / "Unknown / National"
  row rather than dropped.

- **Not all "South Africa" rows are domestic South African news.** GDELT tags events
  by where they're geographically referenced, not strictly where the story is "about."
  A small number of rows are global stories (e.g. international relations coverage)
  that happen to mention South Africa.