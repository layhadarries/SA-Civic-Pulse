-- look at the GDELT Event Cookbook for more fields
-- do we need religious affiliation?

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- -----------------------
--   EVENT INFO tables
-- -----------------------

-- time of event
CREATE TABLE IF NOT EXISTS event_time (
    date_key    INT PRIMARY KEY,    -- SQLDATE as an int [ 20260831 ]
    sql_date    DATE NOT NULL,      -- SQLDATE [ 2026-08-31 ]
    year        INT NOT NULL,       -- SQLDATE (year taken from SQLDATE)
    month       INT NOT NULL       -- SQLDATE (month taken from SQLDATE)
);

-- location of event
CREATE TABLE IF NOT EXISTS event_location (
    location_id     SERIAL PRIMARY KEY,         -- ! (INTEGER PRIMARY KEY AUTOINCREMENT in sqlite)
    adm1_code       TEXT UNIQUE NOT NULL,       -- ActionGeo_ADM1Code (the authoritative field) [ SF11 ]
    province_name   TEXT,                       -- ! we're going to have to determine this ourselves
    country_code    TEXT NOT NULL DEFAULT 'SF'  -- ActionGeo_CountryCode (SA code is SF in GDELT)
);

-- type of event
CREATE TABLE IF NOT EXISTS event_action_type (
    event_type_id     SERIAL PRIMARY KEY,           -- ! (INTEGER PRIMARY KEY AUTOINCREMENT in sqlite)
    cameo_root_code   TEXT NOT NULL,                -- EventRootCode [ 02 ]
    cameo_base_code   TEXT NOT NULL DEFAULT '',     -- EventBaseCode [ 040 ]
    quad_class        INT,                          -- QuadClass [ 1-4 in Verbal Cooperation, Material Cooperation, Verbal Conflict, and Material Conflict]
    UNIQUE NULLS NOT DISTINCT (cameo_root_code, cameo_base_code, quad_class)
);


-- -----------------------
--    EVENT FACTS table
-- -----------------------

CREATE TABLE event_fact (
    global_event_id     BIGINT PRIMARY KEY, -- GLOBALEVENTID [ 1320689300 ]
    date_key            INT NOT NULL REFERENCES event_time (date_key),
    location_id         INT NOT NULL REFERENCES event_location (location_id),
    event_type_id       INT NOT NULL REFERENCES event_action_type (event_type_id),

    actor1_name         TEXT,       -- Actor1Name [ SOUTH AFRICA ]
    actor1_country      TEXT,       -- Actor1CountryCode -- NOTE: different code scheme to ActionGeo ('SAF', not FIPS 'SF')
    actor2_name         TEXT,       -- Actor2Name, e.g. 'POLICE' (can be blank -- normal)
    actor2_country      TEXT,       -- Actor2CountryCode (can be blank -- normal)

    goldstein_scale     DOUBLE PRECISION,   -- GoldsteinScale, theoretical impact score, -10 to +10 -> e.g -5.0
    avg_tone            DOUBLE PRECISION,   -- AvgTone, actual article sentiment, -100 to +100 -> e.g -3.737259
    num_mentions        INT,                -- NumMentions [ 4 ]
    num_sources         INT,                -- NumSources [ 2 ]
    num_articles        INT,                -- NumArticles [ 4 ]

    source_url          TEXT,               -- SOURCEURL [ 'https://www.iol.co.za/news/- ]
    date_added          TIMESTAMPTZ         -- DATEADDED [ 20260831070000 -> 2026-08-31 07:00:00 ]
);


-- -----------------------
--        INDEXES
-- -----------------------
CREATE INDEX idx_fact_event_date_key ON event_fact (date_key);
CREATE INDEX idx_fact_event_location_id ON event_fact (location_id);
CREATE INDEX idx_fact_event_event_type_id ON event_fact (event_type_id);