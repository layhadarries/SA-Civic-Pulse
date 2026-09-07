"""
------------------------------------------------------------------------------------
1] READ     -- load all the raw CSVs into one big Spark DataFrame
2] FILTER   -- keep only South African rows
3] WRITE    -- keep only the columns we actually care about
            -- compute new columns from existing ones (date parts, category labels)
            -- save the result as parquet
------------------------------------------------------------------------------------
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType, IntegerType, FloatType

from pyspark.sql import functions as func

# !! get columns
COLUMN_NAMES = [
    "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode",
    "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code",
    "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
    "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code",
    "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass",
    "GoldsteinScale", "NumMentions", "NumSources", "NumArticles", "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat", "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat", "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL",
]

# !! maunally set the schema attributes with:
# "name", "data_type", "null" (True for optional, False for mandatory)
GDELT_COLUMN_SCHEMA = StructType([
    StructField("GLOBALEVENTID", LongType(), True),
    StructField("SQLDATE", StringType(), True),
    StructField("MonthYear", StringType(), True),
    StructField("Year", IntegerType(), True),
    StructField("FractionDate", FloatType(), True),
    StructField("Actor1Code", StringType(), True),
    StructField("Actor1Name", StringType(), True),
    StructField("Actor1CountryCode", StringType(), True),
    StructField("Actor1KnownGroupCode", StringType(), True),
    StructField("Actor1EthnicCode", StringType(), True),
    StructField("Actor1Religion1Code", StringType(), True),
    StructField("Actor1Religion2Code", StringType(), True),
    StructField("Actor1Type1Code", StringType(), True),
    StructField("Actor1Type2Code", StringType(), True),
    StructField("Actor1Type3Code", StringType(), True),
    StructField("Actor2Code", StringType(), True),
    StructField("Actor2Name", StringType(), True),
    StructField("Actor2CountryCode", StringType(), True),
    StructField("Actor2KnownGroupCode", StringType(), True),
    StructField("Actor2EthnicCode", StringType(), True),
    StructField("Actor2Religion1Code", StringType(), True),
    StructField("Actor2Religion2Code", StringType(), True),
    StructField("Actor2Type1Code", StringType(), True),
    StructField("Actor2Type2Code", StringType(), True),
    StructField("Actor2Type3Code", StringType(), True),
    StructField("IsRootEvent", IntegerType(), True),
    StructField("EventCode", StringType(), True),
    StructField("EventBaseCode", StringType(), True),
    StructField("EventRootCode", StringType(), True),
    StructField("QuadClass", IntegerType(), True),
    StructField("GoldsteinScale", FloatType(), True),
    StructField("NumMentions", IntegerType(), True),
    StructField("NumSources", IntegerType(), True),
    StructField("NumArticles", IntegerType(), True),
    StructField("AvgTone", FloatType(), True),
    StructField("Actor1Geo_Type", IntegerType(), True),
    StructField("Actor1Geo_FullName", StringType(), True),
    StructField("Actor1Geo_CountryCode", StringType(), True),
    StructField("Actor1Geo_ADM1Code", StringType(), True),
    StructField("Actor1Geo_ADM2Code", StringType(), True),
    StructField("Actor1Geo_Lat", FloatType(), True),
    StructField("Actor1Geo_Long", FloatType(), True),
    StructField("Actor1Geo_FeatureID", StringType(), True),
    StructField("Actor2Geo_Type", IntegerType(), True),
    StructField("Actor2Geo_FullName", StringType(), True),
    StructField("Actor2Geo_CountryCode", StringType(), True),
    StructField("Actor2Geo_ADM1Code", StringType(), True),
    StructField("Actor2Geo_ADM2Code", StringType(), True),
    StructField("Actor2Geo_Lat", FloatType(), True),
    StructField("Actor2Geo_Long", FloatType(), True),
    StructField("Actor2Geo_FeatureID", StringType(), True),
    StructField("ActionGeo_Type", IntegerType(), True),
    StructField("ActionGeo_FullName", StringType(), True),
    StructField("ActionGeo_CountryCode", StringType(), True),
    StructField("ActionGeo_ADM1Code", StringType(), True),
    StructField("ActionGeo_ADM2Code", StringType(), True),
    StructField("ActionGeo_Lat", FloatType(), True),
    StructField("ActionGeo_Long", FloatType(), True),
    StructField("ActionGeo_FeatureID", StringType(), True),
    StructField("DATEADDED", StringType(), True),
    StructField("SOURCEURL", StringType(), True),
])

# !! path of csv files
RAW_DIR = "data/raw/*.export.CSV"

# !! where we're saving extracted and processed data
OUTPUT_DIR = "data/processed/events"

# !! event catagories taken from GDELT event cookbook 
#    **used for "topics" in schema - basically for more analytics
#    only the first 20 for now
CAMEO_EVENT_CODES = {
# CAMEOEVENTCODE : EVENTDESCRIPTION
    "01": "Make Public Statement",
    "02": "Appeal",
    "03": "Express Intent to Cooperate",
    "04": "Consult",
    "05": "Engage in Diplomatic Cooperation",
    "06": "Engage in Material Cooperation",
    "07": "Provide Aid",
    "08": "Yield",
    "09": "Investigate",
    "10": "Demand",
    "11": "Disapprove",
    "12": "Reject",
    "13": "Threaten",
    "14": "Protest",
    "15": "Exhibit Force Posture",
    "16": "Reduce Relations",
    "17": "Coerce",
    "18": "Assault",
    "19": "Fight",
    "20": "Use Unconventional Mass Violence",
}


# ===============================
def read(spark_session):
    # built in method! :)
    df = spark_session.read.csv(
        RAW_DIR, 
        sep="\t",
        header=False,
        schema=GDELT_COLUMN_SCHEMA
    )

    return df
# ===============================

# ===============================
def filter(df_read):
    # filter for south african events only "SF" -> ActionGeo_CountyCode
    # sa_rows = df[df["ActionGeo_CountryCode"] == "SF"] <- from example
    df_filtered = df_read.filter(func.col("ActionGeo_CountryCode") == "SF")

    # ----------------------------------------------------------
    df_filtered = df_filtered.withColumn(
        "sql_date", func.to_date(func.col("SQLDATE"), "yyyyMMdd")
    ).withColumn(
        "month", func.month(func.col("sql_date"))
    ).withColumn(
        "quarter", func.quarter(func.col("sql_date"))
    ).withColumn(
        "date_added_ts", func.to_timestamp(func.col("DATEADDED"), "yyyyMMddHHmmss")
    )
 
    # Map EventRootCode -> category_label using the CAMEO lookup above
    # func.create_map turns a Python dict into something Spark can use inside a column expression
    mapping_expr = func.create_map([func.lit(x) for pair in CAMEO_EVENT_CODES.items() for x in pair])
    df_filtered = df_filtered.withColumn("category_label", mapping_expr[func.col("EventRootCode")])

    # ----------------------------------------------------------

    # !! keep only the columns your schema actually needs.
    df_clean = df_filtered.select(
        func.col("GLOBALEVENTID").alias("global_event_id"),
        func.col("sql_date"),
        func.col("Year").alias("year"),
        func.col("month"),
        func.col("quarter"),
        func.col("ActionGeo_ADM1Code").alias("adm1_code"),
        func.col("ActionGeo_FullName").alias("action_geo_full_name"),
        func.col("EventRootCode").alias("event_root_code"),
        func.col("EventBaseCode").alias("event_base_code"),
        func.col("QuadClass").alias("quad_class"),
        func.col("category_label"),
        func.col("Actor1Name").alias("actor1_name"),
        func.col("Actor1CountryCode").alias("actor1_country"),
        func.col("Actor2Name").alias("actor2_name"),
        func.col("Actor2CountryCode").alias("actor2_country"),
        func.col("GoldsteinScale").alias("goldstein_scale"),
        func.col("AvgTone").alias("avg_tone"),
        func.col("NumMentions").alias("num_mentions"),
        func.col("NumSources").alias("num_sources"),
        func.col("NumArticles").alias("num_articles"),
        func.col("SOURCEURL").alias("source_url"),
        func.col("date_added_ts").alias("date_added"),
    )

    # ---------------------------------------------------------

    print("\nSample of cleaned data:")
    df_clean.show(5, truncate=False)

    return df_clean
# ===============================


# ===============================
def write(cleaned_df):
    # ----------------------------------------------------------
    # 5. WRITE -- save as parquet. overwrite = current script get replaced
    # ----------------------------------------------------------
    cleaned_df.write.mode("overwrite").parquet(OUTPUT_DIR)
    print(f"\nWrote cleaned data to {OUTPUT_DIR}")
# ===============================



def main():
    
    # [1] initialize SparkSession (the entry point)
    print("hmm")
    spark = SparkSession.builder \
        .appName("SACivicPulseTransform") \
        .getOrCreate()
    
#--------------------------------------------------------------------------

    # [2] READ 
    df_read = read(spark)
    total_count = df_read.count()
    print(f"----- Loaded {total_count} total rows from all raw files.")

#--------------------------------------------------------------------------

    # [3] FILTER  -- keep only South African rows
    df_filter = filter(df_read)

    result_count = df_filter.count()
    print(f"Filtered down to {result_count} South African rows "
        f"({result_count / total_count * 100:.2f}% of total).")

#--------------------------------------------------------------------------

    # [4] WRITE -- save as parquet (column-oriented binary data storage format)
    write(df_filter)

#--------------------------------------------------------------------------

    # [5] end session
    spark.stop()



if __name__ == "__main__":
    main()

    