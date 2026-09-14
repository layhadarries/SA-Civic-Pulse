# Spark dataframe transformations, schema tests
from datetime import date, datetime
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import Row

from pipeline import transform


@pytest.fixture(scope="session")
def spark_session():
    """
    Creates a single local SparkSession.
    Shut down automatically after the test finishes.
    """
    spark_session = (
        SparkSession.builder
        .master("local[1]")
        .appName("UnitTests-Transform")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.default.parallelism", "1")
        .getOrCreate()
    )

    yield spark_session
    spark_session.stop()

def example_row(**kwargs):
    dict = {
        "GLOBALEVENTID": 1001,
        "SQLDATE": "20251001",
        "MonthYear": "202510",
        "Year": 2025,
        "FractionDate": 2025.75,
        "Actor1Code": "ZAF",
        "Actor1Name": "CIVILIAN",
        "Actor1CountryCode": "SF",
        "Actor1KnownGroupCode": None,
        "Actor1EthnicCode": None,
        "Actor1Religion1Code": None,
        "Actor1Religion2Code": None,
        "Actor1Type1Code": "CVL",
        "Actor1Type2Code": None,
        "Actor1Type3Code": None,
        "Actor2Code": "GOV",
        "Actor2Name": "POLICE",
        "Actor2CountryCode": "SF",
        "Actor2KnownGroupCode": None,
        "Actor2EthnicCode": None,
        "Actor2Religion1Code": None,
        "Actor2Religion2Code": None,
        "Actor2Type1Code": "COP",
        "Actor2Type2Code": None,
        "Actor2Type3Code": None,
        "IsRootEvent": 1,
        "EventCode": "140",
        "EventBaseCode": "140",
        "EventRootCode": "14",
        "QuadClass": 3,
        "GoldsteinScale": -5.0,
        "NumMentions": 10,
        "NumSources": 2,
        "NumArticles": 10,
        "AvgTone": -2.5,
        "Actor1Geo_Type": 4,
        "Actor1Geo_FullName": "Cape Town, Western Cape, South Africa",
        "Actor1Geo_CountryCode": "SF",
        "Actor1Geo_ADM1Code": "SF11",
        "Actor1Geo_ADM2Code": "01",
        "Actor1Geo_Lat": -33.9258,
        "Actor1Geo_Long": 18.4232,
        "Actor1Geo_FeatureID": "-1229023",
        "Actor2Geo_Type": 4,
        "Actor2Geo_FullName": "Cape Town, Western Cape, South Africa",
        "Actor2Geo_CountryCode": "SF",
        "Actor2Geo_ADM1Code": "SF11",
        "Actor2Geo_ADM2Code": "01",
        "Actor2Geo_Lat": -33.9258,
        "Actor2Geo_Long": 18.4232,
        "Actor2Geo_FeatureID": "-1229023",
        "ActionGeo_Type": 4,
        "ActionGeo_FullName": "Cape Town, Western Cape, South Africa",
        "ActionGeo_CountryCode": "SF",
        "ActionGeo_ADM1Code": "SF11",
        "ActionGeo_ADM2Code": "01",
        "ActionGeo_Lat": -33.9258,
        "ActionGeo_Long": 18.4232,
        "ActionGeo_FeatureID": "-1229023",
        "DATEADDED": "20251001120000",
        "SOURCEURL": "https://news.example.com/za-protest",
    }

    dict.update(kwargs)
    return dict


# Primarily testing filter
# > country code not "SF"
def test_filter_out_invalid_country_code(spark_session):
    data = [
        example_row(GLOBALEVENTID=1, ActionGeo_CountryCode="SF"),
        example_row(GLOBALEVENTID=2, ActionGeo_CountryCode="UK")
    ]
    input_df = spark_session.createDataFrame(data, schema=transform.GDELT_COLUMN_SCHEMA)

    output_df = transform.filter(input_df)

    valid_ids = [row.global_event_id for row in output_df.collect()]
    assert valid_ids == [1]


# > SQLDATE="20251001" becomes a Date object 2025-10-01 
# > DATEADDED="20251001120000" becomes a Timestamp
def test_filter_date_and_timestamp_parsing(spark_session):
    data = [
        example_row(
            SQLDATE="20251015",
            DATEADDED="20251015083045"
        )
    ]
    input_df = spark_session.createDataFrame(data, schema=transform.GDELT_COLUMN_SCHEMA)

    output_df = transform.filter(input_df)
    row = output_df.collect()[0]

    assert row.sql_date == date(2025, 10, 15)
    assert row.month == 10
    assert row.date_added == datetime(2025, 10, 15, 8, 30, 45)


# > EventRootCode="14" maps to "Protest"; unmapped codes evaluate to None
# > our program only handles 20 codes currently
def test_filter_unmapped_codes(spark_session):
    data = [
        example_row(GLOBALEVENTID=10, EventRootCode="14"),  # Protest
        example_row(GLOBALEVENTID=30, EventRootCode="99"),  # Code outside top 20
    ]
    input_df = spark_session.createDataFrame(data, schema=transform.GDELT_COLUMN_SCHEMA)

    output_df = transform.filter(input_df)
    results = {row.global_event_id: row.category_label for row in output_df.collect()}

    assert results[10] == "Protest"
    assert results[30] is None  # Uumatched entries in spark map return NULL


# > empty_to_null: "" and whitespace " " become None (NULL)
def test_empty_or_null_values(spark_session):
    data = [Row(val=""), Row(val="   "), Row(val="Valid Name"), Row(val=None)]
    df = spark_session.createDataFrame(data)

    res_df = df.withColumn("cleaned", transform.empty_to_null("val"))
    results = [row.cleaned for row in res_df.collect()]

    assert results == [None, None, "Valid Name", None]


# > df contains only the valid column names
def test_filter_out_invalid_gdelt_column_names(spark_session):
    data = [example_row()]
    input_df = spark_session.createDataFrame(data, schema=transform.GDELT_COLUMN_SCHEMA)

    output_df = transform.filter(input_df)

    expected_columns = [
        "global_event_id", "sql_date", "year", "month", "adm1_code",
        "action_geo_full_name", "event_root_code", "event_base_code",
        "quad_class", "category_label", "actor1_name", "actor1_country",
        "actor2_name", "actor2_country", "goldstein_scale", "avg_tone",
        "num_mentions", "num_sources", "num_articles", "source_url", "date_added"
    ]
    assert output_df.columns == expected_columns