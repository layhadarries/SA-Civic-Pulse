# TODO: day 4 + 5 (and 6 i think)
"""
open pyspark, get data, idk idk get data together ( this layer is cleaning and shit)

PySpark is the Python API for Apache Spark, 
designed to process large-scale datasets distributed across clusters of machines. 

Learning it revolves around understanding distributed architecture, 
transitioning from single-node tools like pandas, 
and mastering Spark SQL and DataFrame operations.


NOTE !!! PySpark comes with SparkSQL. idk the format diff

[1] first initialise the SparkSession
    we use:

    SparkSession.builder \
    .appName("") \
    .master("") \
    .getOrCreate()

[2] get data fields from example
    iterate through the csv file and get the data in those fields
    we use:

    data = [("x", "y", "z")]
    columns = ["xx", "yy", "zz"]

    df = spark.createDataFrame(data, columns) # zip action pretty much which is neat

------------------------------------------------------------------------------------
1] READ    -- load all the raw CSVs into one big Spark DataFrame
2] FILTER  -- keep only South African rows
3] SELECT  -- keep only the columns we actually care about
4] DERIVE  -- compute new columns from existing ones (date parts, category labels)
5] WRITE   -- save the result as parquet
------------------------------------------------------------------------------------




from pyspark.sql import SparkSession

def get_csv_data(csv_file):
    csv_data = []

    with() as file:
        csv.append(file)    

"""

from pyspark.sql import *
from pyspark.sql import functions as F

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

# maunally set the schema attributes with:
# "name", "data_type", "null" (True for optional, False for mandatory)


GDELT_SCHEMA = StructType([
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



# 1. Initialize SparkSession (the entry point)
spark = SparkSession.builder \
    .appName("SataExtraction") \
    .master("local[*]") \
    .getOrCreate()

# 2. Create sample data
data = [
    ("Alice", "Engineering", 95000),
    ("Bob", "Marketing", 62000),
    ("Charlie", "Engineering", 105000),
    ("Diana", "Marketing", 75000),
]
columns = ["name", "department", "salary"]

df = spark.createDataFrame(data, columns)

# 3. Transform: Calculate average salary and headcount by department
summary_df = df.groupBy("department").agg(
    F.round(F.avg("salary"), 2).alias("avg_salary"),
    F.count("name").alias("headcount")
)

print()
print("-----------------------------")
# 4. Action: Display the result
summary_df.show()
print("-----------------------------")
print()
# 5. Stop the session
spark.stop()
